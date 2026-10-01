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


FIXES = {
    'links.local': 'fix the path, or point at a file that exists',
    'secrets.inline': 'remove the value from history and rotate the credential',
    'tribal': 'replace the private instruction with a documented owner or process',
}


def collect_text(path, text):
    """Return findings as dicts: {rule, location, detail}. Never includes a secret value."""
    findings = []
    if path.suffix == '.md':
        if TRIBAL.search(text):
            findings.append({'rule': 'tribal', 'location': str(path),
                             'detail': 'undocumented tribal instruction'})
        for raw in LINK.findall(text):
            url = unquote(raw.split()[0].strip('<>'))
            if url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue  # offline check cannot claim external URLs are live
            target = (path.parent / url.split('#', 1)[0]).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                findings.append({'rule': 'links.local', 'location': str(path),
                                 'detail': f'broken local link {raw}'})
    if KEY.search(text):
        # Names and locations only: the matched line is never copied into the finding.
        findings.append({'rule': 'secrets.inline', 'location': str(path),
                         'detail': 'private key marker detected'})
    return findings


def check_text(path, text):
    """The historical string shape, derived from collect_text so both cannot diverge."""
    return [f"{finding['location']}: {finding['detail']}" for finding in collect_text(path, text)]


def _sources(staged=False):
    """Yield (path, text) for the files this guard inspects, read from the index when staged."""
    if staged:
        files = subprocess.check_output(['git', 'diff', '--cached', '--name-only',
                                         '--diff-filter=ACMRT'], cwd=ROOT, text=True).splitlines()
        paths = [ROOT / name for name in files]
    else:
        paths = [*ROOT.rglob('*.md'), *ROOT.rglob('*.py'), *ROOT.rglob('*.yml')]
        paths = [p for p in paths if not any(part in ('.git', '.venv', '__pycache__', 'node_modules')
                                             for part in p.parts)]
    for path in paths:
        if staged:
            # Inspect the exact blob being committed, not an unstaged worktree revision.
            relative = str(path.relative_to(ROOT))
            yield path, subprocess.check_output(['git', 'show', ':' + relative],
                                                cwd=ROOT).decode('utf-8', errors='replace')
        elif path.is_file():
            yield path, path.read_text(encoding='utf-8', errors='replace')


def collect(staged=False):
    """Return every guard finding as a dict, with the same file selection as check()."""
    findings = []
    for path, content in _sources(staged):
        findings += collect_text(path, content)
    return findings


def check(staged=False):
    errors = [f"{finding['location']}: {finding['detail']}"
              for finding in collect(staged)]
    for error in errors:
        print(error, file=sys.stderr)
    return not errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', action='store_true')
    args = parser.parse_args()
    raise SystemExit(0 if check(args.staged) else 1)
