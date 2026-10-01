"""Tests for §7: the declared event model, and the wiring it claims to describe."""
import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


triggers = load_module('autodoc_triggers', 'scripts/intelligence/triggers.py')
UNCLAIMED = ROOT / '.github/workflows/undeclared-example.yml'


class TriggerModelTests(unittest.TestCase):
    """The declaration is checked against the repository, and the check is hostile to drift."""

    def setUp(self):
        self.model = triggers.load()

    def test_the_declaration_and_the_wiring_agree(self):
        self.assertEqual(triggers.check(), [], 'the model in CONTROL/metadata/TRIGGERS.json '
                                               'must describe the workflows that exist')

    def test_every_workflow_must_be_claimed_by_a_declared_job(self):
        extra = {'name': 'undeclared', 'events': {'push': {'paths_filtered': False,
                                                           'tag_filtered': False,
                                                           'branch_filtered': False}},
                 'jobs': {'job': {'name': 'job'}}}
        errors = triggers.check(workflows_={**triggers.workflows(), UNCLAIMED: extra})
        self.assertTrue(any('no declared job claims this workflow' in error for error in errors),
                        errors)

    def test_a_required_check_may_not_be_filtered(self):
        model = copy.deepcopy(self.model)
        guard = next(job for event in model['events'] for job in event.get('jobs', [])
                     if job.get('required'))
        guard['paths_filtered'] = True
        errors = triggers.check(model)
        self.assertTrue(any('required check may not be paths_filtered' in error for error in errors),
                        errors)

    def test_a_declared_command_must_resolve(self):
        model = copy.deepcopy(self.model)
        model['events'][1]['jobs'][0]['commands'] = ['python scripts/doc-control/not-a-script.py']
        errors = triggers.check(model)
        self.assertTrue(any('no such path' in error for error in errors), errors)

    def test_a_network_event_must_state_its_rate_limit_and_may_not_block(self):
        model = copy.deepcopy(self.model)
        scheduled = next(event for event in model['events'] if event['id'] == 'scheduled')
        scheduled['rate_limit'] = None
        self.assertTrue(any('must state its rate limit' in error for error in triggers.check(model)))
        model = copy.deepcopy(self.model)
        scheduled = next(event for event in model['events'] if event['id'] == 'scheduled')
        scheduled['blocking'] = True
        errors = triggers.check(model)
        self.assertTrue(any('blocking event may not need the network' in error for error in errors),
                        errors)

    def test_a_job_name_mismatch_is_reported(self):
        model = copy.deepcopy(self.model)
        guard = next(job for event in model['events'] for job in event.get('jobs', [])
                     if job.get('required'))
        guard['name'] = guard['name'] + ' '
        errors = triggers.check(model)
        self.assertTrue(any('workflow names it' in error for error in errors), errors)

    def test_a_workflow_the_reader_cannot_parse_is_unverified_not_passed(self):
        errors = triggers.check(workflows_={path: None for path in triggers.workflows()})
        self.assertTrue(all('could not be read' in error or 'no declared job claims' in error
                            for error in errors), errors)
        self.assertTrue(errors)

    def test_exactly_one_gate_and_one_required_check(self):
        model = copy.deepcopy(self.model)
        gate = next(event for event in model['events'] if event['id'] == 'pull_request')
        gate['blocking'] = False
        next(job for event in model['events'] for job in event.get('jobs', [])
             if job.get('required'))['required'] = False
        errors = triggers.check(model)
        self.assertTrue(any('exactly one blocking event' in error for error in errors), errors)
        self.assertTrue(any('exactly one required check' in error for error in errors), errors)


class TriggerViewTests(unittest.TestCase):
    """The printed view is the same implementation the generated reference uses."""

    def test_phase_rows_state_the_declared_phase_and_where_each_severity_came_from(self):
        rows = triggers.phase_rows()
        self.assertEqual(rows['phase'], 'build')
        by_family = {row['family']: row for row in rows['rows']}
        self.assertEqual(by_family['stubs']['severity'], 'warn')
        self.assertIn('autodoc.toml', by_family['stubs']['source'])
        self.assertEqual(by_family['drift']['severity'], 'off')
        self.assertIn('phase default', by_family['drift']['source'],
                      'a family with no override is attributed to the phase')

    def test_the_view_states_the_gate_the_network_limits_and_the_reader_limits(self):
        text = triggers.render()
        self.assertIn('blocks the merge', text)
        self.assertIn('make ci', text)
        self.assertIn('one request per host every 1.0s, at most 200 links per run, '
                      '10s timeout per request', text)
        self.assertIn('never passed', text, 'an unreadable workflow is unverified, not fine')
        self.assertIn('## Never', text)

    def test_the_cli_exits_two_on_a_model_that_does_not_match_the_wiring(self):
        model = triggers.load()
        next(job for event in model['events'] for job in event.get('jobs', [])
             if job.get('required'))['commands'] = ['python scripts/nope.py']
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'TRIGGERS.json'
            path.write_text(json.dumps(model), encoding='utf-8')
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = triggers.main(['--check', '--model', str(path)])
        self.assertEqual(code, 2, buffer.getvalue())
        self.assertIn('no such path', buffer.getvalue())
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertEqual(triggers.main(['--check']), 0)
        self.assertIn('Triggers valid', buffer.getvalue())


class TriggerExitCodeTests(unittest.TestCase):
    """A configuration problem is 2 and a crash is 3; neither may wear the mask of a finding."""

    def test_a_bad_model_is_a_configuration_error(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = triggers.cli(['--check', '--model', str(ROOT / 'CONTROL')])
        self.assertEqual(code, 2, buffer.getvalue())

    def test_a_crash_is_a_tool_failure(self):
        stderr = io.StringIO()
        with mock.patch.object(triggers, 'check', side_effect=RuntimeError('boom')):
            with contextlib.redirect_stderr(stderr):
                code = triggers.cli(['--check'])
        self.assertEqual(code, 3)
        self.assertIn('not a finding about this repository', stderr.getvalue())


class GeneratedReferenceTests(unittest.TestCase):
    """The committed reference is one of the mapped, labeled generated documents."""

    def test_the_trigger_reference_is_generated_and_labeled(self):
        text = (ROOT / 'docs/generated/TRIGGER-REFERENCE.md').read_text(encoding='utf-8')
        self.assertIn('GENERATOR: triggers | EXACTNESS: exact |', text.splitlines()[0])
        self.assertIn('DOC-TRG-001', text)
        body = triggers.render(title=False)
        self.assertIn(body.splitlines()[0][:80], text, 'the file is the rendered view, not a copy')

    def test_the_reference_is_the_only_generated_copy_of_the_model(self):
        mapped = [entry for entry in load_module('autodoc_engine', 'scripts/doc-sync/engine.py')
                  .load_map()['generated'] if entry['id'] == 'triggers']
        self.assertEqual(len(mapped), 1)
        self.assertEqual(mapped[0]['target'], 'docs/generated/TRIGGER-REFERENCE.md')
        self.assertIn('CONTROL/metadata/TRIGGERS.json', mapped[0]['sources'])


if __name__ == '__main__':
    unittest.main()
