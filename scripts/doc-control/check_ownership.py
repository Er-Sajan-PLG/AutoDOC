#!/usr/bin/env python3
"""Ensure every controlled document has a known owner assigned to its path."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/doc-sync'))
from engine import controlled, matches, parse_frontmatter


def check():
    matrix = json.loads((ROOT / 'CONTROL/metadata/OWNERSHIP-MATRIX.yaml').read_text())
    if matrix.get('version') != 1 or not matrix.get('owners'):
        raise ValueError('Missing ownership matrix or unsupported version')
    errors = []
    paths = list(controlled())
    for owner, rule in matrix['owners'].items():
        for pattern in rule.get('paths', []):
            if not any(matches(str(p.relative_to(ROOT)), pattern) for p in paths):
                errors.append(f'{owner}: ownership path pattern has no controlled document: {pattern}')
    for path in paths:
        rel = str(path.relative_to(ROOT))
        metadata = parse_frontmatter(path)
        owner = metadata.get('owner')
        if metadata.get('criticality') in ('critical', 'high') and not metadata.get('reviewer'):
            errors.append(f'{rel}: high/critical document needs reviewer in frontmatter')
        if owner not in matrix['owners'] or not any(
            matches(rel, pattern) for pattern in matrix['owners'][owner]['paths']
        ):
            errors.append(f'{rel}: no assigned owner with path authority ({owner})')
    for error in errors:
        print(error, file=sys.stderr)
    return not errors


if __name__ == '__main__':
    raise SystemExit(0 if check() else 1)
