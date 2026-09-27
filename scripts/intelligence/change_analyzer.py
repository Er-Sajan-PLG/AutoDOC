#!/usr/bin/env python3
"""Check changed sources against the sync map's human review and living state rules."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'doc-sync'))
from engine import impact

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base')
    parser.add_argument('--staged', action='store_true')
    args = parser.parse_args()
    sys.exit(0 if impact(args.base, args.staged) else 1)
