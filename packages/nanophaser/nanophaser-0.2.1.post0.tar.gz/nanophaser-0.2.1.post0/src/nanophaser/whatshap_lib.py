import subprocess, sys
from nanophaser.utils import check_executables, log
from nanophaser import utils, run_minimap

def call_variants(ref, bam, vcf):
    """Call variants using bcftools from aligned BAM file."""
    
    check_executables(required=['bcftools'])
    
    # Run bcftools mpileup and call variants
    # -B: disable BAQ computation (not suitable for long reads)
    # -Q 7: minimum base quality (lower for ONT data)
    # -a FORMAT/AD,FORMAT/DP: output allele depth and depth info
    # -f: reference fasta
    # -Ou: output uncompressed BCF to pipe
    # -mv: multiallelic caller, output variant sites only
    # -Ov: output VCF format
    cmd = f"bcftools mpileup -B -Q 7 -a FORMAT/AD,FORMAT/DP -f {ref} {bam} -Ou | bcftools call -mv -Ov -o {vcf}"
    log(f"Variant calling: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        log(f"Error during variant calling: {e.stderr}")
        raise
    

def run(ref, bam, vcf, fasta, input_vcf):
    """
    Run whatshap variant calling.
    """
    
    # Check if longshot is installed
    check_executables(required = ['whatshap'])
	

    log(f"BAM: {bam}")
    log(f"REF: {ref}")

    # Call the variants.
    call_variants(ref=ref, bam=bam, vcf=input_vcf)


    log(f"REF: {ref}")
    log(f"BAM: {bam}")

    cmd = f"whatshap phase -o {vcf} --reference={ref} {input_vcf} {bam}"
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
    whatshapbam = utils.swap_ext(fasta, 'bam')
    run_minimap.align(ref=ref, fastq=fasta, bam=whatshapbam)

    log(f"VCF: {vcf}")
    log(f"FASTA: {fasta}")
    log(f"BAM: {whatshapbam}")
