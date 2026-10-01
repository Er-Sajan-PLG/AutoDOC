#!/usr/bin/env python3
"""Validate the catalog index against CATALOG-SCHEMA.json and the rules that govern it.

The index is authored data, so it is checked like code. The validator implements an explicit
JSON Schema keyword subset and FAILS on any keyword it does not implement, so the schema can
never contain a constraint that silently does not run. Beyond schema shape, this enforces the
admission rules that keep the catalog honest:

* every catalog id is unique, has a template, and appears at most once in a tier list;
* a core type carries a reason and a phase at which it becomes required, and never an
  `assess`-only predicate (a requirement nobody can detect is not a requirement);
* every predicate token is a detectable fact, a sentinel, a declared kind, or a declared duty;
* every detectable fact has at least one consumer in the catalog, so no fact is inert;
* the admission rule holds for every type any profile can list: it states the reader question it
  answers, who reads it, how it is supported, and named checks or an explicit label;
* a profile is a small delta of the default core set: known ids, a reason per change, no id both
  added and removed, and removals only of default core types.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'CONTROL/metadata/CATALOG-SCHEMA.json'
RULES = ROOT / 'CONTROL/metadata/CATALOG-RULES.json'
MODEL = ROOT / 'CONTROL/metadata/CONTEXT-MODEL.json'
PROFILES = ROOT / 'CONTROL/metadata/PROFILES.json'
PROFILER = ROOT / 'scripts/intelligence/profile.py'
CATALOGS = ('CATALOG-A', 'CATALOG-B')
SENTINELS = ('always', 'assess')
SEVERITIES = ('off', 'report', 'warn', 'error')
SUPPORTED = {'$schema', '$id', 'title', 'description', 'type', 'required', 'properties',
             'additionalProperties', 'items', 'enum', 'pattern', 'minItems', 'uniqueItems',
             'minimum', 'minLength', 'const', 'oneOf'}
SCALARS = {'object': dict, 'array': list, 'string': str,
           'number': (int, float), 'integer': int, 'boolean': bool, 'null': type(None)}


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def implements(value, expected):
    if expected == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == 'boolean':
        return isinstance(value, bool)
    if expected == 'null':
        return value is None
    return isinstance(value, SCALARS[expected])


def validate(instance, schema, path='$', errors=None):
    """Validate `instance` and append human-readable errors. Returns the error list."""
    if errors is None:
        errors = []
    for keyword in schema:
        if keyword not in SUPPORTED:
            errors.append(f'{path}: schema keyword not implemented by this validator: {keyword}')
    if 'oneOf' in schema:
        # Exactly one branch must accept the value: used where a field has two documented forms
        # (a bare reason string, or a table carrying an optional owner and review date).
        matches = [branch for branch in schema['oneOf']
                   if not validate(instance, branch, path, [])]
        if len(matches) != 1:
            errors.append(f'{path}: expected exactly one of {len(schema["oneOf"])} forms, '
                          f'found {len(matches)}')
    if 'const' in schema and instance != schema['const']:
        errors.append(f'{path}: expected {schema["const"]!r}, found {instance!r}')
    if 'enum' in schema and instance not in schema['enum']:
        errors.append(f'{path}: {instance!r} not in {schema["enum"]}')
    expected = schema.get('type')
    if expected is not None:
        wanted = expected if isinstance(expected, list) else [expected]
        unknown = [item for item in wanted if item not in SCALARS]
        if unknown:
            errors.append(f'{path}: unsupported type {unknown}')
        elif not any(implements(instance, item) for item in wanted):
            errors.append(f'{path}: expected type {expected}, found {type(instance).__name__}')
            return errors
    if isinstance(instance, str):
        if 'pattern' in schema and not re.search(schema['pattern'], instance):
            errors.append(f'{path}: {instance!r} does not match {schema["pattern"]}')
        if 'minLength' in schema and len(instance) < schema['minLength']:
            errors.append(f'{path}: shorter than minLength {schema["minLength"]}')
    if isinstance(instance, int) and not isinstance(instance, bool) and 'minimum' in schema:
        if instance < schema['minimum']:
            errors.append(f'{path}: below minimum {schema["minimum"]}')
    if isinstance(instance, list):
        if 'minItems' in schema and len(instance) < schema['minItems']:
            errors.append(f'{path}: fewer than minItems {schema["minItems"]}')
        if schema.get('uniqueItems'):
            seen = [json.dumps(item, sort_keys=True) for item in instance]
            if len(seen) != len(set(seen)):
                errors.append(f'{path}: duplicate items where uniqueItems is set')
        if 'items' in schema:
            for index, item in enumerate(instance):
                validate(item, schema['items'], f'{path}[{index}]', errors)
    if isinstance(instance, dict):
        for key in schema.get('required', []):
            if key not in instance:
                errors.append(f'{path}: missing required property {key}')
        properties = schema.get('properties', {})
        for key, value in instance.items():
            if key in properties:
                validate(value, properties[key], f'{path}.{key}', errors)
            elif isinstance(schema.get('additionalProperties'), dict):
                validate(value, schema['additionalProperties'], f'{path}.{key}', errors)
            elif schema.get('additionalProperties') is False:
                errors.append(f'{path}: unknown property {key}')
    return errors


def profiler_module():
    """The profiler, loaded once: its DETECTORS and KIND_DETECTORS are the detector vocabulary."""
    spec = importlib.util.spec_from_file_location('autodoc_profiler', PROFILER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def detector_specs():
    return profiler_module().DETECTORS


def declared_specs():
    """Facts that are declared, never inferred: no detector exists for these on purpose."""
    return profiler_module().DECLARED_FACTS


def detectors():
    """The closed fact vocabulary, with each fact's detection route."""
    return profiler_module().fact_specs()


def tokens_of(document):
    """Every predicate token of one catalog entry, across both predicate forms."""
    applied = document['applies_when']
    if isinstance(applied, dict):
        return list(applied.get('all', [])) + list(applied.get('any', []))
    return list(applied)


def phase_order(model=None):
    """The declared phase sequence, in order, from the context model."""
    model = model or load(MODEL)
    return [phase['id'] for phase in model['phases']]


def severity_by_phase_errors(document, phases, order):
    """Return errors for one entry's severity_by_phase map: known phases, real severities, monotone."""
    errors = []
    mapping = document.get('severity_by_phase')
    if not isinstance(mapping, dict):
        return [f'{document.get("id")}: severity_by_phase must be an object']
    order = [phase for phase in order if phase in phases]
    for phase_id, severity in mapping.items():
        if phase_id not in phases:
            errors.append(f'{document["id"]}: severity_by_phase names unknown phase {phase_id!r}')
        elif severity not in SEVERITIES:
            errors.append(f'{document["id"]}: severity_by_phase.{phase_id} '
                          f'{severity!r} is not a severity')
    seen_required = None
    for phase_id in order:
        if mapping.get(phase_id) == 'off':
            if seen_required:
                errors.append(f'{document["id"]}: severity_by_phase goes back to off at {phase_id} '
                              f'after being required at {seen_required}; requiredness is monotone')
        elif mapping.get(phase_id) in SEVERITIES:
            seen_required = seen_required or phase_id
    return errors


def first_applicable_phase(mapping, order):
    """The first phase a type is not off at; None when it is off from idea onward."""
    for phase_id in order:
        if (mapping or {}).get(phase_id) != 'off':
            return phase_id
    return None


def kind_errors(model, profiler):
    """Every declared kind says how it can be seen: a detector with limits, or a stated reason.

    A kind that is neither detectable nor explicitly declaration-only would be an inference
    waiting to happen, so the catalog refuses it.
    """
    errors = []
    detectors = profiler.kind_specs()
    declared = {kind['id'] for kind in model['kinds']}
    for kind in model['kinds']:
        spec = detectors.get(kind['id'])
        detection = kind.get('detection')
        if detection == 'files':
            if not spec:
                errors.append(f'kind {kind["id"]}: detection is files but no detector exists')
                continue
            if spec.get('exactness') not in ('exact', 'heuristic'):
                errors.append(f'kind {kind["id"]}: detector needs exactness of exact or heuristic')
            if not spec.get('limits'):
                errors.append(f'kind {kind["id"]}: detector needs a limits statement')
            if not spec.get('sources'):
                errors.append(f'kind {kind["id"]}: detector needs at least one source')
        elif detection == 'declaration-only':
            if not str(kind.get('why_declared_only', '')).strip():
                errors.append(f'kind {kind["id"]}: declaration-only needs a reason no file can '
                              'tell, or it is an inference waiting to happen')
            if spec:
                errors.append(f'kind {kind["id"]}: declaration-only cannot also have a detector')
        else:
            errors.append(f'kind {kind["id"]}: needs detection of files or declaration-only')
    for kind in sorted(set(detectors) - declared):
        errors.append(f'kind {kind}: has a detector but is not declared in the context model')
    return errors


def fact_errors(profiler, facts, consumers):
    """Every fact states how it is answered: file evidence with limits, or a declaration only.

    This is the fact half of the same honesty rule the kinds follow. A detectable fact that
    suddenly loses its detector, or a declaration-only fact that quietly grows one, would turn a
    declared answer into an inferred one, so both are refused. Either way the fact needs a
    consumer: a fact no catalog entry uses is inert data.
    """
    errors = []
    detected = profiler.DETECTORS
    declared = profiler.DECLARED_FACTS
    for name in sorted(set(detected) & set(declared)):
        errors.append(f'{name}: fact is both detectable and declaration-only')
    for name, spec in sorted(facts.items()):
        if spec.get('detection') == 'files':
            if spec.get('exactness') not in ('exact', 'heuristic'):
                errors.append(f'{name}: detector needs exactness of exact or heuristic')
            if not spec.get('limits'):
                errors.append(f'{name}: detector needs a limits statement (what it cannot see)')
            if not spec.get('sources'):
                errors.append(f'{name}: detector needs at least one source')
        elif spec.get('detection') == 'declaration-only':
            if not str(spec.get('why_declared_only', '')).strip():
                errors.append(f'{name}: declaration-only needs a reason no detector can exist, or '
                              'it is an inference waiting to happen')
            if name in detected:
                errors.append(f'{name}: declaration-only cannot also have a detector')
        else:
            errors.append(f'{name}: needs detection of files or declaration-only')
        if name not in consumers:
            errors.append(f'{name}: no catalog entry consumes this fact; wire a consumer or delete it')
    return errors


def admission_errors(rules, model, documents, profiles):
    """The admission rule, enforced for every type any profile can list."""
    errors = []
    spec = rules['admission']
    audiences = {audience['id'] for audience in model['audiences']}
    support = set(spec['support'])
    checks = set(spec['checks'])
    events = set(spec['events'])
    default_core = {entry['id'] for entry in rules['tier']['core']}
    listed = set(default_core)
    for profile in profiles['profiles']:
        for change in profile.get('add', []):
            listed.add(change['id'])
    # A profile-listed type must be admitted; an extended type may be admitted too, and that is
    # not inert: its reader question and checks render into the index and `explain` reads them.
    permitted = listed | set(rules['tier']['extended'])
    admitted = set(spec['by_id'])
    for doc_id in sorted(listed - admitted):
        errors.append(f'admission: {doc_id} is listed by a profile but states no reader question, '
                      'reader, support or checks')
    for profile in profiles['profiles']:
        for change in profile.get('add', []):
            document = documents.get(change['id'])
            if document and tokens_of(document) == ['assess']:
                errors.append(f'profiles.{profile["id"]}: {change["id"]} is assess-only; a type '
                              'nothing can detect cannot be required of anyone')
    for doc_id in sorted(admitted - permitted):
        errors.append(f'admission.by_id: {doc_id} is not listed by any profile, tier.core or '
                      'tier.extended; an admission nobody applies is inert data')
    for doc_id, entry in sorted(spec['by_id'].items()):
        where = f'admission.by_id.{doc_id}'
        if doc_id not in documents:
            errors.append(f'{where}: unknown catalog id')
            continue
        if not str(entry.get('question', '')).strip():
            errors.append(f'{where}: needs the reader question it answers')
        if entry.get('reader') not in audiences:
            errors.append(f'{where}: reader {entry.get("reader")!r} is not a declared audience')
        if entry.get('support') not in support:
            errors.append(f'{where}: support {entry.get("support")!r} is not '
                          f'{sorted(support)}')
        for check in entry.get('checks', []):
            if check not in checks:
                errors.append(f'{where}: unknown check {check!r}')
        if entry.get('support') == 'checked' and not entry.get('checks'):
            errors.append(f'{where}: support=checked needs at least one named check')
        if entry.get('support') in ('template-only', 'human') and entry.get('checks'):
            errors.append(f'{where}: support={entry["support"]} cannot name checks; nothing runs')
        for event in entry.get('events', []):
            if event not in events:
                errors.append(f'{where}: unknown event {event!r}')
    for document in documents.values():
        if document.get('support') not in support:
            errors.append(f'{document["id"]}: support {document.get("support")!r} is not one of '
                          f'{sorted(support)}')
    return errors


def profile_errors(rules, profiles, documents, phases, order):
    """Profiles are deltas of the default core set, and every change states a reason."""
    errors = []
    if profiles.get('version') != 1:
        errors.append('profiles: unsupported version')
    default_core = {entry['id'] for entry in rules['tier']['core']}
    seen = set()
    for profile in profiles['profiles']:
        profile_id = profile.get('id')
        where = f'profiles.{profile_id}'
        if not profile_id:
            errors.append('profiles: an entry has no id')
            continue
        if profile_id in seen:
            errors.append(f'{where}: duplicate profile id')
        seen.add(profile_id)
        if not str(profile.get('why', '')).strip():
            errors.append(f'{where}: needs a reason to exist')
        adds = [change['id'] for change in profile.get('add', [])]
        removes = [change['id'] for change in profile.get('remove', [])]
        if profile_id == 'default' and (adds or removes):
            errors.append(f'{where}: the default profile is tier.core itself and cannot be a delta')
        overlap = set(adds) & set(removes)
        if overlap:
            errors.append(f'{where}: ids both added and removed: {", ".join(sorted(overlap))}')
        for change in profile.get('add', []) + profile.get('remove', []):
            if not str(change.get('why', '')).strip():
                errors.append(f'{where}: {change.get("id")} carries no reason')
        for change in profile.get('add', []):
            if 'severity_by_phase' not in change:
                errors.append(f'{where}: {change.get("id")} must state severity_by_phase; '
                              'core for this kind of project is not the same as required at idea')
            else:
                errors.extend(severity_by_phase_errors(
                    {'id': change['id'], 'severity_by_phase': change['severity_by_phase']},
                    phases, order))
        for doc_id in adds:
            if doc_id not in documents:
                errors.append(f'{where}: unknown catalog id {doc_id}')
            elif doc_id in default_core:
                errors.append(f'{where}: {doc_id} is already default core; nothing to add')
        for doc_id in removes:
            if doc_id not in default_core:
                errors.append(f'{where}: {doc_id} is not default core; nothing to remove')
    if 'default' not in seen:
        errors.append('profiles: no default profile')
    return errors


def index_documents(index):
    return [(domain['domain'], doc) for domain in index['domains'] for doc in domain['documents']]


def check(indices=None):
    """Return (errors, warnings) for the schema, the rules and their cross-references."""
    errors, warnings = [], []
    schema, rules, model, profiles = load(SCHEMA), load(RULES), load(MODEL), load(PROFILES)
    indices = indices or {catalog: load(ROOT / catalog / 'INDEX.yaml') for catalog in CATALOGS}
    order = phase_order(model)
    phases = set(order)
    kinds = {kind['id'] for kind in model['kinds']}
    facts = detectors()
    profiler = profiler_module()

    documents, seen_ids, names, consumers = {}, set(), {}, {}
    for catalog, index in indices.items():
        errors.extend(validate(index, schema, catalog))
        for domain, doc in index_documents(index):
            if doc['id'] in seen_ids:
                errors.append(f'{doc["id"]}: duplicate catalog id')
            seen_ids.add(doc['id'])
            documents[doc['id']] = doc
            names.setdefault(doc['name'], []).append(doc['id'])
            if not (ROOT / doc['template']).is_file():
                errors.append(f'{doc["id"]}: missing template {doc["template"]}')
            applied = tokens_of(doc)
            for token in applied:
                consumers.setdefault(token, []).append(doc['id'])
            if not applied:
                errors.append(f'{doc["id"]}: applies_when must not be empty')
            if doc['tier'] == 'core':
                if not doc.get('tier_reason'):
                    errors.append(f'{doc["id"]}: core type needs a tier_reason for review')
                if applied == ['assess']:
                    errors.append(f'{doc["id"]}: core type cannot be assess-only (no detectable predicate)')
            if doc.get('tier_reason') and doc['tier'] != 'core':
                errors.append(f'{doc["id"]}: tier_reason is only for core types')
            errors.extend(severity_by_phase_errors(doc, phases, order))
            expected_phase = first_applicable_phase(doc['severity_by_phase'], order)
            if doc.get('phase_min') != expected_phase:
                errors.append(f'{doc["id"]}: phase_min {doc.get("phase_min")!r} disagrees with '
                              f'severity_by_phase (derived value is {expected_phase!r}); phase_min '
                              'is generated, never authored')

    # Admission rules for the fact vocabulary: every fact is either detectable (exactness, stated
    # limits, sources) or declaration-only (a stated reason why no detector can exist), and every
    # fact has a consumer, so no fact is inert.
    errors.extend(kind_errors(model, profiler))
    errors.extend(fact_errors(profiler, facts, consumers))
    for token, users in sorted(consumers.items()):
        if token in SENTINELS:
            for doc_id in users:
                if len(tokens_of(documents[doc_id])) != 1:
                    errors.append(f'{doc_id}: sentinel {token} cannot be combined with other flags')
            continue
        if token.startswith('kind:'):
            if token.split(':', 1)[1] not in kinds:
                errors.append(f'{token}: kind is not declared in the context model')
        elif token.startswith('phase>='):
            if token.split('>=', 1)[1] not in phases:
                errors.append(f'{token}: phase is not declared in the context model')
        elif token.startswith('obligation:'):
            if not re.fullmatch(r'[a-z][a-z0-9-]*', token.split(':', 1)[1]):
                errors.append(f'{token}: obligation must be a lowercase hyphenated token')
        elif token not in facts:
            errors.append(f'{token}: undeclared predicate token (used by {", ".join(users)}); '
                          'a predicate must be a detectable fact, a sentinel, kind:<id>, '
                          'phase>=<id> or obligation:<id>')

    for name, ids in sorted(names.items()):
        if len(ids) > 1:
            warnings.append(f'duplicate document name {name!r}: {", ".join(ids)} '
                            '(keep one canonical core type; the others stay contextual)')

    for entry in rules['tier']['core']:
        document = documents.get(entry['id'])
        if document is None:
            errors.append(f'rules tier.core: unknown catalog id {entry["id"]}')
            continue
        if not entry['applies_when']:
            errors.append(f'rules tier.core {entry["id"]}: applies_when must not be empty')
        if document['applies_when'] != entry['applies_when']:
            errors.append(f'rules tier.core {entry["id"]}: applies_when '
                          f'{json.dumps(entry["applies_when"])} disagrees with index '
                          f'{json.dumps(document["applies_when"])}')
        if document.get('severity_by_phase') != entry.get('severity_by_phase', {}):
            errors.append(f'rules tier.core {entry["id"]}: severity_by_phase disagrees with index')
        if 'phase_min' in entry:
            errors.append(f'rules tier.core {entry["id"]}: phase_min is derived, not authored; '
                          'declare severity_by_phase instead')
        if document.get('tier_reason') != entry['why']:
            errors.append(f'rules tier.core {entry["id"]}: why disagrees with the index reason')
    core_ids = {entry['id'] for entry in rules['tier']['core']}
    for doc_id in rules['tier']['extended']:
        if doc_id not in documents:
            errors.append(f'rules tier.extended: unknown catalog id {doc_id}')
        elif documents[doc_id]['tier'] != 'extended':
            errors.append(f'rules tier.extended: {doc_id} is not marked extended in the index')
    overlap = core_ids & set(rules['tier']['extended'])
    if overlap:
        errors.append('rules tier: ids in both core and extended: ' + ', '.join(sorted(overlap)))
    for doc_id in rules['applies_when']['by_id']:
        if doc_id not in documents:
            errors.append(f'rules applies_when.by_id: unknown catalog id {doc_id}')
    domains = {domain for catalog, index in indices.items() for domain, _ in index_documents(index)}
    for domain in rules['applies_when']['by_domain']:
        if domain not in domains:
            errors.append(f'rules applies_when.by_domain: unknown domain {domain}')
    for doc_id in model['sunset_ids']:
        if doc_id not in documents:
            errors.append(f'context model sunset_ids: unknown catalog id {doc_id}')
    errors.extend(admission_errors(rules, model, documents, profiles))
    errors.extend(profile_errors(rules, profiles, documents, phases, order))
    return errors, warnings


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        errors, warnings = check()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'Catalog check error: {error}')
    for warning in warnings:
        print('WARNING:', warning, file=sys.stderr)
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        rules = load(RULES)
        profiles = load(PROFILES)
        added = sum(len(profile.get('add', [])) for profile in profiles['profiles'])
        print(f'Catalog valid: {len(rules["tier"]["core"])} core types, '
              f'{added} profile additions across {len(profiles["profiles"])} profiles, '
              f'{len(rules["admission"]["by_id"])} admitted, '
              f'{len(detector_specs())} detected facts and {len(declared_specs())} declared traits, '
              'each with a consumer, schema and rules agree')
    raise SystemExit(0 if not errors else 1)
