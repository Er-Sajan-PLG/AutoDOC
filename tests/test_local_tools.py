"""Real local-only authorization tests, including symlink and traversal denial."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'examples/local-tools-example'
sys.path.insert(0, str(EXAMPLE))
from src import tool_runner, policy
sys.path.insert(0, str(ROOT / 'engine'))
from extractors.local_policy import tool_matrix


class LocalToolsTests(unittest.TestCase):
    def test_allowed_pure_tools(self):
        self.assertEqual(tool_runner.run('math.add', 2, 3), 5)
        self.assertEqual(tool_runner.run('text.upper', 'aBc'), 'ABC')
        self.assertIn('Local, safe', tool_runner.run('files.read', 'sample.txt'))

    def test_unknown_and_blocked_tools(self):
        with self.assertRaisesRegex(ValueError, 'unknown tool'):
            tool_runner.run('arbitrary.shell', 'anything')
        for name in ('network.fetch', 'shell.run_script'):
            with self.assertRaisesRegex(PermissionError, 'blocked by policy'):
                tool_runner.run(name, 'ignored')

    def test_invalid_arguments_and_traversal(self):
        with self.assertRaisesRegex(ValueError, 'integers'):
            tool_runner.run('math.add', True, 2)
        with self.assertRaisesRegex(ValueError, '1024'):
            tool_runner.run('text.upper', 'x' * 1025)
        for name in ('../README.md', '/etc/passwd'):
            with self.assertRaises(ValueError):
                tool_runner.run('files.read', name)

    def test_symlink_cannot_escape_data_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder) / 'data'
            data.mkdir()
            (data / 'outside.txt').symlink_to(ROOT / 'README.md')
            with self.assertRaisesRegex(ValueError, 'outside'):
                tool_runner.run('files.read', 'outside.txt', data_root=data)

    def test_policy_and_generator_reject_malformed_matrix(self):
        source = EXAMPLE / 'config/tool-authorization.yaml'
        self.assertEqual(len(policy.load()), 5)
        self.assertEqual(len(tool_matrix(source)), 5)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'matrix.yaml'
            content = json.loads(source.read_text())
            content['tools'][3]['status'] = 'allow'
            path.write_text(json.dumps(content))
            with self.assertRaisesRegex(ValueError, 'block'):
                policy.load(path)
            with self.assertRaisesRegex(ValueError, 'blocked'):
                tool_matrix(path)


if __name__ == '__main__':
    unittest.main()
