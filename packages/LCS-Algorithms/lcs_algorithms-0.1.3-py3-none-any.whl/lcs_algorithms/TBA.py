def TBA(s1, s2):
    len_s1 = len(s1)
    len_s2 = len(s2)

    if len_s1 > len_s2:
        s1, s2 = s2, s1
        len_s1, len_s2 = len_s2, len_s1

    current_row = list(range(len_s1 + 1))
    previous_row = [0] * (len_s1 + 1)

    for i in range(1, len_s2 + 1):
        previous_row, current_row = current_row, previous_row
        current_row[0] = i

        for j in range(1, len_s1 + 1):
            insert_cost = current_row[j - 1] + 1
            delete_cost = previous_row[j] + 1
            replace_cost = previous_row[j - 1] + (0 if s1[j - 1] == s2[i - 1] else 1)
            current_row[j] = min(insert_cost, delete_cost, replace_cost)

    return current_row[len_s1]
