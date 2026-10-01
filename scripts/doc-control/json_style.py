"""Render data files in the repository's hand-edited style.

Standard `json.dumps(indent=2)` explodes arrays of short strings one per line. The data files
in CONTROL/metadata are read and diffed by humans, so short scalar arrays stay inline. This
helper exists so a script can rewrite those files without producing a formatting-only diff that
hides the real change.

Usage:
    from json_style import dumps
    path.write_text(dumps(data))
"""
import json
import re

SCALAR_LINE = re.compile(r'^(\s*)"((?:[^"\\]|\\.)*)"(,?)$')
OPEN_ARRAY = re.compile(r'^(\s*)"([^"]+)": \[$')
MAX_INLINE = 100
MAX_ITEM = 60


def _collapse(text):
    lines = text.split('\n')
    out, index = [], 0
    while index < len(lines):
        line = lines[index]
        opening = OPEN_ARRAY.match(line)
        if not opening:
            out.append(line)
            index += 1
            continue
        indent, key = opening.group(1), opening.group(2)
        items, cursor = [], index + 1
        close = f'{indent}]'
        while cursor < len(lines) and lines[cursor] in (close, close + ','):
            break
        while cursor < len(lines):
            match = SCALAR_LINE.match(lines[cursor])
            if not match or match.group(1) != indent + '  ':
                break
            items.append(json.loads('"' + match.group(2) + '"'))
            cursor += 1
        if items and cursor < len(lines) and lines[cursor] in (close, close + ',') \
                and all(len(item) <= MAX_ITEM for item in items):
            inline = json.dumps(items, ensure_ascii=False)
            candidate = f'{indent}"{key}": {inline}' + (',' if lines[cursor].endswith(',') else '')
            if len(candidate) <= MAX_INLINE:
                out.append(candidate)
                index = cursor + 1
                continue
        out.append(line)
        index += 1
    return '\n'.join(out)


def dumps(data):
    """Serialise `data` as indented JSON with short scalar arrays kept on one line."""
    return _collapse(json.dumps(data, indent=2, ensure_ascii=False)) + '\n'
