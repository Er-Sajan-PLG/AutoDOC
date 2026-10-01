#!/usr/bin/env python3
"""Render the CATALOG-A/B indices from the seed and rules in CONTROL/metadata/CATALOG-RULES.json.

Names and ids are seeded by hand; every derived field (type, tier, applies_when, phase,
maturity, mode) is a rule in that data file. This script holds no classification heuristics.
Do not hand-edit an index; edit the rules and run `make generate` (or `--check` in CI).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / 'CONTROL/metadata/CATALOG-RULES.json'
TEMPLATE_DIR = {'SPEC': 'SPECIFICATIONS', 'DEC': 'DECISIONS', 'DES': 'ARCHITECTURE',
                'PROC': 'PROCEDURES', 'POL': 'POLICIES', 'REF': 'REFERENCES',
                'REC': 'RECORDS', 'EVD': 'EVIDENCE', 'TPL': 'AGENT-CONTEXT'}
NOTE = ('Inventory of possible documents. Applicability labels are suggestions, not a mandate or '
        'evidence of adoption. Derived fields come from CONTROL/metadata/CATALOG-RULES.json.')


def load_rules():
    rules = json.loads(RULES.read_text(encoding='utf-8'))
    if rules.get('version') != 1:
        raise ValueError('Unsupported catalog rules version')
    return rules


def kind(name, domain, rules):
    spec = rules['kinds']
    for rule in spec['by_keyword']:
        haystack = name if rule['case_sensitive'] else name.lower()
        needle = rule['match'] if rule['case_sensitive'] else rule['match'].lower()
        if needle in haystack:
            return rule['type']
    result = spec['default']
    override = spec['design_override']
    if result == override['only_when_default'] and (
            domain.startswith(tuple(override['domain_prefixes'])) or name in override['names']):
        return override['type']
    return result


def phase(domain, rules):
    spec = rules['phases']
    if domain[0] in spec['by_prefix']:
        return spec['by_prefix'][domain[0]]
    for label, numbers in spec['by_domain_number'].items():
        if domain[:3] in numbers:
            return label
    return spec['default']


def maturity(domain, phase_label, rules):
    spec = rules['maturity']
    return spec['by_prefix'].get(domain[0]) or spec['by_phase'].get(phase_label)


def applies_when(doc_id, domain, rules):
    """Explicit override, then the core list's own predicate, then the domain default."""
    spec = rules['applies_when']
    if doc_id in spec['by_id']:
        return spec['by_id'][doc_id]
    for entry in rules['tier']['core']:
        if entry['id'] == doc_id:
            return entry['applies_when']
    return spec['by_domain'].get(domain) or spec['default']


def tier(doc_id, rules):
    """Return (tier, why, phase_min) for one document id."""
    spec = rules['tier']
    for entry in spec['core']:
        if entry['id'] == doc_id:
            return 'core', entry['why'], entry.get('phase_min')
    if doc_id in spec['extended']:
        return 'extended', None, None
    return spec['default'], None, None


def entries(seed, prefix, rules):
    result = []
    for index, source in enumerate(seed, 1):
        domain = f'{prefix}{index:02d}-{source["slug"]}'
        documents = []
        for number, name in enumerate(source['names'].split('|'), 1):
            doc_id = f'{"DOC" if prefix == "A" else "DEV"}-{prefix}{index:02d}-{number:03d}'
            doc_kind = kind(name, domain, rules)
            doc_phase = phase(domain, rules)
            doc_tier, why, phase_min = tier(doc_id, rules)
            template_dir = 'AGENT-CONTEXT' if domain.startswith('B09-') else TEMPLATE_DIR[doc_kind]
            documents.append({
                'id': doc_id, 'name': name, 'type': doc_kind, 'tier': doc_tier,
                'tier_reason': why, 'phase_min': phase_min,
                'applies_when': applies_when(doc_id, domain, rules),
                'audience': 'project team', 'owner': '@project-owner', 'owner_type': 'project owner',
                'purpose': f'Record {name.lower()} for {source["purpose"].lower()}.',
                'when': doc_phase, 'maturity': maturity(domain, doc_phase, rules),
                'required_content': ['Purpose and scope', 'Details and decisions', 'Verification and references'],
                'related': [], 'mode': rules['mode_by_kind'].get(doc_kind, rules['mode_by_kind']['default']),
                'template': f'TEMPLATES/{template_dir}/{doc_id}.md'})
        result.append({'domain': domain, 'purpose': source['purpose'], 'documents': documents})
    return {'version': 1, 'note': NOTE, 'domains': result}


def render(rules):
    return {catalog: entries(rules['seed'][catalog[-1]], catalog[-1], rules)
            for catalog in ('CATALOG-A', 'CATALOG-B')}


def run(check=False):
    rules = load_rules()
    drift = []
    for catalog, data in render(rules).items():
        target = ROOT / catalog / 'INDEX.yaml'
        expected = json.dumps(data, indent=2) + '\n'
        if target.exists() and target.read_text(encoding='utf-8') == expected:
            continue
        drift.append(str(target.relative_to(ROOT)))
        if not check:
            target.write_text(expected, encoding='utf-8')
            print('Updated', target.relative_to(ROOT))
    if drift and check:
        print('Catalog index drift (rules changed without regenerating): ' + ', '.join(drift)
              + '; run make generate', file=sys.stderr)
    return not drift


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check instead of writing')
    args = parser.parse_args()
    try:
        raise SystemExit(0 if run(args.check) else 1)
    except (ValueError, OSError) as error:
        raise SystemExit(f'Catalog build error: {error}')
