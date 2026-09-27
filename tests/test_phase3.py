"""Phase 3: strict environment/alerts, directed graph, inventory and staged impact."""
import importlib.util
import json
from datetime import date
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
from extractors.env_alerts import environment, alerts
from extractors.local_policy import tool_matrix

spec = importlib.util.spec_from_file_location('phase3_engine', ROOT / 'scripts/doc-sync/engine.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
spec = importlib.util.spec_from_file_location('phase3_owner', ROOT / 'scripts/doc-control/check_ownership.py')
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)


class Phase3Tests(unittest.TestCase):


    def test_generate_refuses_to_overwrite_human_markdown(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'human.md'
            path.write_text('# Human decision\n')
            entry = {'id': 'outline', 'sources': ['README.md'], 'target': str(path), 'generator': 'outline'}
            with patch.object(engine, 'load_map', return_value={'generated': [entry]}):
                with patch.object(engine, 'safe_path', return_value=path):
                    with self.assertRaisesRegex(ValueError, 'Refusing to overwrite'):
                        engine.generate(check=False)
            self.assertEqual(path.read_text(), '# Human decision\n')

    def test_ownership_rejects_orphan_pattern(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            matrix = root / 'CONTROL/metadata/OWNERSHIP-MATRIX.yaml'
            matrix.parent.mkdir(parents=True)
            matrix.write_text(json.dumps({'version': 1, 'owners': {
                '@Er-Sajan-PLG': {'paths': ['does-not-exist/**']}}}))
            doc = root / 'docs/example.md'
            doc.parent.mkdir(parents=True)
            doc.write_text('example')
            with patch.object(owner, 'ROOT', root), patch.object(owner, 'controlled', return_value=[doc]):
                with patch.object(owner, 'parse_frontmatter', return_value={
                    'owner': '@Er-Sajan-PLG', 'reviewer': '@Er-Sajan-PLG', 'criticality': 'high'}):
                    self.assertFalse(owner.check())

    def test_actual_junit_parser_counts_failures_and_skips(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('test_evidence_p3', ROOT / 'scripts/doc-control/test_evidence.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'results.xml'
            path.write_text('<testsuites><testsuite tests="3" failures="1" errors="0" skipped="1"/></testsuites>')
            self.assertEqual(module.junit_counts(path),
                             {'tests': 3, 'failures': 1, 'errors': 0, 'skipped': 1, 'passed': 1})
            path.write_text('<testsuite tests="1" failures="2"/>')
            with self.assertRaisesRegex(ValueError, 'totals'):
                module.junit_counts(path)

    def test_evidence_collects_real_local_check_exit_codes(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('evidence_check_p3', ROOT / 'scripts/doc-control/evidence_pack.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        results = module.collect_checks()
        self.assertEqual([row['name'] for row in results],
                         ['drift', 'metadata', 'inventory', 'ownership', 'freshness', 'sync-map', 'local-links'])
        self.assertEqual([row['exit_code'] for row in results], [0] * len(results))

    def test_env_reference_is_from_described_values(self):
        rows = environment(ROOT / 'EXAMPLE-PROJECT/.env.example')
        self.assertEqual([r[0] for r in rows], ['PORT', 'DB_PATH'])
        self.assertIn('HTTP listen port', rows[0][2])
        self.assertTrue(engine.generate(check=True, only='env-reference'))

    def test_env_rejects_missing_description(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.env.example'
            path.write_text('PORT=8000\n')
            with self.assertRaisesRegex(ValueError, 'description'):
                environment(path)

    def test_env_rejects_duplicate_key(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.env.example'
            path.write_text('# first\nPORT=1\n# second\nPORT=2\n')
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                environment(path)

    def test_alert_catalog_resolves_runbook(self):
        rows = alerts(ROOT / 'EXAMPLE-PROJECT/monitoring/alerts.yaml', ROOT)
        self.assertEqual(rows[0]['id'], 'service-unhealthy')
        self.assertTrue(engine.generate(check=True, only='alerts'))

    def test_general_yaml_alerts_fail_with_not_implemented_reason(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'alerts.yaml'
            path.write_text('alerts:\n  - id: unavailable\n')
            with self.assertRaisesRegex(ValueError, 'NOT_IMPLEMENTED: only JSON-compatible YAML'):
                alerts(path, ROOT)

    def test_general_yaml_tool_policy_fails_with_not_implemented_reason(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'tools.yaml'
            path.write_text('tools:\n  - name: math.add\n')
            with self.assertRaisesRegex(ValueError, 'NOT_IMPLEMENTED: only JSON-compatible YAML'):
                tool_matrix(path)

    def test_alert_rejects_missing_runbook(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'alerts.yaml'
            path.write_text(json.dumps({'alerts': [{'id': 'down', 'condition': 'offline',
                'severity': 'high', 'runbook': 'no-such-runbook.md'}]}))
            with self.assertRaisesRegex(ValueError, 'runbook'):
                alerts(path, ROOT)

    def test_alert_rejects_unrecognized_severity(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'alerts.yaml'
            path.write_text(json.dumps({'alerts': [{'id': 'down', 'condition': 'offline',
                'severity': 'magical', 'runbook': 'EXAMPLE-PROJECT/docs/HEALTH-RUNBOOK.md'}]}))
            with self.assertRaisesRegex(ValueError, 'severity'):
                alerts(path, ROOT)

    def test_supersedes_cycle_fails(self):
        engine.check_supersedes_cycles({'A': 'B', 'B': 'C'})
        with self.assertRaisesRegex(ValueError, 'Circular'):
            engine.check_supersedes_cycles({'A': 'B', 'B': 'A'})

    def test_graph_contains_mapped_source_and_template_edges(self):
        graph = (ROOT / 'docs/reference/DOC-RELATIONSHIPS.md').read_text()
        self.assertIn('flowchart LR', graph)
        self.assertIn('|generates|', graph)
        self.assertIn('|template|', graph)
        self.assertTrue(engine.generate(check=True, only='relationship-visualization'))

    def test_human_inventory_matches_current_frontmatter(self):
        docs = json.loads((ROOT / 'docs/00-governance/INVENTORY.yaml').read_text())['documents']
        entries = {record['path']: record['id'] for record in docs}
        self.assertEqual(len(entries), len(docs))
        expected = {str(path.relative_to(ROOT)): engine.parse_frontmatter(path)['id']
                    for path in engine.controlled()
                    if engine.parse_frontmatter(path)['auto_generated'] == 'false'}
        self.assertEqual(entries, expected)
        self.assertTrue(owner.check())

    def test_staged_alert_requires_human_runbook(self):
        with patch.object(engine, 'changed', return_value={'EXAMPLE-PROJECT/monitoring/alerts.yaml'}):
            self.assertFalse(engine.impact(staged=True))
        files = {'EXAMPLE-PROJECT/monitoring/alerts.yaml', 'EXAMPLE-PROJECT/docs/HEALTH-RUNBOOK.md',
                 'CURRENT-STATE.md', 'NEXT-ACTION.md', 'RECENT-CHANGES.md'}
        with patch.object(engine, 'changed', return_value=files):
            self.assertTrue(engine.impact(staged=True))


    def test_staged_frontmatter_reads_index_blob(self):
        name = 'docs/00-governance/LIMITATIONS.md'
        valid = (ROOT / name).read_text()
        with patch.object(engine, 'git', return_value=name):
            with patch.object(engine.subprocess, 'check_output', return_value=valid):
                self.assertTrue(engine.validate_staged())
            with patch.object(engine.subprocess, 'check_output', return_value=valid.replace(
                    'owner: "@Er-Sajan-PLG"', 'owner: ')):
                self.assertFalse(engine.validate_staged())

    def test_staged_guard_checks_index_not_worktree(self):
        spec = importlib.util.spec_from_file_location('phase3_guard', ROOT / 'scripts/doc-control/guards.py')
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)
        with patch.object(guard.subprocess, 'check_output', side_effect=[
                'README.md\n', b'-----BEGIN ' + b'PRIVATE KEY-----\n']):
            self.assertFalse(guard.check(staged=True))

    def test_early_next_review_overrides_long_review_interval(self):
        path = ROOT / 'docs/00-governance/LIMITATIONS.md'
        meta = engine.parse_frontmatter(path)
        meta.update(next_review='2026-10-01', review_days='180', criticality='critical')
        with patch.object(engine, 'controlled', return_value=[path]):
            with patch.object(engine, 'parse_frontmatter', return_value=meta):
                self.assertTrue(engine.validate(freshness=False, now=date(2026, 10, 2)))
                self.assertFalse(engine.validate(freshness=True, now=date(2026, 10, 2)))

    def test_health_counts_are_measured_not_catalog_instances(self):
        spec = importlib.util.spec_from_file_location('phase3_health', ROOT / 'scripts/doc-control/health.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data = module.health()
        self.assertEqual(data['controlled_document_instances'], len(engine.controlled()))
        self.assertIsInstance(data['drafts_without_updates_over_60_days'], list)
        self.assertTrue(data['drift_free'])

    def test_catalog_view_is_deterministic(self):
        entry = next(e for e in engine.load_map()['generated'] if e['id'] == 'catalog-view-a')
        self.assertEqual(engine.catalog_view(entry), engine.catalog_view(entry))


if __name__ == '__main__':
    unittest.main()
