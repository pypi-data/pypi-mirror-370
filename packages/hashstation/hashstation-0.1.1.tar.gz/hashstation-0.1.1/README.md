# pycrackhash

[![PyPI version](https://img.shields.io/pypi/v/pycrackhash.svg)](https://pypi.org/project/pycrackhash/)
[![Python version](https://img.shields.io/pypi/pyversions/pycrackhash.svg)](https://pypi.org/project/pycrackhash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**pycrackhash** is a simple Python module for analyzing and cracking hashes using Indonesian wordlists as well as the famous `rockyou.txt`.
It supports cracking a single hash, cracking multiple hashes from a file, and detecting hash types.

---

## Installation

```bash
pip install pycrackhash
```

---

## Features

- Crack a single hash with a specific mode.
- Crack multiple hashes from a file (`all` mode will try all available algorithms).
- Analyze the type of a single hash or all hashes in a file.

---

## Usage Examples

```python
from pycrackhash import crack, crack_file, analyze, analyze_file

# Crack a single hash
status, result = crack("md5", "5d41402abc4b2a76b9719d911017c592")
print(status, result)  # True hello (mode: MD5 (0))

# Crack hashes from a file with all algorithms
for hash_value, status, result in crack_file("hashes.txt", "all"):
    print(hash_value, status, result)

# Analyze a single hash
candidates = analyze("5d41402abc4b2a76b9719d911017c592")
print(candidates)

# Analyze hashes from a file
for hash_value, candidates in analyze_file("hashes.txt"):
    print(hash_value, candidates)
```

---

## Function Parameters

### `crack(mode: str, hash_string: str) -> tuple`
- **mode** (`str`):  
  The hash mode to use. Example: `"md5"` for MD5, `"100"` for SHA1, etc.
- **hash_string** (`str`):  
  The hash value to crack.

**Returns:**
```python
(status: bool, result: str)
```

---

### `crack_file(file_path: str, mode: str) -> generator`
- **file_path** (`str`): Path to the file containing hashes (one hash per line).
- **mode** (`str`): The hash mode to use. Example: `"md5"` for MD5, `"100"` for SHA1, or `"all"` to try every supported mode.

**Yields:**
```python
(hash_value: str, status: bool, result: str)
```

---

### `analyze(hash_string: str) -> dict`
- **hash_string** (`str`): The hash value to analyze.

**Returns:**  
A dictionary with the detected hash type and its description.

---

### `analyze_file(file_path: str) -> generator`
- **file_path** (`str`): Path to the file containing hashes.

**Yields:**  
```python
(hash_value: str, candidates: list)
```

---

## License

MIT License Â© 2025 - Hades