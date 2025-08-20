import numpy as np
import logging
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def is_dna(seq: Seq) -> bool:
    return set(str(seq)) <= set("ATGCN")

class TEPoolBuilder:
    def __init__(self, args):
        # base
        self.consensus = args.consensus
        self.num = args.num
        self.prefix = args.outprefix
        # SNP and INDEL
        self.snp_rate = args.snp_rate
        self.indel_rate = args.indel_rate
        self.ins_ratio = args.ins_ratio
        self.indel_geom_p = args.indel_geom_p
        # truncate
        self.truncated_ratio = args.truncated_ratio
        self.truncated_max_length = args.truncated_max_length
        # polyA
        self.polyA_ratio = args.polyA_ratio
        self.polyA_min = args.polyA_min
        self.polyA_max = args.polyA_max
        # other
        self.random_seed = args.seed
        self.verbose = args.verbose
        if self.random_seed is not None:
            np.random.seed(self.random_seed)
        if self.verbose:
            logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
        
        # data stored
        self.BASES = ['A', 'C', 'G', 'T']
        self.CHOICES_DICT = {b: [c for c in self.BASES if c != b] for b in self.BASES}
        self.current_seq = []
        self.seqID_suffix = ""

    def _run(self):
        records = list(SeqIO.parse(self.consensus, "fasta"))
        if not records:
            raise ValueError(f"No sequences found in consensus FASTA: {self.consensus}")
        logging.info(f"Found {len(records)} sequences in consensus FASTA.")
        # check if all sequence are legal
        for record in records:
            record.seq = record.seq.upper()
            if not is_dna(record.seq):
                raise ValueError(f"Invalid characters found in {record.id}")
        
        # generate random masks for truncation and polyA
        truncated_num = np.random.random(self.num)
        polyA_num = np.random.random(self.num)
        trunc_mask = truncated_num < self.truncated_ratio
        polyA_mask = polyA_num < self.polyA_ratio
        mutate = np.select(
            [trunc_mask & polyA_mask, trunc_mask, polyA_mask],
            [3, 2, 1],
            default=0
        )

        # map numbers to corresponding functions
        func_map = {
            0: lambda: self.INDEL_mutate().SNP_mutate(),
            1: lambda: self.INDEL_mutate().SNP_mutate().apply_polyA(),
            2: lambda: self.INDEL_mutate().SNP_mutate().apply_truncate(),
            3: lambda: self.INDEL_mutate().SNP_mutate().apply_truncate().apply_polyA()
        }

        out_records = []
        for j in mutate:
            idx = np.random.randint(0, len(records))
            record = records[idx]
            self.current_seq = list(str(record.seq))
            self.seqID_suffix = ""  # reset suffix each loop
            func_map[j]()
            new_id = f"{record.id}_{self.seqID_suffix}"
            new_record = SeqRecord(Seq("".join(self.current_seq)), id=new_id, description="")
            out_records.append(new_record)

        # output
        output_fasta = self.prefix if self.prefix.endswith(".fasta") else self.prefix + ".fasta"
        SeqIO.write(out_records, output_fasta, "fasta")
        logging.info(f"Generated {len(out_records)} sequences -> {output_fasta}")
    

    def apply_truncate(self):
        max_trunc = int(len(self.current_seq) * self.truncated_max_length)
        if max_trunc < 1:
            return self
        trunc_len = np.random.randint(1, max_trunc + 1)  # inclusive upper bound
        self.current_seq = self.current_seq[trunc_len:]
        self.seqID_suffix += f"{trunc_len}truncate"
        return self

    def apply_polyA(self):
        polyA_len = np.random.randint(self.polyA_min, self.polyA_max + 1)
        self.current_seq.extend(["A"] * polyA_len)
        self.seqID_suffix += f"{polyA_len}polyA"
        return self
    
    def SNP_mutate(self):
        L = len(self.current_seq)
        n_snp = np.random.poisson(self.snp_rate * L)
        if n_snp < 1:
            return self
        self.seqID_suffix += f"{n_snp}SNP"
        # SNP positions, ensure not exceeding sequence length
        snp_positions = np.random.choice(L, size=min(n_snp, L), replace=False)
        for pos in snp_positions:
            current_base = self.current_seq[pos]
            if current_base in self.CHOICES_DICT:
                self.current_seq[pos] = np.random.choice(self.CHOICES_DICT[current_base])
        return self
    
    def INDEL_mutate(self):
        # total INDEL number
        L = len(self.current_seq)
        n_indel = np.random.poisson(self.indel_rate * L)
        if n_indel < 1:
            return self
        self.seqID_suffix += f"{n_indel}INDEL"
        if n_indel == 0:
            return self
        # generate INDEL lengths
        indel_len_list = np.random.geometric(self.indel_geom_p, n_indel)
        indel_len_list = np.clip(indel_len_list, a_min=None, a_max=30)
        # select positions for INDELs
        indel_positions = np.random.choice(L, size=min(n_indel, L), replace=False)
        for pos, indel_len in zip(sorted(indel_positions, reverse=True), indel_len_list):
            if np.random.random() < self.ins_ratio:
                ins_seq = [np.random.choice(self.BASES) for _ in range(indel_len)]
                self.current_seq[pos:pos] = ins_seq
            else:
                del_end = min(pos + indel_len, len(self.current_seq))
                del self.current_seq[pos:del_end]
        return self

def run(args):
    TEPoolBuilder(args)._run()
    

"""
    def apply_mutate(self):
        L = len(self.current_seq)
        bases = ['A', 'C', 'G', 'T']
        # SNP
        n_snp = np.random.poisson(self.snp_rate * L)
        self.seqID_suffix += f"{n_snp}SNP"
        all_positions = list(range(L))
        # Prevent excessively large values being drawn from the Poisson distribution
        snp_positions = set(random.sample(all_positions, min(n_snp, L)))
        # INDEL
        remaining_positions = list(set(all_positions) - snp_positions)
        n_indel = np.random.poisson(self.indel_rate * L)
        self.seqID_suffix += f"{n_indel}INDEL"
        indel_positions = set(random.sample(remaining_positions, min(n_indel, len(remaining_positions))))
        # 修改 SNP
        for pos in sorted(snp_positions):
            current_base = self.current_seq[pos]
            if current_base in bases:
                choices = [b for b in bases if b != current_base]
                self.current_seq[pos] = random.choice(choices)
        # 修改 INDEL
        indel_len_list = np.random.geometric(self.indel_geom_p, n_indel)
        # Limit the maximum INDEL length to 30
        indel_len_list = np.clip(indel_len_list, a_min=None, a_max=30) 
        for pos, indel_len in zip(sorted(indel_positions, reverse=True), indel_len_list):
            if random.random() < self.ins_ratio:  # 插入
                ins_seq = [random.choice(bases) for _ in range(indel_len)]
                self.current_seq[pos:pos] = ins_seq
            else:  # 删除
                del_end = min(pos + indel_len, len(self.current_seq))
                del self.current_seq[pos:del_end]
        return self
        
"""


