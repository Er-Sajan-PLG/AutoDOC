#!/usr/bin/env python3
"""Generate/check canonical, example and blank templates for every catalog A/B entry."""
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def render(doc, variant):
    name, id_ = doc['name'], doc['id']
    # Catalog IDs name *types*, not instances. Never pretend an illustrative sample is evidence.
    instance = f'SAMPLE-{id_}' if variant == 'example' else 'REPLACE-WITH-UNIQUE-INSTANCE-ID'
    status = 'draft'
    header = (f'---\nid: {instance}\ntitle: "{name}"\ntype: {doc["type"]}\n'
              'owner: "@assign-owner"\nreviewer: "@assign-reviewer"\nclassification: internal\n'
              f'status: {status}\nversion: "0.1"\neffective_date: 2026-09-26\n'
              'next_review: 2026-12-25\nsource_of_truth: human\nsupersedes: null\n'
              'related: []\ncriticality: high\nreview_days: 90\nlast_verified: 1970-01-01\n'
              'last_reviewed: 1970-01-01\nlast_updated: 2026-09-26\nauto_generated: false\n---\n\n')
    if variant == 'example':
        body = (f'> Synthetic illustration of **{name}** (`{id_}`); not an approved project document '
                'or proof of any control. Dates above are sample values.\n\n'
                f'## Purpose and scope\n\nA sample team uses this {name.lower()} to define the boundary '
                'of a fictional service. Real scope, owner and audience must be confirmed.\n\n'
                '## Details and decisions\n\nThe sample team records assumptions, accountable decisions '
                'and alternatives here. It does not claim any service is deployed or audited.\n\n'
                '## Verification and references\n\nThe sample team would link its primary implementation '
                'or review record here and record the verification date. No evidence is supplied.\n')
    elif variant == 'blank':
        body = (f'> Blank instance for {name} (`{id_}`). Replace metadata including dates; '
                'the sample date is **not** verification.\n\n'
                '## Purpose and scope\n\n<!-- Fill in. -->\n\n## Details and decisions\n\n'
                '<!-- Fill in. -->\n\n## Verification and references\n\n<!-- Link evidence. -->\n')
    else:
        body = (f'> Canonical structure for **{name}** (`{id_}`; {doc["type"]}). '
                'Choose an owner and unique instance ID before use.\n\n'
                f'## Purpose and scope\n\nState why {name.lower()} applies, who uses it and what is out of scope.\n\n'
                f'## Details and decisions\n\nDescribe the project-specific {name.lower()} facts, '
                'assumptions, alternatives, failure modes and responsible people.\n\n'
                '## Verification and references\n\nLink the authoritative code, policy, test or human '
                'approval; explain how to check the claims and when they must be reviewed.\n')
    return header + f'# {name}\n\n' + body


def run(check):
    changed = []
    ids = set()
    for catalog in ('CATALOG-A', 'CATALOG-B'):
        data = json.loads((ROOT / catalog / 'INDEX.yaml').read_text())
        if data['version'] != 1:
            raise ValueError('Unsupported catalog version')
        for domain in data['domains']:
            for doc in domain['documents']:
                if doc['id'] in ids:
                    raise ValueError('Duplicate catalog ID: ' + doc['id'])
                ids.add(doc['id'])
                target = ROOT / doc['template']
                for variant, path in [('canonical', target), ('example', Path(str(target) + '.example')),
                                      ('blank', Path(str(target) + '.blank'))]:
                    content = render(doc, variant)
                    if not path.exists() or path.read_text() != content:
                        changed.append(str(path.relative_to(ROOT)))
                        if not check:
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_text(content)
    if changed:
        print(('Template drift: ' if check else 'Generated templates: ') + str(len(changed)))
        for path in changed[:10]:
            print(' ', path)
    return not (check and changed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.check) else 1)
