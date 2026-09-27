"""Extract bounded, factual inventories using the Python standard library.

These functions return records, never free-form generated prose. Files are explicitly
passed in; no extractor walks outside the configured sources.
"""
import ast
import re
import tomllib
from pathlib import Path


def headings(path: Path):
    """ATX headings, excluding fenced code (setext headings are not supported)."""
    rows, fence = [], False
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if re.match(r'^\s*(```|~~~)', line):
            fence = not fence
            continue
        if not fence:
            match = re.match(r'^(#{1,6})\s+(.+?)(?:\s+#+)?\s*$', line)
            if match:
                rows.append((number, len(match.group(1)), match.group(2)))
    if fence:
        raise ValueError(f'Unclosed Markdown code fence: {path}')
    return rows


def python_symbols(path: Path):
    """Public top-level Python classes/functions and class methods from a parsed AST."""
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    rows = []

    def record(node, prefix=''):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            signature = ast.unparse(node.args)
            annotation = ' -> ' + ast.unparse(node.returns) if node.returns else ''
            rows.append((node.lineno, 'async function' if isinstance(node, ast.AsyncFunctionDef) else 'function',
                         prefix + node.name, '(' + signature + ')' + annotation))
        elif isinstance(node, ast.ClassDef):
            rows.append((node.lineno, 'class', prefix + node.name, ''))
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    record(child, prefix + node.name + '.')

    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            record(node)
    return rows


def python_tests(path: Path):
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    tests = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            tests.append((node.lineno, node.name))
        elif isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith('test_'):
                    tests.append((method.lineno, node.name + '.' + method.name))
    return tests


def python_dependencies(path: Path):
    data = tomllib.loads(path.read_text(encoding='utf-8'))
    project = data.get('project')
    if not isinstance(project, dict) or not project.get('name') or not project.get('version'):
        raise ValueError(f'Expected a PEP 621 project with name/version: {path}')
    groups = [('runtime', project.get('dependencies', []))]
    groups += [(f'optional:{k}', v) for k, v in sorted(project.get('optional-dependencies', {}).items())]
    if any(not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps) for _, deps in groups):
        raise ValueError(f'Invalid dependency list: {path}')
    return project['name'], project['version'], [(group, dep) for group, deps in groups for dep in sorted(deps)]


def sqlite_tables(path: Path):
    """Only the deliberately small CREATE TABLE subset used by the demo.

    Reject ALTER/INDEX/constraints and dialect extensions instead of returning a partial
    dictionary that looks complete. Integrators must add a dialect-aware extractor.
    """
    text = '\n'.join(line for line in path.read_text(encoding='utf-8').splitlines()
                     if not line.lstrip().startswith('--'))
    statements = [statement.strip() for statement in text.split(';') if statement.strip()]
    if not statements:
        raise ValueError('No SQL table statements found')
    tables = []
    for statement in statements:
        match = re.fullmatch(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*)\)',
                             statement, re.I | re.S)
        if not match:
            raise ValueError(f'NOT_IMPLEMENTED: Unsupported SQL statement (cannot produce complete dictionary): {statement[:60]}')
        table, body = match.groups()
        columns = []
        for field in body.split(','):
            field = field.strip()
            column = re.fullmatch(r'(\w+)\s+((?:INTEGER|TEXT|REAL|BLOB|NUMERIC)'
                                  r'(?:\s+(?:PRIMARY KEY AUTOINCREMENT|PRIMARY KEY|NOT NULL|UNIQUE))*)',
                                  field, re.I)
            if not column:
                raise ValueError(f'NOT_IMPLEMENTED: Unsupported SQL column definition: {field}')
            columns.append((column.group(1), column.group(2)))
        if not columns:
            raise ValueError('Empty SQL table: ' + table)
        tables.append((table, columns))
    return tables


def demo_routes(path: Path):
    """Only routes actually dispatched by the educational task API."""
    import json
    routes = json.loads(path.read_text(encoding='utf-8'))['routes']
    expected = {('GET', '/tasks'), ('POST', '/tasks'), ('GET', '/health')}
    if not isinstance(routes, list) or len(routes) != len(expected):
        raise ValueError('Route registry differs from implemented demo handlers')
    seen = set()
    for route in routes:
        if set(route) != {'method', 'path', 'description', 'response'}:
            raise ValueError('Incomplete route registry entry')
        key = (route['method'], route['path'])
        if key not in expected or key in seen:
            raise ValueError('NOT_IMPLEMENTED: Unsupported or duplicate route: ' + str(key))
        seen.add(key)
        if any(not isinstance(route[k], str) or not route[k] or '|' in route[k] or '\n' in route[k]
               for k in route):
            raise ValueError('Unsafe route table field: ' + str(key))
    return routes


def config_properties(path: Path):
    """Validate the demo's bounded JSON config before rendering reference and .env."""
    import json
    fields = json.loads(path.read_text(encoding='utf-8'))['properties']
    if not isinstance(fields, dict) or not fields:
        raise ValueError('Empty or invalid config properties')
    for name, field in fields.items():
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*', name) or set(field) != {'type', 'default', 'description'}:
            raise ValueError('Unsupported config property: ' + name)
        if field['type'] not in ('integer', 'string') or (
            field['type'] == 'integer' and type(field['default']) is not int) or (
            field['type'] == 'string' and type(field['default']) is not str):
            raise ValueError('Config default/type mismatch: ' + name)
        if any('\n' in str(field[key]) or '|' in str(field[key]) for key in ('default', 'description')):
            raise ValueError('Unsafe config table/default value: ' + name)
    return fields
