import re
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq

class Simulator:
    def __init__(self, args):
        self.reference = args.reference
        self.pool_fasta = args.pool
        self.bed_file = args.bed
        self.output_prefix = args.outprefix
        self.num_genomes = args.num
        self.af_min = args.af_min
        self.af_max = args.af_max
        self.tsd_min = args.tsd_min
        self.tsd_max = args.tsd_max
        self.sense_strand_ratio = args.sense_strand_ratio
        self.random_seed = args.seed
        self.verbose = args.verbose

        self.TEevents = []
        #self.genotypes = ""
        if self.random_seed is not None:
            np.random.seed(self.random_seed)
    
    def _run(self):
        self._parse_bed()
        self._check_bed()
        self._random_sample_genotypes()
        self.get_TE_tag()
        self.generate_vcf()
        self.generate_genome()

    def _check_bed(self):
        ref_record = next(SeqIO.parse(self.reference, "fasta"))
        self.CHR = ref_record.id
        self.ref_seq = str(ref_record.seq)
        prev_start = -1
        prev_end = -1
        for event in self.TEevents:
            start = event["start"]
            end = event["end"]
            if start >= end:
                raise ValueError(f"Invalid TE event: start >= end. Position: {start}")
            if start < 0 or end > len(self.ref_seq):
                raise ValueError(f"TE event out of genome bounds. Position: {start}")
            if start < prev_start:
                raise ValueError(f"bed file not be sorted by start position. Position: {start}")
            if start < prev_end:
                raise ValueError(f"Overlapping TE events detected. Position: {start}")

    def _parse_bed(self):
        """
        """
        self.TEevents = []
        with open(self.bed_file) as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                _, start, end, te_id = line.strip().split("\t")
                te_id = "DEL" if te_id == "-" else te_id # If TE deletion has no ID, assign "DEL"
                start = int(start)
                end = int(end)
                event_type = "INS" if end == start + 1 else "DEL"
                self.TEevents.append({
                    "start": start,
                    "end": end,
                    "te_id": te_id,
                    "type": event_type
                })
        if self.verbose:
            print(f"[INFO] Parsed {len(self.TEevents)} TE events from BED.")
            print(f"[INFO] Example event: {self.TEevents[0] if self.TEevents else 'No events'}")
    
    def _random_sample_genotypes(self):
        """
        Randomly generate an allele frequency for each TE event, and then generate the genotype for each sample based on that frequency.
        """
        # 1. allele frequency
        nTE = len(self.TEevents)
        afs = np.random.uniform(self.af_min, self.af_max, size=nTE)

        # 2. sample genotypes
        self.genotypes = np.zeros((nTE, self.num_genomes), dtype=int)
        for i, af in enumerate(afs):
            self.genotypes[i] = np.random.binomial(1, af, size=self.num_genomes)

        if self.verbose:
            print(f"[INFO] Generated genotypes for {nTE} events across {self.num_genomes} genomes.")
            print(f"[INFO] Allele frequencies (first 10): {afs[:10]}")
            # print(f"[INFO] Example genotypes (first 5 events):\n{self.genotypes[:5]}")

        return self.genotypes    

    def get_TE_tag(self):
        """
        Generate additional metadata for each TE event:
        strand: the insertion orientation ("+" or "-")
        tsd_len: TSD length (from tsd_min to tsd_max)
        ref: reference sequence
        alt: variant sequence (including the result after TE insertion or deletion)"
        """
        # TE pool
        te_pool = {rec.id: rec.seq for rec in SeqIO.parse(self.pool_fasta, "fasta")}
        for event in self.TEevents:
            start, end, te_id = event["start"], event["end"], event["te_id"]
            # strand
            strand = "+" if np.random.rand() < self.sense_strand_ratio else "-"
            # tsd length
            tsd_len = np.random.randint(self.tsd_min, self.tsd_max + 1)
            if event["type"] == "INS":
                # bed file is 0-based
                ref_allele = self.ref_seq[start - 1]
                te_seq = te_pool[te_id]
                if strand == "-":
                    te_seq = str(te_seq.reverse_complement())
                # tsd_seq = ref_seq[start-tsd_len : start]
                tsd_seq = self.ref_seq[start-tsd_len+1 : start+1]
                alt_allele = self.ref_seq[start - 1] + str(te_seq) + tsd_seq
            else:
                # REF sequence
                ref_allele = self.ref_seq[start-1:end]
                alt_allele = self.ref_seq[start-1]
            # update TE tags
            event.update({
                "strand": strand,
                "tsd_len": tsd_len,
                "ref": ref_allele,
                "alt": alt_allele
            })
    
    def _parse_te_modification(self, te_id: str):
        """
        Parse TE ID into family name and modifications.
        Example: "LINE_1SNP0INDEL5polyA" → ("LINE", {"nSNP":1, "npolyA":5})
        """
        te_family = te_id
        mods = {}
        if "_" in te_id:
            te_family, mod_str = te_id.rsplit("_", 1)
            for key in ["SNP", "INDEL", "polyA", "truncate"]:
                match = re.search(rf"(\d+){key}", mod_str)
                if match:
                    val = int(match.group(1))
                    if val > 0:
                        mods["n" + key] = val
        return te_family, mods
    

    def generate_vcf(self):
        """
        Generate a VCF file from parsed TE events with detailed INFO.
        INFO includes:
            - TYPE: INS or DEL
            - STRAND: +/-
            - TSD: Target site duplication length
            - TEFAMILY: TE family ID (from consensus)
            - SNP/INDEL/polyA/truncate: modification counts (only for INS)
        """
        vcf_path = f"{self.output_prefix}.vcf"
        with open(vcf_path, "w") as vcf:
            # VCF Header
            vcf.write("##fileformat=VCFv4.2\n")
            vcf.write('##INFO=<ID=TYPE,Number=1,Type=String,Description="Variant type (INS or DEL)">\n')
            vcf.write('##INFO=<ID=STRAND,Number=1,Type=String,Description="Insertion strand (+ or -)">\n')
            vcf.write('##INFO=<ID=TSD,Number=1,Type=Integer,Description="Target site duplication length">\n')
            vcf.write('##INFO=<ID=TEFAMILY,Number=1,Type=String,Description="TE family ID from consensus">\n')
            vcf.write('##INFO=<ID=SNP,Number=1,Type=Integer,Description="Number of SNP modifications in TE sequence">\n')
            vcf.write('##INFO=<ID=INDEL,Number=1,Type=Integer,Description="Number of INDEL modifications in TE sequence">\n')
            vcf.write('##INFO=<ID=polyA,Number=1,Type=Integer,Description="Length of added polyA tail in TE sequence">\n')
            vcf.write('##INFO=<ID=truncate,Number=1,Type=Integer,Description="Number of truncated bases at 5\' end of TE sequence">\n')
            samples = [f"Hap{i+1}" for i in range(self.num_genomes)]
            vcf.write(f"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(samples) + "\n")

            for idx, event in enumerate(self.TEevents):
                chrom = self.CHR
                # Although BED files are 0-based and VCF files are 1-based, 
                # VCF files require retrieving one base upstream, so the overall position remains unchanged.
                pos = event["start"]
                var_id = event["te_id"]
                ref = event["ref"]
                alt = str(event["alt"])
                event_type = event["type"]
                strand = event["strand"]
                tsd = event["tsd_len"]

                # parse TEID: TE family + modified information
                te_family, mods = self._parse_te_modification(var_id)

                # INFO
                info_parts = [
                    f"TYPE={event_type}",
                    f"STRAND={strand}",
                    f"TSD={tsd}",
                    f"TEFAMILY={te_family}"
                ]
                if event_type == "INS":  # only insert needs to be changed
                    for key in ["SNP", "INDEL", "polyA", "truncate"]:
                        val = mods.get("n" + key)
                        if val is not None:
                            info_parts.append(f"{key}={val}")

                info_str = ";".join(info_parts)
                genotypes = list(map(str, self.genotypes[idx]))
                vcf.write(f"{chrom}\t{pos}\t{var_id}\t{ref}\t{alt}\t.\tPASS\t{info_str}\tGT\t" + "\t".join(genotypes) + "\n")

        if self.verbose:
            print(f"[INFO] VCF file written to {vcf_path}")


    def generate_genome(self):
        """
        Generate the genome sequence for each sample based on the genotype matrix and variant information.
        """
        # TE sequences
        ref_seq = str(next(SeqIO.parse(self.reference, "fasta")).seq)

        # split genome
        chunks = []
        cols_to_replace = []
        flipped = []
        col_index = 0
        start = 0
        for event in self.TEevents:
            SVtype = event['type']
            left = event['start']
            right = event['end']
            if left != start:
                if SVtype == "INS":
                    chunks.append(ref_seq[start:left+1])
                else:
                    chunks.append(ref_seq[start:left])
                col_index += 1
            if SVtype == "INS":
                chunks.append(event["alt"][1:])
            else:
                chunks.append(event["ref"][1:])
                flipped.append(col_index)
            cols_to_replace.append(col_index)
            col_index += 1
            start = right    

        # Check if the last TE occurs at the end of the genome
        genome_len = len(ref_seq)
        if right != genome_len:
            chunks.append(ref_seq[right:genome_len])

        # combine genome
        with open(f"{self.output_prefix}.fa", "w") as fo:
            indexMat = np.ones((len(chunks), self.num_genomes))
            indexMat[cols_to_replace,:] = self.genotypes
            for idx in range(self.num_genomes):
                mask = indexMat[:, idx].astype(bool)
                mask[flipped] = ~mask[flipped]
                assembly = ''.join(chunk for chunk, use in zip(chunks, mask) if use)
                fo.write(f">Hap{idx+1}\n")
                for i in range(0, len(assembly), 60):
                    fo.write(assembly[i:i+60] + "\n") 

        """
        for k, v in locals().items():
            if k != 'self':
                setattr(self, k, v)          
        """

def run(args):
    Simulator(args)._run()