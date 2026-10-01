"""The enforcement contract: golden fixture cases, exit codes and the branch-protection gate.

Two layers:

* `GoldenMatrixTests` replays `tests/fixtures/enforcement/cases.json`. The four collector
  modules are patched so each case is deterministic — the point is the policy layer (severity
  resolution, baseline, exit codes, report wording), not the checkers, which have their own tests.
* `FailureContractTests` runs the real entry points in a subprocess: usage errors exit 2, an
  internal crash exits 3 and never 1, both entry points agree, `--fail-on-stale` is opt-in, and
  the branch-protection script is dry-run by default and cannot change anything with a broken gh.

`GateTests` checks the CI check name and that the required job cannot be skipped.
"""
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / 'tests/fixtures/enforcement/cases.json').read_text(encoding='utf-8'))
ENFORCE = ROOT / 'scripts/intelligence/enforce.py'
REQUIRE_CHECK = ROOT / 'scripts/doc-control/require-docs-check.py'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


enforce = load_module('contract_enforce', ENFORCE)
context_module = load_module('contract_context', ROOT / 'scripts/intelligence/context.py')


def fake_collect(checks):
    """A drop-in for enforce.collect_findings: raw checks in, policy-resolved findings out."""
    def collect(profile_document, context, documents, groups, enforcement, root=None):
        findings = []
        off = [family for family in context_module.CHECK_FAMILIES
               if context_module.check_severity(context, family)[0] == 'off']
        for raw in checks:
            severity, source = context_module.check_severity(context, raw['rule'])
            if severity == 'off':
                if raw['rule'] not in off:
                    off.append(raw['rule'])
                continue
            findings.append({'kind': 'check', 'rule': raw['rule'], 'severity': severity,
                             'location': raw['location'], 'detail': raw['detail'],
                             'message': f"{raw['location']}: {raw['detail']}",
                             'fix': 'fix the finding', 'because': f'{raw["rule"]} check under {source}'})
        return findings, sorted(off)
    return collect


class GoldenMatrixTests(unittest.TestCase):
    def run_case(self, case):
        """Return (exit code, JSON document, markdown text) for one fixture case."""
        checks = case.get('checks', [])
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / 'autodoc.toml').write_text(case['config'], encoding='utf-8')
            (repo / 'README.md').write_text('# fixture\n', encoding='utf-8')
            baseline = repo / 'autodoc-baseline.json'
            entries = [{'key': enforce.key_of(raw), 'rule': raw['rule'],
                        'location': raw['location'], 'detail': raw['detail'],
                        'recorded_at': raw.get('recorded_at')}
                       for raw in case.get('baseline', [])]
            baseline.write_text(json.dumps({'schema': 1, 'recorded_at': None, 'phase': 'build',
                                            'entries': entries}), encoding='utf-8')
            args = type('Args', (), {'repo': repo, 'config': repo / 'autodoc.toml',
                                     'baseline': baseline, 'write_baseline': False,
                                     'fail_on_stale': case.get('fail_on_stale', False),
                                     'json': True, 'output': None})()
            with mock.patch.object(enforce, 'collect_findings', fake_collect(checks)), \
                    mock.patch.object(enforce.recommend, 'findings', lambda *a, **k: []), \
                    mock.patch.object(enforce.recommend, 'score',
                                      lambda *a, **k: {'readiness': 'fixture'}), \
                    mock.patch.object(enforce.recommend, 'catalog', lambda: []), \
                    mock.patch.object(enforce.recommend, 'evaluate',
                                      lambda *a, **k: {key: [] for key in (
                                          'required', 'recommended', 'contextual', 'reported',
                                          'undetermined', 'assess', 'not_applicable',
                                          'acknowledged', 'off')}):
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    code = enforce.run(args)
                document = json.loads(out.getvalue())
                args.json = False
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    text_code = enforce.run(args)
        return code, text_code, document, out.getvalue(), err.getvalue()

    def test_every_case_matches_its_golden_expectation(self):
        for case in CASES['cases']:
            with self.subTest(case=case['id']):
                expect = case['expect']
                code, text_code, document, text, errors = self.run_case(case)
                self.assertEqual(code, expect['exit'], f"{case['why']}\n{text}")
                self.assertEqual(text_code, code, 'the same run must agree in both renderings')
                for key, field in (('suppressed', 'suppressed'), ('stale', 'stale_baseline')):
                    if key in expect:
                        self.assertEqual(len(document[field]), expect[key],
                                         f"{case['id']}: {key} count")
                for needle in expect.get('report_contains', []):
                    self.assertIn(needle, text, f"{case['id']}: report must contain")
                for needle in expect.get('report_not_contains', []):
                    self.assertNotIn(needle, text, f"{case['id']}: report must not contain")
                for expected in expect.get('findings_contain', []):
                    self.assertTrue(
                        any(finding['rule'] == expected['rule']
                            and finding['severity'] == expected['severity']
                            for finding in document['findings']),
                        f"{case['id']}: JSON findings lack {expected}")

    def test_the_matrix_covers_the_review_contract(self):
        """The fixture list itself is a deliverable: keep the promised cases present."""
        promised = {
            'undeclared-advisory-no-pins', 'undeclared-pinned-check-violated',
            'pin-stricter-than-phase-block', 'pin-weaker-than-phase-block',
            'baseline-does-not-hide-other-rule', 'baseline-does-not-hide-other-location',
            'baseline-fingerprint-distinguishes-a-different-problem',
            'finding-fixed-after-baselining', 'entry-deleted-makes-the-finding-return',
            'recorded-entry-suppresses-and-reports-its-age',
            'security-findings-are-never-baselined',
            'build-fails-structural-breakage-off-drift', 'live-mature-fail-drift-and-freshness',
            'sunset-shrinks-to-its-profile'}
        self.assertEqual(promised - {case['id'] for case in CASES['cases']}, set())


class FailureContractTests(unittest.TestCase):
    def run_enforce(self, repo, *args):
        return subprocess.run([sys.executable, str(ENFORCE), '--repo', str(repo), *args],
                              cwd=ROOT, capture_output=True, text=True)

    def test_usage_errors_exit_two(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / 'autodoc.toml').write_text('schema = 1\n\n[severity]\nteleports = "error"\n',
                                               encoding='utf-8')
            result = self.run_enforce(repo, '--json')
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('not a known rule', result.stderr)
            (repo / 'autodoc.toml').write_text('schema = 1\n', encoding='utf-8')
            (repo / 'autodoc-baseline.json').write_text('{"schema": 1, "entries": "nope"}',
                                                        encoding='utf-8')
            result = self.run_enforce(repo, '--json')
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('baseline', result.stderr.lower())

    def test_forced_internal_crash_exits_three_and_never_one(self):
        script = (
            'import importlib.util, sys\n'
            f'spec = importlib.util.spec_from_file_location("enforce", {str(ENFORCE)!r})\n'
            'module = importlib.util.module_from_spec(spec)\n'
            'spec.loader.exec_module(module)\n'
            'def boom(args):\n'
            '    raise RuntimeError("forced crash")\n'
            'module.build = boom\n'
            'sys.argv = ["enforce.py", "--json", "--repo", "."]\n'
            'print("exit", module.main())\n')
        result = subprocess.run([sys.executable, '-c', script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertIn('exit 3', result.stdout, result.stderr)
        self.assertIn('Internal error: RuntimeError: forced crash', result.stderr)
        self.assertIn('tool failure, not a finding', result.stderr)

    def test_both_entry_points_return_the_same_exit_code(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / 'autodoc.toml').write_text('schema = 1\nphase = "build"\n', encoding='utf-8')
            (repo / 'README.md').write_text('# fixture\n', encoding='utf-8')
            (repo / 'docs').mkdir()
            (repo / 'docs/a.md').write_text('See [the missing file](missing.md).\n', encoding='utf-8')
            result = self.run_enforce(repo)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('[error] links.local', result.stderr)
            from_script = result.returncode
            argv = sys.argv
            try:
                sys.argv = ['enforce.py', '--repo', str(repo)]
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    in_process = enforce.main()
            finally:
                sys.argv = argv
        self.assertEqual(in_process, from_script,
                         f'in-process main() said {in_process}, the script said {from_script}')

    def test_fail_on_stale_is_opt_in(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / 'autodoc.toml').write_text('schema = 1\nphase = "build"\n', encoding='utf-8')
            stale = enforce.key_of({'rule': 'links.local', 'location': 'docs/x.md',
                                    'detail': 'broken local link old.md'})
            (repo / 'autodoc-baseline.json').write_text(json.dumps(
                {'schema': 1, 'recorded_at': '2026-09-01', 'phase': 'build',
                 'entries': [{'key': stale, 'rule': 'links.local', 'location': 'docs/x.md',
                              'detail': 'broken local link old.md',
                              'recorded_at': '2026-09-01'}]}), encoding='utf-8')
            lenient = self.run_enforce(repo, '--json')
            self.assertEqual(lenient.returncode, 0, lenient.stdout + lenient.stderr)
            self.assertIn('WARNING: 1 baseline entr(ies)', lenient.stderr)
            strict = self.run_enforce(repo, '--json', '--fail-on-stale')
            self.assertEqual(strict.returncode, 1, strict.stdout + strict.stderr)

    def test_apply_without_owner_rights_changes_nothing(self):
        """`--apply` with a gh that cannot resolve the repo must fail before any API write."""
        with tempfile.TemporaryDirectory() as folder:
            fake_bin = Path(folder) / 'bin'
            fake_bin.mkdir()
            log = Path(folder) / 'gh.log'
            gh = fake_bin / 'gh'
            gh.write_text(f'#!/bin/sh\necho "$@" >> {log}\nexit 1\n', encoding='utf-8')
            gh.chmod(0o755)
            env = {**os.environ, 'PATH': f'{fake_bin}{os.pathsep}{os.environ["PATH"]}'}
            apply = subprocess.run([sys.executable, str(REQUIRE_CHECK), '--apply'], cwd=ROOT,
                                   capture_output=True, text=True, env=env)
            self.assertEqual(apply.returncode, 2, apply.stdout + apply.stderr)
            self.assertIn('Nothing was changed.', apply.stderr)
            calls = log.read_text() if log.exists() else ''
            self.assertNotIn('api -X PUT', calls, 'no write may be attempted without rights')
            dry = subprocess.run([sys.executable, str(REQUIRE_CHECK)], cwd=ROOT,
                                 capture_output=True, text=True, env=env)
            self.assertEqual(dry.returncode, 2, 'the dry run needs gh too; it must not write')
            self.assertNotIn('api -X PUT', log.read_text())


class BaselineKeyTests(unittest.TestCase):
    def test_the_key_survives_reordering_above_the_finding(self):
        """Line numbers are not part of identity: inserting text above must not look like a fix."""
        finding = {'rule': 'links.local', 'location': 'docs/a.md',
                   'detail': 'broken local link missing.md'}
        before = enforce.key_of(finding)
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / 'docs').mkdir()
            (repo / 'autodoc.toml').write_text('schema = 1\nphase = "build"\n', encoding='utf-8')
            (repo / 'docs/a.md').write_text('See [x](missing.md).\n', encoding='utf-8')
            (repo / 'docs/a.md').write_text('# title\n\n' * 20 + 'See [x](missing.md).\n',
                                            encoding='utf-8')
            result = subprocess.run([sys.executable, str(ENFORCE), '--repo', str(repo), '--json'],
                                    cwd=ROOT, capture_output=True, text=True)
            document = json.loads(result.stdout)
        found = [item for item in document['findings'] if item['rule'] == 'links.local']
        self.assertEqual(len(found), 1, result.stderr)
        self.assertEqual(enforce.key_of({**finding, 'detail': found[0]['detail']}), before)
        self.assertFalse(Path(found[0]['location']).is_absolute(),
                         'a location must not encode where the checkout lives')

    def test_the_key_distinguishes_two_problems_at_one_location(self):
        first = enforce.key_of({'rule': 'links.local', 'location': 'docs/a.md',
                                'detail': 'broken local link one.md'})
        second = enforce.key_of({'rule': 'links.local', 'location': 'docs/a.md',
                                 'detail': 'broken local link two.md'})
        self.assertNotEqual(first, second)


class AdvisoryDecisionTests(unittest.TestCase):
    def test_a_decision_without_owner_or_review_date_is_reported_not_rejected(self):
        context = context_module.normalise({'schema': 1, 'phase': 'build',
                                            'not_applicable': {'DEV-B01-001': 'not needed yet'}})
        self.assertEqual(context_module.validate(context), [])
        recommend = load_module('contract_recommend', ROOT / 'scripts/intelligence/recommend.py')
        enforcement = context_module.enforcement('build')
        documents = recommend.catalog()
        profile = load_module('contract_profile',
                              ROOT / 'scripts/intelligence/profile.py').profile(
            ROOT, context['facts'])
        groups = recommend.evaluate(documents, profile, context, enforcement)
        decisions = [finding for finding in recommend.findings(documents, context, groups,
                                                               enforcement)
                     if finding['rule'] == 'recommend.decision']
        self.assertEqual([finding['location'] for finding in decisions], ['DEV-B01-001'])
        self.assertEqual(decisions[0]['severity'], 'report', 'advice, never a failure')
        self.assertIn('owner', decisions[0]['fix'])

    def test_an_owned_decision_needs_no_nudge_and_a_bad_date_is_an_error(self):
        context = context_module.normalise({
            'schema': 1, 'phase': 'build',
            'not_applicable': {'DEV-B01-001': {'reason': 'not needed yet',
                                               'owner': '@owner', 'review': '2027-01-01'}}})
        self.assertEqual(context_module.validate(context), [])
        self.assertEqual(context['not_applicable']['DEV-B01-001']['owner'], '@owner')
        broken = context_module.normalise({'schema': 1, 'phase': 'build',
                                           'not_applicable': {'DEV-B01-001': {
                                               'reason': 'x', 'review': 'soon'}}})
        self.assertIn('not an ISO date', '; '.join(context_module.validate(broken)))


class GateTests(unittest.TestCase):
    WORKFLOW = ROOT / '.github/workflows/docs-guard.yml'

    def test_the_payload_uses_the_exact_check_name_the_workflow_emits(self):
        require = load_module('require_check', REQUIRE_CHECK)
        workflow = self.WORKFLOW.read_text(encoding='utf-8')
        # GitHub matches a required check by the job's name (the UI shows "workflow / job").
        self.assertIn(f'name: {require.CHECK_NAME}\n', workflow,
                      'the job name is the check context; the payload must use the same string')
        self.assertEqual(require.payload()['contexts'], [require.CHECK_NAME])

    def test_the_required_job_cannot_be_skipped(self):
        workflow = self.WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('  pull_request:', workflow, 'the gate must run on pull requests')
        for line in workflow.splitlines():
            if line.strip().startswith('paths') or line.strip().startswith('paths-ignore'):
                self.fail('a path filter would let the required check be skipped')
        gate = workflow.split('jobs:', 1)[1]
        self.assertNotIn('\n    if:', gate,
                         'a job-level condition must not be able to skip the required check')


if __name__ == '__main__':
    unittest.main()
