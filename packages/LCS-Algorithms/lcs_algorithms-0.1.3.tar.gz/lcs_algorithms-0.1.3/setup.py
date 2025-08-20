from setuptools import setup, find_packages

setup(
    name="lcs",
    version="0.1.1",
    author="Zeshan Khan",
    author_email="zeshankhanalvi@gmail.com",
    description="Finds the longest common subsequence among multiple strings.",
    packages=["lcs_algorithms"],#find_packages(),
    python_requires=">=3.6",
)