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
            self.assertIn(entry['phase_min'], ('idea', 'prototype', 'build', 'beta', 'live', 'mature'))
            document = documents[entry['id']]
            self.assertEqual(document['tier'], 'core')
            self.assertEqual(document['applies_when'], entry['applies_when'])
            self.assertEqual(document['tier_reason'], entry['why'])
            self.assertEqual(document['phase_min'], entry['phase_min'])

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

    def test_core_type_without_a_phase_is_rejected(self):
        indices = repository_indices()
        for domain in indices['CATALOG-B']['domains']:
            for document in domain['documents']:
                if document['id'] == 'DEV-B01-006':
                    document['phase_min'] = None
        errors, _ = checker.check(indices)
        self.assertTrue(any('needs phase_min' in error for error in errors), errors)

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
        }
        for label, (expected, mutate) in mutations.items():
            with self.subTest(label):
                bad = copy.deepcopy(index)
                mutate(bad['domains'][0]['documents'][0])
                errors = checker.validate(bad, schema)
                self.assertTrue(any(expected in error for error in errors), errors)

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
