#!/usr/bin/env python3
"""Create an unsigned release-document snapshot artifact, only after licensing is decided."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/doc-sync'))
import engine


def require_license(root=ROOT):
    """The release gate: the license text is present, whatever the decision record says."""
    path = Path(root) / 'LICENSE'
    if not path.is_file():
        raise ValueError('LICENSE is missing: the release gate needs the license text; '
                         'see docs/00-governance/LICENSE-DECISION.md')
    return path


def snapshot(tag, output):
    if not re.fullmatch(r'v\d+\.\d+\.\d+', tag):
        raise ValueError('Expected a semantic version tag vX.Y.Z')
    require_license()
    commit = subprocess.check_output(['git', 'rev-parse', '--verify', tag + '^{commit}'],
                                     cwd=ROOT, text=True).strip()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if head != commit:
        raise ValueError('Checkout must be at the requested tag commit')
    if not engine.generate(check=True) or not engine.validate(freshness=True):
        raise ValueError('Doc drift or critical freshness failure; release aborted')
    directory = output / tag
    if directory.exists():
        raise ValueError('Release snapshot exists; never mutate an existing snapshot')
    directory.mkdir(parents=True)
    manifest = {'tag': tag, 'commit': commit,
                'scope': 'unsigned local documentation snapshot; store externally for retention',
                'files_sha256': {}}
    for path in engine.controlled():
        rel = path.relative_to(ROOT)
        raw = path.read_bytes()
        target = directory / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        manifest['files_sha256'][str(rel)] = hashlib.sha256(raw).hexdigest()
    (directory / 'RELEASE-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return directory


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(snapshot(args.tag, args.output))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Release blocked: {exc}\n')
