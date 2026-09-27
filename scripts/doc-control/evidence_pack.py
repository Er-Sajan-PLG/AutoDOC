#!/usr/bin/env python3
"""Package actual passing test output and scoped, unsigned source/document facts."""
import argparse
import hashlib
import json
import os
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/doc-sync'))
import engine
sys.path.insert(0, str(ROOT / 'engine'))
from extractors.facts import python_dependencies


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def collect_checks():
    """Capture real command output for the checks that govern this checkout."""
    commands = [
        ('drift', ['scripts/doc-sync/check-doc-drift.py']),
        ('metadata', ['scripts/validate/frontmatter_validator.py']),
        ('inventory', ['scripts/doc-sync/generate-all.py', '--check', '--only', 'human-inventory']),
        ('ownership', ['scripts/doc-control/check_ownership.py']),
        ('freshness', ['scripts/doc-sync/engine.py', 'freshness']),
        ('sync-map', ['scripts/doc-control/check_sync_map.py']),
        ('local-links', ['scripts/doc-control/guards.py']),
    ]
    checks = []
    for name, argv in commands:
        cmd = [sys.executable, *argv]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        checks.append({'name': name, 'command': cmd, 'exit_code': result.returncode,
                       'stdout': result.stdout, 'stderr': result.stderr,
                       'ran_at_utc': datetime.now(timezone.utc).isoformat()})
    return checks


def make_pack(test_path, output):
    test = json.loads(test_path.read_text(encoding='utf-8'))
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if (test.get('kind') != 'autodoc-test-run' or test.get('exit_code') != 0 or
        test.get('commit') != commit or
        digest(test.get('stdout', '').encode()) != test.get('stdout_sha256') or
        digest(test.get('stderr', '').encode()) != test.get('stderr_sha256')):
        raise ValueError('Test evidence is failing, from another commit, or its output hashes do not match')
    if not engine.generate(check=True) or not engine.validate(freshness=True):
        raise ValueError('Documentation checks failed; cannot package passing evidence')
    project, version, declared = python_dependencies(ROOT / 'pyproject.toml')
    if any(group == 'runtime' for group, _ in declared):
        raise ValueError('Runtime dependencies exist; install/resolution-based SBOM integration required')
    now = datetime.now(timezone.utc).isoformat()
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
    sbom = {'bomFormat': 'CycloneDX', 'specVersion': '1.5', 'version': 1,
            'metadata': {'timestamp': now, 'component': {'type': 'application', 'name': project,
                                                          'version': version}},
            'components': [], 'properties': [{'name': 'autodoc:scope',
                'value': 'Declared project only; no installed or optional dependency resolution'}]}
    sources = sorted({*ROOT.glob('scripts/doc-sync/*.py'), *ROOT.glob('scripts/doc-control/*.py'),
                      ROOT / 'pyproject.toml', ROOT / 'docs/.doc-sync-map.yaml',
                      ROOT / 'CONTROL/metadata/FRONT-MATTER-SCHEMA.json',
                      ROOT / 'EXAMPLE-PROJECT/routes.json', ROOT / 'EXAMPLE-PROJECT/db/schema.sql'})
    materials = {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in sources}
    build = {'kind': 'unsigned-source-record', 'source_git_sha': commit,
             'git_branch': branch, 'git_dirty': dirty, 'signed': False,
             'builder': os.environ.get('GITHUB_RUN_ID', 'local'), 'created_at_utc': now,
             'materials_sha256': materials,
             'warning': 'No build was attested or signed; this is not SLSA provenance.'}
    docs = []
    for path in engine.controlled():
        meta = engine.parse_frontmatter(path)
        overdue = meta['auto_generated'] == 'false' and date.today() > min(
            date.fromisoformat(meta['next_review']),
            date.fromisoformat(meta['last_verified']) + timedelta(days=int(meta['review_days'])))
        docs.append({'id': meta['id'], 'path': str(path.relative_to(ROOT)),
                     'auto_generated': meta['auto_generated'] == 'true', 'overdue': overdue})
    doc_record = {'kind': 'documentation-check', 'commit': commit, 'generated_drift_free': True,
                  'mapped_generated_targets': len(engine.load_map()['generated']),
                  'controlled_documents': docs, 'created_at_utc': now}
    checks = collect_checks()
    failures = [row['name'] + ': ' + row['stderr'] for row in checks if row['exit_code'] != 0]
    if failures:
        raise ValueError('Evidence checks failed: ' + '; '.join(failures))
    payloads = {'sbom.json': sbom, 'source-record.json': build,
                'doc-evidence.json': doc_record, 'test-evidence.json': test,
                'checks.json': {'kind': 'actual-command-results', 'checks': checks}}
    output.mkdir(parents=True, exist_ok=True)
    manifest = {'kind': 'autodoc-evidence-pack', 'commit': commit, 'created_at_utc': now,
                'git_branch': branch, 'git_dirty': dirty, 'unsigned': True,
                'artifacts_sha256': {}}
    for name, payload in payloads.items():
        raw = (json.dumps(payload, indent=2) + '\n').encode()
        (output / name).write_bytes(raw)
        manifest['artifacts_sha256'][name] = digest(raw)
    (output / 'evidence-pack.json').write_text(json.dumps(manifest, indent=2) + '\n')
    summary = {'pack_version': 1, 'generated_at_utc': now, 'git_commit_sha': commit,
               'git_branch': branch, 'git_dirty': dirty, 'unsigned': True,
               'test_evidence': {'counts': test.get('counts'), 'exit_code': test['exit_code']},
               'checks': [{'name': row['name'], 'exit_code': row['exit_code']} for row in checks],
               'doc_evidence': {'generated_drift_free': True, 'controlled_documents': len(docs)},
               'sbom_summary': 'Declared project only; no resolved packages',
               'build_attestation_summary': 'Unsigned source record; no build attested',
               'evidence_files': [{'path': name, 'sha256': sha} for name, sha in manifest['artifacts_sha256'].items()]}
    (output / 'evidence-pack-latest.json').write_text(json.dumps(summary, indent=2) + '\n')
    return manifest


def verify(output):
    manifest = json.loads((output / 'evidence-pack.json').read_text())
    if manifest.get('kind') != 'autodoc-evidence-pack' or not manifest.get('artifacts_sha256'):
        raise ValueError('Missing or malformed evidence manifest')
    for name, expected in manifest['artifacts_sha256'].items():
        if Path(name).name != name or digest((output / name).read_bytes()) != expected:
            raise ValueError('Evidence artifact missing or altered: ' + name)
    latest = json.loads((output / 'evidence-pack-latest.json').read_text())
    if (latest.get('unsigned') is not True or latest.get('git_commit_sha') != manifest['commit'] or
        {row['path']: row['sha256'] for row in latest.get('evidence_files', [])} != manifest['artifacts_sha256']):
        raise ValueError('Unsigned evidence summary does not match recorded artifact hashes')
    checks = json.loads((output / 'checks.json').read_text()).get('checks', [])
    if not checks or any(row['exit_code'] != 0 for row in checks):
        raise ValueError('Evidence contains no passing actual doc checks')
    test = json.loads((output / 'test-evidence.json').read_text())
    if test.get('exit_code') != 0 or test.get('commit') != manifest['commit']:
        raise ValueError('Evidence test run did not pass for the recorded commit')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', type=Path, help='Actual test_evidence.py output to package')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'evidence/out')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    try:
        if args.verify:
            verify(args.output_dir)
            print('Evidence hashes verified (not signatures)')
        else:
            if not args.test:
                parser.error('--test required when packaging')
            make_pack(args.test, args.output_dir)
            verify(args.output_dir)
            print('Scoped evidence pack created:', args.output_dir)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(1, f'Evidence error: {exc}\n')
