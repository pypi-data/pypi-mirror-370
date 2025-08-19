import click
import os, json, sys
import pandas as pd
from nanophaser import hapcon_lib, longshot_lib, phaser_lib, run_minimap, whatshap_lib
from nanophaser import utils
from nanophaser.utils import log, mkdir
from pathlib import Path

# List of commands in the order we want them to appear
COMMANDS = ['eval', 'align', 'phaser', 'longshot', 'hapcon', 'whatshap', 'classify']

class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super(OrderedGroup, self).__init__(name, commands, **attrs)
        # Commands in the order we want them to appear
        self.command_order = COMMANDS

    def list_commands(self, ctx):
        """Return commands in specified order"""
        return self.command_order
    
@click.group(invoke_without_command=True, cls=OrderedGroup, context_settings={"help_option_names": ['-h', '--help']})
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()

@cli.command()
@click.option("-b", "--bam",   type=click.Path(), default=utils.DEFAULT_BAM)
@click.option("-r", "--reference", type=click.Path(exists=True), default=utils.DEFAULT_REF)
@click.option("-q", "--fastq", type=click.Path(exists=True), default=utils.DEFAULT_FASTQ)
def align(bam, reference, fastq):
    """
    Aligns reads to the reference to create bam file
    """

    if not bam:
        bam = utils.swap_ext(fastq, "bam")
    
    log(f"REF: {reference}")
    log(f"FASTQ: {fastq}")

    # Make the directories for the bam file.
    utils.mkdir(bam)
    sample_name = Path(fastq).stem
    if "." in sample_name:
        name_list = sample_name.split('.')
        sample_name = name_list[0]
    run_minimap.align(reference, fastq, bam, sample_name)
    
    log(f"BAM: {bam}")
    
@cli.command()
@click.option("-r", "--ref", type=click.Path(exists=True), default=utils.DEFAULT_REF, help="The reference genome")
@click.option("-b", "--bam", type=click.Path(exists=True), default=utils.DEFAULT_BAM, help="The bam file")
@click.option("-v", "--vcf", type=click.Path(), default=utils.DEFAULT_VCF, help="The vcf file")
@click.option("-i", "--input_vcf", type=click.Path(), default=utils.DEFAULT_INPUT_VCF, help="The input vcf file")
@click.option("-f", "--fasta", type=click.Path(), default=utils.DEFAULT_FASTA, help="The output fasta file")
def whatshap(ref, bam, vcf, input_vcf, fasta):
    """
    Generates haplotypes using the longshot tool.
    """
    #whatshap_lib.call_variants(ref, bam, input_vcf)
    whatshap_lib.run(ref=ref, bam=bam, vcf=vcf, fasta=fasta, input_vcf=input_vcf)

@cli.command()
@click.option("-r", "--ref", type=click.Path(exists=True), default=utils.DEFAULT_REF, help="The reference genome")
@click.option("-b", "--bam", type=click.Path(exists=True), default=utils.DEFAULT_BAM, help="The bam file")
@click.option("-v", "--vcf", type=click.Path(), default=utils.DEFAULT_VCF, help="The vcf file")
@click.option("-f", "--fasta", type=click.Path(), default=utils.DEFAULT_FASTA, help="The output fasta file")
def longshot(ref, bam, vcf, fasta):
    """
    Generates haplotypes using the longshot tool.
    """
    longshot_lib.run(ref=ref, bam=bam, vcf=vcf, fasta=fasta)

@cli.command()
@click.option("-r", "--ref", type=click.Path(exists=True), default=utils.DEFAULT_REF, help="The reference genome")
@click.option("-b", "--bam", type=click.Path(exists=True), default=utils.DEFAULT_BAM, help="The bam file")
@click.option("-v", "--vcf", type=click.Path(), default=utils.DEFAULT_VCF, help="The vcf file")
@click.option("-f", "--fasta", type=click.Path(), default=utils.DEFAULT_FASTA, help="The output fasta file")
@click.option("-l", "--limit", type=int, default=2, help="The number of haplotypes to generate")
def hapcon(ref, bam, vcf, fasta, limit):
    """
    Generates haplotypes using the haplotype consensus tool.
    """
    hapcon_lib.run(ref=ref, bam=bam, vcf=vcf, fasta=fasta, limit=limit)

@cli.command()
@click.option("-r", "--ref", type=click.Path(exists=True), default=utils.DEFAULT_REF)
@click.option("-b", "--bam", type=click.Path(), default=utils.DEFAULT_BAM)
@click.option("-g", "--geno", type=click.Path(), default=utils.DEFAULT_CSV)
@click.option("-v", "--vcf", type=click.Path(), default=utils.DEFAULT_VCF)
@click.option("-f", "--fasta", type=click.Path(), default=utils.DEFAULT_FASTA)
@click.option("-t", "--threshold", type=float, default=0.7, help="The number of haplotypes to generate")
def phaser(bam, ref, vcf, geno, fasta, threshold):
    """
    Generates haplotypes using phaser library.
    """
    phaser_lib.run(bam=bam, ref=ref, vcf=vcf, geno=geno, fasta=fasta, threshold=threshold)

@cli.command()
@click.option("-q", "--query", type=click.Path(exists=True), required=True, default=utils.DEFAULT_FASTA)   
@click.option("-s", "--subject", type=click.Path(exists=True), required=True, default=utils.DEFAULT_SUBJECT)
def classify(query, subject):
    """
    Classifies alleles using sequence similarity.
    """
    results = hapcon_lib.classify(query=query, subject=subject)

    output = json.dumps(results, indent=4)
    print(output)
    return output

@cli.command()
@click.option("-a", "--alleles", type=click.Path(exists=True), default=utils.DEFAULT_ALLELES, help="The fasta file that contains the alleles")
@click.option("-r", "--ref", type=click.Path(exists=True), default=utils.DEFAULT_REF, help="The reference genome for alignment")
@click.option("-g", "--genome", type=click.Path(), default=utils.SIM_GENOME, help="The reference genome for alignment")
#@click.option("-n", "--num",   type=int, default=1000, help="The number of reads to generate")
@click.option("-C", "--coverage",   type=int, default=100, help="The coverage")
#@click.option("-e", "--error", type=float, default=0.01, help="The error rate")
@click.option("-e", "--error_model", type=str, default="nanopore2023", help="The error model")
@click.option("-f", "--fasta", type=click.Path(), default=utils.DEFAULT_FASTA, help="The resulting haplotype file")
@click.option("-q", "--fastq", type=click.Path(), default=utils.SIM_READS, help="The simulatedfastq file")
@click.option("-s", "--subject", type=click.Path(exists=True), default=utils.DEFAULT_SUBJECT, help="The subject file for evaluation.")
@click.option("-S", "--seed", type=int, default=0, help="The seed for the random number generator")
@click.option("-b", "--bam", type=click.Path(), default=utils.DEFAULT_BAM, help="The bam file")
@click.option("-I", "--input_vcf", type=click.Path(), default=utils.DEFAULT_INPUT_VCF, help="The input variant file")
@click.option("-v", "--vcf", type=click.Path(), default=utils.DEFAULT_VCF, help="The variant file")
@click.option("-c", "--csv", type=click.Path(), default=utils.DEFAULT_CSV, help="The CSV genotype file")
@click.option("-m", "--method", type=click.Choice(['hapcon', 'longshot', 'phaser', 'whatshap']), default="hapcon", help="The method to evaluate")
@click.option("-l", "--limit", type=int, default=10, help="The number of haplotypes to generate")
@click.option("-t", "--threshold", type=float, default=0.7, help="The threshold for the phaser")
@click.option("-L", "--length", type=str, default="300,30", help="Fragment length distribution (mean,stdev)")
@click.option("-i", "--identity", type=str, default="90,98,5", help="Sequencing identity distribution (mean,max,stdev for beta distribution)")

#def eval(alleles, ref, num, error, fasta, fastq, subject, seed, genome, bam, vcf, csv, method, limit, threshold):
def eval(alleles, ref, coverage, error_model, fasta, fastq, subject, seed, genome, length, identity, bam, vcf, input_vcf, csv, method, limit, threshold):
    """
    Evaluates a method.

    METHOD must be one of: 'hapcon', 'longshot', 'phaser, or whatshap'
    """

    log("nanophaser evaluate")

    required = ['minimap2', 'samtools', 'blast', 'minipileup', 'badread']

    # Add additional executables
    if method in ['longshot']:
        required.append(method)

    if method == 'whatshap':
        required.extend(['whatshap', 'bcftools'])

    utils.check_executables(required = required)
    
    log(f"Alleles: {subject}")

    # Generate the data
    #params = utils.make_data(alleles=alleles, n=num, err=error, genome=genome, fastq=fastq, seed=seed)
    params = utils.make_data(alleles=alleles, genome=genome, coverage=coverage, error_model=error_model, length=length, identity=identity, seed=seed, fastq=fastq)
    
    # Add the method to the params
    params['method'] = method

    log(f"Method: {method}")
    
    # Align the reads to the reference
    run_minimap.align(ref, fastq, bam) 
    
    # if utils.is_empty(bam):
    #     print("# The BAM does not contain alignments. Exiting")
    #     empty_object = {}
    #     print(empty_object)
    #     return
    # Add the alignment file to the params
    params['bam'] = bam

    if method == "hapcon":
        hapcon_lib.run(ref=ref, bam=bam, vcf=vcf, fasta=fasta, limit=limit)
    elif method == "longshot":
        longshot_lib.run(ref=ref, bam=bam, vcf=vcf, fasta=fasta)
    elif method == "phaser":
        phaser_lib.run(bam=bam, ref=ref, vcf=vcf, geno=csv, fasta=fasta, threshold=threshold)
    elif method == "whatshap":
        whatshap_lib.run(ref=ref, bam=bam, vcf=vcf, fasta=fasta, input_vcf=input_vcf)
    else:
        log(f"Invalid method: {method}")
        sys.exit(1)
    
    res = hapcon_lib.classify(subject=subject, query=fasta, params=params, eval=params, bam=bam)

    result = []
    for al_obj in res["params"]["alleles"]:
        result.append({"allele": al_obj, "match": False, "queries": {}}), 

    for a, al_obj in enumerate(res["params"]["alleles"]):
        for r, res_obj in enumerate(res['results']):   
            if al_obj in res_obj['alleles']:
                if result[a]["match"] == False:
                    result[a]["match"] = True 
                result[a]["queries"][res_obj["query"]] = res_obj["pident"]

    res["evaluation"] = result
    text = json.dumps(res, indent=4)

    print(text)

    return

if __name__ == "__main__":
    cli()
