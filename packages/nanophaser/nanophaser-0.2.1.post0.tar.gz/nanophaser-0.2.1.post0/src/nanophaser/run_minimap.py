import subprocess, sys
from nanophaser.utils import check_executables, log, run_cmd

def align(ref, fastq, bam, sample_name="sample"):
    """Run minimap2 alignment and sort with samtools to create a BAM file."""

    check_executables(required = ['minimap2', 'samtools'])
    # Construct and run the pipeline command
    # Older version of minimap2 did not support the --MD flag so we explicitly generate the MD tag.
    cmd = f"minimap2 -x map-ont -a -t 2 {ref} {fastq} -R \'@RG\\tID:{sample_name}\\tSM:{sample_name}\\tLB:{sample_name}\\tPL:illumina\' | samtools calmd - {ref} | samtools sort -@ 2 -o {bam}"
    
    run_cmd(cmd)

    cmd = f"samtools index {bam}"
    
    run_cmd(cmd)

    try:
        cmd1 = f"samtools view -c -F 256 -F 2048 {bam}"
        result = subprocess.run(cmd1, shell=True, check=True, capture_output=True, text=True)
        val1 = result.stdout.strip()

        cmd2 = f"samtools view -c -f 4 {bam}"
        result = subprocess.run(cmd2, shell=True, check=True, capture_output=True, text=True)
        val2 = result.stdout.strip()

        # perc = round(int(val2) / int(val1) * 100, 2)
        # log(f"Primary: {val1}, Unmapped: {val2} ({perc}%)")
        
    except subprocess.CalledProcessError as e:
        log(f"Error during flagstat: {e.stderr}")
        raise
