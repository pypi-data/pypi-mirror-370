#!/usr/bin/env python3
"""
CLI module for termcopy - terminal clipboard operations
"""

import sys
import base64
import argparse
from typing import Union


def is_terminal_input() -> bool:
    """Check if stdin is a terminal (not a pipe)."""
    return sys.stdin.isatty()


def read_input(file_path: Union[str, None] = None) -> bytes:
    """Read input from file or stdin."""
    if file_path:
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.", file=sys.stderr)
            sys.exit(1)
        except PermissionError:
            print(f"Error: Permission denied reading '{file_path}'.", file=sys.stderr)
            sys.exit(1)
    else:
        return sys.stdin.buffer.read()


def encode_and_format(data: bytes) -> str:
    """Base64 encode data and format as OSC 52 escape sequence."""
    # Base64 encode the data
    encoded = base64.b64encode(data)
    # Remove newlines and convert to string
    encoded_str = encoded.decode("ascii").replace("\n", "")
    # Format as OSC 52 escape sequence
    return f"\033]52;c;{encoded_str}\007"


def main() -> None:
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Send data to terminal clipboard via OSC 52 escape sequence",
        epilog="Reads from file if provided, otherwise from stdin",
    )
    parser.add_argument(
        "file", nargs="?", help="File to read from (if not provided, reads from stdin)"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    # Determine input source
    if is_terminal_input():
        # If stdin is a terminal, read from file argument
        if not args.file:
            print(
                "Error: File argument required when reading from terminal.",
                file=sys.stderr,
            )
            parser.print_help()
            sys.exit(1)
        input_data = read_input(args.file)
    else:
        # If stdin is not a terminal (pipe), read from stdin
        input_data = read_input()

    # Process and output
    result = encode_and_format(input_data)
    print(result, end="")


if __name__ == "__main__":
    main()
