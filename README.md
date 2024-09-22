# Git Recursive Grep

[![PyPI version](https://img.shields.io/pypi/v/git-rg)](https://pypi.org/project/git-rg/)
[![Downloads](https://img.shields.io/pypi/dm/git-rg)](https://pypi.org/project/git-rg/)

`git-rg` is a command-line tool for recursively searching for files in Git repositories that contain specific text patterns using regular expressions. It's useful for finding sensitive information like accidentally committed passwords or API keys within `.git` directories.

## Installation

```bash
pip install git-rg
python3 -m pip install git-rg
pipx install git-rg
```

To install latest version from Github:

```bash
pipx install git+https://github.com/s3rgeym/git-rg
```

## Usage

```bash
git-rg <pattern> [path] [-B <num>] [-A <num>] [-L <maxline>]
```

### Example

To search for passwords in all `.git` files within the current directory and show 2 lines before and after the match:

```bash
git-rg "(?i)password\s*=\s*['\"]?(\w+)['\"]?" ~/projects -B 2 -A 2
```

Output seems like this:

![image_2024-09-22_18-56-49](https://github.com/user-attachments/assets/c518f162-839e-4d83-97d0-9864a0abc7f8)

