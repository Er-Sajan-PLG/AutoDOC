"""Tests for §7: the one network-touching check is scheduled, rate-limited and warn-only."""
import importlib.util
import io
import subprocess
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


links = load_module('autodoc_external_links', 'scripts/doc-control/check_external_links.py')
triggers = load_module('autodoc_triggers_for_links', 'scripts/intelligence/triggers.py')


def document(text, folder=None):
    folder = folder or tempfile.mkdtemp()
    path = Path(folder) / 'SAMPLE.md'
    path.write_text(text, encoding='utf-8')
    return path


class ExtractionTests(unittest.TestCase):
    """Line-based extraction states its limits by what it does with each shape."""

    def test_prose_links_are_read_and_fenced_code_is_not(self):
        path = document('See https://docs.python.org/3/ for the parser.\n'
                        '```\ncurl https://never-checked.invalid/example\n```\n'
                        'Done.\n')
        found = links.extract(path.read_text())
        self.assertEqual([url for _, url in found], ['https://docs.python.org/3/'])

    def test_trailing_punctuation_is_stripped_and_duplicates_keep_their_first_home(self):
        path = document('First https://docs.python.org/3/ then https://docs.python.org/3/, again\n')
        entries = links.targets([path])
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['line'], 1)

    def test_local_and_example_hosts_are_placeholders_not_dependencies(self):
        path = document('Local http://localhost:8000/health and sample https://example.com/docs\n'
                        'Real https://docs.python.org/3/\n')
        kept, skipped = links.checkable(links.targets([path]))
        self.assertEqual([entry['url'] for entry in kept], ['https://docs.python.org/3/'])
        self.assertEqual(len(skipped), 2)
        self.assertIn('documented not deployed', skipped[0]['reason'])

    def test_classification_keeps_the_four_honest_buckets(self):
        self.assertEqual([links.classify(status) for status in (200, 302, 401, 429, 404, 410, 500)],
                         ['ok', 'ok', 'restricted', 'restricted', 'missing', 'missing', 'error'])


class RateLimitTests(unittest.TestCase):
    """The declared limits are enforced, and the wait is visible in the result."""

    def test_requests_to_one_host_are_spaced_by_the_declared_delay(self):
        entries = [{'url': url, 'file': 'x.md', 'line': 1} for url in
                   ('https://a.example.org/one', 'https://a.example.org/two',
                    'https://b.example.org/one')]
        state, sleeps = {'t': 0.0}, []

        def clock():
            return state['t']

        def sleep(seconds):
            sleeps.append(round(seconds, 3))
            state['t'] += seconds

        results = links.check_links(entries, probe_=lambda url, timeout: (200, None), delay=1.0,
                                    clock=clock, sleep=sleep)
        self.assertEqual(sleeps, [1.0], 'only the second request to the same host waits')
        self.assertEqual([item['waited_seconds'] for item in results], [0.0, 1.0, 0.0])
        self.assertEqual({item['result'] for item in results}, {'ok'})

    def test_the_cap_stops_the_run_and_the_report_says_so(self):
        entries = [{'url': f'https://host{i}.example.org/', 'file': 'x.md', 'line': i}
                   for i in range(5)]
        results = links.check_links(entries, probe_=lambda url, timeout: (200, None), max_links=2)
        self.assertEqual(len(results), 2)
        report = links.report(entries, results, {'templates': 0, 'placeholders': 0}, 1.0, 2, 10)
        self.assertIn('2 of 5 link(s)', report)
        self.assertIn('not checked this run because of the cap', report)

    def test_placeholders_are_reported_separately(self):
        entries = links.targets([document('http://localhost:8000/health\n')])
        kept, skipped = links.checkable(entries)
        report = links.report(kept, [], {'templates': 5, 'placeholders': len(skipped)}, 1.0, 200, 10)
        self.assertIn('Skipped 1 local or example URL(s)', report)
        self.assertIn('5 template file(s)', report)


class ProbeTests(unittest.TestCase):
    """HEAD first, GET only when the host refuses HEAD; the status decides, not optimism."""

    def test_a_host_that_refuses_head_is_asked_again_with_get(self):
        calls = []

        def fake_urlopen(request, timeout):
            calls.append(request.get_method())
            if request.get_method() == 'HEAD':
                raise urllib.error.HTTPError(request.full_url, 405, 'no HEAD', {}, None)
            probe_response = mock.MagicMock()
            probe_response.__enter__.return_value.status = 200
            return probe_response

        with mock.patch('urllib.request.urlopen', fake_urlopen):
            self.assertEqual(links.probe('https://docs.python.org/3/'), (200, None))
        self.assertEqual(calls, ['HEAD', 'GET'])

    def test_a_missing_page_is_not_retried(self):
        calls = []

        def fake_urlopen(request, timeout):
            calls.append(request.get_method())
            raise urllib.error.HTTPError(request.full_url, 404, 'gone', {}, None)

        with mock.patch('urllib.request.urlopen', fake_urlopen):
            self.assertEqual(links.probe('https://docs.python.org/gone'), (404, None))
        self.assertEqual(calls, ['HEAD'])

    def test_a_transport_failure_is_an_error_with_its_message(self):
        def fake_urlopen(request, timeout):
            raise OSError('connection refused')

        with mock.patch('urllib.request.urlopen', fake_urlopen):
            status, error = links.probe('https://docs.python.org/3/')
        self.assertIsNone(status)
        self.assertIn('connection refused', error)


class CliTests(unittest.TestCase):
    """Warn-only by default, strict only when an owner asks, and never part of the gate."""

    def test_defaults_are_the_declared_rate_limit(self):
        declared = None
        for event in triggers.load()['events']:
            if isinstance(event.get('rate_limit'), dict):
                declared = event['rate_limit']
        self.assertEqual(links.model_defaults(), declared)
        self.assertEqual(declared, {'per_host_seconds': 1.0, 'max_links': 200,
                                    'timeout_seconds': 10})

    def test_list_mode_never_opens_the_network(self):
        def exploding_probe(url, timeout):
            raise AssertionError('--list must not touch the network')

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = links.main(['--list'], probe_=exploding_probe,
                              documents=[document('See https://docs.python.org/3/\n')])
        self.assertEqual(code, 0)
        self.assertIn('https://docs.python.org/3/', buffer.getvalue())

    def test_broken_links_warn_by_default_and_fail_only_with_strict(self):
        document_path = document('See https://docs.python.org/missing\n')
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertEqual(links.main([], probe_=lambda url, timeout: (404, None),
                                        documents=[document_path]), 0)
        self.assertIn('missing', buffer.getvalue())
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertEqual(links.main(['--strict'], probe_=lambda url, timeout: (404, None),
                                        documents=[document_path]), 1)

    def test_a_crash_is_a_tool_failure_not_a_finding(self):
        import contextlib
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = links.cli([], probe_=lambda url, timeout: 1 / 0,
                             documents=[document('See https://docs.python.org/3/\n')])
        self.assertEqual(code, 3)
        self.assertIn('not a finding about this repository', stderr.getvalue())

    def test_the_gate_never_runs_the_network_check(self):
        plan = subprocess.run(['make', '-n', 'ci'], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout
        self.assertNotIn('check_external_links', plan,
                         'a third-party host may never fail a pull request')

    def test_the_scheduled_workflow_runs_every_check_and_then_summarises(self):
        text = (ROOT / '.github/workflows/docs-staleness.yml').read_text(encoding='utf-8')
        self.assertIn('check_external_links.py', text)
        self.assertGreaterEqual(text.count('continue-on-error: true'), 5,
                                'every scheduled check reports even if an earlier one fails')
        self.assertIn('Summarise the triage run', text)
        self.assertIn('exit 1', text, 'the run goes red for triage, in one place, at the end')


if __name__ == '__main__':
    unittest.main()
