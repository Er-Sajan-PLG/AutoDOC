"""Tests for the declared context: shorthands, validation and advisory defaults."""
import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context_module = load_module('autodoc_context', 'scripts/intelligence/context.py')


class ContextTests(unittest.TestCase):
    def test_missing_file_is_an_empty_advisory_context(self):
        context = context_module.normalise(context_module.load('/nonexistent/autodoc.toml'))
        self.assertIsNone(context['phase'])
        self.assertEqual(context_module.validate(context), [])
        enforcement = context_module.enforcement(context['phase'])
        self.assertFalse(enforcement['fail'])
        self.assertFalse(enforcement['declared'])
        self.assertIn('undeclared', enforcement['label'])

    def test_bare_reason_string_is_normalised(self):
        context = context_module.normalise({'version': 1,
                                            'not_applicable': {'DOC-A07-001': 'no personal data'}})
        self.assertEqual(context['not_applicable']['DOC-A07-001'], {'reason': 'no personal data'})
        self.assertEqual(context_module.validate(context), [])

    def test_table_reason_form_is_accepted(self):
        context = context_module.normalise({'version': 1, 'not_applicable': {
            'DOC-A07-001': {'reason': 'no personal data'}}})
        self.assertEqual(context['not_applicable']['DOC-A07-001']['reason'], 'no personal data')

    def test_empty_reason_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'reason must be non-empty'):
            context_module.normalise({'version': 1, 'not_applicable': {'DOC-A07-001': '   '}})

    def test_declared_fact_needs_a_reason(self):
        with self.assertRaisesRegex(ValueError, 'needs a reason'):
            context_module.normalise({'version': 1, 'facts': {'has_cli': True}})
        with self.assertRaisesRegex(ValueError, 'reason must be non-empty'):
            context_module.normalise({'version': 1,
                                      'facts': {'has_cli': {'value': 'true', 'reason': ''}}})

    def test_declared_fact_is_valid_with_a_reason(self):
        context = context_module.normalise({'version': 1, 'facts': {
            'has_cli': {'value': 'true', 'reason': 'documented wrapper script'}}})
        self.assertEqual(context_module.validate(context), [])
        self.assertEqual(context['facts']['has_cli']['value'], 'true')

    def test_unknown_fact_phase_kind_audience_and_severity_are_rejected(self):
        problems = context_module.validate(context_module.normalise({
            'version': 1, 'phase': 'shipping', 'kinds': ['saas'], 'audience': ['everyone'],
            'facts': {'uses_kubernetes': {'value': 'true', 'reason': 'because'}},
            'severity': {'drift': 'error', 'recommend.undetermined': 'error'}}))
        joined = ' '.join(problems)
        self.assertIn('is not a declared phase', joined)
        self.assertIn('unknown kind', joined)
        self.assertIn('unknown audience', joined)
        self.assertIn('is not a detectable fact', joined)
        self.assertIn('unknown rule', joined)
        self.assertNotIn('severity.drift', joined, 'an honoured rule accepts an override')
        self.assertIn("unknown rule 'recommend.undetermined'", joined,
                      'an unhonoured rule accepts no override')

    def test_unknown_top_level_key_is_rejected(self):
        context = context_module.normalise({'version': 1, 'recomendations': {}})
        self.assertTrue(any('unknown property' in problem
                            for problem in context_module.validate(context)))

    def test_shipped_context_is_valid_and_declares_its_phase(self):
        """The tool dogfoods its own declaration path: this repository declares `build` itself."""
        context = context_module.normalise(context_module.load(ROOT / 'autodoc.toml'))
        self.assertEqual(context_module.validate(context), [])
        self.assertEqual(context['phase'], 'build', 'the owner declared the phase; nothing infers it')
        self.assertLessEqual(date.fromisoformat(context['phase_declared']), date.today(),
                             'a phase carries the date it was declared, never a future one')
        self.assertEqual(context['obligations'], [])
        for path in context['instantiated'].values():
            self.assertTrue((ROOT / path).is_file(), path)

    def test_a_config_without_a_phase_stays_advisory(self):
        """Declaring the phase for this repository must not make an undeclared one enforceable."""
        context = context_module.normalise({'schema': 1})
        self.assertEqual(context_module.validate(context), [])
        self.assertFalse(context_module.enforcement(None)['fail'])

    def test_phase_hints_never_set_enforcement(self):
        hint = context_module.phase_hints(ROOT, {'languages': {'python': 10}})
        self.assertIn(hint['suggested'], [phase['id'] for phase in context_module.load_model()['phases']])
        self.assertIn('never sets enforcement', hint['note'])
        self.assertFalse(context_module.enforcement(None)['fail'])

    def test_every_phase_declares_enforcement(self):
        model = context_module.load_model()
        for phase in model['phases']:
            block = context_module.enforcement(phase['id'], model)
            self.assertIn(block['core'], ('error', 'warn', 'report', 'off'))
            self.assertIn('fail', block)
        self.assertTrue(context_module.enforcement('beta')['fail'])
        self.assertFalse(context_module.enforcement('build')['fail'])
        self.assertEqual(context_module.enforcement('sunset')['only'], 'sunset')


if __name__ == '__main__':
    unittest.main()
