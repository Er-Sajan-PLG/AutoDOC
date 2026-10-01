"""Enforcement policy: phase-scaled severity, precedence, baseline, and exit codes.

The policy is data (`CONTROL/metadata/CONTEXT-MODEL.json` plus `[severity]`), so these tests
exercise the resolution order rather than hard-coding one phase's numbers.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context_module = load_module('enforce_context', 'scripts/intelligence/context.py')
enforce = load_module('autodoc_enforce', 'scripts/intelligence/enforce.py')

BASE_CONFIG = {'version': 1, 'phase': 'beta', 'audience': [], 'kinds': [], 'obligations': []}


def context_for(phase=None, severity=None, phase_declared=None):
    return context_module.normalise({**BASE_CONFIG, 'phase': phase,
                                     'severity': severity or {}, 'phase_declared': phase_declared})


class SeverityResolutionTests(unittest.TestCase):
    def test_phase_defaults_scale_with_declared_phase(self):
        """The guide's table: drift and freshness are off until beta, warn at beta, fail after."""
        advisory = context_for(None)
        build, beta, live = context_for('build'), context_for('beta'), context_for('live')
        self.assertEqual(context_module.check_severity(advisory, 'drift')[0], 'off')
        self.assertEqual(context_module.check_severity(build, 'drift')[0], 'off')
        self.assertEqual(context_module.check_severity(beta, 'drift')[0], 'warn')
        self.assertEqual(context_module.check_severity(live, 'drift')[0], 'error')
        self.assertEqual(context_module.check_severity(build, 'links.local')[0], 'error',
                         'broken links are structural breakage even while the rest only warns')
        self.assertEqual(context_module.check_severity(build, 'placeholders')[0], 'error')
        self.assertEqual(context_module.check_severity(advisory, 'placeholders')[0], 'report',
                         'a prototype may be unfinished; structure is only reported there')
        self.assertEqual(context_module.check_severity(beta, 'freshness.review')[0], 'warn')
        self.assertEqual(context_module.check_severity(live, 'freshness.review')[0], 'error')
        self.assertEqual(context_module.check_severity(context_for('sunset'), 'stubs')[0], 'off')

    def test_config_override_wins_and_says_where_it_came_from(self):
        severity, source = context_module.check_severity(context_for('beta', {'drift': 'off'}), 'drift')
        self.assertEqual(severity, 'off')
        self.assertIn('autodoc.toml', source)

    def test_undeclared_phase_is_never_stronger_than_report(self):
        context = context_for(None)
        for family in context_module.CHECK_FAMILIES:
            with self.subTest(family):
                self.assertIn(context_module.check_severity(context, family)[0], ('off', 'report'),
                              'an undeclared phase never warns and never fails')

    def test_model_is_valid_and_every_family_is_declared_for_every_block(self):
        self.assertEqual(context_module.validate_model(), [])
        model = context_module.load_model()
        for name, block in model['enforcement'].items():
            with self.subTest(name):
                self.assertEqual(sorted(block['checks']), sorted(context_module.CHECK_FAMILIES))

    def test_an_unlisted_family_or_severity_is_rejected(self):
        model = context_module.load_model()
        broken = json.loads(json.dumps(model))
        broken['enforcement']['strict']['checks']['teleports'] = 'error'
        broken['enforcement']['strict']['checks']['drift'] = 'shout'
        problems = ' '.join(context_module.validate_model(broken))
        self.assertIn('unknown family', problems)
        self.assertIn('is not a severity', problems)

    def test_phase_age_is_shown_and_flags_an_old_declaration(self):
        from datetime import date
        fresh = context_module.phase_age(context_for('beta', phase_declared='2026-09-01'),
                                         today=date(2026, 10, 1))
        old = context_module.phase_age(context_for('beta', phase_declared='2024-01-01'),
                                       today=date(2026, 10, 1))
        self.assertEqual(fresh['days'], 30)
        self.assertFalse(fresh['review'])
        self.assertTrue(old['review'])
        self.assertIsNone(context_module.phase_age(context_for(None)))

    def test_phase_declared_needs_a_real_date_and_a_phase(self):
        problems = ' '.join(context_module.validate(context_for(None, phase_declared='2026-13-99')))
        self.assertIn('is not an ISO date', problems)
        self.assertIn('needs a declared phase', problems)

    def test_schema_alias_and_the_renamed_declaration(self):
        context = context_module.normalise({'schema': 1, 'phase': 'beta'})
        self.assertEqual(context['version'], 1)
        with self.assertRaisesRegex(ValueError, 'contradicts'):
            context_module.normalise({'schema': 1, 'version': 2})
        with self.assertRaisesRegex(ValueError, 'renamed to phase_declared'):
            context_module.normalise({'version': 1, 'declared_on': '2026-01-01'})


class BaselineTests(unittest.TestCase):
    def finding(self, rule='drift', location='docs/META/OUTLINE.md'):
        return {'kind': 'check', 'rule': rule, 'location': location, 'detail': 'stale',
                'severity': 'error', 'fix': 'run make docs:generate', 'because': 'drift check'}

    def test_recorded_findings_suppress_and_new_ones_do_not(self):
        baseline = {'schema': 1, 'entries': [{'key': enforce.key_of(self.finding()), 'rule': 'drift',
                                              'location': 'docs/META/OUTLINE.md'}]}
        kept, suppressed, stale = enforce.apply_baseline(
            [self.finding(), self.finding(location='docs/META/CODE-INVENTORY.md')], baseline)
        self.assertEqual([item['location'] for item in kept], ['docs/META/CODE-INVENTORY.md'])
        self.assertEqual(len(suppressed), 1)
        self.assertEqual(stale, [])

    def test_entry_that_no_longer_matches_is_stale_not_silence(self):
        baseline = {'schema': 1, 'entries': [{'key': 'drift|docs/META/GONE.md', 'rule': 'drift',
                                              'location': 'docs/META/GONE.md'}]}
        kept, suppressed, stale = enforce.apply_baseline([], baseline)
        self.assertEqual((kept, suppressed), ([], []))
        self.assertEqual(stale[0]['key'], 'drift|docs/META/GONE.md')

    def test_a_suppression_never_hides_a_different_rule_at_the_same_location(self):
        baseline = {'schema': 1, 'entries': [{'key': 'stubs|README.md'}]}
        kept, suppressed, _ = enforce.apply_baseline([self.finding(location='README.md')], baseline)
        self.assertEqual(suppressed, [], 'only the recorded rule is suppressed')
        self.assertEqual(len(kept), 1)

    def test_write_and_read_round_trip_is_machine_json(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / 'autodoc-baseline.json'
            enforce.write_baseline(path, [self.finding()], 'beta', today=None)
            data = json.loads(path.read_text())
            self.assertEqual(data['schema'], 1)
            self.assertEqual(data['phase'], 'beta')
            self.assertEqual(data['entries'][0]['key'], enforce.key_of(self.finding()))
            self.assertEqual(enforce.load_baseline(path)['entries'][0]['rule'], 'drift')

    def test_malformed_baseline_is_a_usage_error(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / 'autodoc-baseline.json'
            path.write_text('{"schema": 99, "entries": []}')
            with self.assertRaisesRegex(ValueError, 'expected schema 1'):
                enforce.load_baseline(path)
            path.write_text('{"schema": 1, "entries": ["drift"]}')
            with self.assertRaisesRegex(ValueError, 'list of objects'):
                enforce.load_baseline(path)
        self.assertEqual(enforce.load_baseline(Path('/nonexistent/baseline.json'))['entries'], [])

    def test_summarize_maps_findings_to_documented_exit_codes(self):
        enforcement = context_module.enforcement('beta')
        error = {'kind': 'check', 'severity': 'error'}
        report = {'kind': 'check', 'severity': 'report'}
        config = {'kind': 'config', 'severity': 'error'}
        self.assertEqual(enforce.summarize([report], [], [], enforcement)['exit_code'], 0)
        self.assertEqual(enforce.summarize([error], [], [], enforcement)['exit_code'], 1)
        self.assertEqual(enforce.summarize([config], [], [], enforcement)['exit_code'], 2)
        self.assertEqual(enforce.summarize([], [error], [], enforcement)['exit_code'], 0,
                         'suppressed findings never fail the run')


class EndToEndTests(unittest.TestCase):
    """The shipped repository is advisory: the phase is undeclared and the pins hold its gates."""

    def build(self, config, baseline):
        args = type('Args', (), {'repo': ROOT, 'config': config, 'baseline': baseline})()
        return enforce.build(args)

    def test_phase_table_matches_the_guide(self):
        """The four columns of the guide's enforcement table, read from the model as data."""
        model = context_module.load_model()
        blocks = {name: block['checks'] for name, block in model['enforcement'].items()}
        by_phase = {phase['id']: phase['enforcement'] for phase in model['phases']}
        for phase in ('idea', 'prototype'):
            self.assertEqual(by_phase[phase], 'advisory')
            self.assertEqual(blocks['advisory']['drift'], 'off')
            self.assertEqual(blocks['advisory']['placeholders'], 'report')
        self.assertEqual(by_phase['build'], 'warn')
        self.assertEqual(blocks['warn']['drift'], 'off')
        self.assertEqual(blocks['warn']['freshness.review'], 'off')
        self.assertEqual(blocks['warn']['placeholders'], 'error')
        self.assertEqual(model['enforcement']['warn']['core'], 'warn')
        self.assertEqual(by_phase['beta'], 'strict')
        self.assertEqual((blocks['strict']['drift'], blocks['strict']['freshness.critical']),
                         ('warn', 'warn'))
        for phase in ('live', 'mature'):
            self.assertEqual(by_phase[phase], 'full')
            self.assertEqual((blocks['full']['drift'], blocks['full']['freshness.critical']),
                             ('error', 'error'))
        self.assertEqual(by_phase['sunset'], 'sunset')
        for family, severity in blocks['sunset'].items():
            self.assertEqual(severity, 'off', f'sunset shrinks: {family}')

    def test_off_families_are_named_not_silently_skipped(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            config = Path(folder) / 'autodoc.toml'
            config.write_text('schema = 1\nphase = "build"\n')
            data, findings, _, _, _, summary = self.build(config, Path(folder) / 'none.json')
        self.assertIn('drift', data['off_families'])
        self.assertIn('freshness.critical', data['off_families'])
        self.assertIn('freshness.review', data['off_families'])
        self.assertFalse(any(finding['rule'] == 'drift' for finding in findings),
                         'an off family emits nothing')
        text = enforce.report(data, findings, [], [], data['enforcement'], summary['exit_code'])
        self.assertIn('Off at this phase', text)

    def test_informational_findings_never_fail_the_run(self):
        data, findings, _, _, _, summary = self.build(
            ROOT / 'autodoc.toml', ROOT / 'autodoc-baseline.json')
        informational = [finding for finding in findings if finding['severity'] == 'report']
        self.assertTrue(informational, 'the advisory phase reports the recommended set')
        self.assertEqual(summary['exit_code'], 0)
        text = enforce.report(data, findings, [], [], data['enforcement'], 0)
        self.assertIn('Informational', text)
        self.assertIn('never failed', text)

    def test_readiness_is_relative_to_the_declared_phase(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            config = Path(folder) / 'autodoc.toml'
            config.write_text('schema = 1\nphase = "beta"\n')
            data, _, _, _, _, _ = self.build(config, Path(folder) / 'none.json')
        self.assertTrue(data['readiness'].startswith('beta-ready:'))
        text = enforce.report(data, [], [], [], data['enforcement'], 0)
        self.assertIn('beta-ready:', text)

    def test_shipped_repository_declares_build_and_passes(self):
        """The dogfooded declaration: build warns about the required set and fails structure only."""
        data, findings, suppressed, stale, enforcement, summary = self.build(
            ROOT / 'autodoc.toml', ROOT / 'autodoc-baseline.json')
        self.assertTrue(enforcement['declared'], 'this repository declares its own phase')
        self.assertEqual(enforcement['label'], 'build (warn)')
        self.assertEqual(summary['exit_code'], 0,
                         'warnings are work to do, not a failed build')
        self.assertFalse([finding for finding in findings if finding['severity'] == 'error'],
                         'the shipped repository has no failing finding')
        self.assertEqual(stale, [])
        text = enforce.report(data, findings, suppressed, stale, enforcement, 0)
        self.assertIn('never certifies compliance', text)
        self.assertNotIn('Advisory: phase undeclared', text)

    def test_pins_are_deliberate_policy_not_a_second_copy_of_the_phase_block(self):
        """Review point: a pin that repeats the phase default is noise, so only the rest remain."""
        context = context_module.normalise(context_module.load(ROOT / 'autodoc.toml'))
        phase_defaults = context_module.enforcement('build')['checks']
        for rule, pinned in context['severity'].items():
            with self.subTest(rule):
                self.assertNotEqual(pinned, phase_defaults[rule],
                                    'a pin that duplicates the phase block hides the phase')
                self.assertEqual(context_module.check_severity(context, rule)[0], pinned)
        for rule in ('recommend.core', 'recommend.extended'):
            self.assertNotIn(rule, context['severity'],
                             'open decisions stay at the phase default until they are recorded')

    def test_a_declared_phase_turns_the_same_repository_into_failures(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            config = Path(folder) / 'autodoc.toml'
            config.write_text('version = 1\nphase = "beta"\n')
            data, findings, _, _, enforcement, summary = self.build(config, Path(folder) / 'none.json')
        self.assertTrue(enforcement['declared'])
        self.assertEqual(summary['exit_code'], 1)
        self.assertTrue(any(finding['rule'] == 'recommend.core' and finding['severity'] == 'error'
                            for finding in findings))
        self.assertTrue(all(finding['because'].startswith('phase=beta') for finding in findings
                            if finding['kind'] == 'requirement'))

    def test_the_report_never_certifies_compliance_and_names_its_level(self):
        data, findings, suppressed, stale, enforcement, summary = self.build(
            ROOT / 'autodoc.toml', ROOT / 'autodoc-baseline.json')
        text = enforce.report(data, findings, suppressed, stale, enforcement, 0)
        self.assertIn('Checks ran at', text)
        self.assertIn('never certifies compliance', text)
        self.assertIn('Baseline-suppressed', text)


if __name__ == '__main__':
    unittest.main()
