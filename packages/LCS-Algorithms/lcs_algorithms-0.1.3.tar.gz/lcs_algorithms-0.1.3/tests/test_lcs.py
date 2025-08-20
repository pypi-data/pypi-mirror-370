# test_lcs.py
import pytest
import sys
import os

# Add project root to sys.path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lcs_algorithms import lcsDP, mlcsdp, mlcsdpa, RAA, rrmlcs, TA, TBA

def test_lcs_simple():
    sequences = ["abcde", "abfde", "abgde"]
    sigma="abcdefghijklmnopqrstuvwxyz"
    result = rrmlcs(sequences,Sigma=list(sigma))
    print(result)
    assert result == ['a','b','d','e'], f"Expected 'abde', got '{result}'"

def test_lcs_identical_sequences():
    sequences = ["abcdef", "abcdef", "abcdef"]
    sigma="abcdefghijklmnopqrstuvwxyz"
    result = rrmlcs(sequences,Sigma=sigma)
    assert result == ['a','b','c','d','e','f'], "Should return the full sequence when all are identical"

def test_lcs_no_common():
    sequences = ["abc", "xyz", "123"]
    sigma="abcdefghijklmnopqrstuvwxyz1234567890"
    result = rrmlcs(sequences,Sigma=sigma)
    assert result == [], f"No common subsequence should return an empty string, got '{result}'"

def test_lcs_case_sensitivity():
    sequences = ["abc", "ABC", "abC"]
    sigma="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    result = rrmlcs(sequences,Sigma=sigma)
    # Assuming case-sensitive match
    assert result == [], f"Function should be case-sensitive, got '{result}'"

def test_lcs_single_sequence():
    sequences = ["abcde"]
    sigma="abcdefghijklmnopqrstuvwxyz1234567890"
    result = rrmlcs(sequences,Sigma=sigma)
    assert result == ['a','b','c','d','e'], "Single sequence should return itself"

def test_lcs_with_empty_sequence():
    sequences = ["abcde", "", "abc"]
    sigma="abcdefghijklmnopqrstuvwxyz1234567890"
    result = rrmlcs(sequences,Sigma=sigma)
    assert result == [], "Any empty sequence means no common subsequence"

if __name__ == "__main__":
    pytest.main()
