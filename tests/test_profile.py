"""Fixture matrix for the profiler: kind x phase x ecosystem, with three-valued facts.

The awkward cases are the point (spec section 11): a repository with no manifest, one whose
ecosystem has no reader, one whose declared dependencies are empty, and one that is docs-only.
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/repos'


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


profiler = load_module('autodoc_profiler', 'scripts/intelligence/profile.py')


class FixtureMatrixTests(unittest.TestCase):
    def profile(self, repo):
        return profiler.profile(FIXTURES / repo)

    def value(self, repo, fact):
        return self.profile(repo)['facts'][fact]['value']

    def test_no_manifest_reports_unknown_not_false(self):
        """A repository with no manifest cannot answer a manifest question."""
        self.assertEqual(self.value('docs-only', 'has_third_party_deps'), 'unknown')
        self.assertEqual(self.value('docs-only', 'has_cli'), 'unknown')

    def test_unread_ecosystem_reports_unknown_for_manifest_facts(self):
        """Go is recognised but has no reader, so its dependency state is unknown, not false."""
        data = self.profile('go-service')
        self.assertEqual(data['ecosystems']['present'], ['go'])
        self.assertEqual(data['ecosystems']['unread'], ['go'])
        self.assertEqual(data['facts']['has_third_party_deps']['value'], 'unknown')
        for fact in ('has_cli', 'has_ci', 'has_docker', 'has_network_listener'):
            self.assertEqual(data['facts'][fact]['value'], 'true', fact)
        self.assertEqual(data['facts']['has_deploy']['value'], 'false')

    def test_read_ecosystem_answers_manifest_facts(self):
        data = self.profile('node-library')
        self.assertEqual(data['ecosystems']['readers'], ['javascript'])
        self.assertEqual(data['facts']['has_cli']['value'], 'true')
        self.assertEqual(data['facts']['has_ui']['value'], 'true')
        self.assertEqual(data['facts']['is_public']['value'], 'true')
        self.assertEqual(data['facts']['has_third_party_deps']['value'], 'true')

    def test_empty_declared_dependencies_are_false(self):
        data = self.profile('python-empty')
        self.assertEqual(data['facts']['has_third_party_deps']['value'], 'false')
        self.assertEqual(data['facts']['has_cli']['value'], 'false')
        self.assertEqual(data['facts']['has_tests']['value'], 'false')

    def test_every_fact_declares_exactness_and_limits(self):
        for name, spec in profiler.DETECTORS.items():
            with self.subTest(name):
                self.assertIn(spec['exactness'], ('exact', 'heuristic'))
                self.assertTrue(spec['limits'].strip())
                self.assertTrue(spec['sources'])

    def test_declared_override_replaces_detection_and_keeps_the_reason(self):
        data = profiler.profile(FIXTURES / 'node-library',
                                {'is_public': {'value': 'false', 'reason': 'internal fork'}})
        entry = data['facts']['is_public']
        self.assertEqual(entry['value'], 'false')
        self.assertEqual(entry['evidence'], ['declared'])
        self.assertEqual(entry['declared_reason'], 'internal fork')

    def test_unknown_declared_fact_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown declared fact'):
            profiler.profile(FIXTURES / 'docs-only',
                             {'runs_kubernetes': {'value': 'true', 'reason': 'x'}})

    def test_profile_is_deterministic_and_path_free(self):
        first, second = profiler.profile(ROOT), profiler.profile(ROOT)
        self.assertEqual(first, second)
        self.assertNotIn(str(ROOT), json.dumps(first))

    def test_this_repository_facts(self):
        data = profiler.profile(ROOT)
        self.assertEqual(data['ecosystems']['readers'], ['python'])
        for fact in ('has_tests', 'has_ci', 'has_public_api_surface', 'has_persistent_state',
                     'has_ai', 'uses_agents', 'has_third_party_deps'):
            self.assertEqual(data['facts'][fact]['value'], 'true', fact)
        # No licence yet, no containers, no deployment and no CLI: the tool reports this on itself.
        for fact in ('is_public', 'has_docker', 'has_deploy', 'has_cli'):
            self.assertEqual(data['facts'][fact]['value'], 'false', fact)

    def test_test_input_directories_are_skipped_and_declared(self):
        """A fixture corpus is an input to the tests, not evidence about the project.

        The fixture repositories themselves are profiled normally: the skip applies to paths
        *inside* the profiled root, so a fixture repo answers for its own files.
        """
        data = self.profile('node-library')
        self.assertEqual(data['facts']['has_cli']['value'], 'true')
        mine = profiler.profile(ROOT)
        self.assertEqual(mine['ecosystems']['readers'], ['python'],
                         'the JavaScript fixtures must not make this a JavaScript project')
        self.assertEqual(mine['facts']['has_ui']['value'], 'false')
        self.assertIn('tests/fixtures', mine['excluded'])

    def test_content_scan_records_the_file_not_the_value(self):
        entry = profiler.profile(FIXTURES / 'go-service')['facts']['has_network_listener']
        self.assertEqual(entry['value'], 'true')
        self.assertTrue(all('=' not in item for item in entry['evidence']))


if __name__ == '__main__':
    unittest.main()
