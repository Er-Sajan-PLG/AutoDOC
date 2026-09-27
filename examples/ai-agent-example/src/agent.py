"""Explicit tool dispatcher, intentionally NOT an LLM or autonomous reasoning runtime."""
import importlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def run(tool: str, *args):
    """Dispatch a requested tool only if declared in the versioned allowlist."""
    manifest = json.loads((ROOT / 'src/tools.json').read_text(encoding='utf-8'))
    authorized = {item['name']: item for item in manifest['tools']}
    if tool not in authorized:
        raise ValueError('tool not authorized: ' + tool)
    entry = authorized[tool]
    if entry['module'] not in ('tools.calculator', 'tools.file_ops'):
        raise ValueError('module not in implementation allowlist')
    module = importlib.import_module(entry['module'])
    return getattr(module, entry['function'])(*args)


if __name__ == '__main__':
    print(run('add', 2, 3))
