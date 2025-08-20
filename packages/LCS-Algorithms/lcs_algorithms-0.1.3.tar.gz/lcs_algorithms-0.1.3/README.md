# LCS Algorithms Library
<p align="center">
  <a href="https://pypi.org/project/LCS-Algorithms/"><img src="https://img.shields.io/pypi/v/lcs-algorithms.svg" alt="PyPI Version"></a>
  <a href="https://github.com/zeshanalvi/LCS_Algorithms/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/lcs-algorithms.svg" alt="License"></a>
  <a href="https://pepy.tech/project/LCS-Algorithms/"><img src="https://static.pepy.tech/badge/lcs-algorithms" alt="Downloads"></a>
  <a href="https://pypi.org/project/LCS-Algorithms/"><img src="https://img.shields.io/pypi/pyversions/lcs-algorithms.svg" alt="Python Versions"></a>
  <a href="https://github.com/zeshanalvi/lcs_algorithms/stargazers"><img src="https://img.shields.io/github/stars/zeshanalvi/lcs_algorithms?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/zeshanalvi/lcs_algorithms/commits/main"><img src="https://img.shields.io/github/last-commit/zeshanalvi/lcs_algorithms.svg" alt="Last Commit"></a>
  <a href="https://github.com/zeshanalvi/lcs_algorithms/issues"><img src="https://img.shields.io/github/issues/zeshanalvi/lcs_algorithms.svg" alt="Open Issues"></a>
</p>

A Python library implementing multiple algorithms for computing the **Longest Common Subsequence (LCS)** between sequences (strings), including multi-sequence LCS.

## Features

- **Dynamic Programming LCS**
  - `lcsdp(sequence1, sequence2)` — Finds the LCS of two sequences using dynamic programming.
- **Multiple Sequence LCS (Dynamic Programming)**
  - `mlcsdp(sequences)` — Finds the LCS among multiple sequences using dynamic programming.
- **Dominant Point Approach**
  - `mlcsdpa(sequences, Sigma)` — Finds the multi-sequence LCS using the dominant point approach.
- **Parallel Algorithm**
  - `RAA(sequences, Sigma)` — Parallel multi-sequence LCS computation.
- **Redundancy Reduced Dominant Point Approach**
  - `rrmlcs(sequences, Sigma)` — Optimized multi-sequence LCS using redundancy reduction.
- **Pairwise Solution (1997)**
  - `TA(sequences)` — Pairwise multi-sequence LCS based on a 1997 published method.
- **Tournament Based Approach**
  - `TBA(s1, s2)` — Tournament method for LCS of two sequences.

## Installation

```bash
pip install lcs
```

## Usage

```python
from lcs import lcsdp, mlcsdp, mlcsdpa, RAA, rrmlcs, TA, TBA

# Example: LCS of two sequences
s1 = "AGGTAB"
s2 = "GXTXAYB"
print(lcsdp(s1, s2))

# Example: Multiple sequences
sequences = ["AGGTAB", "GXTXAYB", "GTAB"]
print(mlcsdp(sequences))
```

### 2. mlcsdp(sequences)
Dynamic Programming-based Multiple Sequence LCS.

Example:

```python
from lcs_algorithms import mlcsdp
seqs = ["ABCBDAB", "BDCAB", "BCAB"]
result = mlcsdp(seqs)
print(result)  # Output: "BCAB"

```
### 2. mlcsdp(sequences)
Dynamic Programming-based Multiple Sequence LCS.

Example:

```python
from lcs_algorithms import mlcsdp
seqs = ["ABCBDAB", "BDCAB", "BCAB"]
result = mlcsdp(seqs)
print(result)  # Output: "BCAB"

```
### 2. mlcsdp(sequences)
Dynamic Programming-based Multiple Sequence LCS.

Example:

```python
from lcs_algorithms import mlcsdp
seqs = ["ABCBDAB", "BDCAB", "BCAB"]
result = mlcsdp(seqs)
print(result)  # Output: "BCAB"

```
### 3. mlcsdpa(sequences, Sigma)
Dominant Point Approach for multiple sequence LCS.
```Sigma``` is the alphabet set of all possible characters in the sequences.

Example:

```python
from lcs_algorithms import mlcsdpa
Sigma = {'A', 'B', 'C', 'D'}
seqs = ["ABCBDAB", "BDCAB", "BCAB"]
result = mlcsdpa(seqs, Sigma)
print(result)

```
### 4. RAA(sequences, Sigma)
Parallel Algorithm for multiple sequence LCS computation.

Example:

```python
from lcs_algorithms import RAA
Sigma = {'A', 'B', 'C', 'D'}
seqs = ["ABCBDAB", "BDCAB", "BCAB"]
result = RAA(seqs, Sigma)
print(result)
```

### 5. rrmlcs(sequences, Sigma)
Redundancy-Reduced Dominant Point based algorithm.

Example:
```python
from lcs_algorithms import rrmlcs
Sigma = {'A', 'B', 'C', 'D'}
seqs = ["ABCBDAB", "BDCAB", "BCAB"]
result = rrmlcs(seqs, Sigma)
print(result)

```
### 6. TA(sequences)
Pairwise LCS Solution (1997 algorithm).

Example:

```python
from lcs_algorithms import TA
seqs = ["ABCBDAB", "BDCAB"]
result = TA(seqs)
print(result)

```

### 7. TBA(s1, s2)
Tournament-Based Algorithm for LCS of two sequences.

Example:
```
from lcs_algorithms import TBA
result = TBA("ABCBDAB", "BDCAB")
print(result)

```

## Installation
You can install via:
```bash
pip install lcs_algorithms
```
or you can clone and install it via:
```bash
git clone https://github.com/zeshanalvi/lcs_algorithms.git
cd lcs_algorithms
pip install .
```

## Parameters

- **sequence1**, **sequence2**, **s1**, **s2**: Strings representing sequences.
- **sequences**: List of strings (multiple sequences).
- **Sigma**: Set of symbols (alphabet) used for dominant point and parallel algorithms.

## License

This project is licensed under the MIT License.

