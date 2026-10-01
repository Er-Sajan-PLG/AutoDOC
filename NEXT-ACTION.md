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
last_updated: 2026-09-26
auto_generated: false
---
# Next action

## Immediate focus
Next bounded integrations: add migration prose validation and a real OpenAPI contract only
when the demo source implements one. Existing env/alert references are example-only; review
their runbooks and applicability rather than claiming deployed monitoring. Review
catalog applicability and human-owned drafts with a real maintainer.

## Owner decisions
Done: the license is Apache-2.0 (owner decision, 2026-10-01): canonical text in `LICENSE`, SPDX
expression in `pyproject.toml`, decision record in `docs/00-governance/LICENSE-DECISION.md`.
Release snapshots are no longer gated on the licence; they still require a `vX.Y.Z` tag checked
out at the same commit. Remaining: enable protected branch required checks/CODEOWNERS review in
GitHub settings, and close the 12 open core decisions. Those actions are not automated by
checked-in files and must not be claimed as complete.

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
   - **Review the 27-type core list** and the phasing in `CATALOG-RULES.json` — three of the core
     types (`PII inventory`, `Cardholder data flow`, `Hazard analysis`) are gated by declared
     traits and only apply once an owner answers; then record the 12 applicable core decisions
     with `[instantiated]`, `[satisfied_by]` or `[not_applicable]` reasons. Four of them rest on
     facts that are true only because `EXAMPLE-PROJECT` contains those files, so their reasons
     matter more than their answer.
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
