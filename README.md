# `README.md`

`git-rg` is a command-line tool for recursively searching for files in Git repositories that contain specific text patterns using regular expressions. It's useful for finding sensitive information like accidentally committed passwords or API keys within `.git` directories.

## Installation

```bash
pipx install git-rg
```

To install latest version from Github:

```bash
pipx install git+https://github.com/s3rgeym/git-rg
```

## Usage

```bash
git-rg <pattern> [path] [-B <num>] [-A <num>]
```

### Arguments

- `pattern`: Regular expression to search for.
- `path`: Path to the directory where the search should begin (default: current directory).
- `-B`, `--before`: Number of lines to show before the match.
- `-A`, `--after`: Number of lines to show after the match.

### Example

To search for passwords in all `.git` files within the current directory and show 2 lines before and after the match:

```bash
git-rg "(?i)password\s*=\s*['\"]?(\w+)['\"]?" -B 2 -A
```
