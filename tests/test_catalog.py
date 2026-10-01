"""Regression tests for the catalog schema, its rules and the generated index."""
import copy
import importlib.util
import json
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load_module('catalog_check', 'scripts/doc-control/check_catalog.py')
builder = load_module('catalog_builder', 'scripts/doc-control/build_catalogs.py')
RULES = json.loads((ROOT / 'CONTROL/metadata/CATALOG-RULES.json').read_text())


def repository_indices():
    return {catalog: json.loads((ROOT / catalog / 'INDEX.yaml').read_text())
            for catalog in ('CATALOG-A', 'CATALOG-B')}


def all_documents():
    return [doc for index in repository_indices().values()
            for domain in index['domains'] for doc in domain['documents']]


class CatalogTests(unittest.TestCase):
    def test_repository_catalog_is_valid(self):
        errors, warnings = checker.check()
        self.assertEqual(errors, [])
        self.assertTrue(all('duplicate document name' in warning for warning in warnings))

    def test_index_matches_rules(self):
        self.assertTrue(builder.run(check=True), 'catalog index drift; run make generate')

    def test_core_list_is_hand_picked_and_justified(self):
        documents = {doc['id']: doc for doc in all_documents()}
        self.assertEqual(len(RULES['tier']['core']), 24)
        for entry in RULES['tier']['core']:
            self.assertNotEqual(entry['applies_when'], ['assess'],
                                'a core type needs a detectable predicate')
            self.assertTrue(entry['why'].strip())
            self.assertNotIn('phase_min', entry,
                             'phase_min is derived from severity_by_phase, never authored')
            document = documents[entry['id']]
            self.assertEqual(document['tier'], 'core')
            self.assertEqual(document['applies_when'], entry['applies_when'])
            self.assertEqual(document['tier_reason'], entry['why'])
            self.assertEqual(document['severity_by_phase'], entry['severity_by_phase'])
            self.assertEqual(document['phase_min'], checker.first_applicable_phase(
                entry['severity_by_phase'], checker.phase_order()), 'phase_min must be derived')

    def test_admission_rule_holds_for_every_type_a_profile_can_list(self):
        """The guide's admission rule: reader question + predicate + phases + check or a label."""
        profiles = checker.load(checker.PROFILES)
        listed = {entry['id'] for entry in RULES['tier']['core']}
        for profile in profiles['profiles']:
            listed |= {change['id'] for change in profile.get('add', [])}
        self.assertEqual(set(RULES['admission']['by_id']), listed,
                         'every listed type is admitted, and nothing else claims to be')
        for doc_id in sorted(listed):
            entry = RULES['admission']['by_id'][doc_id]
            with self.subTest(doc_id):
                self.assertTrue(entry['question'].strip(), 'states the reader question')
                self.assertIn(entry['reader'], ('external-users', 'contributors', 'operators',
                                                'auditors', 'successors'))
                self.assertIn(entry['support'], RULES['admission']['support'])
                if entry['support'] == 'checked':
                    self.assertTrue(entry['checks'], 'a claim of checking names its checks')
                for check in entry['checks']:
                    self.assertIn(check, RULES['admission']['checks'])
                for event in entry['events']:
                    self.assertIn(event, RULES['admission']['events'])

    def test_a_profile_addition_must_be_detectable(self):
        """A type nothing can detect cannot be required of anyone, profile or not."""
        indices = repository_indices()
        for domain in indices['CATALOG-A']['domains'] + indices['CATALOG-B']['domains']:
            for document in domain['documents']:
                if document['id'] == 'DOC-A09-009':
                    document['applies_when'] = ['assess']
        errors, _ = checker.check(indices)
        self.assertTrue(any('assess-only' in error for error in errors), errors)

    def test_profile_delta_must_be_reviewable(self):
        """A profile is data an owner reviews: known ids, reasons, phases, no contradictions."""
        profiles = checker.load(checker.PROFILES)
        documents = {doc['id']: doc for doc in all_documents()}
        rules = checker.load(checker.RULES)
        self.assertEqual(checker.profile_errors(rules, profiles, documents,
                                                {'idea', 'prototype', 'build', 'beta', 'live',
                                                 'mature', 'sunset'},
                                                ['idea', 'prototype', 'build', 'beta', 'live',
                                                 'mature', 'sunset']), [])
        for profile in profiles['profiles']:
            if profile['id'] == 'default':
                continue
            with self.subTest(profile['id']):
                self.assertTrue(profile['why'].strip())
                for change in profile.get('add', []):
                    self.assertTrue(change['why'].strip())
                    self.assertIn('severity_by_phase', change,
                                  'an addition states the phases it is off in')
                for change in profile.get('remove', []):
                    self.assertTrue(change['why'].strip())
                    self.assertIn(change['id'], {entry['id'] for entry in rules['tier']['core']})

    def test_every_fact_has_a_detector_and_a_consumer(self):
        used = {token for document in all_documents() for token in checker.tokens_of(document)}
        for name, spec in checker.detector_specs().items():
            self.assertIn(name, used, 'a fact no catalog entry consumes is inert data')
            self.assertIn(spec['exactness'], ('exact', 'heuristic'))
            self.assertTrue(spec['limits'].strip())

    def test_fact_without_a_consumer_is_rejected(self):
        fake = dict(checker.detector_specs())
        fake['has_kubernetes'] = {'exactness': 'exact', 'limits': 'x', 'sources': [{'patterns': ['k8s/**']}]}
        with unittest.mock.patch.object(checker, 'detector_specs', return_value=fake):
            errors, _ = checker.check()
        self.assertTrue(any('no catalog entry consumes this fact' in error for error in errors), errors)

    def test_a_core_type_that_never_applies_or_contradicts_its_phases_is_rejected(self):
        indices = repository_indices()
        for domain in indices['CATALOG-B']['domains']:
            for document in domain['documents']:
                if document['id'] == 'DEV-B01-006':
                    document['phase_min'] = None  # no longer derived from its own map
        errors, _ = checker.check(indices)
        self.assertTrue(any('phase_min' in error and 'disagrees' in error for error in errors),
                        errors)

        indices = repository_indices()
        for domain in indices['CATALOG-B']['domains']:
            for document in domain['documents']:
                if document['id'] == 'DEV-B01-006':
                    document['severity_by_phase'] = {'idea': 'off', 'build': 'warn',
                                                     'beta': 'off'}
        errors, _ = checker.check(indices)
        self.assertTrue(any('requiredness is monotone' in error for error in errors), errors)

    def test_an_unadmitted_profile_type_is_rejected(self):
        rules = checker.load(checker.RULES)
        rules['admission']['by_id']['DOC-A09-009']['question'] = '   '
        model = checker.load(checker.MODEL)
        indices = repository_indices()
        documents = {doc['id']: doc for _, doc in checker.index_documents(indices['CATALOG-A'])
                     + checker.index_documents(indices['CATALOG-B'])}
        errors = checker.admission_errors(rules, model, documents,
                                          checker.load(checker.PROFILES))
        self.assertTrue(any('reader question' in error for error in errors), errors)

    def test_undeclared_kind_token_is_rejected(self):
        indices = repository_indices()
        indices['CATALOG-A']['domains'][0]['documents'][0]['applies_when'] = ['kind:saas']
        errors, _ = checker.check(indices)
        self.assertTrue(any('kind is not declared' in error for error in errors), errors)

    def test_validator_rejects_invalid_documents(self):
        schema = checker.load(checker.SCHEMA)
        index = repository_indices()['CATALOG-A']
        self.assertEqual(checker.validate(index, schema), [])
        mutations = {
            'tier': ('not in', lambda doc: doc.update(tier='golden')),
            'missing field': ('missing required property', lambda doc: doc.pop('template')),
            'empty applies_when': ('fewer than minItems', lambda doc: doc.update(applies_when=[])),
            'bad id': ('does not match', lambda doc: doc.update(id='A03-001')),
            'retired audience field': ('unknown property',
                                       lambda doc: doc.update(audience='project team')),
            'unknown reader': ('not in', lambda doc: doc.update(reader='management')),
            'unknown support level': ('not in', lambda doc: doc.update(support='verified')),
            'unknown check': ('not in', lambda doc: doc.update(checks=['links.external'])),
            'unknown event': ('does not match', lambda doc: doc.update(events=['New Release'])),
            'authored phase_min': ('expected type', lambda doc: doc.update(phase_min=7)),
        }
        for label, (expected, mutate) in mutations.items():
            with self.subTest(label):
                bad = copy.deepcopy(index)
                mutate(bad['domains'][0]['documents'][0])
                errors = checker.validate(bad, schema)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_every_kind_is_either_detected_with_limits_or_declared_only_with_a_reason(self):
        """§3's honesty rule: a kind is seen by a detector that states its limits, or not seen."""
        model = checker.load(checker.MODEL)
        profiler = checker.profiler_module()
        self.assertEqual(checker.kind_errors(model, profiler), [])
        detectors = profiler.kind_specs()
        detected = {kind['id'] for kind in model['kinds'] if kind['detection'] == 'files'}
        self.assertEqual(detected, set(detectors),
                         'a kind detected from files must have a detector, and vice versa')
        for kind in model['kinds']:
            with self.subTest(kind['id']):
                if kind['detection'] == 'files':
                    spec = detectors[kind['id']]
                    self.assertIn(spec['exactness'], ('exact', 'heuristic'))
                    self.assertTrue(spec['limits'].strip())
                    self.assertTrue(spec['sources'])
                else:
                    self.assertTrue(kind['why_declared_only'].strip())

    def test_a_kind_that_is_neither_detectable_nor_justified_is_rejected(self):
        model = checker.load(checker.MODEL)
        profiler = checker.profiler_module()
        broken = copy.deepcopy(model)
        target = next(kind for kind in broken['kinds'] if kind['detection'] == 'declaration-only')
        del target['why_declared_only']
        self.assertTrue(any('declaration-only needs a reason' in error
                            for error in checker.kind_errors(broken, profiler)))
        broken = copy.deepcopy(model)
        target = next(kind for kind in broken['kinds'] if kind['detection'] == 'files')
        target['detection'] = 'whenever'
        self.assertTrue(any('needs detection of files or declaration-only' in error
                            for error in checker.kind_errors(broken, profiler)))

    def test_a_phase_predicate_with_an_unknown_phase_is_rejected(self):
        indices = repository_indices()
        for domain in indices['CATALOG-A']['domains']:
            for document in domain['documents']:
                if document['id'] == 'DOC-A16-007':
                    document['applies_when'] = ['phase>=shipping']
        errors, _ = checker.check(indices)
        self.assertTrue(any('phase is not declared' in error for error in errors), errors)

    def test_validator_fails_on_unimplemented_schema_keyword(self):
        errors = checker.validate({'anything': 1},
                                  {'type': 'object', 'allOf': [{'type': 'object'}]})
        self.assertTrue(any('keyword not implemented' in error for error in errors), errors)

    def test_validator_supports_one_of_for_two_documented_forms(self):
        schema = {'oneOf': [{'type': 'string'}, {'type': 'object', 'required': ['reason']}]}
        self.assertEqual(checker.validate('a reason', schema), [])
        self.assertEqual(checker.validate({'reason': 'a reason', 'owner': '@o'}, schema), [])
        self.assertTrue(any('exactly one' in error for error in checker.validate(7, schema)))
        self.assertTrue(any('exactly one' in error
                            for error in checker.validate({'nothing': 1}, schema)))

    def test_cross_checks_catch_rules_that_drift(self):
        indices = repository_indices()
        first = indices['CATALOG-A']['domains'][0]['documents'][0]
        first['applies_when'] = ['always', 'has_tests']
        errors, _ = checker.check(indices)
        self.assertTrue(any('cannot be combined' in error for error in errors), errors)

        indices = repository_indices()
        indices['CATALOG-B']['domains'][0]['documents'][0]['id'] = \
            indices['CATALOG-A']['domains'][0]['documents'][0]['id']
        errors, _ = checker.check(indices)
        self.assertTrue(any('duplicate catalog id' in error for error in errors), errors)

        indices = repository_indices()
        third = indices['CATALOG-A']['domains'][1]['documents'][0]
        third['applies_when'] = ['teleports']
        errors, _ = checker.check(indices)
        self.assertTrue(any('undeclared predicate token' in error for error in errors), errors)


if __name__ == '__main__':
    unittest.main()
