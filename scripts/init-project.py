#!/usr/bin/env python3
"""Scaffold a small, explicit starter set of controlled docs in an existing project directory."""
import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = ['Problem statement', 'Goals and non goals', 'Scope', 'Success metrics',
              'System overview', 'ADR', 'Test strategy', 'Local setup', 'Current state', 'Next action']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True, help='Project name (not the AutoDOC repository name)')
    parser.add_argument('--type', default='generic', choices=['generic', 'web-api', 'cli', 'library', 'ai-agent'])
    parser.add_argument('--output', required=True, type=Path, help='Existing project directory')
    args = parser.parse_args()
    if not args.output.is_dir():
        parser.error('--output must be an existing directory (never scaffolds over a missing path)')
    catalog = json.loads((ROOT / 'CATALOG-B/INDEX.yaml').read_text())
    docs = [d for domain in catalog['domains'] for d in domain['documents']]
    chosen = [next(d for d in docs if d['name'] == name) for name in FOUNDATION]
    target = args.output / 'docs' / 'autodoc'
    slug = re.sub(r'[^A-Z0-9]+', '-', args.name.upper()).strip('-') or 'PROJECT'
    today = date.today()
    for doc in chosen:
        name = doc['name'].lower().replace(' ', '-')
        path = target / (name + '.md')
        if path.exists():
            print('Skipped existing', path)
            continue
        content = (f'---\nid: INST-{slug}-{doc["id"]}\ntitle: "{args.name}: {doc["name"]}"\n'
                   f'type: {doc["type"]}\nowner: "@assign-owner"\nreviewer: "@assign-reviewer"\n'
                   f'classification: internal\nstatus: draft\nversion: "0.1"\n'
                   f'effective_date: {today}\nnext_review: {today + timedelta(days=90)}\n'
                   f'source_of_truth: human\nsupersedes: null\nrelated: []\ncriticality: high\n'
                   f'review_days: 90\nlast_verified: 1970-01-01\nlast_reviewed: 1970-01-01\nlast_updated: {today}\n'
                   f'auto_generated: false\n---\n\n'
                   f'# {doc["name"]}\n\n> Draft scaffold for {args.name} ({args.type}). '
                   'Replace owner, reviewer and content; dates are creation dates, not proof of verification.\n\n'
                   '## Purpose and scope\n\n<!-- Describe applicability. -->\n\n'
                   '## Details and decisions\n\n<!-- Add project facts and reasoning. -->\n\n'
                   '## Verification and references\n\n<!-- Link primary sources. -->\n')
        target.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        print('Created', path)
    print('Next: assign owners, replace placeholders, select other applicable catalog entries and configure a sync map.')


if __name__ == '__main__':
    main()
