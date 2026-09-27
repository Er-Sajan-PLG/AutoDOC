"""Regression tests for deterministic docs, impact rules, metadata and the demo API."""
import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('engine', ROOT / 'scripts/doc-sync/engine.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


class EngineTests(unittest.TestCase):
    def test_repo_generated_docs_are_in_sync(self):
        self.assertTrue(engine.generate(check=True))

    def test_controlled_metadata_and_ids(self):
        self.assertTrue(engine.validate())
        self.assertTrue(engine.validate(freshness=True, now=date(2026, 9, 26)))
        ids = [engine.parse_frontmatter(p)['id'] for p in engine.controlled()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_drift_is_detected_without_rewriting(self):
        target = ROOT / 'EXAMPLE-PROJECT/docs/API-REFERENCE.md'
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder) / 'API-REFERENCE.md'
            fake.write_text('stale')
            entry = {'id': 'api', 'sources': ['EXAMPLE-PROJECT/routes.json'],
                     'target': str(fake), 'generator': 'api'}
            with patch.object(engine, 'load_map', return_value={'generated': [entry]}):
                with patch.object(engine, 'safe_path', return_value=fake):
                    self.assertFalse(engine.generate(check=True))
            self.assertEqual(fake.read_text(), 'stale')
            self.assertTrue(target.exists())

    def test_impact_requires_human_and_living_docs(self):
        with patch.object(engine, 'changed', return_value={'EXAMPLE-PROJECT/src/app.py'}):
            self.assertFalse(engine.impact())
        with patch.object(engine, 'changed', return_value={
            'EXAMPLE-PROJECT/src/app.py', 'EXAMPLE-PROJECT/docs/ARCHITECTURE.md',
            'CURRENT-STATE.md', 'NEXT-ACTION.md', 'RECENT-CHANGES.md', 'CHANGELOG.md'}):
            self.assertTrue(engine.impact())

    def test_missing_source_fails_closed(self):
        data = engine.load_map()
        data['generated'][0]['sources'] = ['this-path-does-not-exist/*.json']
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder) / 'map.yaml'
            fake.write_text(json.dumps(data))
            with patch.object(engine, 'MAP', fake):
                with self.assertRaisesRegex(ValueError, 'Missing source'):
                    engine.load_map()

    def test_catalog_template_coverage(self):
        for catalog in ('CATALOG-A', 'CATALOG-B'):
            data = json.loads((ROOT / catalog / 'INDEX.yaml').read_text())
            for domain in data['domains']:
                for doc in domain['documents']:
                    path = ROOT / doc['template']
                    for suffix in ('', '.example', '.blank'):
                        self.assertTrue(Path(str(path) + suffix).is_file())


    def test_self_hosted_sources_have_generated_references(self):
        data = engine.load_map()
        ids = {e['id'] for e in data['generated']}
        self.assertIn('catalog', ids)
        self.assertIn('workflows', ids)
        text = (ROOT / 'docs/generated/CATALOG-REFERENCE.md').read_text()
        self.assertIn('DOC-A03-005', text)
        self.assertIn('DEV-B09-001', text)
        import hashlib
        workflow = ROOT / '.github/workflows/docs-guard.yml'
        digest = hashlib.sha256(workflow.read_bytes()).hexdigest()
        self.assertIn(digest, (ROOT / 'docs/generated/WORKFLOW-REFERENCE.md').read_text())

    def test_workflow_generator_requires_inline_purpose(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            workflow = Path(folder) / 'bad.yml'
            workflow.write_text('name: Bad workflow\non: workflow_dispatch\n')
            with patch.object(engine, 'paths', return_value=[workflow]):
                with self.assertRaisesRegex(ValueError, 'purpose comment'):
                    engine.workflows({'sources': ['.github/workflows/*.yml']})

    def test_self_review_rules_are_enforced(self):
        with patch.object(engine, 'changed', return_value={'CATALOG-C/INDEX.yaml'}):
            self.assertFalse(engine.impact())
        with patch.object(engine, 'changed', return_value={
            'CATALOG-C/INDEX.yaml', 'docs/00-governance/ADOPTION.md',
            'CURRENT-STATE.md', 'NEXT-ACTION.md', 'RECENT-CHANGES.md'}):
            self.assertTrue(engine.impact())
        with patch.object(engine, 'changed', return_value={'scripts/doc-sync/engine.py'}):
            self.assertFalse(engine.impact())

    def test_rejects_map_target_outside_checkout(self):
        data = engine.load_map()
        data['generated'][0]['target'] = '../outside.md'
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder) / 'map.yaml'
            fake.write_text(json.dumps(data))
            with patch.object(engine, 'MAP', fake):
                with self.assertRaisesRegex(ValueError, 'inside the repository'):
                    engine.load_map()

    def test_critical_stale_fails(self):
        path = ROOT / 'CURRENT-STATE.md'
        fields = engine.parse_frontmatter(path)
        fields['criticality'] = 'critical'
        with patch.object(engine, 'controlled', return_value=[path]):
            with patch.object(engine, 'parse_frontmatter', return_value=fields):
                self.assertFalse(engine.validate(freshness=True, now=date(2028, 1, 1)))


if __name__ == '__main__':
    unittest.main()
