import concurrent.futures

# Initialize buckets for the given sequences
def initialize_buckets(sequences,Sigma):
    buckets = {'A': [], 'C': [], 'T': [], 'G': []}
    #print(buckets)
    for i in Sigma:
        buckets[i]=[]
    #print(buckets)
    for seq_id, seq in enumerate(sequences):
        for idx, nucleotide in enumerate(seq):
            if nucleotide in buckets:
                while len(buckets[nucleotide]) <= idx:
                    buckets[nucleotide].append([])
                buckets[nucleotide][idx].append(seq_id + 1)
    return buckets

# Function to calculate LCS for a given nucleotide in parallel
def calculate_for_nucleotide(bucket, nucleotide, I, J, K):
    r = 1
    LCS = []
    max_length = max(len(bucket.get(nucleotide, [])), r)

    while r <= max_length:
        indices = bucket.get(nucleotide, [])
        Xm = sum(indices[r - 1]) if r - 1 < len(indices) else 0
        Ym = sum(abs(indices[r - 1][i] - indices[r - 1][i+1]) for i in range(len(indices[r - 1]) - 1)) if r - 1 < len(indices) else 0
        Zm = Xm + Ym

        Zmin = min(
            sum(bucket['A'][r - 1]) if r - 1 < len(bucket['A']) else float('inf'),
            sum(bucket['C'][r - 1]) if r - 1 < len(bucket['C']) else float('inf'),
            sum(bucket['T'][r - 1]) if r - 1 < len(bucket['T']) else float('inf'),
            sum(bucket['G'][r - 1]) if r - 1 < len(bucket['G']) else float('inf')
        )

        if Zm == Zmin:
            LCS.append(nucleotide)
            I = Zmin
            J = Zmin
            K = Zmin

        r += 1

    return LCS

# Parallel MSLCS algorithm
def parallel_mslcs(sequences,Sigma):
    global I, J, K
    nucleotides = Sigma#['A', 'C', 'T', 'G']
    LCS = []

    buckets = initialize_buckets(sequences,nucleotides)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(calculate_for_nucleotide, buckets, nucleotide, I, J, K) for nucleotide in nucleotides]
        for future in concurrent.futures.as_completed(futures):
            LCS.extend(future.result())

    return ''.join(LCS)

# Function to take sequences as input and find LCS
def RAA(sequences,Sigma):
    #print(list(Sigma))
    global I, J, K
    I = J = K = 0
    LCS_result = parallel_mslcs(sequences,list(Sigma))
    return LCS_result
