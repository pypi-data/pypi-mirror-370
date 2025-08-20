def mlcsdp(sequences):
    num_sequences = len(sequences)
    lengths = [len(seq) for seq in sequences]

    # Initialize the DP table with zeros
    dp = {}

    def dp_value(indices):
        if indices in dp:
            return dp[indices]
        if any(index == 0 for index in indices):
            dp[indices] = 0
            return 0

        matching = [sequences[i][indices[i] - 1] for i in range(num_sequences)]
        if all(char == matching[0] for char in matching):
            dp[indices] = dp_value(tuple(index - 1 for index in indices)) + 1
        else:
            dp[indices] = max(dp_value(tuple(indices[i] - (i == j) for i in range(num_sequences))) for j in range(num_sequences))
        return dp[indices]

    lcs_length = dp_value(tuple(length for length in lengths))

    # Recover the MLCS from the DP table
    def recover_lcs(indices):
        if any(index == 0 for index in indices):
            return ""
        matching = [sequences[i][indices[i] - 1] for i in range(num_sequences)]
        if all(char == matching[0] for char in matching):
            return recover_lcs(tuple(index - 1 for index in indices)) + matching[0]
        for j in range(num_sequences):
            if dp_value(indices) == dp_value(tuple(indices[i] - (i == j) for i in range(num_sequences))):
                return recover_lcs(tuple(indices[i] - (i == j) for i in range(num_sequences)))
        return ""

    lcs = recover_lcs(tuple(length for length in lengths))
    return lcs