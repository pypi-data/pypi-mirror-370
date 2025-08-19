import sys, random, os, time
import Bio.SeqIO
import click
import subprocess
import pysam
from importlib.resources import files

#DEFAULT_REF = "files/bola_genome.fa" # Default paths for files.
# DEFAULT_REF = "files/bola_genome.fa"
# DEFAULT_FASTQ = "files/test_reads.fq.gz"
# DEFAULT_ALLELES = "files/bola-original-alleles.fa"
# DEFAULT_SUBJECT = "files/bola-truncated-allele.fasta"
DEFAULT_REF     = str(files("nanophaser") / "data" / "bola_genome.fa")
DEFAULT_FASTQ   = str(files("nanophaser") / "data" / "test_reads.fq.gz")
DEFAULT_ALLELES = str(files("nanophaser") / "data" / "bola-original-alleles.fa")
DEFAULT_SUBJECT = str(files("nanophaser") / "data" / "bola-truncated-allele.fasta")

# Output files.
DEFAULT_BAM = "run/alignments.bam"
DEFAULT_CSV = "run/genotypes.csv"
DEFAULT_VCF = "run/variants.vcf"
DEFAULT_INPUT_VCF = "run/variants_input.vcf"
DEFAULT_FASTA = "run/haplotypes.fa"

# Simulation files
SIM_GENOME = "run/simulated_genome.fa"
SIM_READS = "run/simulated_reads.fq"

# Simulation parameters.
def log(msg):
    """
    Message logger.
    """
    print(f"# {msg}", file=sys.stderr)

try:
    from cyvcf2 import VCF
    from pyfaidx import Fasta
except ImportError:
    log("Please install required packages to use this command:")
    log("pip install cyvcf2 pyfaidx")

def check_executables(required = ['samtools']):
    """Check if required executables are available in PATH."""
    for cmd in required:
        # Hacky fix for blastn.
        cmd = 'blastn' if cmd == 'blast' else cmd
        if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
            log(f"Missing executable: {cmd}")
            log(f"Installation: micromamba install {' '.join(required)}")
            sys.exit()

def mkdir(fname):
    """
    Make the directories for a file.
    """
    dirname = os.path.dirname(fname)
    if not os.path.isdir(dirname):
        os.makedirs(dirname, exist_ok=True)

def add_errors(seq, error_rate=0.01):
    """
    Add random sequencing errors to a DNA sequence.
    """
    nucleotides = ['A', 'C', 'G', 'T']
    output = list(seq)
    
    for i in range(len(output)):
        if random.random() < error_rate:
            # Get the reference nucleotide
            ref = output[i]

            # Randomly choose a different nucleotide
            alt = random.choice(nucleotides)

            # Make sure the alternative nucleotide is different from the reference
            while alt == ref:
                alt = random.choice(nucleotides)

            # Replace the reference nucleotide with the alternative
            output[i] = alt
    
    return ''.join(output)

def make_data(alleles=DEFAULT_ALLELES, genome=SIM_GENOME, coverage=100, error_model="nanopore2023", length="300,30", identity="90,98,5", seed=109, fastq=SIM_READS):
    
    """
    Generate a fastq file with errors from a genome file.
    """

    recs = Bio.SeqIO.parse(alleles, 'fasta')
    recs = list(recs)
    
    # Generate a random seed if not provided.
    #seed = seed
    #seed = random.randint(0, 2**32 - 1) if not seed else seed 
    
    # Set the seed.
    random.seed(seed)
        
    # Shuffle the records.
    random.shuffle(recs)
    
    recs = recs[:2]
    # log(f"Coverage={coverage} Error Model={error_model} Contigs={len(recs)} Seed={seed}")
    # log(f"Allele 1: {recs[0].id}")
    # log(f"Allele 2: {recs[1].id}")
    
    # Make the directory for the genome file.
    if not os.path.exists(genome):
        os.makedirs(os.path.dirname(genome), exist_ok=True)
    
    # Write the selected genome alleles to a fasta file.
    #Bio.SeqIO.write(recs, open(genome, 'w'), 'fasta')
    with open(genome, 'w') as out_handle:
        Bio.SeqIO.write(recs, out_handle, 'fasta')

    log(f"Simulated genome: {genome}")
 

    cmd = f"badread simulate --reference {genome} --quantity {coverage}x --error_model {error_model} --length {length} --qscore_model {error_model}  --identity {identity} --seed {seed} > {fastq}"
    
    run_cmd(cmd, stderr=subprocess.DEVNULL)
    
    # Calculate the coverage.
    # fastq_len = sum(len(rec.seq) for rec in Bio.SeqIO.parse(fastq, 'fastq'))
    # genome_len = sum(len(rec.seq) for rec in Bio.SeqIO.parse(genome, 'fasta'))
    # coverage = round(fastq_len / genome_len, 0)
    res = dict(
        genome=genome,
        fastq=fastq,
        alleles=[recs[0].id, recs[1].id], 
        error_model=error_model, seed=seed,
        coverage=coverage)

    return res



def make_data_old(alleles=DEFAULT_ALLELES, n=1000, err=0.01, genome=SIM_GENOME, fastq=SIM_READS, seed=None):
    """
    Generate a fastq file with errors from a genome file.
    """

    recs = Bio.SeqIO.parse(alleles, 'fasta')
    recs = list(recs)
    
    # Generate a random seed if not provided.
    seed = int(time.time_ns()) if not seed else seed
    
    # Set the seed.
    random.seed(seed)
        
    # Shuffle the records.
    random.shuffle(recs)
    
    recs = recs[:2]
    log(f"Reads={n} Error={err} Contigs={len(recs)} Seed={seed}")
    log(f"Allele 1: {recs[0].id}")
    log(f"Allele 2: {recs[1].id}")
    
    # Make the directory for the genome file.
    if not os.path.exists(genome):
        os.makedirs(os.path.dirname(genome), exist_ok=True)
    
    # Write the selected genome alleles to a fasta file.
    Bio.SeqIO.write(recs, open(genome, 'w'), 'fasta')

    stream = open(fastq, 'w')
    for i in range(n):
        for rec in recs:
            print(f"@{rec.id}|{i}", file=stream)
            if err > 0:
                seq = ins_del(rec.seq, ins=err, del_=err)
                seq = add_errors(seq, err)
            else:
                seq = rec.seq

            trim = random.randint(1, 100)
            if random.random() < 0.5:
                seq = seq[trim:]
            else:
                seq = seq[:-trim]
            print(seq, file=stream)
            print("+", file=stream)
            print("I" * len(seq), file=stream)
    stream.close()
 
    # Calculate the coverage.
    fastq_len = sum(len(rec.seq) for rec in Bio.SeqIO.parse(fastq, 'fastq'))
    genome_len = sum(len(rec.seq) for rec in Bio.SeqIO.parse(genome, 'fasta'))
    coverage = round(fastq_len / genome_len, 0)
    res = dict(
        genome=genome,
        fastq=fastq,
        alleles=[recs[0].id, recs[1].id], 
        N=n, error=err, seed=seed,
        coverage=coverage)

    return res

def ins_del(seq, ins=None, del_=None):
    """
    Insertions and deletions in a sequence.
    """
    output = []
    
    for base in seq:
        # Randomly decide whether to insert or delete
        if random.random() < ins:
            # Insert a random base
            output.append(random.choice(['A', 'C', 'G', 'T']))
        
        if random.random() < del_:
            # Skip the base (deletion)
            continue
        
        # Add the original base
        output.append(base)
    
    return ''.join(output)

def newer(file1, file2):
    """
    Check if file1 is newer than file2.
    """
    
    if not os.path.exists(file1) or not os.path.exists(file2):
        return True
    
    return os.path.getmtime(file1) > os.path.getmtime(file2)


def swap_ext(fname,  ext):
    """
    Swap the extension of a filename.
    """
    name, _ = os.path.splitext(fname)
    name = f"{name}.{ext}"
    return name

def evaluate(info_res, info_make, fname='logging.txt'):
    """
    Evaluate the nanophaser pipeline.
    """

    # Write the header to the logfile
    if not os.path.isfile(fname):
        stream = open(fname, 'w')
        stream.write(f"label\tseed\tmethod\tpident\tsseqid\n")
        stream.close()

    # Open the logfile for appending
    stream = open(fname, 'a')

    params = dict(info_res['params'])
    
    data = dict(params)
    data.update(info_make)
    seed = data['seed']
    method = data['method']

    # Input alleles
    expected_alleles = set(data['alleles'])

    new_alleles = []
    
    results = info_res['results']
    
    # Sort the results by sseqid
    results.sort(key=lambda x: x['sseqid'])

    for row in results:
        pident = row['pident']
        sseqid = row['sseqid']
        equiv  = set(row['equivalent_alleles'])
        
        if expected_alleles.intersection(equiv):
            label = 'MATCH' if pident > 99.999 else 'PARTIAL'
            row = [sseqid, label, pident]
            line = f"{label}\t{seed}\t{method}\t{pident}\t{sseqid}"
        else:
            label = 'MISS'
            row = [sseqid, label, pident]
            line = f"{label}\t{seed}\t{method}\t{pident}\t{sseqid}"

        # Append the row to the new alleles
        new_alleles.append(row)

        # Print line to the screen and the log file.
        log(line)
        print(line, file=stream)

    data['alleles'] = new_alleles

    return data

def vcf2fasta(ref, vcf, fname=None):
    """
    Convert a VCF file to a FASTA file.
    Handles variable numbers of samples/haplotypes.
    """
    # If no output file is provided, use stdin
    vcf = vcf if vcf else sys.stdin

    # Load reference sequence
    ref = Fasta(ref)
    vcf_reader = VCF(vcf)
    
    # Get number of samples in VCF
    num_samples = len(vcf_reader.samples) if vcf_reader.samples else 1
    
    # Collect variants by chromosome
    vars = {}
    for variant in vcf_reader:
        vars.setdefault(variant.CHROM, []).append(variant)

    # Dictionary to store haplotypes for each sample
    all_haplotypes = {}
    
    # Process each chromosome in the reference
    for chrom in ref.keys():
        ref_seq = str(ref[chrom])
        
        # Initialize haplotypes for each sample
        # Each sample can have multiple haplotypes (usually 2 for diploid)
        sample_haplotypes = {}
        
        # Process each sample
        for sample_idx in range(num_samples):
            sample_name = vcf_reader.samples[sample_idx] if vcf_reader.samples else f"sample_{sample_idx}"
            
            # Determine ploidy from first variant (if any)
            ploidy = 2  # Default to diploid
            if chrom in vars and vars[chrom]:
                first_variant = vars[chrom][0]
                if sample_idx < len(first_variant.genotypes):
                    # Count non-None values in genotype (excluding phasing info)
                    gt = first_variant.genotypes[sample_idx]
                    ploidy = sum(1 for x in gt[:-1] if x is not None)
            
            # Initialize haplotypes for this sample
            sample_haplotypes[sample_name] = [list(ref_seq) for _ in range(ploidy)]
        
        # Process variants for this chromosome
        if chrom in vars:
            for variant in vars[chrom]:
                pos = variant.POS - 1  # Convert to 0-based position
                ref_allele = variant.REF
                alt_alleles = variant.ALT
                
                # Create alleles list
                alleles = [ref_allele] + alt_alleles
                
                # Process each sample
                for sample_idx, (sample_name, haplotypes) in enumerate(sample_haplotypes.items()):
                    if sample_idx >= len(variant.genotypes):
                        # No genotype for this sample, keep reference
                        continue
                    
                    gt = variant.genotypes[sample_idx]
                    
                    # Process each haplotype for this sample
                    for hap_idx in range(len(haplotypes)):
                        if hap_idx >= len(gt) - 1:  # -1 because last element is phasing
                            continue
                            
                        allele_idx = gt[hap_idx]
                        
                        # Handle missing genotypes
                        if allele_idx is None or allele_idx == -1:
                            continue
                        
                        # Check if allele index is valid
                        if 0 <= allele_idx < len(alleles):
                            allele = alleles[allele_idx]
                            # Replace reference bases with variant alleles
                            haplotypes[hap_idx][pos:pos+len(ref_allele)] = list(allele)
                        else:
                            log(f"Warning: Invalid allele index {allele_idx} at position {variant.POS} "
                                f"(only {len(alleles)} alleles available)")
        
        # Store completed haplotypes
        for sample_name, haplotypes in sample_haplotypes.items():
            if sample_name not in all_haplotypes:
                all_haplotypes[sample_name] = {}
            all_haplotypes[sample_name][chrom] = [''.join(hap) for hap in haplotypes]
    
    # Generate the text output
    lines = []
    hap_counter = 1
    
    # If only one sample, use simple haplotype naming
    if num_samples == 1:
        sample_name = list(all_haplotypes.keys())[0]
        for chrom_haps in all_haplotypes[sample_name].values():
            for hap_idx, hap_seq in enumerate(chrom_haps):
                lines.append(f">haplotype_{hap_counter}")
                lines.append(hap_seq)
                hap_counter += 1
    else:
        # Multiple samples: include sample name in haplotype ID
        for sample_name, sample_data in all_haplotypes.items():
            for chrom, chrom_haps in sample_data.items():
                for hap_idx, hap_seq in enumerate(chrom_haps):
                    lines.append(f">haplotype_{hap_counter}_{sample_name}_hap{hap_idx+1}")
                    lines.append(hap_seq)
                    hap_counter += 1
    
    # Handle case where no haplotypes were generated
    if not lines:
        log("Warning: No haplotypes generated from VCF")
        # Return reference sequence as default
        for chrom in ref.keys():
            lines.append(f">haplotype_1")
            lines.append(str(ref[chrom]))
            break  # Just use first chromosome
    
    # Write the text output
    stream = sys.stdout if fname is None else open(fname, 'w')
    stream.write("\n".join(lines))
    if fname is not None:
        stream.close()

def trim_fasta(bam_path, fasta):
    """
    Trim the reads in a fasta file to match the region defined by the BAM file.
    The original FASTA will be replaced with the trimmed version.
    """
    start = 999999
    end = 0
    with pysam.AlignmentFile(bam_path, "rb") as bam:
        for read in bam:
            # Only process mapped reads
            if read.is_unmapped:
                continue
            if read.reference_start < start:
                start = read.reference_start 
            if read.reference_end is not None and read.reference_end > end:
                end = read.reference_end 

    # Create a temporary filename for the trimmed FASTA.
    temp_fasta = fasta + ".tmp"
    
    # Process the FASTA file: accumulate sequences and trim them.
    with open(fasta, "r") as fin, open(temp_fasta, "w") as fout:
        seq_lines = []
        for line in fin:
            if line.startswith(">"):
                # Process previous sequence, if any.
                if seq_lines:
                    full_seq = "".join(seq_lines)
                    trimmed_seq = full_seq[start:end]
                    fout.write(trimmed_seq + "\n")
                    seq_lines = []
                # Write out the header as is.
                fout.write(line)
            else:
                seq_lines.append(line.strip())
        # Handle any final sequence.
        if seq_lines:
            full_seq = "".join(seq_lines)
            trimmed_seq = full_seq[start:end]
            fout.write(trimmed_seq + "\n")
    
    # Replace the original FASTA with the trimmed file.
    os.replace(temp_fasta, fasta)
    return fasta


def run_cmd(cmd, stderr=subprocess.PIPE):
    """
    Run a command and check for errors.
    """

    # Log the command.
    log(f"{cmd}")

    # First word is the executable.
    exe = cmd.split()[0]
    check_executables(required = [exe])
    
    # Run the command.
    try:
        status = subprocess.run(cmd, shell=True, check=True, stderr=stderr, text=True)
        if status.returncode != 0:
            log(f"Error: {exe} failed with exit code {status.returncode}")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        log(f"Error: {exe} failed with exception {e}")
        sys.exit(1)


def is_empty(bam_path):

    try:
        with pysam.AlignmentFile(bam_path, "rb") as bam:
            return bam.mapped == 0
    except Exception as e:
        log(f"BAM file {bam_path} error: {e}")
        return sys.exit(1)

if __name__ == "__main__":

	#To make 1000 reads
    make_data(alleles="files/bola-original-alleles.fa", coverage=5, genome="run/simulated_genome.fa", fastq="run/simulated_reads.fq")

    # ref = "refs/bola_genome.fa"
    # vcf = "eval/variants.vcf"
    # vcf2fasta(ref, vcf)
