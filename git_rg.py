#!/usr/bin/env python
import argparse
import re
import sys
import typing
import zlib
from collections import deque
from contextlib import suppress
from functools import partial
from pathlib import Path
from signal import SIG_DFL, SIGPIPE, signal

__version__ = "0.2.1"
__author__ = "s3rgeym"

# https://stackoverflow.com/questions/14207708/ioerror-errno-32-broken-pipe-when-piping-prog-py-othercmd
signal(SIGPIPE, SIG_DFL)

CSI = "\033["
RESET = CSI + "0m"

BOLD = CSI + "1m"
UNDERLINE = CSI + "4m"

BLACK = CSI + "30m"
RED = CSI + "31m"
GREEN = CSI + "32m"
YELLOW = CSI + "33m"
BLUE = CSI + "34m"
MAGENTA = CSI + "35m"
CYAN = CSI + "36m"
WHITE = CSI + "37m"

BG_BLACK = CSI + "40m"
BG_RED = CSI + "41m"
BG_GREEN = CSI + "42m"
BG_YELLOW = CSI + "43m"
BG_BLUE = CSI + "44m"
BG_MAGENTA = CSI + "45m"
BG_CYAN = CSI + "46m"
BG_WHITE = CSI + "47m"

BRIGHT_BLACK = CSI + "90m"  # Grey
BRIGHT_RED = CSI + "91m"
BRIGHT_GREEN = CSI + "92m"
BRIGHT_YELLOW = CSI + "93m"
BRIGHT_BLUE = CSI + "94m"
BRIGHT_MAGENTA = CSI + "95m"
BRIGHT_CYAN = CSI + "96m"
BRIGHT_WHITE = CSI + "97m"


print_err = partial(print, file=sys.stderr)


def is_compressed(f: typing.BinaryIO) -> bool:
    try:
        # https://stackoverflow.com/a/17176881/2240578
        return f.read(2) in [b"\x1f\x8b", b"\x78\x9c", b"\x78\x01", b"\x78\xda"]
    finally:
        f.seek(0)


def git_readlines(file_path: Path) -> typing.Iterable[str]:
    with file_path.open("rb") as f:
        if is_compressed(f):
            decompressor = zlib.decompressobj()
            buffer = ""
            while chunk := f.read(1 << 16):
                decompressed = decompressor.decompress(chunk)
                buffer += decompressed.decode("utf-8", errors="ignore")
                *lines, buffer = buffer.split("\n")
                yield from map(str.rstrip, lines)
            if buffer:
                yield buffer
        else:
            yield from map(
                str.rstrip,
                map(partial(bytes.decode, errors="ignore"), f),
            )


def highlight_matches(text: str, matches: list[re.Match]) -> str:
    highlighted_text = text
    for match in reversed(matches):
        start, end = match.span()
        highlighted_text = (
            highlighted_text[:start]
            + BG_RED
            + BOLD
            + highlighted_text[start:end]
            + RESET
            + highlighted_text[end:]
        )
    return highlighted_text


def truncate_string(s: str, l: int) -> str:
    return s[: l - 1] + "…" if len(s) > l else s


def print_line(linenum: int, line: str) -> None:
    print(f"{BLUE}{linenum:4d}{RESET} {line}")


def git_grep(
    pattern: re.Pattern,
    file_path: Path,
    before: int,
    after: int,
    maxline: int,
) -> None:
    try:
        before_lines = deque(maxlen=before)
        line_it = enumerate(git_readlines(file_path), 1)

        for linenum, line in line_it:
            matches = list(pattern.finditer(line))

            if not matches:
                before_lines.append((linenum, line))
                continue

            print(f"{GREEN}{UNDERLINE}Found: {file_path}{RESET}")

            while before_lines:
                before_linenum, before_line = before_lines.popleft()
                print_line(
                    before_linenum,
                    f"{CYAN}{truncate_string(before_line, maxline)}{RESET}",
                )

            line = truncate_string(line, maxline)

            print_line(linenum, highlight_matches(line, matches))

            for _ in range(after):
                try:
                    next_linenum, next_line = next(line_it)
                    print_line(
                        next_linenum,
                        f"{MAGENTA}{truncate_string(next_line, maxline)}{RESET}",
                    )
                except StopIteration:
                    break
    except Exception as e:
        print_err(f"{RED}Error: {e}{RESET}")


def git_rg(
    pattern: re.Pattern,
    directory: Path,
    before: int,
    after: int,
    maxline: int = 256,
) -> None:
    for file in directory.glob("**/*.git/**/*"):
        if file.is_file():
            # if file.name in ["index", "config", "HEAD", "packed-refs"]:
            #     continue
            git_grep(pattern, file, before, after, maxline)


def main(argv: typing.Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Search recursively for a regex pattern in .git files"
    )
    parser.add_argument(
        "pattern",
        help="Regular expression pattern to search for",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=Path.cwd(),
        type=Path,
        help="Directory path to search (default: current directory)",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        help="Case insensetive search",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-B",
        "-b",
        "--before",
        type=int,
        default=0,
        help="Number of lines to show before the match",
    )
    parser.add_argument(
        "-A",
        "-a",
        "--after",
        type=int,
        default=0,
        help="Number of lines to show after the match",
    )
    parser.add_argument(
        "-L",
        "--maxline",
        type=int,
        default=256,
        help="Maximum length of the output line",
    )

    args = parser.parse_args(argv)

    with suppress(KeyboardInterrupt):
        git_rg(
            re.compile(args.pattern, re.IGNORECASE if args.ignore else 0),
            args.path,
            args.before,
            args.after,
            args.maxline,
        )


if __name__ == "__main__":
    sys.exit(main())
