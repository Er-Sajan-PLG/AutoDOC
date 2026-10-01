#!/usr/bin/env python3
"""Report measured catalog/template and instantiated-document health; never infer audit coverage."""
import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/doc-sync'))
import engine
sys.path.insert(0, str(ROOT / 'scripts/doc-control'))
import stub_check


def health():
    entries = [doc for catalog in ('CATALOG-A', 'CATALOG-B')
               for domain in json.loads((ROOT / catalog / 'INDEX.yaml').read_text())['domains']
               for doc in domain['documents']]
    complete = sum(all(Path(str(ROOT / doc['template']) + suffix).is_file()
                       for suffix in ('', '.blank', '.example')) for doc in entries)
    controlled = engine.controlled()
    stale, old_drafts = [], []
    today = date.today()
    for path in controlled:
        meta = engine.parse_frontmatter(path)
        due = min(date.fromisoformat(meta['next_review']),
                  date.fromisoformat(meta['last_verified']) + timedelta(days=int(meta['review_days'])))
        if meta['auto_generated'] == 'false' and today > due:
            stale.append({'id': meta['id'], 'criticality': meta['criticality'],
                          'path': str(path.relative_to(ROOT))})
        if (meta['auto_generated'] == 'false' and meta['status'] == 'draft' and
                today > date.fromisoformat(meta['last_updated']) + timedelta(days=60)):
            old_drafts.append(str(path.relative_to(ROOT)))
    approved_stubs, draft_stubs = stub_check.scan()
    return {'created_at_utc': datetime.now(timezone.utc).isoformat(),
            'catalog_document_types': len(entries), 'template_triples_present': complete,
            'controlled_document_instances': len(controlled), 'overdue_human_reviews': stale,
            'drafts_without_updates_over_60_days': old_drafts,
            'substantive_documents': len(controlled) - len(approved_stubs) - len(draft_stubs),
            'approved_stub_documents': approved_stubs, 'draft_stub_documents': draft_stubs,
            'generated_targets': len(engine.load_map()['generated']),
            'drift_free': engine.generate(check=True),
            'note': 'Counts files, deadlines and structural stubs, not semantic correctness or compliance status.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional CI JSON artifact; not committed')
    parser.add_argument('--markdown-output', type=Path, help='Optional CI Markdown report artifact; not committed')
    args = parser.parse_args()
    data = health()
    text = json.dumps(data, indent=2) + '\n'
    print(text, end='')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        lines = ['# AutoDOC health — ' + date.today().isoformat(), '',
                 'Runtime report from checked-out files; not a signed compliance assessment.', '',
                 f'- Catalog types: {data["catalog_document_types"]}',
                 f'- Template triples present: {data["template_triples_present"]}',
                 f'- Controlled documents: {data["controlled_document_instances"]}',
                 f'- Substantive documents: {data["substantive_documents"]}',
                 f'- Approved stub documents: {len(data["approved_stub_documents"])}',
                 f'- Draft stub documents: {len(data["draft_stub_documents"])}',
                 f'- Mapped generated targets: {data["generated_targets"]}',
                 f'- Generated drift-free: {data["drift_free"]}', '',
                 '## Overdue human-owned reviews', '']
        lines.extend('- `' + item['path'] + '` (' + item['criticality'] + ')' for item in data['overdue_human_reviews'])
        if not data['overdue_human_reviews']:
            lines.append('- None detected.')
        lines += ['', '## Drafts not updated in 60 days', '']
        lines.extend('- `' + path + '`' for path in data['drafts_without_updates_over_60_days'])
        if not data['drafts_without_updates_over_60_days']:
            lines.append('- None detected.')
        lines += ['', '## Approved title-only stubs', '']
        lines.extend('- `' + path + '`' for path in data['approved_stub_documents'])
        if not data['approved_stub_documents']:
            lines.append('- None detected.')
        lines += ['', 'External links and prose semantics were not checked.']
        args.markdown_output.write_text('\n'.join(lines) + '\n')
    raise SystemExit(0 if data['drift_free'] and not any(
        item['criticality'] == 'critical' for item in data['overdue_human_reviews']) else 1)
