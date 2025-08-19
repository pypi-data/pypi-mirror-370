
import subprocess
from nanophaser.utils import check_executables, log


INT_FIELDS = set('length qlen'.split())
FLOAT_FIELDS = set('pident'.split())

def recast(x):
    """Recast a value to a specific type."""
    name, value = x
    if name in INT_FIELDS:
        value =  int(value)
    
    elif name in FLOAT_FIELDS:
        value = float(value)

    return name, value


def classify(query, subject):
    """Classify alleles using sequence similarity."""
    check_executables(required = ['blastn'])
    
    fields = "qseqid sseqid pident length qlen".split()

    # Run blastn with tabular output format and capture stdout
    cmd = f"blastn -query {query} -subject {subject} -outfmt '6 {' '.join(fields)}'"
    log(f"Running blastn: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        log(f"Error during blastn: {e.stderr}")
        raise
    
    # Parse results
    output = result.stdout.splitlines()
    
    # Modified approach: collect ALL results first
    all_matches = {}  # Dictionary of lists to store all matches for each query
    top_scores = {}   # Track the highest score for each query
    
    for line in output:
        if not line:  # Skip empty lines
            continue
        
        values = line.strip().split('\t')
        pairs = zip(fields, values)
        pairs = map(recast, pairs)
        row = dict(pairs)
        
        query_id = row['qseqid']
        
        # Initialize if this is first match for this query
        if query_id not in all_matches:
            all_matches[query_id] = []
            top_scores[query_id] = row['pident']
        
        # Update top score if this match is better
        if row['pident'] > top_scores[query_id]:
            top_scores[query_id] = row['pident']
        
        # Add this match to the list
        all_matches[query_id].append(row)
    
    # Now filter to keep only the top matches for each query
    results = []
    
    for query_id, matches in all_matches.items():
        top_matches = []
        top_score = top_scores[query_id]
        
        # Keep all matches that have the top score
        for match in matches:
            if match['pident'] == top_score:
                # Create a copy of the match with a new field for equivalent alleles
                modified_match = dict(match)
                
                # Find all equivalent top matches and store their IDs
                equivalent_alleles = [m['sseqid'] for m in matches if m['pident'] == top_score]
                modified_match['equivalent_alleles'] = equivalent_alleles
                
                top_matches.append(modified_match)
        
        # Add the first top match to results (it contains the list of all equivalent alleles)
        if top_matches:
            results.append(top_matches[0])
    
    return results