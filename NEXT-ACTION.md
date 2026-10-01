---
id: NEXT-ACTION-MD
title: "Next action"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "1.0"
effective_date: 2026-09-26
next_review: 2027-03-25
source_of_truth: human
supersedes: null
related: []
criticality: medium
review_days: 180
last_verified: 2026-09-26
last_reviewed: 2026-09-26
last_updated: 2026-10-01
auto_generated: false
---
# Next action

## Immediate focus
Next bounded integrations: add migration prose validation and a real OpenAPI contract only
when the demo source implements one. Existing env/alert references are example-only; review
their runbooks and applicability rather than claiming deployed monitoring. The catalog
applicability review is done — recorded 2026-10-01 (see Owner decisions below).

## Owner decisions
Done: the license is Apache-2.0 (owner decision, 2026-10-01): canonical text in `LICENSE`, SPDX
expression in `pyproject.toml`, decision record in `docs/00-governance/LICENSE-DECISION.md`.
Release snapshots are no longer gated on the licence; they still require a `vX.Y.Z` tag checked
out at the same commit. Done: the core list and the five profiles are owner-reviewed
(2026-10-01) — `owner_reviewed` is recorded in `CONTROL/metadata/CATALOG-RULES.json` and
`PROFILES.json`, `docs/00-governance/CORE-LIST-REVIEW.md` is `approved`, and every applicable
core decision is closed (the resolver reports 15/15 build-ready with 0 open). Remaining: apply
the required check in GitHub settings — owner-run, `APPLY=1 make docs-require-check` (without
it, the payload prints). That action is not automated by checked-in files and must not be
claimed as complete.

## Shrink before detection (owner decision, 2026-10-01)
1. Done. The approved-stub check failed on 28 title-only placeholders and they were retired;
   controlled documents went from 92 to 64 without losing any content.
2. Done. Classification rules moved into `CATALOG-RULES.json`, a catalog schema plus validator
   were added, `priority` was replaced by a hand-picked core tier with detectable `applies_when`
   predicates, and `profile.py` + `recommend.py` evaluate them against recorded decisions.
3. Done. Context schema, phase ladder and three-valued facts: undeclared phase is advisory, so
   **nothing fails here yet by design**, and `save`/`promote`-style phase changes are a later step.
4. **Owner decisions pending, in order:**
   - Done: the phase is declared (`build`, 2026-09-30) and kinds too (`library`); the evidence
     for both comes from `make docs-hint` and the declaration is what counts.
   - Done (2026-10-01): the 24-type core list and the phasing in `CATALOG-RULES.json` are
     owner-reviewed, and all 12 applicable core decisions are recorded (`[instantiated]`,
     `[satisfied_by]`; the last one closed by declaring `has_persistent_state` false with a
     reason) — the resolver reports 15/15 build-ready with 0 open. Three core types
     (`PII inventory`, `Cardholder data flow`, `Hazard analysis`) remain gated by declared
     traits and apply only once the owner answers. The demo-only facts
     (`has_public_api_surface`, `has_http_api`, `has_persistent_state`, `has_env`, `has_ai`)
     are declared false with reasons in `autodoc.toml`, and the detector no longer matches
     its own source.
   - Kinds and traits are implemented: `kind:` and `phase>=` are three-valued and now consumed,
     and `handles_personal_data`, `handles_payments`, `safety_critical` are declaration-only
     facts whose documents stay undetermined until answered. `audience` is validated and
     displayed but no predicate consumes it yet. Do not describe it as working.
5. Done. Enforcement is one policy: `scripts/intelligence/enforce.py` runs obligations and the
   structural families at the severity the declared phase sets, with a baseline for adoption,
   documented exit codes, a pre-push hook and a dry-run branch-protection helper. `make ci` runs it.
6. Partly done. Per-language references: Python is extracted in-process (exact) and Go's
   toolchain is integrated behind a probe; every other language is reported as L0 with the reason.
   Next in this step: more integrated toolchains (JavaScript/TypeScript and Rust have canonical
   tools to wire), then `init`, `adopt`, `promote` and `add` — scaffolding per phase, with `adopt` writing the
   baseline and `promote` showing the delta and an optional baseline before it writes the phase.
   Then render templates on demand instead of committing 780 variants, and dogfood on a
   repository that is not this one.
7. Done. Event triggers are declared in `CONTROL/metadata/TRIGGERS.json` and verified by
   `triggers.py --check` (in `make ci`): one blocking event, one required check, no undeclared
   workflow, no filtered required check, and no network from a gate. The scheduled workflow reports
   every check and summarises once; the external link check is scheduled, rate-limited and
   warn-only. Next in this direction: adopters' repositories need their own trigger model, which is
   part of `adopt` in step 6.

A heuristic generator may warn by default only if its output names what it cannot see.
