#!/usr/bin/env python3
"""Resolve catalog requirements against a declared context and a detected profile.

    Obligations = Catalog x Context -> (applies?, severity, enforcement)

Applicability is decided by a predicate, never by a project-type label. A predicate token is a
fact name, the sentinel `always` or `assess`, `kind:<id>`, or `obligation:<id>`; a bare list means
every token must hold, and `{"all": [...], "any": [...]}` states a mixed condition. A fact is
three-valued, so a predicate over an unknown fact yields *undetermined* — reported separately,
never counted as satisfied and never failed. Severity comes from the declared phase: an undeclared
phase is advisory-only, and nothing fails until the owner declares one.
"""
import argparse
import importlib.util
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOGS = ('CATALOG-A', 'CATALOG-B')
PHASE_ORDER = ('idea', 'prototype', 'build', 'beta', 'live', 'mature', 'sunset')
SENTINELS = ('always', 'assess')
PREFIXES = ('kind:', 'obligation:')
PHASE_PREFIX = 'phase>='


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context_module = load_module('autodoc_context', 'scripts/intelligence/context.py')
profiler = load_module('autodoc_profiler', 'scripts/intelligence/profile.py')
MODEL = context_module.load_model()


def catalog():
    """Return every catalog entry as a dict in stable id order."""
    documents = []
    for catalog_name in CATALOGS:
        data = json.loads((ROOT / catalog_name / 'INDEX.yaml').read_text(encoding='utf-8'))
        for domain in data['domains']:
            for document in domain['documents']:
                documents.append({**document, 'domain': domain['domain']})
    return sorted(documents, key=lambda item: item['id'])


def predicate(document):
    """Normalise applies_when into (all_tokens, any_tokens)."""
    applied = document['applies_when']
    if isinstance(applied, dict):
        return list(applied.get('all', [])), list(applied.get('any', []))
    return list(applied), []


def token_state(token, facts, context, model=None):
    """Return 'true', 'false' or 'unknown' for one predicate token.

    The declaration points are three-valued on purpose. A kind or a phase that nobody declared is
    not a negative fact about the repository; it is a question the owner has not answered yet, so
    the token is `unknown` and the document it gates is *undetermined* — reported, never failed.
    Only once a declaration exists does absence become a real `false`.
    """
    model = model or MODEL
    if token == 'always':
        return 'true'
    if token == 'assess':
        return 'unknown'
    if token.startswith('kind:'):
        kind = token.split(':', 1)[1]
        if kind in context['kinds']:
            return 'true'
        # Nothing declared at all: the kind question is unanswered, not answered "no".
        return 'unknown' if not context['kinds'] else 'false'
    if token.startswith(PHASE_PREFIX):
        wanted = token[len(PHASE_PREFIX):]
        phase = context.get('phase')
        if phase not in PHASE_ORDER:
            return 'unknown'  # an undeclared phase cannot be compared
        if wanted not in PHASE_ORDER:
            return 'unknown'
        return 'true' if PHASE_ORDER.index(phase) >= PHASE_ORDER.index(wanted) else 'false'
    if token.startswith('obligation:'):
        return 'true' if token.split(':', 1)[1] in context['obligations'] else 'false'
    entry = facts.get(token)
    if entry is None:
        return 'unknown'
    return entry['value']


def state_of(document, facts, context, model=None):
    """Return (state, detail) where state is applicable, not-applicable, undetermined or assess."""
    every, any_of = predicate(document)
    if every == ['assess']:
        return 'assess', {}
    detail = {token: token_state(token, facts, context, model) for token in every + any_of}

    def all_state(tokens):
        if any(detail[token] == 'false' for token in tokens):
            return 'not-applicable'      # one false token settles an AND
        if any(detail[token] == 'unknown' for token in tokens):
            return 'undetermined'        # no false, but a fact could not be read
        return 'applicable'

    def any_state(tokens):
        if any(detail[token] == 'true' for token in tokens):
            return 'applicable'          # one true token settles an OR
        if any(detail[token] == 'unknown' for token in tokens):
            return 'undetermined'
        return 'not-applicable'

    state = all_state(every) if every else 'applicable'
    if state == 'applicable' and any_of:
        state = any_state(any_of)
    return state, detail


def profile_placement(documents, context):
    """Which types are core under the declared profile, as data rather than a guess.

    `default` is tier.core; every other profile is a delta. A removed type is off with a reason
    instead of quietly disappearing, and an added type is as required as any default core type —
    the difference is visible in the profile, not in how hard the resolver looks at it.
    """
    profiles = context_module.load_profiles()
    by_id = {profile['id']: profile for profile in profiles['profiles']}
    chosen = context.get('profile') or 'default'
    profile = by_id[chosen]
    default_core = {document['id'] for document in documents if document['tier'] == 'core'}
    added = {change['id'] for change in profile.get('add', [])}
    removed = {change['id'] for change in profile.get('remove', [])}
    return {'id': chosen, 'name': profile['name'], 'why': profile['why'],
            'core': (default_core | added) - removed, 'default_core': default_core,
            'added': sorted(added), 'removed': sorted(removed),
            # An addition states its own phases: "core for this kind of project" is not
            # "required at idea", and the document's own map knows nothing about the profile.
            'added_phases': {change['id']: change.get('severity_by_phase', {})
                             for change in profile.get('add', [])}}


def placement_of(document, placement):
    """The tier this type has *here*: core, removed-by-profile, or its catalog tier."""
    if document['id'] in placement['core']:
        return 'core'
    if document['id'] in placement['removed']:
        return 'removed'
    return document['tier']


def severity_for(document, state, decision, enforcement, context, placement):
    """Return the severity of one requirement under the declared phase and profile."""
    tier = placement_of(document, placement)
    if decision:
        return 'acknowledged'
    if state == 'assess':
        return 'assess'
    if state == 'undetermined':
        return 'undetermined'
    if state == 'not-applicable':
        return 'not-applicable'
    if not enforcement['declared']:
        return 'report' if tier == 'core' else 'recommended'
    if enforcement.get('only') == 'sunset':
        return 'required' if document['id'] in MODEL['sunset_ids'] else 'off'
    if tier == 'removed':
        return 'off'
    if tier == 'core':
        # severity_by_phase is sparse: it states where the type is off, and the phase block
        # supplies the severity once it applies. An explicit severity here wins over the block.
        mapping = (placement['added_phases'].get(document['id'])
                   or document.get('severity_by_phase') or {})
        override = mapping.get(enforcement['phase'])
        if override:
            return 'off' if override == 'off' else 'required'
        return 'required'
    if tier == 'extended':
        return 'recommended'
    return 'contextual'


def effective_phase_min(document, placement):
    """The phase a type actually becomes required at, profile additions included."""
    mapping = placement.get('added_phases', {}).get(document['id'])
    if mapping is None:
        return document.get('phase_min')
    for phase_id in PHASE_ORDER:
        if mapping.get(phase_id) != 'off':
            return phase_id
    return None


def off_reason(document, placement, enforcement):
    """Why a type is off at this phase, so the skip is never a silent one."""
    if document['id'] in placement['removed']:
        return f"removed by profile {placement['id']}: not required for this kind of project"
    if enforcement.get('only') == 'sunset':
        return 'sunset: only the sunset profile is still required'
    phase_min = effective_phase_min(document, placement)
    if phase_min and enforcement['phase'] and PHASE_ORDER.index(phase_min) \
            > PHASE_ORDER.index(enforcement['phase']):
        return f'not required before {phase_min}'
    return 'off by declaration'


EFFECTIVE_RULE = {'required': 'recommend.core', 'early': 'recommend.core',
                 'recommended': 'recommend.extended', 'contextual': 'recommend.extended'}


def score_profile(placement):
    """How the selected profile changed the core set, so the report can state it."""
    return {'id': placement['id'], 'name': placement['name'], 'why': placement['why'],
            'core_types': len(placement['core']), 'default_core_types': len(placement['default_core']),
            'added': placement['added'], 'removed': placement['removed']}


def enforced_reason(item, enforcement):
    """Why this item is or is not enforced, in the terms the decision was made in.

    The machine output has to answer the same question the terminal does — "is anything going to
    happen about this?" — so a boolean without the cause would be less than the text it replaces.
    """
    severity = item['severity_effective']
    phase = enforcement['phase'] or 'undeclared'
    if severity in ('error', 'warn'):
        tier = 'required' if item['tier'] == 'core' else 'recommended'
        return (f"phase {phase}: missing {tier} documents have severity {severity} "
                f"({enforcement['description'].split(',')[0]})")
    if severity == 'off':
        return f'phase {phase}: off, so nothing is checked for this type'
    if severity in ('report', 'recommended', 'contextual'):
        return f'phase {phase}: reported, never failed'
    if severity == 'early':
        return f"phase {phase}: not required before {item.get('phase_min')}"
    if severity == 'off':
        return item.get('off_reason') or 'off at this phase'
    if severity in ('acknowledged', 'not-applicable'):
        decision = item.get('decision') or 'recorded'
        reason = item.get('reason') or item.get('path') or item.get('locations')
        return f'{decision}: {reason}'
    if severity == 'assess':
        return 'assess-only type: nothing can detect it, so it is reported for a human'
    return f'{severity}: no check applies' 


def effective_severity(item, enforcement, context):
    """Map a semantic level to the severity the declared phase enforces.

    The semantic level answers 'why is this required of me'; this answers 'does it fail'.
    Only here do phase defaults, and any config override of an honoured rule, take effect.
    """
    severity = item['severity']
    rule = EFFECTIVE_RULE.get(severity)
    override = context['severity'].get(rule) if rule else None
    if override:
        return override
    if severity == 'required':
        return enforcement['core']
    if severity == 'recommended':
        return enforcement['extended']
    if severity in ('early', 'contextual'):
        return 'report'
    return severity


def evaluate(documents, profile_document, context, enforcement=None, placement=None):
    """Resolve every catalog entry into a group, with its severity and reason."""
    facts = profile_document['facts']
    enforcement = enforcement or context_module.enforcement(context['phase'])
    placement = placement or profile_placement(documents, context)
    instantiated, not_applicable = context['instantiated'], context['not_applicable']
    satisfied = context['satisfied_by']
    groups = {'required': [], 'recommended': [], 'contextual': [], 'reported': [],
              'undetermined': [], 'assess': [], 'not_applicable': [], 'acknowledged': [], 'off': []}
    for document in documents:
        doc_id = document['id']
        state, detail = state_of(document, facts, context)
        decision = ('instantiated' if doc_id in instantiated else
                    'not_applicable' if doc_id in not_applicable else
                    'satisfied_by' if doc_id in satisfied else None)
        severity = severity_for(document, state, decision, enforcement, context, placement)
        item = {'id': doc_id, 'name': document['name'], 'tier': document['tier'],
                'effective_tier': placement_of(document, placement),
                'decision': decision, 'type': document['type'], 'domain': document['domain'],
                'applies_when': document['applies_when'],
                'phase_min': effective_phase_min(document, placement),
                'why': document.get('tier_reason'), 'severity': severity, 'state': state,
                'tokens': detail,
                'evidence': next((facts[token]['evidence'][0] for token, value in detail.items()
                                  if value == 'true' and token in facts and facts[token]['evidence']),
                                 None)}
        item['severity_effective'] = effective_severity(item, enforcement, context)
        item['enforced'] = item['severity_effective'] in ('error', 'warn')
        item['enforced_reason'] = enforced_reason(item, enforcement)
        if item['severity_effective'] == 'off':
            item['off_reason'] = off_reason(document, placement, enforcement)
        item['because'] = because(item, enforcement)
        if decision == 'instantiated':
            item['path'] = instantiated[doc_id]
        if decision == 'satisfied_by':
            item['locations'] = satisfied[doc_id]
        if decision == 'not_applicable':
            item['reason'] = not_applicable[doc_id]['reason']
            for key in ('owner', 'review'):
                if not_applicable[doc_id].get(key):
                    item[key] = not_applicable[doc_id][key]
            # A skip is re-surfaced when the reason may have expired: the predicate is true now.
            if state == 'applicable':
                item['stale_decision'] = True
        key = {'acknowledged': 'acknowledged', 'assess': 'assess', 'undetermined': 'undetermined',
               'not-applicable': 'not_applicable', 'report': 'reported'}.get(severity, severity)
        groups[key].append(item)
    return groups


def score(documents, groups, enforcement):
    required = [item for item in groups['required']
                if item['severity_effective'] != 'off']
    acknowledged = [item for item in groups['acknowledged']
                    if item['effective_tier'] == 'core' and item['severity'] == 'acknowledged']
    reported = [item for item in groups['reported'] if item['effective_tier'] == 'core']
    open_items = len(required) + len(reported)
    return {'applicable_core_types': open_items + len(acknowledged),
            'acknowledged_core_types': len(acknowledged),
            'open_core_decisions': open_items,
            'core_acknowledged_percent': round(100 * len(acknowledged) / (open_items + len(acknowledged)))
            if (open_items + len(acknowledged)) else 100,
            'undetermined_types': len(groups['undetermined']),
            'assess_only_types': len(groups['assess']),
            'inapplicable_types': len(groups['not_applicable']),
            'off_types': len(groups['off']),
            'catalog_types': len(documents), 'enforcement': enforcement['label'],
            'readiness': (f'{enforcement["phase"]}-ready: {len(acknowledged)}/'
                          f'{len(required) + len(acknowledged)}')
            if enforcement['declared'] else
            f'undeclared phase: advisory only ({len(reported)} applicable core types reported, '
            f'{len(acknowledged)} acknowledged)'}


def because(item, enforcement):
    """The context that caused this requirement, in one line: phase plus the predicate values."""
    tokens = ', '.join(f'{token}={value}' for token, value in sorted(item.get('tokens', {}).items()))
    phase = enforcement['phase'] or 'undeclared'
    return f'phase={phase}' + (f' and {tokens}' if tokens else '')


def findings(documents, context, groups, enforcement=None):
    """Return one structured finding per problem: rule, severity, location, reason, fix, cause.

    Config findings and requirement findings are both here, distinguished by `kind`, because a
    broken autodoc.toml is a usage error (exit 2) while a missing document is a real finding
    (exit 1). Neither this function nor its callers decide exit codes; the enforcement layer does.
    """
    enforcement = enforcement or context_module.enforcement(context['phase'])
    ids = {document['id'] for document in documents}
    out = []

    def config(section, detail, fix):
        out.append({'kind': 'config', 'rule': 'context.config', 'severity': 'error',
                    'location': f'autodoc.toml [{section}]', 'detail': detail,
                    'message': f'autodoc.toml [{section}]: {detail}', 'fix': fix,
                    'because': 'the declared context must name catalog ids and existing paths'})

    for section in ('not_applicable', 'instantiated'):
        for doc_id in context[section]:
            if doc_id not in ids:
                config(section, f'unknown catalog id {doc_id}',
                       'remove it, or use an id from CATALOG-A/B')
    for doc_id, path in context['instantiated'].items():
        if doc_id in ids and not (ROOT / path).is_file():
            config('instantiated', f'{doc_id} points at a missing path {path}',
                   'point it at the document that exists')
    for doc_id, entry in context['not_applicable'].items():
        if doc_id in ids and not entry.get('reason'):
            config('not_applicable', f'{doc_id} needs a reason',
                   'record why the document is not applicable')
    for doc_id, locations in context['satisfied_by'].items():
        if doc_id not in ids:
            config('satisfied_by', f'unknown catalog id {doc_id}',
                   'remove it, or use an id from CATALOG-A/B')
            continue
        for location in locations:
            if location.startswith(('http://', 'https://')):
                continue  # offline: a declared URL is recorded, never fetched or asserted live
            if not (ROOT / location).is_file():
                config('satisfied_by', f'{doc_id} location does not exist: {location}',
                       'fix the path, or declare the URL instead')
    for item in groups['acknowledged']:
        if item.get('stale_decision'):
            detail = (f"recorded not_applicable, but its predicate is true now "
                      f"({', '.join(item['applies_when'])}); re-check")
            out.append({'kind': 'requirement', 'rule': 'recommend.core', 'severity': 'warn',
                        'location': item['id'], 'detail': detail,
                        'message': f"{item['id']} ({item['name']}): {detail}",
                        'fix': 'confirm the reason still holds, or remove the skip',
                        'because': because(item, enforcement)})
    for item in groups['required']:
        detail = (f"required at phase {enforcement['phase']} ({item['phase_min']}) "
                  f'with no document and no recorded decision')
        severity = item['severity_effective']
        if severity == 'error':
            # A phase that does not fail yet still reports how far it is from the required set.
            severity = 'error' if enforcement['fail'] else 'warn'
        if severity not in ('report', 'warn', 'error'):
            continue  # `off` is silence by declaration
        out.append({'kind': 'requirement', 'rule': 'recommend.core', 'severity': severity,
                    'location': item['id'], 'detail': detail,
                    'message': f"{item['id']} ({item['name']}): {detail}",
                    'fix': 'write the document, or record a decision in autodoc.toml '
                           '([instantiated], [satisfied_by] or [not_applicable])',
                    'because': because(item, enforcement)})
    for item in groups['acknowledged']:
        if item.get('decision') == 'not_applicable' and not item.get('owner') \
                and not item.get('review'):
            detail = ('recorded not applicable with no owner or review date; an advisory '
                      'decision nobody owns is never re-checked')
            out.append({'kind': 'decision', 'rule': 'recommend.decision', 'severity': 'report',
                        'location': item['id'], 'detail': detail,
                        'message': f"{item['id']} ({item['name']}): {detail}",
                        'fix': 'add owner = "@handle" or review = "YYYY-MM-DD" to the [not_applicable] entry',
                        'because': because(item, enforcement)})
    for item in groups['recommended']:
        if item['severity_effective'] in ('report', 'warn'):
            detail = (f"recommended at phase {enforcement['phase']} with no document"
                      if item['severity_effective'] == 'warn' else
                      f"recommended, informational at phase {enforcement['phase']}")
            out.append({'kind': 'requirement', 'rule': 'recommend.extended',
                        'severity': item['severity_effective'],
                        'location': item['id'], 'detail': detail,
                        'message': f"{item['id']} ({item['name']}): {detail}",
                        'fix': 'write it, or record a decision in autodoc.toml',
                        'because': because(item, enforcement)})
    return out


def check(documents, context, groups, enforcement=None):
    """Fail only what the declared phase says must fail; an undeclared phase never fails."""
    errors, warnings = [], []
    for finding in findings(documents, context, groups, enforcement):
        if finding['kind'] == 'config' or finding['severity'] == 'error':
            errors.append(finding['message'])
        elif finding['severity'] == 'warn':
            warnings.append(finding['message'])
    return errors, warnings


def explain(document, profile_document, context, enforcement=None, placement=None, documents=None,
            groups=None):
    """Return the derivation chain that explains one requirement."""
    facts = profile_document['facts']
    enforcement = enforcement or context_module.enforcement(context['phase'])
    placement = placement or profile_placement(documents or [document], context)
    decision = ('instantiated' if document['id'] in context['instantiated'] else
                'not_applicable' if document['id'] in context['not_applicable'] else None)
    state, detail = state_of(document, facts, context)
    severity = severity_for(document, state, decision, enforcement, context, placement)
    placed = placement_of(document, placement)
    lines = [f"{document['id']} — {document['name']}", '',
             f"- Tier: {document['tier']}" + (f" ({document['tier_reason']})" if document.get('tier_reason') else '')
             + (f"; core under profile {placement['id']}" if placed == 'core' and document['tier'] != 'core' else '')
             + (f"; removed by profile {placement['id']}" if placed == 'removed' else ''),
             f"- Applies when: {json.dumps(document['applies_when'])}",
             f"- Current phase: {enforcement['label']}",
             f"- Phase that requires it: {effective_phase_min(document, placement) or 'none (never required before sunset)'}",
             f"- Reader question: {document.get('question') or 'not stated yet (catalog admission backlog)'}",
             f"- Reader: {document.get('reader') or '—'}",
             f"- Support: {document.get('support')}"
             + (f" (checks: {', '.join(document['checks'])})" if document.get('checks') else '')
             + (' — nothing verifies this type' if document.get('support') == 'template-only' else ''),
             f"- Lifecycle events: {', '.join(document.get('events') or []) or 'none (periodic review)'}",
             f"- State: {state}", f"- Severity: {severity}"
             + (f" ({off_reason(document, placement, enforcement)})"
                if severity == 'off' else ''), '']
    lines.append('| Token | Value | Evidence | Limits |')
    lines.append('| --- | --- | --- | --- |')
    every, any_of = predicate(document)
    for token in every + any_of:
        if token in facts:
            entry = facts[token]
            lines.append(f"| `{token}` | {entry['value']} | {', '.join(entry['evidence']) or '—'} | "
                         f"{entry['limits']} |")
        elif token in SENTINELS:
            lines.append(f'| `{token}` | sentinel | — | — |')
        else:
            declared = (context['kinds'] if token.startswith('kind:') else context['obligations']) \
                if token.startswith(PREFIXES) else []
            lines.append(f'| `{token}` | {"declared" if token.split(":", 1)[1] in declared else "not declared"} | '
                         'declared context | — |')
    if decision:
        reference = {'not_applicable': context['not_applicable'].get(document['id'], {}).get('reason'),
                     'instantiated': context['instantiated'].get(document['id']),
                     'satisfied_by': ', '.join(context['satisfied_by'].get(document['id'], []))}.get(decision)
        lines += ['', f"Recorded decision: {decision} — {reference or '—'}"]
    return '\n'.join(lines) + '\n'


def kind_summary(profile_document, context):
    """The kind situation: what is declared, what the evidence suggests, and what that means.

    Kinds are a declaration, so the useful thing to report is not a verdict but the gap between
    the two: declared kinds nothing supports, evidence for kinds nobody declared (which makes
    kind-gated documents undetermined rather than failed), and — when neither side has anything —
    the generic baseline, which is not a guess about what the project is.
    """
    hints = context_module.kind_hints(profile_document)
    declared = list(context.get('kinds') or [])
    evidence = (profile_document or {}).get('kinds') or {}
    unevidenced = [kind for kind in declared
                   if (evidence.get(kind) or {}).get('value') == 'false']
    return {'declared': declared, 'suggested': hints['suggested'], 'evidence': hints['evidence'],
            'declared_without_evidence': unevidenced,
            'declaration_only_available': sorted(
                kind['id'] for kind in MODEL['kinds']
                if kind.get('detection') == 'declaration-only'),
            'generic_baseline': not declared,
            'note': hints['note']}


def kind_line(kinds, groups):
    """One line that says what is declared, what is only evidence, and what is still undetermined."""
    line = "- Kinds: " + (', '.join(kinds.get('declared') or []) or 'undeclared')
    if kinds.get('declared_without_evidence'):
        line += f" (declared with no file evidence: {', '.join(kinds['declared_without_evidence'])})"
    if not kinds.get('declared'):
        gated = [item for item in (groups.get('undetermined') or [])
                 if any(token.startswith('kind:') for token in (item.get('tokens') or {}))]
        if kinds.get('suggested'):
            line += f" — evidence suggests {', '.join(kinds['suggested'])}"
        line += '; kinds are declared, never inferred'
        line += (f', so {len(gated)} kind-gated document(s) are undetermined rather than not '
                 'applicable' if gated else '')
        if not kinds.get('suggested'):
            line += ' and no detector matched, so the generic baseline applies'
    return line


def trait_summary(profile_document, context):
    """The declared traits: the facts no detector can answer, each answered or still a question.

    Traits are a declaration, so the report does not hedge about them: it lists the answer the
    owner recorded, or says the question is open. An open trait is not a failure — the documents
    that depend on it are undetermined — but it is never quietly read as `false` either.
    """
    traits = []
    for name, entry in sorted(((profile_document or {}).get('facts') or {}).items()):
        if entry.get('detection') != 'declaration-only':
            continue
        answered = entry.get('value') in ('true', 'false')
        traits.append({'id': name, 'label': entry.get('label') or name,
                       'value': entry['value'] if answered else None, 'declared': answered,
                       'reason': entry.get('declared_reason') if answered else None,
                       'why_declared_only': entry.get('limits')})
    return {'asked': traits, 'unanswered': [trait['id'] for trait in traits if not trait['declared']]}


def trait_line(traits, groups):
    """One line: each trait's recorded answer, or the open question and what it leaves hanging."""
    if not traits.get('asked'):
        return '- Declared traits: none in the vocabulary'
    answered = [f"{trait['id']} = {trait['value']}" for trait in traits['asked'] if trait['declared']]
    line = '- Declared traits: ' + (', '.join(answered) or 'none answered')
    if traits.get('unanswered'):
        gated = [item for item in (groups.get('undetermined') or [])
                 if any(token in traits['unanswered'] for token in (item.get('tokens') or {}))]
        line += (f"; asked but not answered: {', '.join(traits['unanswered'])}")
        line += (f" ({len(gated)} document(s) undetermined until answered)" if gated else '')
        line += '; a trait is declared once and recorded, never inferred'
    return line


def report(data):
    summary, groups, enforcement = data['summary'], data['groups'], data['enforcement']
    profile = data.get('catalog_profile') or {}
    kinds = data.get('kinds') or {}
    lines = ['# AutoDOC requirements', '',
             f"- Phase: {enforcement['label']}",
             f"- Detected ecosystems: {', '.join(data['ecosystems']['present']) or 'none'}"
             + (f" (readers: {', '.join(data['ecosystems']['readers']) or 'none'}; "
                f"unread: {', '.join(data['ecosystems']['unread']) or 'none'})"
                if data['ecosystems']['present'] else ''),
             f"- Undeclared facts: {', '.join(data['unknown_facts']) or 'none'}",
             f"- Catalog profile: {profile['name']} ({profile['core_types']} core types: "
             f"{profile['default_core_types']} default"
             + (f", {len(profile['added'])} added" if profile['added'] else '')
             + (f", {len(profile['removed'])} removed" if profile['removed'] else '') + ')',
             kind_line(kinds, groups),
             trait_line(data.get('traits') or {}, groups),
             f"- {summary['readiness']}",
             f"- Open core decisions: {summary['open_core_decisions']}",
             f"- Undetermined types (unknown fact): {summary['undetermined_types']}",
             f"- Assess-only types (no detectable predicate): {summary['assess_only_types']}",
             f"- Not applicable, with a recorded reason: {summary['inapplicable_types']}",
             f"- Off at this phase or profile: {summary['off_types']}",
             f"- Catalog types: {summary['catalog_types']}", '']
    sections = [('required', 'Required now', '| Type | Name | Required since | Severity | Evidence | Why core |',
                 lambda i: f"| `{i['id']}` | {i['name']} | {i['phase_min']} | "
                          f"{i['severity_effective']} | "
                           f"{i['evidence'] or '—'} | {i['why'] or '—'} |"),
                ('reported', 'Applicable, advisory only (no phase declared)',
                 '| Type | Name | Becomes required at | Evidence | Why core |',
                 lambda i: f"| `{i['id']}` | {i['name']} | {i['phase_min'] or '—'} | "
                           f"{i['evidence'] or '—'} | {i['why'] or '—'} |"),
                ('off', 'Not applicable at this phase (off, with the reason)',
                 '| Type | Name | Reason | Becomes required at |', None),
                ('recommended', 'Recommended (extended)',
                 '| Type | Name | Applies when | Evidence |', None),
                ('undetermined', 'Undetermined — a fact could not be detected',
                 '| Type | Name | Unknown fact | Why it matters |', None),
                ('acknowledged', 'Acknowledged decisions', '| Type | Name | Decision | Reference |', None)]
    for key, title, header, renderer in sections:
        items = groups.get(key) or []
        if not items:
            continue
        lines += [f'## {title}', '', header, '| --- | --- | --- | --- |']
        for item in items:
            if renderer:
                lines.append(renderer(item))
            elif key == 'off':
                lines.append(f"| `{item['id']}` | {item['name']} | "
                             f"{item.get('off_reason') or 'off at this phase'} | "
                             f"{item['phase_min'] or '—'} |")
            elif key == 'recommended':
                lines.append(f"| `{item['id']}` | {item['name']} | "
                             f"{json.dumps(item['applies_when'])} | {item['evidence'] or '—'} |")
            elif key == 'undetermined':
                unknown = ', '.join(token for token, value in item['tokens'].items() if value == 'unknown')
                lines.append(f"| `{item['id']}` | {item['name']} | {unknown} | "
                             f"{item['why'] or 'applicability unknown'} |")
            else:
                reference = (item.get('path') or ', '.join(item.get('locations') or [])
                             or item.get('reason') or '—')
                stale = ' (predicate now true — re-check)' if item.get('stale_decision') else ''
                lines.append(f"| `{item['id']}` | {item['name']} | {item['severity']}{stale} | {reference} |")
        lines.append('')
    if not any(groups[name] for name in ('required', 'off', 'recommended', 'reported')):
        lines += ['No applicable requirement was found for this context.', '']
    lines += ['Applicability is decided by detected facts and declared decisions, never by a '
              'project-type guess. An unknown fact makes a type undetermined, which is reported '
              'and never silently satisfied.', '',
              'Use `--explain <type-id>` to see the derivation chain for one requirement.']
    return '\n'.join(lines) + '\n'


def build(args):
    raw = context_module.load(args.config)
    context = context_module.normalise(raw)
    problems = context_module.validate(context)
    if problems:
        raise ValueError('; '.join(problems))
    if args.profile:
        profile_document = json.loads(args.profile.read_text(encoding='utf-8'))
    else:
        profile_document = profiler.profile(args.repo, context['facts'])
    enforcement = context_module.enforcement(context['phase'])
    documents = catalog()
    placement = profile_placement(documents, context)
    groups = evaluate(documents, profile_document, context, enforcement, placement)
    unknown = sorted(name for name, entry in profile_document['facts'].items()
                     if entry['value'] == 'unknown')
    return {'version': 2, 'repo': profile_document['repo'], 'phase': context['phase'],
            'kinds': kind_summary(profile_document, context),
            'traits': trait_summary(profile_document, context),
            'enforcement': enforcement, 'ecosystems': profile_document['ecosystems'],
            'unknown_facts': unknown, 'facts': profile_document['facts'],
            'profile': profile_document, 'catalog_profile': score_profile(placement),
            'summary': score(documents, groups, enforcement), 'groups': groups}, \
        documents, context, groups, enforcement


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT, help='Repository to profile')
    parser.add_argument('--config', type=Path, help='Context file (default <repo>/autodoc.toml)')
    parser.add_argument('--profile', type=Path, help='Use a saved profile.json instead of detecting')
    parser.add_argument('--json', action='store_true', help='Print JSON instead of Markdown')
    parser.add_argument('--output', type=Path, help='Write the report here instead of stdout')
    parser.add_argument('--check', action='store_true', help='Fail what the declared phase requires')
    parser.add_argument('--explain', help='Explain one catalog type id and exit')
    parser.add_argument('--hint', action='store_true',
                        help='Suggest a phase and project kinds from observable evidence')
    args = parser.parse_args()
    if args.config is None:
        args.config = (args.repo / 'autodoc.toml')
    try:
        data, documents, context, groups, enforcement = build(args)
    except (ValueError, KeyError, OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print('Recommendation error:', error, file=sys.stderr)
        return 2
    if args.explain:
        match = next((document for document in documents if document['id'] == args.explain), None)
        if match is None:
            print('Unknown catalog id:', args.explain, file=sys.stderr)
            return 2
        print(explain(match, data['profile'], context, enforcement, groups=groups), end='')
        return 0
    if args.hint:
        # Both hints answer the same question — "what would you declare?" — and neither sets
        # anything: they are printed, the owner decides, and the declaration is what counts.
        print(json.dumps({'phase': context_module.phase_hints(args.repo, data['profile']),
                          'kinds': context_module.kind_hints(data['profile']),
                          'traits': data['traits']}, indent=2))
        return 0
    errors, warnings = ([], []) if not args.check else check(documents, context, groups, enforcement)
    for warning in warnings:
        print('WARNING:', warning, file=sys.stderr)
    for error in errors:
        print(error, file=sys.stderr)
    if args.check and errors:
        # Usage errors are exit 2, findings are exit 1; see docs/reference/EXIT-CODES.md.
        usage = any(finding['kind'] == 'config'
                    for finding in findings(documents, context, groups, enforcement))
        if not usage:
            print(f"Required at phase {enforcement['phase']} and missing: {len(errors)}",
                  file=sys.stderr)
        return 2 if usage else 1
    if args.json:
        document = json.dumps(data, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(document, encoding='utf-8')
            print('Wrote', args.output)
        else:
            print(document, end='')
    else:
        text = report(data)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding='utf-8')
            print('Wrote', args.output)
        else:
            print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
