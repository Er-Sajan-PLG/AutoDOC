#!/usr/bin/env python3
"""Enforce AutoDOC requirements and structural checks at the severity the declared phase sets.

One policy, one gate:

  requirements (recommend)      required / recommended documents that are missing
  drift                         generated targets out of step with their sources
  stubs                         approved documents with no content beyond the title
  placeholders                  drafts that are still placeholders
  links.local                   relative links and paths that do not resolve
  secrets.inline                private key markers committed into text
  tribal                        instructions that depend on private knowledge
  freshness                     human-owned documents past their review date

Each family's severity comes from `[severity]` in autodoc.toml first, then from the declared
phase's enforcement block in CONTROL/metadata/CONTEXT-MODEL.json. An undeclared phase is
advisory: findings are reported and nothing fails. A baseline (`autodoc-baseline.json`, written
by `--write-baseline`) suppresses findings recorded during adoption, so a messy repository can
enforce only what is new and ratchet down from there.

AutoDOC checks that records exist and are structured. It never certifies compliance, and the
report says which capability level ran. Exit codes are documented in docs/reference/EXIT-CODES.md.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTELLIGENCE = Path(__file__).resolve().parent
CONTROL = ROOT / 'scripts/doc-control'
BASELINE_NAME = 'autodoc-baseline.json'
BASELINE_SCHEMA = 1
FINGERPRINT_LENGTH = 12
# Security findings are never baselined: suppressing a committed private key would hide a
# problem that stays in git history. A baseline entry for one is ignored, so it always fails.
BASELINE_EXEMPT = ('secrets.inline',)
LEVELS = ('L0 generic (files and git)', 'L1 manifest-aware (facts from manifests)')
INTERNAL_ERROR_EXIT = 3


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context_module = load_module('autodoc_context', INTELLIGENCE / 'context.py')
recommend = load_module('autodoc_recommend', INTELLIGENCE / 'recommend.py')
profiler = load_module('autodoc_profiler', INTELLIGENCE / 'profile.py')
engine = load_module('autodoc_engine', ROOT / 'scripts/doc-sync/engine.py')
guards = load_module('autodoc_guards', CONTROL / 'guards.py')
stub_check = load_module('autodoc_stub_check', CONTROL / 'stub_check.py')


def fingerprint(detail):
    """A stable digest of what was found, so a different problem at the same path is new.

    Location alone is not enough: two different broken links in one file share a path, and
    neither is a new violation only because the other was fixed first.
    """
    normalized = ' '.join(str(detail).split()).lower()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:FINGERPRINT_LENGTH]


def key_of(finding):
    """The identity a baseline records: rule, location, and a fingerprint of the detail."""
    return f"{finding['rule']}|{finding['location']}|{fingerprint(finding['detail'])}"


@contextlib.contextmanager
def repo_scope(root):
    """Point the delegated checkers at `root` for one run, then put them back.

    guards.py, stub_check.py and engine.py are single-repository tools that read a module-level
    ROOT; `enforce.py --repo <elsewhere>` has to answer about *that* repository, so the root is
    rebound for the duration of the collection instead of running three copies of their logic.
    Derived constants (`engine.MAP`) are rebound with it.
    """
    saved = [(module, module.ROOT, getattr(module, 'MAP', None))
             for module in (guards, stub_check, engine)]
    for module, _, _ in saved:
        module.ROOT = root
        if hasattr(module, 'MAP'):
            module.MAP = root / 'docs/.doc-sync-map.yaml'
    try:
        yield
    finally:
        for module, previous_root, previous_map in saved:
            module.ROOT = previous_root
            if hasattr(module, 'MAP'):
                module.MAP = previous_map


def repo_relative(location, root):
    """A path as the repository sees it. Baseline keys must not depend on where the repo lives."""
    try:
        return str(Path(location).resolve().relative_to(Path(root).resolve()))
    except (ValueError, OSError):
        return location


def collect_findings(profile_document, context, documents, groups, enforcement, root=None):
    """Gather findings from every enabled family. Returns (findings, families turned off).

    A family at `off` emits nothing at all, and the report names it: `off` is a decision, not a
    silent skip, so a reader can see which checks did not run. The off list is derived from the
    policy, not from whether a finding happened to exist, or a repo with a clean drive would
    look as if drift had been checked.
    """
    findings = list(recommend.findings(documents, context, groups, enforcement))

    # The delegated checkers keep their own human output for their own entry points; here their
    # findings are carried as data, so their printing is captured rather than duplicated.
    drift, freshness = [], []
    with repo_scope(root or ROOT), \
            contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        engine.generate(check=True, findings=drift)
        engine.validate(freshness=True, findings=freshness)
        structural = drift + freshness + guards.collect() + stub_check.collect()

    if not (root / 'CONTROL/metadata/FRONT-MATTER-SCHEMA.json').is_file():
        for family in ('freshness.critical', 'freshness.review'):
            severity, source = context_module.check_severity(context, family)
            if severity != 'off':
                # Never report clean for a check that could not read its inputs.
                findings.append({
                    'kind': 'check', 'rule': family, 'severity': 'report',
                    'location': 'CONTROL/metadata/FRONT-MATTER-SCHEMA.json',
                    'detail': 'no front-matter schema in this repository, so review dates cannot '
                              'be read; freshness is reported, not checked',
                    'message': 'freshness inputs are missing',
                    'fix': 'adopt CONTROL/metadata/FRONT-MATTER-SCHEMA.json, or turn freshness off',
                    'because': f'{family} check under {source}'})
                break
    off = [family for family in context_module.CHECK_FAMILIES
           if context_module.check_severity(context, family)[0] == 'off']
    for finding in structural:
        finding['location'] = repo_relative(finding['location'], root or ROOT)
        rule = finding['rule']
        severity, source = context_module.check_severity(context, rule)
        if severity == 'off':
            if rule not in off:
                off.append(rule)
            continue
        findings.append({
            'kind': 'check', 'rule': rule, 'severity': severity,
            'location': finding['location'], 'detail': finding['detail'],
            'message': f"{finding['location']}: {finding['detail']}",
            'fix': finding.get('fix', guards.FIXES.get(rule, 'fix the finding')),
            'because': f'{rule} check under {source}',
        })
    return findings, sorted(off)


def load_baseline(path):
    """Read and validate the baseline. A malformed baseline is a usage error, never a pass."""
    if not path.is_file():
        return {'schema': BASELINE_SCHEMA, 'recorded_at': None, 'entries': []}
    # Nothing here trusts the file: entries are data written by a previous run, and a hand-edited
    # entry must not be able to suppress a finding it does not describe.
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != BASELINE_SCHEMA:
        raise ValueError(f'{path.name}: expected schema {BASELINE_SCHEMA}')
    entries = data.get('entries')
    if not isinstance(entries, list) or not all(
            isinstance(entry, dict) and isinstance(entry.get('key'), str) for entry in entries):
        raise ValueError(f'{path.name}: entries must be a list of objects with a key')
    return data


def apply_baseline(findings, baseline, today=None):
    """Split findings into new and suppressed; report baseline entries whose finding is gone.

    The two directions are opposite events and must not be confused:

    * an entry that matches a current finding suppresses it (counted, never failing);
    * an entry whose finding no longer exists is **stale** — the ratchet can be pruned, and a
      stale entry is a warning, not a failure, so fixing something never turns the build red;
    * deleting an entry makes its finding reappear and fail again, which is what makes the
      baseline a ratchet rather than a blanket.
    """
    today = today or date.today()
    recorded = {entry['key']: entry for entry in baseline['entries']}
    kept, suppressed = [], []
    seen = set()
    for finding in findings:
        key = key_of(finding)
        seen.add(key)
        exempt = finding['rule'] in BASELINE_EXEMPT
        if key in recorded and not exempt:
            entry = recorded[key]
            age = None
            if entry.get('recorded_at'):
                try:
                    age = (today - date.fromisoformat(entry['recorded_at'])).days
                except ValueError:
                    age = None
            suppressed.append({**finding, 'baseline': entry, 'baseline_age_days': age})
        else:
            kept.append({**finding, 'baseline_exempt': True} if exempt else finding)
    stale = [entry for key, entry in recorded.items() if key not in seen]
    return kept, suppressed, stale


def write_baseline(path, findings, phase, today=None):
    """Record current findings. Machine-generated JSON, never round-tripped through TOML.

    Security findings are not recorded: see BASELINE_EXEMPT. Entries carry the date they were
    recorded so the ratchet can report their age.
    """
    today = (today or date.today()).isoformat()
    exempt = sorted({finding['rule'] for finding in findings
                     if finding['rule'] in BASELINE_EXEMPT})
    entries = sorted(({'key': key_of(finding), 'rule': finding['rule'],
                       'location': finding['location'], 'detail': finding['detail'],
                       'recorded_at': today}
                      for finding in findings
                      if finding['kind'] != 'config' and finding['rule'] not in BASELINE_EXEMPT),
                     key=lambda entry: entry['key'])
    data = {'schema': BASELINE_SCHEMA, 'recorded_at': today, 'phase': phase, 'entries': entries,
            'exempt': exempt,
            'note': 'Violations recorded during adoption. AutoDOC enforces only what is new; '
                    'prune an entry by fixing it and re-running --write-baseline. Security '
                    'findings are never recorded.'}
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return data


def summarize(findings, suppressed, stale, enforcement):
    """Counts and the exit code, stated once."""
    by_severity = {}
    for finding in findings:
        by_severity[finding['severity']] = by_severity.get(finding['severity'], 0) + 1
    errors = [finding for finding in findings if finding['severity'] == 'error']
    config = [finding for finding in findings if finding['kind'] == 'config']
    exit_code = 2 if config else 1 if errors else 0
    return {'by_severity': dict(sorted(by_severity.items())), 'errors': len(errors),
            'warnings': by_severity.get('warn', 0), 'reported': by_severity.get('report', 0),
            'config_errors': len(config), 'suppressed': len(suppressed),
            'stale_baseline': len(stale), 'exit_code': exit_code,
            'enforcement': enforcement['label'], 'fails': bool(errors) and enforcement['fail']}


def report(data, findings, suppressed, stale, enforcement, exit_code):
    """Markdown: what is enforced, what is new, what the baseline hides, and what it cannot see."""
    lines = ['# AutoDOC enforcement', '',
             f"- Phase: {enforcement['label']}",
             f"- Readiness: {data.get('readiness', 'unknown')} (relative to the declared phase)",
             f"- Enforcement: {enforcement['description']}"]
    pins = data.get('pins') or []
    if not enforcement['declared']:
        # An exit 0 for this reason must not look like a clean run: say what is actually enforced.
        pinned = ', '.join(pins) if pins else 'none'
        lines.append(f'- Advisory: phase undeclared, nothing is enforced except pins: {pinned}')
    elif pins:
        lines.append(f"- Severity pins: {', '.join(pins)}")
    profile = data.get('catalog_profile') or {}
    if profile:
        delta = []
        if profile['added']:
            delta.append(f"adds {', '.join(profile['added'])}")
        if profile['removed']:
            delta.append(f"removes {', '.join(profile['removed'])}")
        lines.append(f"- Catalog profile: {profile['name']} ({profile['core_types']} core types"
                     + (': ' + '; '.join(delta) if delta else '') + ')')
    kinds = data.get('kinds') or {}
    if kinds:
        lines.append(recommend.kind_line(
            kinds, {'undetermined': data.get('undetermined_types') or []}))
    traits = data.get('traits') or {}
    if traits.get('asked'):
        lines.append(recommend.trait_line(
            traits, {'undetermined': data.get('undetermined_types') or []}))
    lines.append(f"- Checks ran at: {', '.join(LEVELS)}; no L2 code-aware checks exist yet")
    age = data.get('phase_age')
    if age:
        lines.append(f"- Phase declared: {age['phase_declared']} ({age['days']} days ago)"
                     + (f" — {age['note']}" if age['review'] else ''))
    actionable = [finding for finding in findings if finding['severity'] in ('warn', 'error')]
    informational = [finding for finding in findings if finding['severity'] == 'report']
    lines += ['', '## Findings', '']
    if not actionable:
        lines.append('None at warning or error severity.')
    for finding in sorted(actionable, key=lambda item: (item['severity'] != 'error', item['rule'],
                                                        str(item['location']))):
        lines.append(f"- **[{finding['severity']}] {finding['rule']}** `{finding['location']}` — "
                     f"{finding['detail']}")
        lines.append(f"  - Fix: {finding['fix']}")
        lines.append(f"  - Because: {finding['because']}")
    if informational:
        # Informational findings never fail; listing a hundred of them would bury the actionable
        # ones, so the report counts them, names the first few, and points at the full JSON.
        shown = ', '.join(f"`{finding['location']}`" for finding in informational[:10])
        more = f' and {len(informational) - 10} more' if len(informational) > 10 else ''
        lines += ['', f"### Informational ({len(informational)})", '',
                  f"{shown}{more}.",
                  '',
                  'These are reported, never failed. `--json` lists them with reasons; '
                  '`make docs-recommend` shows them by section.']
    lines += ['', '## Baseline-suppressed', '',
              f"{len(suppressed)} finding(s) recorded during adoption are suppressed." if suppressed
              else 'None recorded.']
    for finding in suppressed:
        recorded = finding['baseline'].get('recorded_at') or 'date not recorded'
        age = finding.get('baseline_age_days')
        lines.append(f"- `{finding['rule']}` `{finding['location']}` "
                     f"(recorded {recorded}{f', {age} days old' if age is not None else ''})")
    exempt = [finding for finding in findings if finding.get('baseline_exempt')]
    if exempt:
        lines += ['', 'Security findings are never baselined, so they always fail: '
                  + ', '.join(f"`{finding['rule']}` `{finding['location']}`" for finding in exempt)]
    lines += ['', '## Stale baseline entries', '']
    if stale:
        # Stale entries warn: failing on them would turn a fixed violation into a red build.
        lines.append(f"{len(stale)} entr(ies) no longer match anything; this is a warning, not a "
                     'failure. Re-run --write-baseline to prune the ratchet:')
        lines += [f"- `{entry['rule']}` `{entry['location']}`" for entry in stale]
    else:
        lines.append('None.')
    off_types = data.get('off_types') or []
    if off_types:
        # A type that is off at this phase is a decision with a reason, not a silent skip.
        lines += ['', f'## Not applicable at this phase ({len(off_types)})', '']
        for entry in off_types:
            becomes = f"; becomes required at {entry['becomes_required_at']}" \
                if entry.get('becomes_required_at') else ''
            lines.append(f"- `{entry['id']}` {entry['name']} — {entry.get('reason')}{becomes}")
    undetermined = data.get('undetermined_types') or []
    if undetermined:
        # An undetermined type is a question, not a failure: say what is unknown and why.
        lines += ['', f'## Undetermined ({len(undetermined)})', '']
        for entry in undetermined:
            unknown = ', '.join(sorted(token for token, value in entry['tokens'].items()
                                       if value == 'unknown'))
            lines.append(f"- `{entry['id']}` {entry['name']} — cannot be decided from {unknown}; "
                         'declaring the fact or kind answers it')
    lines += ['', '## Cannot see', '']
    if data.get('off_families'):
        lines.append(f"Off at this phase, so not run: {', '.join(data['off_families'])}. "
                     'An off check is a declared decision; a [severity] override turns it back on.')
    lines += ['Facts are file-presence evidence with stated limits; undetermined items are '
              'reported, never failed. External links are not fetched while offline.',
              '',
              '---', '',
              'AutoDOC checks that records exist and are structured. **It never certifies '
              'compliance.**', '']
    return '\n'.join(lines)


def build(args):
    """Load context, resolve requirements, collect every family and apply the baseline."""
    context = context_module.load(args.config) if args.config.is_file() else {}
    context = context_module.normalise(context)
    problems = context_module.validate_model() + context_module.validate(context)
    if problems:
        raise ValueError('; '.join(problems))
    profile_document = profiler.profile(args.repo, context['facts'])
    enforcement = context_module.enforcement(context['phase'])
    documents = recommend.catalog()
    placement = recommend.profile_placement(documents, context)
    groups = recommend.evaluate(documents, profile_document, context, enforcement, placement)
    findings, off = collect_findings(profile_document, context, documents, groups, enforcement,
                                     root=args.repo.resolve())
    baseline = load_baseline(args.baseline)
    kept, suppressed, stale = apply_baseline(findings, baseline)
    data = {'version': 1, 'repo': profile_document['repo'], 'phase': context['phase'],
            'phase_age': context_module.phase_age(context), 'enforcement': enforcement,
            'readiness': recommend.score(documents, groups, enforcement)['readiness'],
            'off_families': off, 'levels': list(LEVELS),
            'kinds': recommend.kind_summary(profile_document, context),
            'traits': recommend.trait_summary(profile_document, context),
            'catalog_profile': recommend.score_profile(placement),
            'off_types': [{'id': item['id'], 'name': item['name'],
                           'reason': item.get('off_reason'),
                           'becomes_required_at': item.get('phase_min')}
                          for item in groups['off']],
            'pins': [f'{rule} = "{severity}"'
                     for rule, severity in sorted(context['severity'].items())],
            'unknown_facts': sorted(name for name, entry in profile_document['facts'].items()
                                    if entry['value'] == 'unknown'),
            'undetermined_types': [{'id': item['id'], 'name': item['name'],
                                    'tokens': {token: value
                                               for token, value in item['tokens'].items()
                                               if value == 'unknown'}}
                                   for item in groups['undetermined']]}
    summary = summarize(kept, suppressed, stale, enforcement)
    data['summary'] = summary
    return data, kept, suppressed, stale, enforcement, summary


def machine_document(data, findings, suppressed, stale, enforcement, summary):
    """The JSON shape: everything the terminal text says, not only the prose."""
    return {'version': 1, 'phase': data['phase'], 'phase_age': data['phase_age'],
            'readiness': data['readiness'], 'levels': data['levels'],
            'off_families': data['off_families'], 'pins': data['pins'],
            'catalog_profile': data['catalog_profile'], 'off_types': data['off_types'],
            'kinds': data['kinds'], 'traits': data['traits'],
            'undetermined': [{'id': item['id'], 'name': item['name'],
                              'unknown': sorted(item['tokens'])}
                             for item in data['undetermined_types']],
            'enforcement': enforcement, 'summary': summary, 'findings': findings,
            'suppressed': [{key: value for key, value in finding.items() if key != 'baseline'}
                           for finding in suppressed],
            'stale_baseline': [{'rule': entry['rule'], 'location': entry['location'],
                                'recorded_at': entry.get('recorded_at')} for entry in stale]}


def run(args):
    data, findings, suppressed, stale, enforcement, summary = build(args)
    if args.write_baseline:
        recorded = write_baseline(args.baseline, findings + suppressed, data['phase'])
        print(f"Recorded {len(recorded['entries'])} finding(s) in {args.baseline.name}")
        for rule in recorded.get('exempt', []):
            print(f'Not recorded: {rule} findings are never baselined')
        return 0
    document = (machine_document(data, findings, suppressed, stale, enforcement, summary)
                if args.json else
                report(data, findings, suppressed, stale, enforcement, summary['exit_code']))
    text = json.dumps(document, indent=2) + '\n' if args.json else document
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
        print('Wrote', args.output)
    else:
        print(text, end='')
    for finding in findings:
        if finding['severity'] == 'error':
            print(f"[error] {finding['rule']} {finding['location']}: {finding['detail']}",
                  file=sys.stderr)
    if stale:
        # A stale entry is a warning: failing on it would punish fixing a violation.
        print(f'WARNING: {len(stale)} baseline entr(ies) no longer match anything; '
              're-run --write-baseline to prune the ratchet', file=sys.stderr)
    exit_code = summary['exit_code']
    if args.fail_on_stale and stale and exit_code == 0:
        exit_code = 1
    if exit_code:
        print(f"Enforcement failed: {summary['errors']} error(s), "
              f"{summary['warnings']} warning(s), {summary['suppressed']} suppressed, "
              f"{len(stale)} stale", file=sys.stderr)
    return exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--config', type=Path, help='Context file (default <repo>/autodoc.toml)')
    parser.add_argument('--baseline', type=Path, help=f'Baseline file (default <repo>/{BASELINE_NAME})')
    parser.add_argument('--write-baseline', action='store_true',
                        help='Record current findings as the baseline and exit')
    parser.add_argument('--fail-on-stale', action='store_true',
                        help='Fail (exit 1) when baseline entries no longer match anything')
    parser.add_argument('--json', action='store_true', help='Print JSON instead of Markdown')
    parser.add_argument('--output', type=Path, help='Write the report here instead of stdout')
    args = parser.parse_args()
    args.config = args.config or (args.repo / 'autodoc.toml')
    args.baseline = args.baseline or (args.repo / BASELINE_NAME)
    try:
        return run(args)
    except (KeyboardInterrupt, SystemExit):
        raise
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        # A usage or configuration problem: never a statement about the documentation.
        print('Enforcement error:', error, file=sys.stderr)
        return 2
    except Exception as error:  # noqa: BLE001 - the point is to keep it off exit 1
        # An unhandled exception exits 1 by default, which would impersonate "findings".
        print(f'Internal error: {type(error).__name__}: {error}', file=sys.stderr)
        print('This is a tool failure, not a finding about this repository.', file=sys.stderr)
        return INTERNAL_ERROR_EXIT


if __name__ == '__main__':
    raise SystemExit(main())
