#!/usr/bin/env python3
"""Conservative offline Markdown link, key-marker, and tribal-knowledge guards."""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote
ROOT = Path(__file__).resolve().parents[2]
TRIBAL = re.compile(r'\b(?:ask John|ask Sarah|just ask|ask in DM)\b', re.I)
KEY = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
LINK = re.compile(r'(?<!!)\[[^]]+\]\(([^)]+)\)')


def check_text(path, text):
    errors = []
    if path.suffix == '.md':
        if TRIBAL.search(text):
            errors.append(f'{path}: undocumented tribal instruction; replace with a documented owner/process')
        for raw in LINK.findall(text):
            url = unquote(raw.split()[0].strip('<>'))
            if url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue  # offline check cannot claim external URLs are live
            target = (path.parent / url.split('#', 1)[0]).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(f'{path}: broken local link {raw}')
    if KEY.search(text):
        errors.append(f'{path}: private key marker detected; remove the secret and rotate it')
    return errors


def check(staged=False):
    if staged:
        files = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMRT'],
                                        cwd=ROOT, text=True).splitlines()
        paths = [ROOT / name for name in files]
    else:
        paths = [*ROOT.rglob('*.md'), *ROOT.rglob('*.py'), *ROOT.rglob('*.yml')]
        paths = [p for p in paths if not any(part in ('.git', '.venv', '__pycache__', 'node_modules') for part in p.parts)]
    errors = []
    for path in paths:
        if staged:
            # Inspect the exact blob being committed, not an unstaged worktree revision.
            relative = str(path.relative_to(ROOT))
            content = subprocess.check_output(['git', 'show', ':' + relative], cwd=ROOT).decode(
                'utf-8', errors='replace')
            errors += check_text(path, content)
        elif path.is_file():
            errors += check_text(path, path.read_text(encoding='utf-8', errors='replace'))
    for error in errors:
        print(error, file=sys.stderr)
    return not errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', action='store_true')
    args = parser.parse_args()
    raise SystemExit(0 if check(args.staged) else 1)
