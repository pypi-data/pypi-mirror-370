import subprocess, sys, json
from nanophaser.utils import check_executables, log
import nanophaser.utils as utils
from cyvcf2 import VCF
import pysam
from collections import  Counter
from itertools import *
from pprint import pprint
import click
from tqdm import tqdm

MIN_LEN = 200

def run(ref=utils.DEFAULT_REF, fastq=None, bam=utils.DEFAULT_BAM, vcf=utils.DEFAULT_VCF, fasta=utils.DEFAULT_FASTA, min_len=MIN_LEN, limit=2):
    # Create the bam for the haplotype.
    from nanophaser import run_minimap

    # If a fastq file is provided, align the reads to the reference.
    if fastq:
        run_minimap.align(ref=ref, fastq=fastq, bam=bam)

    log(f"BAM: {bam}")
    log(f"REF: {ref}")
    log(f"MIN_LEN: {min_len}")
    # Call the variants with minipileup.

    if utils.is_empty(bam):
        print("# Waring: the BAM does not contain alignments.")
    
    
    call(ref=ref, bam=bam, vcf=vcf, min_len=min_len)

    # Phase the variants.
    phase(ref=ref, bam=bam, vcf=vcf, out=fasta, limit=limit)

    # Create the bam for the haplotype.
    hapbam = utils.swap_ext(fasta, 'bam')
    run_minimap.align(ref=ref, fastq=fasta, bam=hapbam)

    log(f"VCF: {vcf}")
    log(f"FASTA: {fasta}")
    log(f"HAPBAM: {hapbam}")

def call(ref, bam, vcf, min_len=MIN_LEN):
    """
    Run minipile and generates a phased VCF
    """

    # Construct and run the pipeline command
    cmd = f"minipileup -l {min_len} -vc -p 0.2 -f {ref} {bam} > {vcf}"
    
    # Run the command.
    utils.run_cmd(cmd)

def get_coord(vcf):
    """
    Returns a dictionary keyed by chromosome containing potential variants
    """
    vcf = VCF(vcf)
    data = {}
    for var in vcf:
       key = (var.CHROM, var.POS)
       data[key] = var
    return data

def phase(ref, bam, vcf, out=utils.DEFAULT_FASTA, limit=2):
    """
    Phase a VCF according to the reads in the BAM file.
    """
    variants = get_coord(vcf)

    bam = pysam.AlignmentFile(bam, "rb")
    
    haps = []

    # Get the valid positions
    #valid_pos = set(variants.keys())

    # Fetch all reads for the chromosome
    alns = bam.fetch()

    alns = islice(alns, None)


    # Count the number of aligned reads
    def check_read(read):
        return not read.is_secondary and not read.is_supplementary and read.query_alignment_length >= MIN_LEN

    # Count the number of primary alignments
    count = bam.count(read_callback=check_read)

    log(f"Primary alignments (len>={MIN_LEN}): {count:,d}")
    
    # Filter out secondary and supplementary alignments
    alns = filter(check_read, alns)

    pbar = tqdm(alns, total=count, leave=False)

    # Populate the data list with the aligned reads.
    for aln in pbar:

        hap = []
        
        # Get the read sequence
        query_seq = aln.query_sequence
        chrom = aln.reference_name

        try:
            stream = aln.get_aligned_pairs(with_seq=True)
        except Exception as exc:
            name = aln.query_name
            log(f"BAM processing error: {exc} for {name}") 
            continue
        
        last_ref_idx = None

        # Check the index.
        def get_variant(idx):
            if idx is None:
                return False
            return variants.get((chrom, idx+1))

        for read_idx, ref_idx, ref_seq in stream:

            # The base of the read at the current position
            read_seq = query_seq[read_idx] if read_idx is not None else None

            # Shortcuts
            is_del = read_idx is None
            is_ins = ref_idx is None

            # Get the variant at the current position.
            var = get_variant(ref_idx)

            # The sequence of the reference at the current position
            elem = (read_idx, read_seq, ref_idx, ref_seq)

            if is_del and var:
                # Check if any of the ALT alleles is a deletion
                is_vcf_del = any(len(alt) < len(var.REF) for alt in var.ALT)
                if is_vcf_del:
                    # Deletion from the read. Deletion found in the VCF.
                    seq = ''
                else:
                    # Deletion from the read but not matching VCF deletion
                    seq = ref_seq
            elif is_del and not var:
                # Deletion from the read. Deletion not found in the VCF.
                seq = ref_seq
            elif is_ins and get_variant(last_ref_idx):
                var = get_variant(last_ref_idx)
                is_vcf_ins = any(len(alt) > len(var.REF) for alt in var.ALT)
                if is_vcf_ins:
                    # Confirmed insertion in VCF
                    subset = [elem] + list(takewhile(lambda x: x[1] is None, stream))
                    seq = last_ref_seq + ''.join([query_seq[x[0]] for x in subset])
                else:
                    # Not a matching insertion
                    seq = ''
            elif is_ins and not get_variant(last_ref_idx):
                # Insertion in the read. Insertion not found in the VCF.
                seq = ''
            elif read_seq and ref_seq and (read_seq == ref_seq):
                # Match. Add the read sequence.
                seq = read_seq
            elif read_seq and ref_seq and (read_seq != ref_seq) and var:
                # Check if the mismatch matches any of the ALT alleles
                if read_seq in var.ALT:
                    # Mismatch present in the VCF.
                    seq = read_seq
                else:
                    # Mismatch not present in the VCF.
                    seq = ref_seq.upper()
            elif read_seq and ref_seq and (read_seq != ref_seq) and not var:
                # Mismatch not present in the VCF.
                seq = ref_seq.upper()
            else:
                # All valid states should have been handled by now.
                raise ValueError(f"Invalid state: {elem}")
            
            hap.append(seq)

            # Store the last valid reference position and sequence
            if not is_ins:
                last_ref_idx = ref_idx
                last_ref_seq = ref_seq

        line = ''.join(hap)
        haps.append(line)

    # Count the number of haplotypes
    hap_counts = Counter(haps)
    top10 = hap_counts.most_common(10)
    counts = ', '.join(map(str, (count for _, count in top10)))
    log(f"Haplotypes: {counts}")
    
    fp = open(out, 'w')
    top = hap_counts.most_common(limit)
    for i, (seq, count) in enumerate(top):
        name = f"hap_{i} chrom={chrom} count={count}"
        text = f">{name}\n{seq}\n"
        fp.write(text)
        log(f"Haplotype: {name}")
    
    log(f"Top {limit} haplotypes saved to: {out}")


def classify(subject=utils.DEFAULT_ALLELES, query=utils.DEFAULT_FASTA,  out="blastout.txt", params=None, eval=None, bam=utils.DEFAULT_BAM):
    utils.check_executables(required = ['blastn'])

    PIDENT = 'pident'
    FIELDS = f"qseqid sseqid {PIDENT} length qlen qcovhsp"


    cmd = f"blastn -query {query} -subject {subject} -out {out} -outfmt '7 {FIELDS}'"
    log(f"Classifying: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        if utils.is_empty(bam):
            print("# Warning: the BAM does not contain alignments.")
            pass
        else:
            log(f"Error during classifying: {e.stderr}")
            raise
    
    hits = {}
    stream = open(out, 'r')
    stream = map(lambda line: line.strip(), stream)
    stream = filter(lambda line: not line.startswith('#'), stream)
    stream = filter(None, stream)
    keys = FIELDS.split()
    #stream = islice(stream, 10)
    for line in stream:
        elems = line.strip().split('\t')
        data = dict(zip(keys, elems))
        data[PIDENT] = float(data[PIDENT])
        hits.setdefault(data['qseqid'], []).append(data)

    eval = eval or dict()
    params = params or dict()
    params.update(dict(query=query, subject=subject, fields=FIELDS, output=out)) 

    expected = set(eval.get('alleles', []))

    # For each haplotype, select the best hit based on pident
    out = dict(params=params, results=[])
    eps = 0.0001
    for hit in hits:

        vals = hits[hit]
        vals = sorted(vals, key=lambda x: x[PIDENT], reverse=True)
        best = vals[0]
        alleles = [ v['sseqid'] for v in vals if abs(v[PIDENT] - best[PIDENT]) < eps ]
        
        data = dict(query=hit, pident=best[PIDENT], alleles=alleles)

        if expected:
            data['match'] = bool(set(alleles) & expected)
   
        out['results'].append(data)
    
    return out


def eval(seed, fastq, fasta, alleles):

    params = utils.make_data(fastq=fastq, seed=seed)
    
    run(fastq=fastq)

    res = classify(subject=alleles, query=fasta, params=params, eval=params)
  
    text = json.dumps(res, indent=4)

    print(text)

if __name__ == "__main__":
    
    #run()

    eval()