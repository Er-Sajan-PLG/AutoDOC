"""Extract the local example's closed JSON-compatible YAML tool matrix."""
import json
from pathlib import Path


def tool_matrix(path: Path):
    try:
        rows = json.loads(path.read_text(encoding='utf-8'))['tools']
    except json.JSONDecodeError as exc:
        raise ValueError(f'{path}: NOT_IMPLEMENTED: only JSON-compatible YAML tool policies are supported; {exc}') from exc
    names = [row['name'] for row in rows]
    expected = {'math.add', 'text.upper', 'files.read', 'shell.run_script', 'network.fetch'}
    if len(names) != len(expected) or set(names) != expected:
        raise ValueError(f'{path}: incomplete or duplicate local tool allowlist')
    if any(row['status'] != 'blocked' for row in rows if row['name'] in ('network.fetch', 'shell.run_script')):
        raise ValueError(f'{path}: unimplemented network/shell tools must remain blocked')
    return sorted(rows, key=lambda row: row['name'])
