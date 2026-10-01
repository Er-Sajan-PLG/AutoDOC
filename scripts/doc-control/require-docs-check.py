#!/usr/bin/env python3
"""Print (and only with --apply, set) the branch protection that makes the docs gate required.

Owner-run by design: it changes repository settings, so it is dry-run by default and prints the
exact payload before anything else. The pre-push hook is bypassable; a required CI check is the
only gate that cannot be skipped. This script needs the `gh` CLI and repository-admin rights.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK_NAME = 'AutoDOC guard / check'


def gh(*args, **kwargs):
    return subprocess.check_output(['gh', *args], cwd=ROOT, text=True, **kwargs)


def payload(check=CHECK_NAME):
    """The classic required-status-checks payload; one required check, no push restrictions."""
    return {'strict': True, 'contexts': [check]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--branch', default='master', help='Protected branch (default master)')
    parser.add_argument('--check', default=CHECK_NAME, help='Required check name')
    parser.add_argument('--apply', action='store_true',
                        help='Actually PUT the payload (default is dry-run)')
    args = parser.parse_args()
    try:
        repo = json.loads(gh('repo', 'view', '--json', 'nameWithOwner'))
        owner, name = repo['nameWithOwner'].split('/', 1)
    except (subprocess.CalledProcessError, OSError, KeyError, ValueError) as error:
        print('Cannot resolve the repository with gh:', error, file=sys.stderr)
        print('Nothing was changed.', file=sys.stderr)
        return 2
    body = payload(args.check)
    endpoint = f'repos/{owner}/{name}/branches/{args.branch}/protection/required_status_checks'
    print(f'Repository: {owner}/{name}')
    print(f'Branch:     {args.branch}')
    print(f'Check:      {args.check}  (must match the GitHub Actions job name exactly)')
    print('Payload:')
    print(json.dumps(body, indent=2))
    if not args.apply:
        print('\nDry run. Nothing was changed. Re-run with --apply to PUT this payload.\n'
              f'gh api -X PUT {endpoint} --input -')
        return 0
    result = subprocess.run(['gh', 'api', '-X', 'PUT', endpoint, '--input', '-'],
                            cwd=ROOT, input=json.dumps(body), text=True)
    if result.returncode:
        print('Branch protection update failed. Nothing was changed.', file=sys.stderr)
        return 2
    print('Required status check set. Verify the check name in a pull request.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
