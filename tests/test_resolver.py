"""Tests for the resolver: phase-scaled severity, three-valued facts and recorded decisions."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context_module = load_module('autodoc_context', 'scripts/intelligence/context.py')
profiler = load_module('autodoc_profiler', 'scripts/intelligence/profile.py')
recommend = load_module('autodoc_recommend', 'scripts/intelligence/recommend.py')


def facts(**overrides):
    values = {}
    for name, spec in profiler.DETECTORS.items():
        values[name] = {'value': overrides.pop(name, 'false'), 'exactness': spec['exactness'],
                        'evidence': ['example/path'] if overrides.get(name) == 'true' else [],
                        'limits': spec['limits']}
    assert not overrides, overrides
    return values


def profile_document(**overrides):
    return {'version': 2, 'repo': 'synthetic', 'file_count': 1, 'languages': {'python': 1},
            'ecosystems': {'present': ['python'], 'readers': ['python'], 'unread': []},
            'facts': facts(**overrides)}


def context(**raw):
    return context_module.normalise({'version': 1, **raw})


def resolve(**raw):
    declared = context(**{key: value for key, value in raw.items()
                          if key in ('phase', 'kinds', 'obligations', 'not_applicable',
                                     'instantiated', 'satisfied_by', 'severity', 'facts',
                                     'profile')})
    detected = {key: value for key, value in raw.items() if key in profiler.DETECTORS}
    enforcement = context_module.enforcement(declared['phase'])
    documents = recommend.catalog()
    groups = recommend.evaluate(documents, profile_document(**detected), declared, enforcement)
    return documents, declared, groups, enforcement


def ids(groups, key):
    return {item['id'] for item in groups[key]}


def find(groups, key, doc_id):
    return next((item for item in groups[key] if item['id'] == doc_id), None)


def group_of(groups, doc_id):
    return next((name for name, items in groups.items()
                 if any(item['id'] == doc_id for item in items)), None)


class PhaseScalingTests(unittest.TestCase):
    def test_undeclared_phase_is_advisory_and_never_fails(self):
        documents, declared, groups, enforcement = resolve()
        errors, warnings = recommend.check(documents, declared, groups, enforcement)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(groups['required'], [])
        self.assertIn('DEV-B01-006', ids(groups, 'reported'))
        readiness = recommend.score(documents, groups, enforcement)['readiness']
        self.assertIn('undeclared phase', readiness)

    def test_prototype_reports_without_warning(self):
        documents, declared, groups, enforcement = resolve(phase='prototype')
        errors, warnings = recommend.check(documents, declared, groups, enforcement)
        self.assertEqual((errors, warnings), ([], []))
        self.assertTrue(groups['required'])

    def test_build_warns_but_does_not_fail(self):
        documents, declared, groups, enforcement = resolve(phase='build')
        errors, warnings = recommend.check(documents, declared, groups, enforcement)
        self.assertEqual(errors, [])
        self.assertTrue(warnings)
        self.assertTrue(all(item['severity_effective'] == 'warn' for item in groups['required']))

    def test_beta_fails_required_core_types(self):
        documents, declared, groups, enforcement = resolve(phase='beta')
        errors, warnings = recommend.check(documents, declared, groups, enforcement)
        self.assertTrue(errors)
        self.assertTrue(all(item['severity_effective'] == 'error' for item in groups['required']))
        self.assertTrue(any('required at phase beta' in error for error in errors))

    def test_severity_by_phase_defers_a_type_until_its_phase(self):
        """Off before its phase, required after it, and the reason is stated either way."""
        _, _, groups_build, _ = resolve(phase='build', is_public='true')
        self.assertIn('DOC-A15-003', ids(groups_build, 'off'), 'changelog is beta work')
        self.assertNotIn('DOC-A15-003', ids(groups_build, 'required'))
        entry = find(groups_build, 'off', 'DOC-A15-003')
        self.assertIn('not required before beta', entry['off_reason'])
        self.assertEqual(entry['phase_min'], 'beta')
        _, _, groups_beta, _ = resolve(phase='beta', is_public='true')
        self.assertIn('DOC-A15-003', ids(groups_beta, 'required'))

    def test_a_normalised_phase_is_required_from_idea(self):
        """A core type with no off phases is required as soon as a phase is declared."""
        _, _, groups, _ = resolve(phase='build')
        self.assertIn('DEV-B01-001', ids(groups, 'required'))
        self.assertEqual(find(groups, 'required', 'DEV-B01-001')['phase_min'], 'idea')


class ProfileTests(unittest.TestCase):
    """§5.2: which types are core is declared data, and switching it moves real types."""

    def test_the_default_profile_is_tier_core(self):
        documents, declared, groups, enforcement = resolve(phase='build', profile='default')
        placement = recommend.profile_placement(documents, declared)
        self.assertEqual(placement['core'],
                         {doc['id'] for doc in documents if doc['tier'] == 'core'})
        self.assertEqual(placement['added'], [])
        self.assertEqual(placement['removed'], [])

    def test_the_oss_profile_adds_the_social_documents(self):
        documents, declared, groups, _ = resolve(phase='build', profile='oss-library',
                                                is_public='true', has_deploy='true')
        placement = recommend.profile_placement(documents, declared)
        self.assertIn('DOC-A09-009', placement['core'], 'code of conduct comes with the profile')
        self.assertIn('DOC-A09-009', ids(groups, 'required'))
        self.assertIn('DOC-A16-003', placement['removed'])
        runbook = find(groups, 'off', 'DOC-A16-003')
        self.assertIn('removed by profile oss-library', runbook['off_reason'])

    def test_an_internal_service_does_not_need_redistribution_terms(self):
        documents, declared, groups, _ = resolve(phase='build', profile='internal-service',
                                                has_deploy='true', is_public='true')
        placement = recommend.profile_placement(documents, declared)
        self.assertNotIn('DOC-A10-008', placement['core'])
        self.assertIn('DOC-A16-005', placement['core'], 'on-call arrives with the profile')
        self.assertIn('DOC-A16-003', placement['core'], 'the runbook stays')
        self.assertEqual(find(groups, 'off', 'DOC-A10-008')['off_reason'],
                         'removed by profile internal-service: not required for this kind of '
                         'project')

    def test_a_profile_addition_states_when_it_lands(self):
        documents, declared, groups, _ = resolve(phase='build', profile='internal-service',
                                                has_deploy='true')
        on_call = find(groups, 'off', 'DOC-A16-005')
        self.assertIn('not required before live', on_call['off_reason'])
        _, _, groups_live, _ = resolve(phase='live', profile='internal-service', has_deploy='true')
        self.assertIn('DOC-A16-005', ids(groups_live, 'required'))

    def test_an_unknown_profile_is_rejected(self):
        broken = context_module.normalise({'schema': 1, 'profile': 'unicorn'})
        self.assertIn('is not a declared profile', ' '.join(context_module.validate(broken)))

    def test_the_regulated_profile_requires_records(self):
        documents, declared, groups, _ = resolve(phase='beta', profile='regulated',
                                                has_personal_data='true',
                                                has_persistent_state='true')
        placement = recommend.profile_placement(documents, declared)
        for doc_id in ('DOC-A07-001', 'DOC-A05-006', 'DOC-A20-002', 'DOC-A24-003'):
            with self.subTest(doc_id):
                self.assertIn(doc_id, placement['core'])

    def test_sunset_requires_only_the_end_of_life_set(self):
        documents, declared, groups, enforcement = resolve(phase='sunset', is_public='true')
        self.assertEqual(ids(groups, 'required'), {'DOC-A23-001', 'DOC-A23-003', 'DOC-A23-007'})
        self.assertTrue(groups['off'])
        self.assertNotIn('DEV-B01-006', ids(groups, 'required'))
        errors, _ = recommend.check(documents, declared, groups, enforcement)
        self.assertEqual(len(errors), 3)

    def test_severity_override_can_switch_a_rule_off(self):
        documents, declared, groups, enforcement = resolve(phase='beta',
                                                           severity={'recommend.core': 'off'})
        errors, _ = recommend.check(documents, declared, groups, enforcement)
        self.assertEqual(errors, [])
        self.assertTrue(all(item['severity_effective'] == 'off' for item in groups['required']))


class ApplicabilityTests(unittest.TestCase):
    def test_always_applies_and_predicates_gate_the_rest(self):
        _, _, groups, _ = resolve()
        reported = ids(groups, 'reported')
        self.assertIn('DEV-B01-006', reported)
        self.assertNotIn('DOC-A05-001', reported, 'no persistent state was detected')

    def test_predicate_true_promotes_a_type(self):
        _, _, groups, _ = resolve(has_persistent_state='true')
        self.assertIn('DOC-A05-001', ids(groups, 'reported'))

    def test_unknown_fact_makes_a_type_undetermined_and_not_failing(self):
        documents, declared, groups, enforcement = resolve(phase='beta',
                                                           has_third_party_deps='unknown')
        item = find(groups, 'undetermined', 'DOC-A10-002')
        self.assertIsNotNone(item)
        self.assertEqual(item['tokens']['has_third_party_deps'], 'unknown')
        errors, warnings = recommend.check(documents, declared, groups, enforcement)
        self.assertFalse(any('DOC-A10-002' in message for message in errors + warnings))

    def test_any_of_predicate_needs_one_true_token(self):
        _, _, none, _ = resolve()
        self.assertIn('DOC-A22-001', ids(none, 'not_applicable'), 'every token is false')
        _, _, api, _ = resolve(has_public_api_surface='true')
        self.assertIn(group_of(api, 'DOC-A22-001'), ('reported', 'recommended'),
                      'one true token satisfies an OR')
        _, _, unclear, _ = resolve(has_cli='unknown')
        self.assertIsNotNone(find(unclear, 'undetermined', 'DOC-A22-001'),
                             'no true token and one unknown leaves it undetermined')

    def test_obligation_gated_types_need_a_declaration(self):
        _, _, without, _ = resolve()
        self.assertIn('DOC-A07-001', ids(without, 'not_applicable'))
        _, _, with_gdpr, _ = resolve(obligations=['gdpr'])
        self.assertIsNotNone(find(with_gdpr, 'recommended', 'DOC-A07-001'),
                             'declaring the obligation makes the type applicable')

    def test_assess_types_are_never_auto_required(self):
        _, _, groups, _ = resolve(phase='beta')
        self.assertTrue(groups['assess'])
        self.assertFalse([item for item in groups['assess'] if item['tier'] == 'core'])
        self.assertNotIn('DOC-A24-001', ids(groups, 'required'))


class DecisionTests(unittest.TestCase):
    def test_instantiated_acknowledges_and_does_not_fail(self):
        documents, declared, groups, enforcement = resolve(
            phase='beta', instantiated={'DEV-B01-001': 'CONTRIBUTING.md'})
        self.assertIsNotNone(find(groups, 'acknowledged', 'DEV-B01-001'))
        errors, _ = recommend.check(documents, declared, groups, enforcement)
        self.assertFalse(any('DEV-B01-001' in error for error in errors))

    def test_not_applicable_requires_a_reason(self):
        with self.assertRaisesRegex(ValueError, 'reason must be non-empty'):
            resolve(not_applicable={'DEV-B01-001': ''})

    def test_stale_decision_is_resurfaced(self):
        documents, declared, groups, enforcement = resolve(
            phase='beta', not_applicable={'DEV-B01-006': 'we have no readers'})
        item = find(groups, 'acknowledged', 'DEV-B01-006')
        self.assertTrue(item['stale_decision'], 'its predicate is true now')
        _, warnings = recommend.check(documents, declared, groups, enforcement)
        self.assertTrue(any('re-check' in warning for warning in warnings))

    def test_satisfied_by_acknowledges_external_locations(self):
        documents, declared, groups, enforcement = resolve(
            satisfied_by={'DOC-A06-001': ['https://wiki.example.com/threat-model']})
        item = find(groups, 'acknowledged', 'DOC-A06-001')
        self.assertIsNotNone(item)
        errors, _ = recommend.check(documents, declared, groups, enforcement)
        self.assertEqual(errors, [])

    def test_satisfied_by_local_path_must_exist(self):
        documents, declared, groups, enforcement = resolve(satisfied_by={'DOC-A06-001': ['docs/missing.md']})
        errors, _ = recommend.check(documents, declared, groups, enforcement)
        self.assertTrue(any('location does not exist' in error for error in errors))

    def test_check_rejects_unknown_ids_and_dead_paths(self):
        documents, declared, groups, enforcement = resolve(
            not_applicable={'DOC-A99-999': 'typo'}, instantiated={'DEV-B04-001': 'docs/gone.md'})
        errors, _ = recommend.check(documents, declared, groups, enforcement)
        joined = ' '.join(errors)
        self.assertIn('unknown catalog id DOC-A99-999', joined)
        self.assertIn('points at a missing path', joined)


class ExplainTests(unittest.TestCase):
    def test_explain_shows_the_derivation_chain(self):
        documents, declared, groups, enforcement = resolve(phase='beta', has_public_api_surface='true')
        document = next(item for item in documents if item['id'] == 'DOC-A08-001')
        text = recommend.explain(document, profile_document(has_public_api_surface='true'),
                                 declared, enforcement, groups=groups)
        self.assertIn('Phase that requires it: beta', text)
        self.assertIn('| `has_public_api_surface` | true |', text)
        self.assertIn('Limits', text)

    def test_explain_answers_the_reader_question_and_names_the_profile(self):
        documents, declared, groups, enforcement = resolve(phase='build', profile='oss-library',
                                                           is_public='true')
        document = next(item for item in documents if item['id'] == 'DOC-A09-009')
        text = recommend.explain(document, profile_document(is_public='true'), declared,
                                 enforcement, groups=groups)
        self.assertIn('core under profile oss-library', text)
        self.assertIn('What behaviour is expected here', text)
        self.assertIn('Reader: contributors', text)
        self.assertIn('Support: checked', text)
        self.assertIn('Lifecycle events: onboarding, incident', text)

    def test_explain_states_the_recorded_decision(self):
        documents, declared, groups, enforcement = resolve(
            not_applicable={'DEV-B01-006': 'no readers'})
        document = next(item for item in documents if item['id'] == 'DEV-B01-006')
        text = recommend.explain(document, profile_document(), declared, enforcement)
        self.assertIn('Recorded decision: not_applicable — no readers', text)

    def test_explain_covers_declared_tokens(self):
        documents, declared, groups, enforcement = resolve(obligations=['gdpr'])
        document = next(item for item in documents if item['id'] == 'DOC-A07-001')
        text = recommend.explain(document, profile_document(), declared, enforcement)
        self.assertIn('| `obligation:gdpr` | declared |', text)


if __name__ == '__main__':
    unittest.main()
