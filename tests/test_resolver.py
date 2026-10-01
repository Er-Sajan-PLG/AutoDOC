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
        values[name] = {'value': overrides.pop(name, 'false'), 'detection': 'files',
                        'exactness': spec['exactness'],
                        'evidence': ['example/path'] if overrides.get(name) == 'true' else [],
                        'limits': spec['limits']}
    for name, spec in profiler.DECLARED_FACTS.items():
        # A trait nobody declared is `unknown`, exactly as the profiler emits it.
        value = overrides.pop(name, 'unknown')
        answered = value in ('true', 'false')
        values[name] = {'value': value, 'detection': 'declaration-only', 'exactness': None,
                        'evidence': ['declared'] if answered else [],
                        'limits': spec['why_declared_only'],
                        'declared_reason': 'synthetic reason' if answered else None}
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
    profile = profile_document(**detected)
    for name, entry in (declared.get('facts') or {}).items():
        # The same merge the profiler performs: a declaration replaces the value and records
        # the reason, whether the fact has a detector or is declaration-only.
        profile['facts'][name] = {**profile['facts'][name], 'value': entry['value'],
                                  'evidence': ['declared'], 'declared_reason': entry['reason']}
    enforcement = context_module.enforcement(declared['phase'])
    documents = recommend.catalog()
    groups = recommend.evaluate(documents, profile, declared, enforcement)
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


class KindTests(unittest.TestCase):
    """§3: kinds are declared, never guessed, and the two predicate forms stay three-valued."""

    def test_a_kind_gated_document_is_undetermined_until_someone_declares_the_kind(self):
        _, declared, groups, _ = resolve(phase='build', has_public_api_surface='true')
        self.assertEqual(declared['kinds'], [])
        self.assertIn('DOC-A08-008', ids(groups, 'undetermined'))
        item = find(groups, 'undetermined', 'DOC-A08-008')
        self.assertEqual(item['tokens']['kind:library'], 'unknown')
        self.assertEqual(item['tokens']['has_public_api_surface'], 'true',
                         'the known half of the predicate is still evaluated')
        summary = recommend.kind_summary(profile_document(has_public_api_surface='true'), declared)
        self.assertTrue(summary['generic_baseline'])
        line = recommend.kind_line(summary, groups)
        self.assertIn('undeclared', line)
        self.assertIn('declared, never inferred', line)

    def test_file_evidence_never_becomes_a_requirement(self):
        """The hint may say `library`; only the declaration can make the SDK guide apply."""
        declared = context(**{'phase': 'build', 'kinds': [], 'facts': {}})
        documents = recommend.catalog()
        enforcement = context_module.enforcement('build')
        profile = profile_document(has_public_api_surface='true')
        profile['kinds'] = {'library': {'value': 'true', 'exactness': 'heuristic',
                                        'evidence': ['packaged_library in python manifest'],
                                        'limits': 'x'}}
        groups = recommend.evaluate(documents, profile, declared, enforcement)
        self.assertIn('DOC-A08-008', ids(groups, 'undetermined'),
                      'evidence is a hint; without a declaration the question stays open')
        self.assertNotIn('DOC-A08-008', ids(groups, 'recommended'))

    def test_declaring_a_kind_answers_the_question_both_ways(self):
        _, _, declared_library, _ = resolve(phase='build', kinds=['library'],
                                            has_public_api_surface='true')
        self.assertIn('DOC-A08-008', ids(declared_library, 'contextual'))
        self.assertNotIn('DOC-A08-008', ids(declared_library, 'undetermined'))
        _, _, declared_data, _ = resolve(phase='build', kinds=['data'],
                                         has_public_api_surface='true')
        self.assertIn('DOC-A08-008', ids(declared_data, 'not_applicable'),
                      'a declared kind list is closed: absence is a real no')

    def test_a_kind_the_model_cannot_detect_is_declarable(self):
        """`plugin`, `embedded`, `template` and friends have no detector on purpose."""
        model = context_module.load_model()
        declaration_only = {kind['id'] for kind in model['kinds']
                            if kind.get('detection') == 'declaration-only'}
        self.assertTrue(declaration_only)
        for kind in declaration_only:
            with self.subTest(kind):
                entry = next(item for item in model['kinds'] if item['id'] == kind)
                self.assertTrue(entry['why_declared_only'].strip(),
                                'a kind nobody can see needs a stated reason')
        _, _, groups, _ = resolve(phase='build', kinds=['plugin'], has_ui='true')
        self.assertNotIn('DOC-A11-010', ids(groups, 'undetermined'),
                         'a declared declaration-only kind is answered like any other')

    def test_phase_predicates_are_three_valued(self):
        """`phase>=live` gates observability: open while undeclared, then decided by the phase."""
        _, _, undeclared, _ = resolve(has_deploy='true')
        self.assertIn('DOC-A16-007', ids(undeclared, 'undetermined'))
        _, _, build, _ = resolve(phase='build', has_deploy='true')
        self.assertIn('DOC-A16-007', ids(build, 'not_applicable'),
                      'a build-phase project does not operate anything yet')
        _, _, live, _ = resolve(phase='live', has_deploy='true')
        self.assertIn('DOC-A16-007', ids(live, 'contextual'))
        _, _, mature, _ = resolve(phase='mature', has_deploy='true')
        self.assertIn('DOC-A16-007', ids(mature, 'contextual'), 'phase>= stays true afterwards')

    def test_the_kind_hint_shows_evidence_and_claims_nothing(self):
        hint = context_module.kind_hints(profile_document(has_public_api_surface='true'))
        self.assertIn('suggested', hint)
        self.assertIn('never inferred', hint['note'])
        empty = context_module.kind_hints({'kinds': {}})
        self.assertEqual(empty['suggested'], [])
        self.assertIn('generic baseline', empty['note'])

    def test_the_kind_line_reports_a_declaration_with_no_supporting_evidence(self):
        _, declared, groups, _ = resolve(phase='build', kinds=['ml'])
        profile = profile_document()
        profile['kinds'] = {'ml': {'value': 'false', 'exactness': 'heuristic', 'evidence': [],
                                   'limits': 'x'}}
        summary = recommend.kind_summary(profile, declared)
        self.assertEqual(summary['declared_without_evidence'], ['ml'])
        self.assertIn('no file evidence', recommend.kind_line(summary, groups))


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


class TraitTests(unittest.TestCase):
    """§4: traits are facts about the world, declared once, never inferred from files."""

    TRAITS = ('handles_payments', 'handles_personal_data', 'safety_critical')
    DECLARED_FALSE = {name: {'value': 'false', 'reason': 'declared false for this test'}
                      for name in TRAITS}

    def test_an_unanswered_trait_leaves_its_documents_undetermined_never_false(self):
        _, declared, groups, _ = resolve(phase='build')
        self.assertEqual(declared['facts'], {})
        self.assertIn('DOC-A05-009', ids(groups, 'undetermined'),
                      'PII inventory depends on a question nobody answered')
        item = find(groups, 'undetermined', 'DOC-A05-009')
        self.assertEqual(item['tokens']['handles_personal_data'], 'unknown')
        self.assertNotIn('DOC-A05-009', ids(groups, 'not_applicable'))
        traits = recommend.trait_summary(profile_document(), declared)
        self.assertEqual(traits['unanswered'], list(self.TRAITS))
        line = recommend.trait_line(traits, groups)
        self.assertIn('asked but not answered', line)
        self.assertIn('never inferred', line)
        self.assertIn('document(s) undetermined', line)

    def test_declaring_a_trait_answers_the_question_both_ways(self):
        _, _, answered, _ = resolve(phase='build', facts=self.DECLARED_FALSE)
        self.assertIn('DOC-A05-009', ids(answered, 'not_applicable'))
        self.assertIn('DOC-A07-003', ids(answered, 'not_applicable'),
                      'the deeper privacy set follows the same answer')
        self.assertNotIn('DOC-A05-009', ids(answered, 'undetermined'))
        traits = recommend.trait_summary(profile_document(), {'facts': {}})
        self.assertEqual(traits['unanswered'], list(self.TRAITS), 'sanity: profile alone is open')
        line = recommend.trait_line(traits, answered)
        self.assertIn('none answered', line)

    def test_a_declared_true_trait_activates_its_documents(self):
        _, _, active, _ = resolve(phase='build', facts={
            'handles_payments': {'value': 'true', 'reason': 'the service takes cards'},
            'handles_personal_data': {'value': 'true', 'reason': 'customer accounts'},
            'safety_critical': {'value': 'true', 'reason': 'controls hospital equipment'}})
        self.assertIn('DOC-A06-011', ids(active, 'required'),
                      'cardholder data flow is required at build once payments are declared')
        self.assertIn('DOC-A20-008', ids(active, 'required'))
        self.assertIn('DOC-A05-009', ids(active, 'required'))
        self.assertEqual(recommend.trait_summary(profile_document(), {})['unanswered'],
                         list(self.TRAITS))
        self.assertNotIn('DOC-A05-009', ids(active, 'undetermined'))

    def test_a_trait_value_can_only_arrive_through_a_declaration(self):
        """There is no detector to disagree with: the vocabulary itself is the guarantee."""
        for name, spec in profiler.DECLARED_FACTS.items():
            self.assertNotIn(name, profiler.DETECTORS)
            self.assertEqual(profiler.fact_specs()[name]['detection'], 'declaration-only')
            self.assertFalse(spec.get('sources'), 'a declared trait has no source to read')

    def test_phase_and_kinds_stay_three_valued_next_to_traits(self):
        documents, declared, groups, enforcement = resolve(phase='build',
                                                            has_public_api_surface='true')
        self.assertIn('DOC-A08-008', ids(groups, 'undetermined'),
                      'an undeclared kind is still a question, not a no')
        self.assertEqual(declare_only_values(declared), {},
                         'no trait value is ever inferred into the context')


def declare_only_values(declared):
    """The trait values the context itself declares (never what a profile detected)."""
    return {name: entry['value'] for name, entry in declared['facts'].items()
            if name in profiler.DECLARED_FACTS}


if __name__ == '__main__':
    unittest.main()
