"""Strict, bounded extractors for example environment and alert declarations."""
import json
import re
from pathlib import Path


def environment(path: Path):
    """Parse described KEY=value entries; never silently accept undocumented keys."""
    rows, description = [], None
    for number, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line:
            description = None
            continue
        if line.startswith('#'):
            if line.lower().startswith('# generated from'):
                continue
            description = line[1:].strip()
            continue
        match = re.fullmatch(r'([A-Z][A-Z0-9_]*)=(.*)', line)
        if not match or not description:
            raise ValueError(f'{path}:{number}: expected described KEY=value; add a # description')
        key, value = match.groups()
        if any(key == previous[0] for previous in rows):
            raise ValueError(f'{path}:{number}: duplicate environment key {key}')
        if '|' in description or '|' in value:
            raise ValueError(f'{path}:{number}: unsafe Markdown table value for {key}')
        rows.append((key, value, description))
        description = None
    if not rows:
        raise ValueError(f'{path}: no described environment keys')
    return rows


def alerts(path: Path, root: Path):
    """JSON-compatible YAML subset; validate actual runbook existence and mandatory fields."""
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise ValueError(f'{path}: NOT_IMPLEMENTED: only JSON-compatible YAML alert files are supported; {exc}') from exc
    rows = data.get('alerts')
    if not isinstance(rows, list) or not rows:
        raise ValueError(f'{path}: expected nonempty alerts list')
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'id', 'condition', 'severity', 'runbook'}:
            raise ValueError(f'{path}: alert needs id, condition, severity and runbook')
        if row['id'] in seen or not re.fullmatch(r'[a-z][a-z0-9-]*', row['id']):
            raise ValueError(f'{path}: duplicate/invalid alert ID: {row["id"]}')
        seen.add(row['id'])
        if row['severity'] not in ('critical', 'high', 'medium', 'low'):
            raise ValueError(f'{path}: invalid severity for {row["id"]}')
        for field in ('condition', 'runbook'):
            if not isinstance(row[field], str) or not row[field] or '|' in row[field]:
                raise ValueError(f'{path}: invalid {field} for {row["id"]}')
        target = root / row['runbook']
        if (Path(row['runbook']).is_absolute() or '..' in Path(row['runbook']).parts or
            not target.resolve().is_relative_to(root.resolve()) or not target.is_file()):
            raise ValueError(f'{path}: {row["id"]} missing/unsafe runbook {row["runbook"]}')
    return sorted(rows, key=lambda row: row['id'])
