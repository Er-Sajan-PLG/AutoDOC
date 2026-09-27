#!/usr/bin/env python3
"""Reject unfilled instantiated starter documents; catalogs and templates are not instances."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SECTIONS = ('## Purpose and scope', '## Details and decisions', '## Verification and references')


def check():
    errors = []
    paths = [ROOT / 'EXAMPLE-PROJECT/docs/ARCHITECTURE.md']
    if (ROOT / 'docs/autodoc').exists():
        paths += list((ROOT / 'docs/autodoc').rglob('*.md'))
    for path in paths:
        text = path.read_text()
        for section in SECTIONS:
            if section not in text:
                errors.append(f'{path.relative_to(ROOT)}: missing {section}')
        if '<!-- Fill in.' in text or '@assign-owner' in text:
            errors.append(f'{path.relative_to(ROOT)}: unfilled scaffold')
    for error in errors:
        print(error, file=sys.stderr)
    return not errors


if __name__ == '__main__':
    raise SystemExit(0 if check() else 1)
