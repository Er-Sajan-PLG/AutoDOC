#!/usr/bin/env python3
"""Event triggers: declare when AutoDOC runs, and prove the wiring matches the declaration.

The model in `CONTROL/metadata/TRIGGERS.json` says which event runs what, what is allowed to stop
a merge, and what is only triage. This module prints it (`make docs-triggers`, and the generated
`docs/generated/TRIGGER-REFERENCE.md`) and checks it (`--check`, part of `make ci`).

The check is deliberately hostile to silent drift: every workflow file must be claimed by a
declared job, every declared job must exist with that name and those trigger events, every
declared command must resolve to a file or a Make target, a required check may not be path-, tag-
or branch-filtered (a filtered required check can stay pending forever), and anything that opens
a network connection must be non-blocking with a stated rate limit.

The workflow reader is line-based and stdlib-only, like the frontmatter reader: it reads workflow
`name`, trigger keys, per-trigger filters and job names, which is all the model claims. A job
produced by a reusable workflow, or a file it cannot parse, is reported as unverified — never
passed.

Exit codes: 0 printed or valid, 1 reserved, 2 the declaration and the wiring disagree or the
model cannot be read, 3 the tool itself failed (never reported as a finding).
"""
import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / 'CONTROL/metadata/TRIGGERS.json'
WORKFLOWS = ROOT / '.github/workflows'
HOOK = ROOT / 'scripts/hooks/pre-push'
FILTERS = {'paths': 'paths_filtered', 'paths-ignore': 'paths_filtered',
           'tags': 'tag_filtered', 'tags-ignore': 'tag_filtered',
           'branches': 'branch_filtered', 'branches-ignore': 'branch_filtered'}
POSTURES = ('gate', 'convenience', 'report', 'advisory', 'release')


def load(path=None):
    model = json.loads(Path(path or MODEL).read_text(encoding='utf-8'))
    if model.get('version') != 1:
        raise ValueError('triggers: unsupported model version')
    return model


def context_module():
    spec = importlib.util.spec_from_file_location('autodoc_triggers_context',
                                                  ROOT / 'scripts/intelligence/context.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_workflow(path):
    """Read the fields the model claims: workflow name, trigger keys, filters, job names.

    Returns None for a file this reader cannot read (no `on:` or no `jobs:`), so the check reports
    it as unverified instead of assuming it is fine.
    """
    text = Path(path).read_text(encoding='utf-8')
    name, events, jobs = None, {}, {}
    section = None
    current_event = None
    current_job = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip(' '))
        key = line.strip().split(':', 1)[0]
        if indent == 0:
            if key == 'on':
                section = 'on'
                continue
            if key == 'jobs':
                section = 'jobs'
                continue
            if key == 'name' and name is None:
                name = line.split(':', 1)[1].strip()
            if not line.startswith((' ', '\t')) and key not in ('on', 'jobs'):
                section = None
            continue
        if section == 'on':
            if indent == 2:
                events[key] = {'paths_filtered': False, 'tag_filtered': False, 'branch_filtered': False}
                current_event = key
            elif indent == 4 and current_event:
                flag = FILTERS.get(key)
                if flag:
                    events[current_event][flag] = True
        elif section == 'jobs':
            if indent == 2:
                jobs[key] = {'name': key}
                current_job = key
            elif indent == 4 and key == 'name' and current_job:
                jobs[current_job]['name'] = line.split(':', 1)[1].strip()
    if not events or not jobs:
        return None
    return {'name': name, 'events': events, 'jobs': jobs}


def workflows():
    """Every workflow file, read; an unreadable one maps to None and is reported, never skipped."""
    return {path: read_workflow(path) for path in sorted(WORKFLOWS.glob('*.yml'))}


def make_targets():
    text = (ROOT / 'Makefile').read_text(encoding='utf-8')
    return {match.group(1) for match in re.finditer(r'^([A-Za-z0-9_.-]+):', text, re.MULTILINE)}


def resolve_command(command):
    """(True, None) when a declared command names something that exists, else (False, reason)."""
    parts = command.split()
    if not parts:
        return False, 'empty command'
    if parts[0] == 'make':
        if len(parts) < 2:
            return False, 'make without a target'
        target = parts[1].split('=')[0] if '=' in parts[1] else parts[1]
        if target not in make_targets():
            return False, f'no Makefile target {target!r}'
        return True, None
    executable = parts[1] if parts[0] in ('python', 'python3') and len(parts) > 1 else parts[0]
    candidate = executable.strip('"\'')
    if '$' in candidate:
        return False, f'cannot resolve {candidate!r} because it interpolates a variable'
    if not (ROOT / candidate).exists():
        return False, f'no such path {candidate!r}'
    return True, None


def check(model=None, workflows_=None):
    """Every rule the model claims, checked against the repository. Returns a list of errors."""
    model = model or load()
    workflows_ = workflows_ if workflows_ is not None else workflows()
    errors = []
    if not model.get('principle'):
        errors.append('model.principle: the event model must state its principle')
    if len(model.get('never', [])) < 3:
        errors.append('model.never: state at least the network, bot-commit and scheduled-run '
                      'guarantees')
    declared_events = set()
    claimed = {}
    blocking = [event for event in model.get('events', []) if event.get('blocking')]
    for event in model.get('events', []):
        event_id = event['id']
        declared_events.add(event_id)
        if event.get('posture') not in POSTURES:
            errors.append(f'events.{event_id}.posture: {event.get("posture")!r} is not a posture')
        if event.get('blocking') and event.get('network'):
            errors.append(f'events.{event_id}: a blocking event may not need the network')
        if event.get('network') and not event.get('rate_limit'):
            errors.append(f'events.{event_id}: a network event must state its rate limit')
        for item in event.get('runs', []):
            ok, reason = resolve_command(item)
            if not ok:
                errors.append(f'events.{event_id}.runs: {reason}')
        for item in event.get('wiring', []):
            if item.startswith('Makefile:'):
                if item.split(':', 1)[1] not in make_targets():
                    errors.append(f'events.{event_id}.wiring: no Makefile target in {item!r}')
            elif not (ROOT / item).exists():
                errors.append(f'events.{event_id}.wiring: no such path {item!r}')
        for job in event.get('jobs', []):
            label = f'events.{event_id}.jobs.{job["job"]}'
            path = ROOT / job['workflow']
            if not path.exists():
                errors.append(f'{label}: no such workflow {job["workflow"]!r}')
                continue
            read = workflows_.get(path)
            if read is None:
                errors.append(f'{label}: {job["workflow"]!r} could not be read; unverified, not passed')
                continue
            claimed.setdefault(path, []).append(label)
            actual = read['jobs'].get(job['job'])
            if actual is None:
                errors.append(f'{label}: {job["workflow"]!r} has no job {job["job"]!r}')
            elif actual['name'] != job['name']:
                errors.append(f'{label}: workflow names it {actual["name"]!r}, model says '
                              f'{job["name"]!r}')
            for wanted in job.get('events', []):
                if wanted not in read['events']:
                    errors.append(f'{label}: {job["workflow"]!r} is not triggered by {wanted!r}')
            if 'pull_request' in read['events']:
                actual_filter = read['events']['pull_request']
                for flag in ('paths_filtered', 'tag_filtered', 'branch_filtered'):
                    if bool(job.get(flag)) != bool(actual_filter[flag]):
                        errors.append(f'{label}: {flag} is declared {bool(job.get(flag))} but the '
                                      f'workflow says {bool(actual_filter[flag])}')
            if job.get('required'):
                if event_id != 'pull_request' or not event.get('blocking'):
                    errors.append(f'{label}: a required check must be on the blocking pull-request event')
                for flag in ('paths_filtered', 'tag_filtered', 'branch_filtered'):
                    if job.get(flag):
                        errors.append(f'{label}: required check may not be {flag}; it could stay '
                                      f'pending forever')
            for command in job.get('commands', []):
                ok, reason = resolve_command(command)
                if not ok:
                    errors.append(f'{label}.commands: {reason}')
    for path in workflows_:
        if path not in claimed:
            errors.append(f'{path.relative_to(ROOT)}: no declared job claims this workflow; an '
                          f'undeclared trigger is an unreviewed trigger')
    if len(blocking) != 1:
        errors.append(f'model.events: exactly one blocking event is expected, found {len(blocking)}')
    required = [job for event in model.get('events', []) for job in event.get('jobs', [])
                if job.get('required')]
    if len(required) != 1:
        errors.append(f'model.events: exactly one required check is expected, found {len(required)}')
    gate = next((event for event in blocking), None)
    if gate and required and gate.get('required_check') != required[0]['name']:
        errors.append('events.pull_request.required_check: must equal the required job name '
                      f'{required[0]["name"]!r}')
    if not HOOK.exists():
        errors.append('local event: scripts/hooks/pre-push is missing')
    elif not os.access(HOOK, os.X_OK):
        errors.append('local event: scripts/hooks/pre-push is not executable, so the hook is a no-op')
    return errors


def phase_rows(model=None):
    """The declared phase's severity per check family — what the gate actually enforces today."""
    context = context_module()
    declared = context.normalise(context.load(ROOT / 'autodoc.toml'))
    block = context.enforcement(declared['phase'])
    overrides = declared.get('severity') or {}
    rows = []
    for family, severity in (block.get('checks') or {}).items():
        rows.append({'family': family, 'severity': severity,
                     'source': 'autodoc.toml [severity]' if family in overrides
                     else f'phase default ({block["label"]})'})
    return {'phase': declared['phase'], 'label': block['label'], 'rows': rows}


def rate_limit_text(limit):
    """The limits as prose, from the numbers the link checker's defaults must equal."""
    if not isinstance(limit, dict):
        return str(limit)
    return (f"one request per host every {limit['per_host_seconds']}s, at most "
            f"{limit['max_links']} links per run, {limit['timeout_seconds']}s timeout per request")


def posture_text(event):
    if event.get('blocking'):
        return 'blocks the merge'
    return {'convenience': 'warns locally, bypassable',
            'report': 'reports, never blocks',
            'advisory': 'triage only, never blocks',
            'release': 'produces the release snapshot',
            'gate': 'blocks the merge'}.get(event.get('posture'), event.get('posture'))


def render(model=None, rows=None, title=True):
    """The reference as a Markdown body. `title=False` is for the engine, which writes its own
    frontmatter and heading so the file stays a governed controlled document."""
    model = model or load()
    rows = rows if rows is not None else phase_rows()
    lines = (['# Trigger reference', ''] if title else []) + [
             'When AutoDOC runs, what each event is allowed to do, and what it never does. '
             'Generated from `CONTROL/metadata/TRIGGERS.json` and checked against the workflows in '
             '`.github/workflows/` by `triggers.py --check`: every workflow must be claimed by a '
             'declared job, every declared command must resolve, and a required check may not be '
             'filtered.', '']
    for sentence in model['principle']:
        lines.append(f'- {sentence}')
    lines.extend(['', '## Events', '',
                  '| Event | When | Posture | Network | What runs | On failure |',
                  '| --- | --- | --- | --- | --- | --- |'])
    for event in model['events']:
        network = 'yes — ' + rate_limit_text(event['rate_limit']) if event.get('network') else 'no'
        runs = '<br>'.join(f'`{item}`' for item in event['runs']) or '—'
        lines.append(f"| {event['label']} | {event['when']} | {posture_text(event)} | {network} | "
                     f"{runs} | {event['failure']} |")
    lines.extend(['', '## Job wiring', '',
                  '| Job | Workflow | Triggered by | Required | Filtered | Commands |',
                  '| --- | --- | --- | --- | --- | --- |'])
    for event in model['events']:
        for job in event.get('jobs', []):
            filters = [name.replace('_filtered', '') for name in
                       ('paths_filtered', 'tag_filtered', 'branch_filtered') if job.get(name)]
            lines.append(f"| `{job['name']}` | `{job['workflow']}` | "
                         f"{', '.join('`' + item + '`' for item in job['events'])} | "
                         f"{'yes' if job.get('required') else 'no'} | "
                         f"{', '.join(filters) if filters else '—'} | "
                         f"{'<br>'.join('`' + item + '`' for item in job['commands'])} |")
    lines.extend(['', f"## What the gate enforces at the declared phase (`{rows['label']}`)", '',
                  'The pull-request gate runs the same checks as `make ci`, at the severity the '
                  'declared phase sets. `off` means the check does not run at this phase; `report` '
                  'means it is printed and never fails; `warn` fails nothing; `error` fails the '
                  'gate.', '', '| Check family | Severity | Source |', '| --- | --- | --- |'])
    for row in rows['rows']:
        lines.append(f"| `{row['family']}` | {row['severity']} | {row['source']} |")
    lines.extend(['', '## Never', ''])
    for sentence in model['never']:
        lines.append(f'- {sentence}')
    lines.extend(['', 'The workflow reader is line-based and stdlib-only: it reads workflow names, '
                      'trigger keys, per-trigger filters and job names. A job produced by a reusable '
                      'workflow, or a workflow this reader cannot parse, is reported as unverified '
                      'and fails `--check` — never passed.', ''])
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='Verify the declaration against the workflows, hook and Makefile')
    parser.add_argument('--json', action='store_true', help='Print machine-readable output')
    parser.add_argument('--model', type=Path, default=None,
                        help='Check a different trigger model file (default CONTROL/metadata/TRIGGERS.json)')
    args = parser.parse_args(argv)
    model = load(args.model)
    if args.check:
        errors = check(model)
        if args.json:
            print(json.dumps({'version': 1, 'valid': not errors, 'errors': errors}, indent=2))
        else:
            for error in errors:
                print(f'triggers: {error}')
            if not errors:
                print(f'Triggers valid: {len(model["events"])} events, '
                      f'{sum(len(event.get("jobs", [])) for event in model["events"])} jobs, '
                      f'one required check, one blocking event.')
        return 2 if errors else 0
    if args.json:
        print(json.dumps({'version': 1, 'model': model, 'phase': phase_rows()}, indent=2))
        return 0
    print(render(model), end='')
    return 0


def cli(argv=None):
    """The exit-code contract: 2 for a configuration problem, 3 for a tool failure, never 1."""
    try:
        return main(argv)
    except (KeyboardInterrupt, SystemExit):
        raise
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        # A usage or configuration problem: never a statement about the documentation.
        print('Trigger error:', error, file=sys.stderr)
        return 2
    except Exception as error:  # noqa: BLE001 - keep a crash off exit 1
        print(f'Internal error: {type(error).__name__}: {error}', file=sys.stderr)
        print('This is a tool failure, not a finding about this repository.', file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(cli())

