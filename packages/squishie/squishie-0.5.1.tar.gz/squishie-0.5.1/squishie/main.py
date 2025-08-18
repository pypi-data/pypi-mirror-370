# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import argparse
import sys
from pathlib import Path

from .builder import build_document
from .serializers import load_document


def main():
    parser = argparse.ArgumentParser(prog="squishie")
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        type=argparse.FileType("r"),
        help="document config file path",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="output file path",
    )
    args = parser.parse_args()

    document = load_document(args.config)
    output = build_document(Path(args.config.name).parent, document)
    args.output.write(output)
