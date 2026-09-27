#!/usr/bin/env python3
"""Fail on invalid mapping schema, missing sources, target collisions or orphan review targets."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/doc-sync'))
from engine import load_map, safe_path


def check():
    data = load_map()
    ids = {entry['id'] for entry in data['generated']}
    for rule in data['review']:
        if rule['id'] in ids or rule['level'] not in ('block', 'warn'):
            raise ValueError('Duplicate rule ID or invalid level: ' + rule['id'])
        ids.add(rule['id'])
        if not rule.get('sources') or not rule.get('targets'):
            raise ValueError('Missing review sources/targets: ' + rule['id'])
        for target in rule['targets']:
            if not safe_path(target).is_file():
                raise ValueError('Missing human review target: ' + target)
    for target in data['living']['targets'] + [data['changelog']['target']]:
        if not safe_path(target).is_file():
            raise ValueError('Missing living state or changelog target: ' + target)
    return True


if __name__ == '__main__':
    try:
        check()
        print('Sync map valid')
    except (ValueError, KeyError, OSError) as exc:
        raise SystemExit(f'Sync map error: {exc}')
