import pysam
import csv, sys
from itertools import islice
from tqdm import tqdm
from cyvcf2 import VCF, Writer
from datetime import datetime
from nanophaser import run_minimap, utils

# The name of the column that contains the phased genotype
PHASE_KEY = "Phase"

# The headers of the genotypes
GTS_HEADERS = ["Position", "Coverage", "Reference", "A", "T", "G", "C", "Genotype", "Confidence"]

# The headers of the phased genotypes
GTS_PHASED_HEADERS = GTS_HEADERS + [PHASE_KEY]

from nanophaser.utils import log

def get_reference_info(bam_file, ref_file):
    """
    Extract chromosome name and length from BAM and reference files.
    Returns: (chromosome_name, chromosome_length)
    """
    bam = pysam.AlignmentFile(bam_file, "rb")
    reference = pysam.FastaFile(ref_file)
    
    # Get the first reference sequence name from BAM
    if bam.nreferences > 0:
        chr_name = bam.get_reference_name(0)
        chr_length = bam.get_reference_length(chr_name)
    else:
        # Fallback to reference file
        chr_name = reference.references[0]
        chr_length = reference.get_reference_length(chr_name)
    
    bam.close()
    reference.close()
    
    return chr_name, chr_length

def run(bam, ref, geno, vcf, fasta, fastq=None,limit=None, threshold=0.7):
    

    chr_name, chr_length = get_reference_info(bam, ref)
    # Align the reads to the reference if a fastq file is provided.
    if fastq:
        run_minimap.align(ref, fastq, bam)
    
    if utils.is_empty(bam):
        print("# Waring: the BAM does not contain alignments.")
        
    gts = compute_genotypes(bname=bam, rname=ref, limit=limit, threshold=threshold)

    # Write genotypes as a CSV file to stdout
    write_csv(data=gts, fname=geno)

    log(f"GENOTYPES: {geno}")

    # Read phased genotypes from stdin
    data = read_csv(geno)

    # Phase the genotypes
    phased = phase_genotypes(data, bam)
    
    write_vcf(phased, chr_name, chr_length, vcf)

    log(f"VCF: {vcf}")

    utils.vcf2fasta(ref=ref, vcf=vcf, fname=fasta)
    fasta = utils.trim_fasta(bam, fasta)
    phaserbam = utils.swap_ext(fasta, 'bam')
    run_minimap.align(ref=ref, fastq=fasta, bam=phaserbam)
    
    log(f"FASTA: {fasta}")
    log(f"BAM: {phaserbam}")

def compute_genotypes(bname, rname, limit=None, threshold=0.9):
    """
    Call variants from a BAM file and a reference sequence.
    """
    chromosome = None 
    #######################################################
    # Process BAM file and collect variant data

    bam = pysam.AlignmentFile(bname, "rb")
    reference = pysam.FastaFile(rname)
    len_str = ''.join(map(str, reference.lengths))
    data = []
    
    # Get total number of alignments for progress bar
    total_alignments = bam.count()

    log(f"REF: {rname} ({len_str} bp)")
    log(f"BAM: {bname} ({total_alignments} alignments)")

    stream = bam.pileup(min_nucleotide_depth=1, min_mapq=0, min_base_quality=0, max_depth=1000000)
    
    stream = islice(stream, limit)
    
    # This should be the lenght of the covered region in the bam file.
    sizes = sum(reference.lengths)

    stream = tqdm(stream, desc="# Genotyping", total=sizes)

    for pileupcolumn in stream:
        # updating position number, start from 1
        position = pileupcolumn.reference_pos + 1
        #extracting ID for the reference sequence from BAM file header
        ref_name = bam.get_reference_name(pileupcolumn.tid)
        # Store chromosome name (first time through the loop)
        if chromosome is None:
            chromosome = ref_name
        #extract the pos base based on the information passed in, end base is exclusive
        ref_base = reference.fetch(ref_name, pileupcolumn.reference_pos, pileupcolumn.reference_pos + 1).upper()
        count_A = count_T = count_G = count_C = 0
        coverage = 0
        genotype = ""

        #pileupcolumn is the column of single position, pileups is the reads (rows) that align to the position
        for pileupread in pileupcolumn.pileups:
            if pileupread.is_del:
                continue
            #query_sequence is the read sequence, query_position gives the position of the base aligned to the reference sequence
            base = pileupread.alignment.query_sequence[pileupread.query_position].upper()
            coverage += 1

            # Count the base if it is one of A, T, G, or C.
            if base == "A":
                count_A += 1
            elif base == "T":
                count_T += 1
            elif base == "G":
                count_G += 1
            elif base == "C":
                count_C += 1
            else:
                continue
        # Calcuylate Genotype
        dic_genotype = {"A": 1, "T": 2, "G": 3, "C": 4}
        # Create dictionaries with nucleotide counts and percentages
        counts = {"A": count_A, "T": count_T, "G": count_G, "C": count_C}
        #calculate percentage of each base
        percents = {base: counts[base]/coverage if coverage > 0 else 0 for base in counts}

        # Sort nucleotides by count
        sorted_nucs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        nucs = [n[0] for n in sorted_nucs]  # List of nucleotides in descending order

        # Calculate differences between percentages
        diffs = {
            "max_sec": percents[nucs[0]] - percents[nucs[1]] if len(nucs) > 1 else 0,
            "sec_third": percents[nucs[1]] - percents[nucs[2]] if len(nucs) > 2 else 0
        }

        # Determine confidence level
        def get_confidence(diff):
            if diff >= 0.3: return "2"
            elif diff >= 0.2: return "1"
            elif diff >= 0.1: return "0"
            else: return "-1"

        # Determine genotype
        if nucs[0] == ref_base:
            if diffs["max_sec"] >= threshold:
                genotype = "0,0"
                confident = get_confidence(diffs["max_sec"])
            else:
                genotype = f"0,{dic_genotype[nucs[1]]}"
                confident = get_confidence(diffs["sec_third"])
        elif nucs[1] == ref_base:
            if diffs["max_sec"] >= threshold:
                genotype = f"{dic_genotype[nucs[0]]},{dic_genotype[nucs[0]]}"
                confident = get_confidence(diffs["max_sec"])
            else:
                genotype = f"0,{dic_genotype[nucs[0]]}"
                confident = get_confidence(diffs["sec_third"])
        else:
            if diffs["max_sec"] >= threshold:
                genotype = f"{dic_genotype[nucs[0]]},{dic_genotype[nucs[0]]}"
                confident = get_confidence(diffs["max_sec"])
            else:
                smaller, larger = sorted([dic_genotype[nucs[0]], dic_genotype[nucs[1]]])
                genotype = f"{smaller},{larger}"
                confident = get_confidence(diffs["sec_third"])
        
        row = [position, coverage, ref_base, count_A, count_T, count_G, count_C, genotype, confident]
        data.append(row)
    # Close files
    bam.close()
    reference.close()

    return data


    


def phase_genotypes(data, bam):
    all_variants = []
    variant_positions_for_phasing = []
    
    bamfile = pysam.AlignmentFile(bam, "rb")
    
    #size = len(data)

    for row in data:
        
        position = int(row[0])  # convert to int here
        coverage = int(row[1])  # convert to int if needed
        ref_base = row[2]
        count_A = int(row[3])
        count_T = int(row[4])
        count_G = int(row[5])
        count_C = int(row[6])
        genotype = row[7]          # eighth element
        confident = row[8]         # ninth element
        variant_data = [position, coverage, ref_base, count_A, count_T, count_G, count_C, genotype, confident]
        all_variants.append(variant_data)
        # If heterozygous, add to phasing list
        # In try1.py, modify how variant_positions_for_phasing is created:
        if "," in genotype and genotype[0] != genotype[2]:
            # Parse the actual genotype numbers
            geno_parts = genotype.split(",")
            geno1 = int(geno_parts[0])
            geno2 = int(geno_parts[1])
            ref_base = variant_data[2]
            # Find corresponding bases for these genotypes
            num_to_base = {0: ref_base, 1: "A", 2: "T", 3: "G", 4: "C"}
            
            alt1 = num_to_base[geno1]
            alt2 = num_to_base[geno2]
            
            # Pass original genotype numbers along with the variant data
            variant_positions_for_phasing.append((position, ref_base, alt1, alt2, genotype))
        # if chromosome is None:  # Safety check
    
    chromosome = bamfile.get_reference_name(0)
    phased_genotypes = phase_variants(bam, variant_positions_for_phasing, chromosome)
        
    
    for variant in all_variants:
        position = variant[0]
        genotype = variant[7]
        
        # If position is in phased_genotypes, add phased genotype
        if position in phased_genotypes:
            phased = phased_genotypes[position]
        elif "," in genotype and genotype[0] != genotype[2]:
            # For unphased heterozygous, use original but with pipe
            phased = genotype.replace(",", "|")
        else:
            # For homozygous, keep original
            phased = genotype.replace(",", "|")
        variant.append(phased)
        
    
    bamfile.close()
        
    return all_variants
     

def phase_variants(bam_file, variant_positions, chromosome):

        # print(f"Positions to phase: {len(variant_positions)}")
        bamfile = pysam.AlignmentFile(bam_file, "rb")

        # Create dictionary of original genotypes
        original_genotypes = {}
        valid_bases = {}

        for pos, ref, alt1, alt2, genotype in variant_positions:
            if ',' in genotype:
                geno_parts = genotype.split(',')
                geno1, geno2 = int(geno_parts[0]), int(geno_parts[1])
                original_genotypes[pos] = (geno1, geno2)

                # Store valid bases for each position
                num_to_base = {0: ref, 1: "A", 2: "T", 3: "G", 4: "C"}
                valid_bases[pos] = set([num_to_base[geno1], num_to_base[geno2]])
        
        # Filter heterozygous positions and extract alleles
        het_variants = []
        ref_bases = {}
        
        for pos, ref, alt1, alt2, genotype in variant_positions:
            if ',' in genotype and genotype[0] != genotype[2]:
                alleles = [ref]
                if alt1 != ref: alleles.append(alt1)
                if alt2 != ref and alt2 != alt1: alleles.append(alt2)
                het_variants.append((pos, alleles))
                ref_bases[pos] = ref
        
        # Remove duplicates
        unique_het_variants = {}
        for pos, alleles in het_variants:
            unique_het_variants[pos] = alleles
        
        # Convert back to list
        het_variants = [(pos, alleles) for pos, alleles in unique_het_variants.items()]
        het_variants.sort()  # Sort by position
        
        # Initialize phasing data structures
        phased_genotypes = {}  # {position: "allele1|allele2"}
        
        #log(f"Variants: {len(het_variants)}")
        
        # Process pairs of heterozygous positions
        stream = list(range(len(het_variants) - 1))
        stream = tqdm(stream, desc="# Phasing   ", total=len(stream)+1, initial=1,)
        for i in stream:
            pos1, alleles1 = het_variants[i]
            pos2, alleles2 = het_variants[i + 1]
            #print(f"Checking positions {pos1} and {pos2}", file=sys.stderr)
            # print_base_dist(bamfile, pos1, ref_bases[pos1])
            # print_base_dist(bamfile, pos2, ref_bases[pos2])
            # print(f"Original genotype for pos {pos1}: {original_genotypes[pos1]}", file=sys.stderr)
            #print(f"Original genotype for pos {pos2}: {original_genotypes[pos2]}", file=sys.stderr)
            
            pair_counts = {}
            pos1_bases = {}
            pos2_bases = {}

            # Get bases at position 1 using pileup
            for pileupcolumn in bamfile.pileup(reference=chromosome, start=pos1-1, end=pos1):
                if pileupcolumn.reference_pos == pos1-1:  # 0-based
                    for pileup in pileupcolumn.pileups:
                        if not pileup.is_del and not pileup.is_refskip:
                            base = pileup.alignment.query_sequence[pileup.query_position].upper()
                            pos1_bases[pileup.alignment.query_name] = base

            # Get bases at position 2 using pileup
            for pileupcolumn in bamfile.pileup(reference=chromosome, start=pos2-1, end=pos2):
                if pileupcolumn.reference_pos == pos2-1:  # 0-based
                    for pileup in pileupcolumn.pileups:
                        if not pileup.is_del and not pileup.is_refskip:
                            base = pileup.alignment.query_sequence[pileup.query_position].upper()
                            pos2_bases[pileup.alignment.query_name] = base

            # Find common reads and count pairs
            common_reads = set(pos1_bases.keys()) & set(pos2_bases.keys())
            for read_name in common_reads:
                pair = (pos1_bases[read_name], pos2_bases[read_name])
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

            #print(f"Reads at pos1: {len(pos1_bases)}, Reads at pos2: {len(pos2_bases)}, Common: {len(common_reads)}", file=sys.stderr)
            
            # print(f"Pair counts: {pair_counts}", file=sys.stderr)
            if not pair_counts:
                continue
                
            # Sort pairs by frequency
            sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Check if pos1 is already phased
            # For existing phase
            if pos1 in phased_genotypes:
                # Respect existing phasing at pos1
                existing_alleles = phased_genotypes[pos1].split("|")

                # Convert existing genotype numbers to actual bases
                num_to_base_pos1 = {0: ref_bases[pos1], 1: "A", 2: "T", 3: "G", 4: "C"}
                existing_base1 = num_to_base_pos1.get(int(existing_alleles[0]), ref_bases[pos1])
                existing_base2 = num_to_base_pos1.get(int(existing_alleles[1]), ref_bases[pos1])

                # Get original genotypes for pos2
                orig_geno1_pos2, orig_geno2_pos2 = original_genotypes[pos2]

                # Get original genotypes for pos2
                orig_geno1_pos2, orig_geno2_pos2 = original_genotypes[pos2]
                
                # Convert genotypes to bases
                num_to_base = {0: ref_bases[pos2], 1: "A", 2: "T", 3: "G", 4: "C"}
                base2_orig1 = num_to_base.get(orig_geno1_pos2, ref_bases[pos2])
                base2_orig2 = num_to_base.get(orig_geno2_pos2, ref_bases[pos2])
                
                # Count evidence for each possible phasing
                count_hap1_orig1 = 0
                count_hap1_orig2 = 0
                count_hap2_orig1 = 0
                count_hap2_orig2 = 0
                
                for (base1, base2), count in sorted_pairs:
                    if base1 == existing_base1:
                        if base2 == base2_orig1:
                            count_hap1_orig1 += count
                        elif base2 == base2_orig2:
                            count_hap1_orig2 += count
                    elif base1 == existing_base2:
                        if base2 == base2_orig1:
                            count_hap2_orig1 += count
                        elif base2 == base2_orig2:
                            count_hap2_orig2 += count
                
                # Use phasing with most evidence
                # print(f"Existing phase for pos {pos1}: {phased_genotypes[pos1]}", file=sys.stderr)
                # print(f"Existing bases: {existing_base1}/{existing_base2}", file=sys.stderr)
                # print(f"Genotype bases for pos {pos2}: {base2_orig1}/{base2_orig2}", file=sys.stderr)
                # print(f"Pos: {pos2}, Counts: {count_hap1_orig1}, {count_hap1_orig2}, {count_hap2_orig1}, {count_hap2_orig2}", file=sys.stderr)
                if count_hap1_orig1 + count_hap2_orig2 >= count_hap1_orig2 + count_hap2_orig1:
                    phased_genotypes[pos2] = f"{orig_geno1_pos2}|{orig_geno2_pos2}"
                else:
                    phased_genotypes[pos2] = f"{orig_geno2_pos2}|{orig_geno1_pos2}"
            else:
                # For new phase
                # Get original genotypes
                orig_geno1_pos1, orig_geno2_pos1 = original_genotypes[pos1]
                orig_geno1_pos2, orig_geno2_pos2 = original_genotypes[pos2]
                
                # Convert genotypes to bases
                num_to_base = {0: ref_bases[pos1], 1: "A", 2: "T", 3: "G", 4: "C"}
                base1_orig1 = num_to_base.get(orig_geno1_pos1, ref_bases[pos1])
                base1_orig2 = num_to_base.get(orig_geno2_pos1, ref_bases[pos1])
                
                num_to_base = {0: ref_bases[pos2], 1: "A", 2: "T", 3: "G", 4: "C"}
                base2_orig1 = num_to_base.get(orig_geno1_pos2, ref_bases[pos2])
                base2_orig2 = num_to_base.get(orig_geno2_pos2, ref_bases[pos2])
                
                # Count evidence for each phasing
                count_1_1_2_2 = 0  # orig1:orig1, orig2:orig2
                count_1_2_2_1 = 0  # orig1:orig2, orig2:orig1
                
                for (base1, base2), count in sorted_pairs:
                    if (base1 == base1_orig1 and base2 == base2_orig1) or (base1 == base1_orig2 and base2 == base2_orig2):
                        count_1_1_2_2 += count
                    elif (base1 == base1_orig1 and base2 == base2_orig2) or (base1 == base1_orig2 and base2 == base2_orig1):
                        count_1_2_2_1 += count
                
                # print(f"Genotype bases for pos {pos1}: {base1_orig1}/{base1_orig2}", file=sys.stderr)
                # print(f"Genotype bases for pos {pos2}: {base2_orig1}/{base2_orig2}", file=sys.stderr)
                # print(f"Counts: 1-1/2-2={count_1_1_2_2}, 1-2/2-1={count_1_2_2_1}", file=sys.stderr)
                # Use phasing with more evidence
                if count_1_1_2_2 >= count_1_2_2_1:
                    phased_genotypes[pos1] = f"{orig_geno1_pos1}|{orig_geno2_pos1}"
                    phased_genotypes[pos2] = f"{orig_geno1_pos2}|{orig_geno2_pos2}"
                else:
                    phased_genotypes[pos1] = f"{orig_geno1_pos1}|{orig_geno2_pos1}"
                    phased_genotypes[pos2] = f"{orig_geno2_pos2}|{orig_geno1_pos2}"
                
        # Close files
        bamfile.close()
        # print(f"Phased positions: {len(phased_genotypes)}", file=sys.stderr)
        return phased_genotypes



def genotypes2fasta(gts):
    """
    Convert a CSV file to a FASTA file with two phased alleles.
    """
    # Initialize sequences
    allele1 = []
    allele2 = []
    base_lookup = {0: "Reference", 1: 'A', 2: 'T', 3: 'G', 4: 'C'}
    

    for row in gts:

        # Make row into a dict
        row = dict(zip(GTS_PHASED_HEADERS, row))

        # Get phased genotype
        phased = row[PHASE_KEY].split('|')

        if len(phased) == 2:
            idx1 = int(phased[0])
            idx2 = int(phased[1])
            
            # Get base for each allele
            base1 = base_lookup[idx1] if idx1 != 0 else row['Reference']
            base2 = base_lookup[idx2] if idx2 != 0 else row['Reference']
            
            allele1.append(base1)
            allele2.append(base2)
    
    a1 = f">a\n{''.join(allele1)}"
    a2 = f">b\n{''.join(allele2)}"

    # print(a1)
    # print(a2)
    return a1, a2


def write_csv(data, headers=GTS_HEADERS, fname=None):

    stream = open(fname, 'w') if fname else sys.stdout
    writer = csv.writer(stream)
    writer.writerow(headers)
    for row in data:
        writer.writerow(row)

def read_csv(fname=None):
    stream = open(fname, 'r') if fname else sys.stdin
    
    # Create a reader
    reader = csv.reader(stream)
    
    # Skip the header
    reader = islice(reader, 1, None)

    # Convert to list
    data = list(reader)
    
    return data

def write_gff(data, chrname):
    """
    Write phased genotype data as GFF format to stdout.
    Only includes positions where there are variants.
    """
    # GFF header
    print("##gff-version 3")
    

    # GFF columns
    # seqid source type start end score strand phase attributes
    for row in data:
        # Convert row to dict for easier access
        row_dict = dict(zip(GTS_PHASED_HEADERS, row))
        
        # Only process if there's a variant (non-reference base)
        genotype = row_dict['Genotype']
        if ',' not in genotype or genotype[0] != genotype[2]:  # If heterozygous or homozygous variant
            position = row_dict['Position']
            ref_base = row_dict['Reference']
            phased = row_dict[PHASE_KEY]
            
            # Convert genotype numbers to bases
            base_lookup = {0: ref_base, 1: 'A', 2: 'T', 3: 'G', 4: 'C'}
            alleles = phased.split('|')
            alt1 = base_lookup[int(alleles[0])]
            alt2 = base_lookup[int(alleles[1])]
            
            # Create GFF attributes with just the Name showing the phased genotype
            attributes = f"Name={ref_base}/{alt1}|{alt2}"
            
            # Print GFF line
            # Using '.' for unknown values
            print(f"{chrname}\t.\tSNV\t{position}\t{position}\t.\t.\t.\t{attributes}")

def write_vcf(data, chr_name, chr_length, fname=None):
    stream = open(fname, 'w') if fname else sys.stdout
    header_str = f"##fileformat=VCFv4.2\n##contig=<ID={chr_name},length={chr_length}>\n##INFO=<ID=pass,Number=1,Type=Integer,Description=\"Total Depth of reads passing MAPQ filter\">\n##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE"
    print(header_str, file=stream)
    # VCF columns
    # seqid source type start end score strand phase attributes
    for row in data:
        # Convert row to dict for easier access
        row_dict = dict(zip(GTS_PHASED_HEADERS, row))
        
        # Only process if there's a variant (non-reference base)
        genotype = row_dict['Genotype']
        if ((genotype[0] == genotype[2]) and (int(genotype[0]) != 0)) or (genotype[0] != genotype[2]):  # If heterozygous or homozygous variant
            position = row_dict['Position']
            ref_base = row_dict['Reference']
            base_lookup = {0: ref_base, 1: 'A', 2: 'T', 3: 'G', 4: 'C'}
            phased = row_dict[PHASE_KEY]
            
            # Convert the genotype values to integers before using them as keys
            allele1 = int(genotype[0])
            allele2 = int(genotype[2])

            # if allele1 == allele2:
            #     alt = f"{base_lookup[allele1]}"
            # elif base_lookup[allele1] != ref_base:
            #     alt = f"{base_lookup[allele1]},{base_lookup[allele2]}"
            # else:
            #     alt = f"{base_lookup[allele2]}"
            
            # alleles = phased.split('|')

            # if alleles[0] == alleles[1]:
            #     alleles[0] = alleles[1] = "1"
            # elif int(alleles[0]) == 0:
            #     alleles[1] = "1"
            # elif int(alleles[1]) == 0:
            #     alleles[0] = "1"
            # elif int(alleles[0]) == allele1:
            #     alleles[0] = "1" 
            #     alleles[1] = "2"
            # else:
            #     alleles[0] = "2"
            #     alleles[1] = "1"

            # print(f"{chrname}\t{position}\t.\t{ref_base}\t{alt}\t.\t.\t{'pass'}\tGT\t{alleles[0]}|{alleles[1]}", file=stream)
            alt_alleles = []
            if allele1 != 0 and base_lookup[allele1] != ref_base:
                alt_alleles.append(base_lookup[allele1])
            if allele2 != 0 and base_lookup[allele2] != ref_base and base_lookup[allele2] not in alt_alleles:
                alt_alleles.append(base_lookup[allele2])
            
            alt = ",".join(alt_alleles) if alt_alleles else "."
            
            # Process phased genotype
            alleles = phased.split('|')
            gt_indices = []
            
            for allele in alleles:
                allele = int(allele)
                if allele == 0:
                    gt_indices.append("0")
                else:
                    base = base_lookup[allele]
                    if base == ref_base:
                        gt_indices.append("0")
                    else:
                        try:
                            idx = alt_alleles.index(base) + 1
                            gt_indices.append(str(idx))
                        except ValueError:
                            # If base not in alt_alleles, use ref
                            gt_indices.append("0")
            
            gt = "|".join(gt_indices)
            
            print(f"{chr_name}\t{position}\t.\t{ref_base}\t{alt}\t.\t.\t{'pass'}\tGT\t{gt}", file=stream)

if __name__ == "__main__":
   from nanophaser import utils
   bam = utils.DEFAULT_BAM
   reference = utils.DEFAULT_REF
   limit = None
   
   chr_name, chr_length = get_reference_info(bam, reference)
   gts = compute_genotypes(bname=bam, rname=reference, limit=limit)