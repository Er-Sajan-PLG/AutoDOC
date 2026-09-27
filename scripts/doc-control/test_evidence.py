#!/usr/bin/env python3
"""Run the real test suite and save a scoped, unsigned CI test evidence artifact."""
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import xml.etree.ElementTree as ET
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def junit_counts(path):
    """Use actual JUnit attributes; never infer a count from a console progress bar."""
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == 'testsuite' else list(root.findall('testsuite'))
    if not suites:
        raise ValueError('No JUnit testsuite in actual pytest output')
    values = {key: sum(int(suite.get(key, '0')) for suite in suites)
              for key in ('tests', 'failures', 'errors', 'skipped')}
    values['passed'] = values['tests'] - values['failures'] - values['errors'] - values['skipped']
    if values['passed'] < 0:
        raise ValueError('Invalid JUnit test totals')
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    pytest_available = importlib.util.find_spec('pytest') is not None
    junit = args.output.parent / 'test-results.xml'
    cmd = ([sys.executable, '-m', 'pytest', '-v', '--junitxml', str(junit)] if pytest_available else
           [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)
    counts = junit_counts(junit) if pytest_available else None
    if not pytest_available:
        match = re.search(r'Ran (\d+) tests?', result.stderr)
        if match and result.returncode == 0:
            counts = {'tests': int(match.group(1)), 'passed': int(match.group(1)),
                      'failures': 0, 'errors': 0, 'skipped': None}
    pytest_version = (subprocess.check_output([sys.executable, '-m', 'pytest', '--version'], text=True).strip()
                      if pytest_available else None)
    payload = {'kind': 'autodoc-test-run', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
               'commit': os.environ.get('GITHUB_SHA') or subprocess.check_output(
                   ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'run_id': os.environ.get('GITHUB_RUN_ID'), 'command': cmd, 'exit_code': result.returncode,
               'counts': counts, 'tests_total': counts['tests'] if counts else None,
               'passed': counts['passed'] if counts else None,
               'failed': counts['failures'] if counts else None,
               'skipped': counts['skipped'] if counts else None,
               'errors': counts['errors'] if counts else None,
               'python_version': platform.python_version(),
               'platform': platform.platform(), 'pytest_version': pytest_version,
               'stdout_sha256': hashlib.sha256(result.stdout.encode()).hexdigest(),
               'stderr_sha256': hashlib.sha256(result.stderr.encode()).hexdigest(),
               'stdout': result.stdout, 'stderr': result.stderr,
               'output': result.stdout + result.stderr,
               'warning': 'Unsigned test-run record only; not an SBOM, provenance attestation or audit approval.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + '\n')
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
