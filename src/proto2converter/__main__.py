import sys
import argparse
import pathlib

from .converter import converters


def main():
    parser = argparse.ArgumentParser(description="Convert a ModelConfig protobuf to a JSON or YAML string.")
    parser.add_argument("--format", choices=converters.keys(), help="Output format.")
    parser.add_argument("filepath", type=pathlib.Path, help="Path to the ModelConfig protobuf file.")

    args = parser.parse_args()

    dst_format, filepath = args.format, args.filepath

    converter = converters[dst_format]

    print(converter(filepath))
    return 0


sys.exit(main())
