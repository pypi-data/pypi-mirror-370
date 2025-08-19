# MHC_central


## Install

```bash
# Create a new conda environment
conda create -c conda-forge -yn phaser minimap2 minipileup samtools longshot blast pywgsim python
pip3 install git+https://github.com/rrwick/Badread.git
```

then install nanophaser:

```bash
pip install nanophaser
```

## Install for development

```bash
pip install --editable .
```

## Usage

1. Generate BAM from the fastq file in the test folder (*put commands in the makefile)

2. Move your code so that it runs as some nanophaser command

3. Add the commands to the Makefile


```
nanophaser run
```


## Evaluation

```bash
nanophaser loop -n 1000 | parallel --eta --verbose 
``


## Reference 

Location of the reference files:

https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Bos_taurus/reference/GCF_002263795.3_ARS-UCD2.0/

    wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Bos_taurus/all_assembly_versions/suppressed/GCF_000003055.6_Bos_taurus_UMD_3.1.1/GCF_000003055.6_Bos_taurus_UMD_3.1.1_genomic.fna.gz

## Installation steps

    conda install nanoplot


## Quality control

Run nanoplot on the MinION data

## Fast way to create csv file and copy all the files names

    Go into the directory, ls >test.csv to store everything into this csv file

## Choose one of the following method BWA or Minimap2, Use BWA for short reads, Minimap2 for assemblies or long reads.

## Create Genome BWA Index (Only one time for lignment BWA)

    bwa index ~/refs/GCF_002263795.3_ARS-UCD2.0_genomic.fna 

## Alignment BWA 

    bwa mem -x ont2d ~/refs/GCF_002263795.3_ARS-UCD2.0_genomic.fna reads/demo.fq.gz | samtools sort --write-index -o bam/demo_bwa.bam

## Alignment Minimap2 

    minimap2 -t 6 -a -x splice ~/refs/GCF_002263795.3_ARS-UCD2.0_genomic.fna reads/demo.fq.gz | samtools sort --write-index -o bam/demo.bam