"""Second example: real local tool authorization and honest NOT_IMPLEMENTED behavior."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'examples/ai-agent-example/src'
sys.path.insert(0, str(SRC))
from tools import file_ops, web_search

spec = importlib.util.spec_from_file_location('local_agent', SRC / 'agent.py')
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)

spec = importlib.util.spec_from_file_location('pack_tests', ROOT / 'scripts/doc-control/evidence_pack.py')
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)

spec = importlib.util.spec_from_file_location('snapshot_tests', ROOT / 'scripts/doc-control/release_snapshot.py')
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class AgentExampleTests(unittest.TestCase):
    def test_allowlisted_tools_work(self):
        self.assertEqual(agent.run('add', 2, 3), 5)
        self.assertIn('System prompt', agent.run('read_prompt', 'system.md'))
        with self.assertRaises(ValueError):
            agent.run('add', True, 1)

    def test_disallowed_tools_fail_without_side_effects(self):
        with self.assertRaisesRegex(ValueError, 'not authorized'):
            agent.run('search', 'query')
        with self.assertRaises(ValueError):
            file_ops.read_prompt('../README.md')
        with self.assertRaisesRegex(NotImplementedError, 'NOT_IMPLEMENTED'):
            web_search.search('query')

    def test_tool_registry_fails_when_manifest_points_to_missing_implementation(self):
        import importlib.util
        sync = importlib.util.spec_from_file_location('agent_sync_test', ROOT / 'scripts/doc-sync/engine.py')
        engine = importlib.util.module_from_spec(sync)
        sync.loader.exec_module(engine)
        self.assertTrue(engine.generate(check=True, only='agent-tools'))
        with tempfile.TemporaryDirectory() as folder:
            fake_root = Path(folder)
            source = fake_root / 'examples/ai-agent-example/src'
            (source / 'tools').mkdir(parents=True)
            (source / 'tools/calculator.py').write_bytes((SRC / 'tools/calculator.py').read_bytes())
            data = json.loads((SRC / 'tools.json').read_text())
            data['tools'] = [dict(data['tools'][0], function='does_not_exist')]
            (source / 'tools.json').write_text(json.dumps(data))
            from unittest.mock import patch
            with patch.object(engine, 'ROOT', fake_root):
                with self.assertRaisesRegex(ValueError, 'not implemented'):
                    engine.agent_tools({'sources': ['examples/ai-agent-example/src/tools.json']})

    def test_passing_unsigned_evidence_detects_tampering(self):
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            test_path = base / 'test.json'
            test = {'kind': 'autodoc-test-run', 'exit_code': 0, 'commit': commit,
                    'stdout': 'synthetic unit-test fixture', 'stderr': '',
                    'stdout_sha256': hashlib.sha256(b'synthetic unit-test fixture').hexdigest(),
                    'stderr_sha256': hashlib.sha256(b'').hexdigest()}
            test_path.write_text(json.dumps(test))
            pack.make_pack(test_path, base / 'pack')
            self.assertTrue(pack.verify(base / 'pack'))
            (base / 'pack/sbom.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'altered'):
                pack.verify(base / 'pack')

    def test_release_blocks_without_owner_license_choice(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'License not selected'):
                snapshot.snapshot('v1.0.0', Path(folder))
            with self.assertRaisesRegex(ValueError, 'semantic version'):
                snapshot.snapshot('anything', Path(folder))


if __name__ == '__main__':
    unittest.main()
