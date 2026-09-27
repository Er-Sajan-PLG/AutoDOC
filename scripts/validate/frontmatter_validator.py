#!/usr/bin/env python3
"""Validate controlled Markdown metadata (no external YAML dependency)."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'doc-sync'))
from engine import validate, validate_staged

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', action='store_true', help='Also inspect exact index blobs')
    args = parser.parse_args()
    good = validate()
    if args.staged:
        good = validate_staged() and good
    sys.exit(0 if good else 1)
