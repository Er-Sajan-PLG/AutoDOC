"""Focused extractor, generated metadata, governance and evidence negative-path tests."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
from extractors.facts import (headings, python_symbols, python_tests, python_dependencies,
                              sqlite_tables, demo_routes, config_properties)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


engine = module('sync_engine_p2', 'scripts/doc-sync/engine.py')
guards = module('guards_p2', 'scripts/doc-control/guards.py')
evidence = module('evidence_p2', 'scripts/doc-control/evidence_pack.py')


class Phase2Tests(unittest.TestCase):


    def test_catalog_views_partition_stable_ids_without_inventing_adoption(self):
        facet_ids = [doc['id'] for groups in engine.catalog_facets().values()
                     for domain in groups for doc in domain['documents']]
        # Counted from the indices, not hardcoded: the catalog grows, and the invariant that
        # matters is that every id appears exactly once across the views.
        declared = [doc['id'] for catalog in ('CATALOG-A', 'CATALOG-B')
                    for domain in json.loads((ROOT / catalog / 'INDEX.yaml').read_text())['domains']
                    for doc in domain['documents']]
        self.assertEqual(len(facet_ids), len(declared))
        self.assertEqual(set(facet_ids), set(declared))
        self.assertEqual(len(set(facet_ids)), len(facet_ids))
        for view in ('A', 'B', 'C'):
            document = ROOT / f'docs/01-catalogs/UNIVERSAL-DOCUMENT-CATALOG-{view}.md'
            self.assertTrue(document.read_text().startswith('<!-- AUTO-GENERATED'))
        for domain in engine.catalog_facets()['A']:
            for doc in domain['documents']:
                self.assertIn('when', doc)
                self.assertIn('applies_when', doc)
                self.assertIn('tier', doc)
                self.assertIn('maturity', doc)

    def test_sql_unknown_ddl_fails_instead_of_partial_dictionary(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'schema.sql'
            path.write_text('CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY);')
            self.assertEqual(sqlite_tables(path), [('t', [('id', 'INTEGER PRIMARY KEY')])])
            path.write_text('CREATE TABLE t (id INTEGER); CREATE INDEX idx ON t(id);')
            with self.assertRaisesRegex(ValueError, 'NOT_IMPLEMENTED: Unsupported SQL statement'):
                sqlite_tables(path)
            path.write_text('CREATE TABLE t (id INTEGER, price DECIMAL(10,2));')
            with self.assertRaisesRegex(ValueError, 'NOT_IMPLEMENTED: Unsupported SQL column'):
                sqlite_tables(path)

    def test_route_registry_rejects_unimplemented_endpoints(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'routes.json'
            current = json.loads((ROOT / 'EXAMPLE-PROJECT/routes.json').read_text())
            self.assertEqual(len(demo_routes(ROOT / 'EXAMPLE-PROJECT/routes.json')), 3)
            current['routes'][0]['path'] = '/not-implemented'
            path.write_text(json.dumps(current))
            with self.assertRaisesRegex(ValueError, 'Unsupported'):
                demo_routes(path)

    def test_config_schema_rejects_mismatched_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'config.json'
            data = json.loads((ROOT / 'EXAMPLE-PROJECT/config.schema.json').read_text())
            self.assertEqual(config_properties(ROOT / 'EXAMPLE-PROJECT/config.schema.json')['PORT']['default'], 8000)
            data['properties']['PORT']['default'] = 'not an integer'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                config_properties(path)

    def test_markdown_headings_ignore_fenced_code(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'doc.md'
            path.write_text('# Title\n```py\n# not a title\n```\n## Details\n')
            self.assertEqual(headings(path), [(1, 1, 'Title'), (5, 2, 'Details')])
            path.write_text('```\n# bad\n')
            with self.assertRaisesRegex(ValueError, 'Unclosed'):
                headings(path)

    def test_python_ast_symbols_and_tests(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'source.py'
            path.write_text('class Worker:\n    def run(self, value: int) -> str:\n        return str(value)\n'
                            'def test_public():\n    pass\n')
            symbols = python_symbols(path)
            self.assertEqual([item[2] for item in symbols], ['Worker', 'Worker.run', 'test_public'])
            self.assertIn('(self, value: int) -> str', symbols[1][3])
            self.assertEqual(python_tests(path), [(4, 'test_public')])
            path.write_text('def broken(:\n')
            with self.assertRaises(SyntaxError):
                python_symbols(path)

    def test_pep621_dependencies_are_declared_not_resolved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'pyproject.toml'
            path.write_text('[project]\nname="example"\nversion="1.2.3"\ndependencies=["z>=1", "a"]\n')
            self.assertEqual(python_dependencies(path), ('example', '1.2.3',
                                                           [('runtime', 'a'), ('runtime', 'z>=1')]))
            path.write_text('[project]\nname="example"\n')
            with self.assertRaisesRegex(ValueError, 'name/version'):
                python_dependencies(path)

    def test_generated_docs_have_marker_and_cannot_be_manual(self):
        path = ROOT / 'docs/META/CODE-INVENTORY.md'
        self.assertTrue(path.read_text().startswith('<!-- AUTO-GENERATED BY AUTODOC ENGINE.'))
        self.assertEqual(engine.parse_frontmatter(path)['auto_generated'], 'true')
        self.assertTrue(engine.validate())

    def test_only_generator_can_check_without_write(self):
        self.assertTrue(engine.generate(check=True, only='outline'))
        with self.assertRaisesRegex(ValueError, 'Unknown generator ID'):
            engine.generate(check=True, only='does-not-exist')

    def test_human_inventory_has_no_generated_docs(self):
        data = json.loads((ROOT / 'docs/00-governance/INVENTORY.yaml').read_text())
        paths = {entry['path'] for entry in data['documents']}
        self.assertIn('NEXT-ACTION.md', paths)
        self.assertNotIn('docs/META/OUTLINE.md', paths)
        self.assertTrue(engine.generate(check=True, only='human-inventory'))

    def test_relationship_graph_tracks_real_links(self):
        graph = json.loads((ROOT / 'CONTROL/metadata/RELATIONSHIP-GRAPH.yaml').read_text())
        self.assertIn({'from': 'EX-AGENT-001', 'to': 'EXAMPLE-PROJECT-DOCS-ARCHITECTURE-MD',
                       'kind': 'related'}, graph['edges'])
        self.assertTrue(engine.generate(check=True, only='relationships'))

    def test_offline_guards_report_broken_local_links_and_tribal_phrases(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / 'test.md'
            self.assertEqual(guards.check_text(path, '[bad](missing.md)'),
                             [f'{path}: broken local link missing.md'])
            self.assertEqual(len(guards.check_text(path, 'just ask someone')), 1)
            self.assertFalse(guards.check_text(path, '[remote](https://example.org)'))

    def test_tribal_fixtures_cover_every_declared_pattern_and_the_false_positive(self):
        """The rule is heuristic, so its fixtures state which phrases it knows and which not."""
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / 'test.md'
            for phrase in ('ask John about the deploy key', 'Ask Sarah for the number',
                           'just ask in the channel', 'ask in DM'):
                with self.subTest(phrase=phrase):
                    self.assertEqual(len(guards.check_text(path, phrase)), 1)
            for documented in ('open an issue and the maintainer will answer',
                               'see CONTRIBUTING.md for the review process',
                               'the on-call engineer is named in docs/oncall.md'):
                with self.subTest(documented=documented):
                    self.assertEqual(guards.check_text(path, documented), [],
                                     'a documented process is not tribal knowledge')
            self.assertEqual(guards.check_text(Path(folder) / 'notes.txt', 'just ask John'), [],
                             'the rule declares Markdown only')

    def test_update_state_preserves_human_prose(self):
        text = '# Current state\nHuman intent stays here.\n'
        updated = engine.replace_block(text, '- measured: 4')
        self.assertIn('Human intent stays here.', updated)
        self.assertEqual(engine.replace_block(updated, '- measured: 4'), updated)
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            engine.replace_block('<!-- auto:start -->', 'X')

    def test_evidence_pack_rejects_failing_or_altered_tests(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            path = output / 'test.json'
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            sample = {'kind': 'autodoc-test-run', 'commit': commit, 'exit_code': 1,
                      'stdout': 'bad', 'stderr': '',
                      'stdout_sha256': hashlib.sha256(b'bad').hexdigest(),
                      'stderr_sha256': hashlib.sha256(b'').hexdigest()}
            path.write_text(json.dumps(sample))
            with self.assertRaisesRegex(ValueError, 'failing'):
                evidence.make_pack(path, output / 'pack')
            sample['exit_code'] = 0
            sample['stdout_sha256'] = 'tampered'
            path.write_text(json.dumps(sample))
            with self.assertRaisesRegex(ValueError, 'hashes'):
                evidence.make_pack(path, output / 'pack')


if __name__ == '__main__':
    unittest.main()
