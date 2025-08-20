def lcsDP(seq1, seq2):
    m = len(seq1)
    n = len(seq2)
    
    # Initialize a 2D list to store the lengths of LCSs
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Build the dp array
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    # Trace back to find the LCS itself
    lcs_length = dp[m][n]
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if seq1[i - 1] == seq2[j - 1]:
            lcs.append(seq1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1    
    lcs.reverse()
    return lcs