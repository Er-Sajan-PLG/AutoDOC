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
* every detectable fact has at least one consumer in the catalog, so no fact is inert.
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
PROFILER = ROOT / 'scripts/intelligence/profile.py'
CATALOGS = ('CATALOG-A', 'CATALOG-B')
SENTINELS = ('always', 'assess')
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


def detector_specs():
    spec = importlib.util.spec_from_file_location('autodoc_profiler', PROFILER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DETECTORS


def detectors():
    """The closed fact vocabulary: fact name -> detector spec."""
    return detector_specs()


def tokens_of(document):
    """Every predicate token of one catalog entry, across both predicate forms."""
    applied = document['applies_when']
    if isinstance(applied, dict):
        return list(applied.get('all', [])) + list(applied.get('any', []))
    return list(applied)


def index_documents(index):
    return [(domain['domain'], doc) for domain in index['domains'] for doc in domain['documents']]


def check(indices=None):
    """Return (errors, warnings) for the schema, the rules and their cross-references."""
    errors, warnings = [], []
    schema, rules, model = load(SCHEMA), load(RULES), load(MODEL)
    indices = indices or {catalog: load(ROOT / catalog / 'INDEX.yaml') for catalog in CATALOGS}
    phases = {phase['id'] for phase in model['phases']}
    kinds = {kind['id'] for kind in model['kinds']}
    facts = detector_specs()

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
            if len(str(doc.get('tier'))) and doc['tier'] == 'core':
                if not doc.get('tier_reason'):
                    errors.append(f'{doc["id"]}: core type needs a tier_reason for review')
                if not doc.get('phase_min'):
                    errors.append(f'{doc["id"]}: core type needs phase_min (the phase that requires it)')
                elif doc['phase_min'] not in phases:
                    errors.append(f'{doc["id"]}: phase_min {doc["phase_min"]!r} is not a declared phase')
                if applied == ['assess']:
                    errors.append(f'{doc["id"]}: core type cannot be assess-only (no detectable predicate)')
            elif doc.get('phase_min'):
                errors.append(f'{doc["id"]}: phase_min is only for core types; extended and contextual '
                              'types are never required')
            if doc.get('tier_reason') and doc['tier'] != 'core':
                errors.append(f'{doc["id"]}: tier_reason is only for core types')

    # Admission rules for the fact vocabulary: a fact needs a detector, stated limits, and a consumer.
    for name, spec in sorted(facts.items()):
        if spec.get('exactness') not in ('exact', 'heuristic'):
            errors.append(f'{name}: detector needs exactness of exact or heuristic')
        if not spec.get('limits'):
            errors.append(f'{name}: detector needs a limits statement (what it cannot see)')
        if not spec.get('sources'):
            errors.append(f'{name}: detector needs at least one source')
        if name not in consumers:
            errors.append(f'{name}: no catalog entry consumes this fact; wire a consumer or delete it')
    for token, users in sorted(consumers.items()):
        if token in SENTINELS:
            for doc_id in users:
                if len(tokens_of(documents[doc_id])) != 1:
                    errors.append(f'{doc_id}: sentinel {token} cannot be combined with other flags')
            continue
        if token.startswith('kind:'):
            if token.split(':', 1)[1] not in kinds:
                errors.append(f'{token}: kind is not declared in the context model')
        elif token.startswith('obligation:'):
            if not re.fullmatch(r'[a-z][a-z0-9-]*', token.split(':', 1)[1]):
                errors.append(f'{token}: obligation must be a lowercase hyphenated token')
        elif token not in facts:
            errors.append(f'{token}: undeclared predicate token (used by {", ".join(users)}); '
                          'a predicate must be a detectable fact, a sentinel, kind:<id> or obligation:<id>')

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
        if document.get('phase_min') != entry.get('phase_min'):
            errors.append(f'rules tier.core {entry["id"]}: phase_min disagrees with index')
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
        print(f'Catalog valid: {len(load(RULES)["tier"]["core"])} core types, '
              f'{len(detector_specs())} facts each with a consumer, schema and rules agree')
    raise SystemExit(0 if not errors else 1)
