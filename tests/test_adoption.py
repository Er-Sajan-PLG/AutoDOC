"""Scaffolding is opt-in, creates unique instance IDs and never overwrites edits."""
import importlib.util
import json
from unittest.mock import patch
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AdoptionTests(unittest.TestCase):
    def test_new_project_scaffold_is_safe_to_rerun(self):
        with tempfile.TemporaryDirectory() as folder:
            command = [sys.executable, str(ROOT / 'scripts/init-project.py'), '--name', 'Sample App',
                       '--type', 'web-api', '--output', folder]
            subprocess.run(command, check=True, capture_output=True)
            docs = sorted((Path(folder) / 'docs/autodoc').glob('*.md'))
            self.assertEqual(len(docs), 10)
            self.assertIn('id: INST-SAMPLE-APP-DEV-', docs[0].read_text())
            docs[0].write_text('intentionally edited')
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(docs[0].read_text(), 'intentionally edited')


    def test_owned_documents_are_within_declared_scope(self):
        spec = importlib.util.spec_from_file_location('ownership', ROOT / 'scripts/doc-control/check_ownership.py')
        ownership = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ownership)
        self.assertTrue(ownership.check())
        doc = ROOT / 'CURRENT-STATE.md'
        with patch.object(ownership, 'controlled', return_value=[doc]):
            with patch.object(ownership, 'parse_frontmatter', return_value={'owner': '@unknown'}):
                self.assertFalse(ownership.check())

    def test_adoption_is_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'go.mod'
            path.write_text('module example')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/adopt.py'),
                                     '--project-path', folder], capture_output=True, text=True, check=True)
            self.assertIn('A10-BUILD', result.stdout)
            self.assertEqual([p.name for p in Path(folder).iterdir()], ['go.mod'])


if __name__ == '__main__':
    unittest.main()
