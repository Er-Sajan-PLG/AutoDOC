#!/usr/bin/env python3
"""Load, normalise and validate the declared context in autodoc.toml.

Human-edited configuration is TOML (tomllib reads it; Python cannot write it). Shorthands are
normalised before validation, so the schema needs no union types: a bare reason string becomes
{"reason": ...} and a bare fact boolean becomes {"value": ..., "reason": ...}. Declaring a fact
override without a reason is an error, because an override without a reason is an unexplained
claim. A missing file is an empty context, and an empty context means advisory-only output.
"""
import json
import re
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / 'CONTROL/metadata/CONTEXT-MODEL.json'
SEVERITIES = ('off', 'report', 'warn', 'error')
CHECK_FAMILIES = ('drift', 'stubs', 'placeholders', 'links.local', 'secrets.inline',
                  'tribal', 'freshness.critical', 'freshness.review')
SCHEMA = ROOT / 'CONTROL/metadata/CONTEXT-SCHEMA.json'
PROFILES = ROOT / 'CONTROL/metadata/PROFILES.json'
CATALOG_CHECK = ROOT / 'scripts/doc-control/check_catalog.py'
PROFILER = ROOT / 'scripts/intelligence/profile.py'
DEFAULTS = {'version': 1, 'phase': None, 'phase_declared': None, 'profile': None, 'audience': [],
            'kinds': [], 'obligations': [], 'facts': {}, 'not_applicable': {}, 'satisfied_by': {},
            'instantiated': {}, 'severity': {}, 'resolved_aliases': {}, 'alias_problems': []}
CODE_LANGUAGES = ('python', 'javascript', 'typescript', 'go', 'rust', 'java', 'csharp', 'c',
                  'cpp', 'ruby', 'shell', 'sql', 'terraform')


def load_module(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_model():
    model = json.loads(MODEL.read_text(encoding='utf-8'))
    if model.get('version') != 1:
        raise ValueError('Unsupported context model version')
    return model


def load(path):
    """Read a raw context file; a missing file is an empty context."""
    path = Path(path)
    if not path.is_file():
        return {}
    return tomllib.loads(path.read_text(encoding='utf-8'))


def normalise(raw):
    """Apply the documented shorthands and fill defaults.

    The documented config spelling is `schema = 1` (the guide's versioned schema) while the
    internal name stays `version`; stating both is only allowed when they agree.
    """
    data = {key: (dict(value) if isinstance(value, dict) else list(value) if isinstance(value, list)
                  else value) for key, value in raw.items()}
    if 'schema' in data:
        stated = data.pop('schema')
        if 'version' in data and data['version'] != stated:
            raise ValueError(f'context: schema = {stated} contradicts version = {data["version"]}')
        data['version'] = stated
    if 'declared_on' in data:
        raise ValueError('context: declared_on was renamed to phase_declared')
    context = {**DEFAULTS, **data}
    facts = {}
    for name, entry in context['facts'].items():
        if isinstance(entry, bool):
            raise ValueError(f'[facts] {name}: a declared fact needs a reason; '
                             f'write {name} = {{ value = "{str(entry).lower()}", reason = "..." }}')
        value = entry.get('value')
        if isinstance(value, bool):
            entry = {**entry, 'value': str(value).lower()}
        reason = (entry.get('reason') or '').strip()
        if not reason:
            raise ValueError(f'[facts] {name}: reason must be non-empty')
        facts[name] = {'value': entry.get('value'), 'reason': reason}
    context['facts'] = facts
    declared = context.get('phase_declared')
    context['phase_declared'] = declared.strip() if isinstance(declared, str) and declared.strip() else None
    not_applicable = {}
    for doc_id, entry in context['not_applicable'].items():
        if isinstance(entry, str):
            entry = {'reason': entry}
        if not isinstance(entry, dict):
            raise ValueError(f'[not_applicable] {doc_id}: use a reason string or a table')
        reason = entry.get('reason')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f'[not_applicable] {doc_id}: reason must be non-empty')
        record = {'reason': reason.strip()}
        # An advisory decision is a promise to re-check; say who owns it or when. A decision with
        # neither is reported (never failed) so an unowned skip cannot linger unnoticed.
        for key in ('owner', 'review'):
            if entry.get(key) is not None:
                record[key] = str(entry[key]).strip()
        not_applicable[doc_id] = record
    context['not_applicable'] = not_applicable
    context['severity'] = {key: str(value).lower() for key, value in context['severity'].items()}
    context['profile'] = str(context['profile']).strip() if context.get('profile') else None
    resolve_aliases(context)
    return context


def load_profiles():
    """The profile data: which catalog types count as core for a kind of project."""
    return json.loads(PROFILES.read_text(encoding='utf-8'))


def profile_ids():
    """The declared profile ids, in file order (default first)."""
    return [profile['id'] for profile in load_profiles()['profiles']]


def catalog_ids():
    """Return {catalog id: name} and {slug: [ids]} for the generated catalogs."""
    ids, slugs = {}, {}
    for catalog_name in ('CATALOG-A', 'CATALOG-B'):
        path = ROOT / catalog_name / 'INDEX.yaml'
        if not path.is_file():
            continue
        for domain in json.loads(path.read_text(encoding='utf-8'))['domains']:
            for document in domain['documents']:
                ids[document['id']] = document['name']
                slug = re.sub(r'[^a-z0-9]+', '-', document['name'].lower()).strip('-')
                slugs.setdefault(slug, []).append(document['id'])
    return ids, slugs


def resolve_aliases(context):
    """Accept a catalog id or an unambiguous name slug in the three decision tables.

    The guide writes `code-of-conduct = "..."`; this repository's catalog uses stable ids. Both
    are accepted, and ambiguity is an error rather than a silent pick. Every substitution is
    recorded so the audit can show the id that was actually used.
    """
    ids, slugs = catalog_ids()
    resolved, problems = {}, []
    for section in ('not_applicable', 'satisfied_by', 'instantiated'):
        for key in list(context[section]):
            if key in ids:
                continue
            matches = slugs.get(re.sub(r'[^a-z0-9]+', '-', key.lower()).strip('-'), [])
            if len(matches) == 1:
                value = context[section].pop(key)
                context[section][matches[0]] = value
                resolved.setdefault(section, {})[key] = matches[0]
            elif len(matches) > 1:
                problems.append(f'context.{section}: {key!r} matches {len(matches)} types '
                                f'({", ".join(matches)}); use the type id')
    context['resolved_aliases'] = resolved
    context['alias_problems'] = problems
    return context


def validate(context, model=None):
    """Return a list of errors for a normalised context."""
    model = model or load_model()
    checker = load_module('catalog_check', CATALOG_CHECK)
    profiler = load_module('autodoc_profiler', PROFILER)
    errors = checker.validate(context, json.loads(SCHEMA.read_text(encoding='utf-8')), 'context')
    phases = {phase['id'] for phase in model['phases']}
    if context['phase'] is not None and context['phase'] not in phases:
        errors.append(f'context.phase: {context["phase"]!r} is not a declared phase')
    kinds = {kind['id'] for kind in model['kinds']}
    for kind in context['kinds']:
        if kind not in kinds:
            errors.append(f'context.kinds: unknown kind {kind!r}')
    audiences = {audience['id'] for audience in model['audiences']}
    for audience in context['audience']:
        if audience not in audiences:
            errors.append(f'context.audience: unknown audience {audience!r}')
    # Only honoured rules accept an override: a severity for a rule nothing applies is inert data.
    honored = {rule['id'] for rule in model['severity_rules'] if rule.get('honored')}
    known = {rule['id'] for rule in model['severity_rules']}
    for rule_id, severity in context['severity'].items():
        if rule_id not in honored:
            reason = ('is not honoured by any check' if rule_id in known
                      else 'is not a known rule')
            errors.append(f'context.severity: unknown rule {rule_id!r} ({reason}); '
                          'a severity for a rule nothing honours is inert data')
        if severity not in SEVERITIES:
            errors.append(f'context.severity.{rule_id}: {severity!r} is not a severity')
    for name in context['facts']:
        if name not in profiler.DETECTORS:
            errors.append(f'context.facts: {name!r} is not a detectable fact')
    errors += context.get('alias_problems', [])
    if context.get('profile') and context['profile'] not in profile_ids():
        errors.append(f'context.profile: {context["profile"]!r} is not a declared profile; '
                      f'choose one of {", ".join(profile_ids())}')
    for doc_id, entry in context['not_applicable'].items():
        # A decision without an owner or a review date is valid, but it is advice nobody owns, so
        # the report surfaces it (informational, never failing) rather than rejecting the config.
        review = entry.get('review')
        if review:
            try:
                date.fromisoformat(review)
            except ValueError:
                errors.append(f'context.not_applicable.{doc_id}: review {review!r} is not an ISO date')
    if context['phase_declared']:
        try:
            declared = date.fromisoformat(context['phase_declared'])
            if declared > date.today():
                errors.append(f'context.phase_declared: {context["phase_declared"]!r} is in the '
                              'future; a declaration cannot be dated ahead of today')
        except ValueError:
            errors.append(f'context.phase_declared: {context["phase_declared"]!r} is not an ISO date')
        if not context['phase']:
            errors.append('context.phase_declared: a phase age needs a declared phase')
    return errors


def validate_model(model=None):
    """Check the context model itself: phases, enforcement blocks, checks and vocabularies.

    The model is data, so it can drift like any other data. An unknown check family, a severity
    outside the vocabulary, or a phase pointing at a missing enforcement block is an error.
    """
    model = model or load_model()
    errors = []
    phases = {item['id']: item for item in model['phases']}
    if len(phases) != len(model['phases']):
        errors.append('model.phases: duplicate phase id')
    blocks = model['enforcement']
    for name, block in blocks.items():
        missing = [key for key in ('core', 'extended', 'fail', 'description') if key not in block]
        if missing:
            errors.append(f'model.enforcement.{name}: missing {", ".join(missing)}')
            continue
        for severity in (block['core'], block['extended']):
            if severity not in SEVERITIES:
                errors.append(f'model.enforcement.{name}: {severity!r} is not a severity')
        checks = block.get('checks')
        if not isinstance(checks, dict) or not checks:
            errors.append(f'model.enforcement.{name}: needs a checks map for the check families')
            continue
        for family, severity in checks.items():
            if family not in CHECK_FAMILIES:
                errors.append(f'model.enforcement.{name}.checks: unknown family {family!r}')
            if severity not in SEVERITIES:
                errors.append(f'model.enforcement.{name}.checks.{family}: '
                              f'{severity!r} is not a severity')
        for family in CHECK_FAMILIES:
            if family not in checks:
                errors.append(f'model.enforcement.{name}.checks: {family} is not stated')
    for phase_id, entry in phases.items():
        if entry['enforcement'] not in blocks:
            errors.append(f'model.phases.{phase_id}: unknown enforcement block '
                          f'{entry["enforcement"]!r}')
    rules = [rule['id'] for rule in model['severity_rules']]
    if len(set(rules)) != len(rules):
        errors.append('model.severity_rules: duplicate rule id')
    for phase_id, entry in phases.items():
        for family in blocks.get(entry['enforcement'], {}).get('checks', {}):
            if family not in rules:
                errors.append(f'model.severity_rules: {family!r} is enforceable but not listed')
    for rule in model['severity_rules']:
        if not isinstance(rule.get('honored'), bool):
            errors.append(f'model.severity_rules.{rule["id"]}: needs honored true or false')
        missing = [key for key in ('purpose', 'exactness', 'limits') if not rule.get(key)]
        if missing:
            errors.append(f'model.severity_rules.{rule["id"]}: needs {", ".join(missing)}; a '
                          'check without stated limits is a claim it cannot support')
        elif rule['exactness'] not in ('exact', 'heuristic'):
            errors.append(f'model.severity_rules.{rule["id"]}: exactness must be exact or heuristic')
    for name in CHECK_FAMILIES:
        if name not in rules:
            errors.append(f'model.severity_rules: {name!r} is not listed')
    for name, values in (('kinds', model['kinds']), ('audiences', model['audiences']),
                         ('obligations', model['obligations'])):
        ids = [item['id'] for item in values]
        if len(set(ids)) != len(ids):
            errors.append(f'model.{name}: duplicate id')
    for doc_id in model['sunset_ids']:
        if not re.fullmatch(r'[A-Z]+-[A-Z]\d{2}-\d{3}', doc_id):
            errors.append(f'model.sunset_ids: {doc_id!r} is not a catalog id')
    return errors


def enforcement(phase, model=None):
    """Return the enforcement block for a phase; an undeclared phase is advisory-only."""
    model = model or load_model()
    by_id = {item['id']: item for item in model['phases']}
    if phase is None:
        return {**model['enforcement']['advisory'], 'phase': None, 'declared': False,
                'label': 'undeclared (advisory)'}
    entry = by_id[phase]
    return {**model['enforcement'][entry['enforcement']], 'phase': phase, 'declared': True,
            'label': f'{phase} ({entry["enforcement"]})'}


def check_severity(context, family, model=None):
    """Return (severity, source) for a check family under the declared phase.

    Precedence: an explicit [severity] override in autodoc.toml, then the phase default from the
    model's enforcement block, then `report`. An undeclared phase is advisory, so the phase
    default there is `report` and nothing fails.
    """
    model = model or load_model()
    override = context['severity'].get(family)
    if override:
        return override, 'autodoc.toml [severity]'
    block = enforcement(context['phase'], model)
    default = block.get('checks', {}).get(family)
    if default:
        return default, f'phase default ({block["label"]})'
    return 'report', 'default'


def phase_age(context, today=None):
    """Return how long the declared phase has stood, or None when it was never dated."""
    if not context.get('phase_declared'):
        return None
    today = today or date.today()
    days = (today - date.fromisoformat(context['phase_declared'])).days
    return {'phase_declared': context['phase_declared'], 'days': days,
            'review': days > 365,
            'note': 'a phase is a declaration: review it at the next tag or milestone'}


def _git(root, *args):
    try:
        return subprocess.check_output(['git', '-C', str(root), *args], text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, OSError):
        return ''


def kind_hints(profile_document):
    """Suggest project kinds from file evidence. A hint never sets requirements.

    The guide's rule for kinds is the rule for phases: they are declared by the owner, asked once
    and recorded. Evidence is worth showing — "the shape of this repository looks like a library
    and a service" is useful — but it must never be the thing that decides whether a document is
    required, or a repository would be graded against a guess.
    """
    evidence = (profile_document or {}).get('kinds') or {}
    suggested = sorted(kind for kind, entry in evidence.items() if entry['value'] == 'true')
    return {'suggested': suggested,
            'evidence': {kind: entry['evidence'] for kind, entry in evidence.items()
                         if entry['value'] == 'true'},
            'considered': sorted(evidence),
            'note': 'A hint only. Kinds are declared in autodoc.toml and are never inferred into '
                    'requirements; with no declaration, kind-gated documents are undetermined.'
                    + ('' if suggested else
                       ' No detector matched, so this repository gets the generic baseline: only '
                       'requirements that do not depend on a kind apply.')}


def phase_hints(root, profile_document=None, today=None):
    """Suggest a phase from observable history. A hint never sets enforcement."""
    model = load_model()
    root = Path(root)
    today = today or date.today()
    first = _git(root, 'log', '--reverse', '--format=%ad', '--date=short').splitlines()
    years = None
    if first:
        try:
            years = round((today - date.fromisoformat(first[0])).days / 365.25, 1)
        except ValueError:
            years = None
    major_tags = []
    for tag in _git(root, 'tag', '--list').splitlines():
        match = re.fullmatch(r'v?(\d+)\.\d+\.\d+', tag.strip())
        if match and int(match.group(1)) >= 1:
            major_tags.append(tag.strip())
    has_source = bool(profile_document and any(language in CODE_LANGUAGES
                                               for language in profile_document['languages']))
    readme = any((root / name).is_file() for name in
                 ('README.md', 'README.rst', 'README.txt', 'Readme.md', 'readme.md'))
    results = {'history_years>=3': years is not None and years >= 3,
               'tag>=1.0.0': bool(major_tags),
               'has_source_and_readme': has_source and readme,
               'has_source': has_source,
               'always': True}
    for rule in model['phase_hints']:
        if results.get(rule['test']):
            evidence = {'history_years': years, 'major_tags': major_tags, 'has_source': has_source,
                        'readme': readme}
            return {'suggested': rule['id'], 'reason': rule['reason'], 'evidence': evidence,
                    'note': 'Suggestion only, derived from observable history. It never sets '
                            'enforcement; declare `phase` in autodoc.toml to confirm.'}
    return {'suggested': 'idea', 'reason': 'no history was readable', 'evidence': {},
            'note': 'Suggestion only; declare `phase` in autodoc.toml to confirm.'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'autodoc.toml')
    parser.add_argument('--hint', action='store_true', help='Also print a phase suggestion')
    args = parser.parse_args()
    try:
        context = normalise(load(args.config))
        problems = validate_model() + validate(context)
    except (ValueError, KeyError, OSError, tomllib.TOMLDecodeError) as error:
        print('Context error:', error, file=sys.stderr)
        raise SystemExit(2)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(f'Context invalid: {len(problems)} problem(s)', file=sys.stderr)
        raise SystemExit(2)
    summary = {key: value for key, value in context.items() if value not in ({}, [], None)}
    print(json.dumps(summary, indent=2, default=str))
    if args.hint:
        profiler = load_module('autodoc_profiler', PROFILER)
        print(json.dumps(phase_hints(ROOT, profiler.profile(ROOT)), indent=2))
