"""Command-line interface for the video processor."""

import argparse
import os
import sys

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        sys.stderr.write(f'\nerror: {message}\n')
        sys.exit(2)

def positive_int(value: str) -> int:
    """Type function for argparse to ensure a positive integer."""
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(f"{{value}} is an invalid positive int value. Must be >= 1.")
    return ivalue

def parse_args() -> tuple[argparse.Namespace, argparse.ArgumentParser]:
    """
    Parses command-line arguments.

    Returns:
        tuple[argparse.Namespace, argparse.ArgumentParser]: A tuple containing the parsed arguments and the parser object.
    """
    parser = CustomArgumentParser(description="Extract, clean, and process frames from videos.")
    parser.add_argument("input_path", nargs='?', default=os.getcwd(), help="Path to a video file or a directory containing videos. Defaults to the current directory.")
    parser.add_argument("-o", "--output", default=None, help="Path to the output directory. If not specified, output is saved relative to the input path.")
    parser.add_argument("-i", "--interval", type=positive_int, default=1, help="Interval at which to extract frames. Default is 1 (every frame).")
    parser.add_argument("-s", "--sharpness", type=int, default=100, help="Set the sharpness threshold for blur detection. Lower values are more permissive. Default is 100.")
    parser.add_argument("-d", "--duplicate", type=float, dest="duplicate_threshold", metavar='THRESHOLD', default=1.0, help="Set the threshold for duplicate detection. Higher values (closer to 1.0) are more strict, meaning frames must be nearly identical to be considered duplicates. Default is 1.0.")
    parser.add_argument("-r", "--rotate", type=int, choices=[0, 90, 180, 270], default=0, help="Rotate frames by 0, 90, 180, or 270 degrees. Default is 0 (no rotation).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (debug) output.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the process without creating or deleting files.")
    parser.add_argument("-l", "--limit", type=int, default=None, help="Limit the number of videos to process.")

    return parser.parse_args(), parser