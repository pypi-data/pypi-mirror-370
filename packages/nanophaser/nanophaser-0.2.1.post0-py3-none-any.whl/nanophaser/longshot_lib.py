
import subprocess, sys
from nanophaser.utils import check_executables, log
from nanophaser import utils, run_minimap

def run(ref, bam, vcf, fasta):
    """
    Run longshot variant calling.
    """
    
    # Check if longshot is installed
    check_executables(required = ['longshot'])

    log(f"REF: {ref}")
    log(f"BAM: {bam}")

    if utils.is_empty(bam):
        print("# Waring: the BAM does not contain alignments.")

    # Run longshot
    cmd = f"longshot -F --bam {bam} --ref {ref} --out {vcf}"
    log(f"Call: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        if utils.is_empty(bam):
            print("# Waring: the BAM does not contain alignments.")
            pass
        else:
            log(f"Error during variant calling: {e.stderr}")
            raise
    
    utils.vcf2fasta(ref, vcf, fasta)
    fasta = utils.trim_fasta(bam, fasta)
    longshotbam = utils.swap_ext(fasta, 'bam')
    run_minimap.align(ref=ref, fastq=fasta, bam=longshotbam)

    log(f"VCF: {vcf}")
    log(f"FASTA: {fasta}")
    log(f"BAM: {longshotbam}")
