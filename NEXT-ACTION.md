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
Choose a license (`LICENSE-CHOICE.md`) before enabling release snapshots. Enable protected
branch required checks/CODEOWNERS review in GitHub settings. Those actions are not automated
by checked-in files and must not be claimed as complete.

## Shrink before detection (owner decision, 2026-10-01)
1. Done. The approved-stub check failed on 28 title-only placeholders and they were retired;
   controlled documents went from 92 to 64 without losing any content.
2. Done. Classification rules moved into `CATALOG-RULES.json`, a catalog schema plus validator
   were added, `priority` was replaced by a hand-picked core tier with detectable `applies_when`
   predicates, and `profile.py` + `recommend.py` evaluate them against recorded decisions.
3. Done. Context schema, phase ladder and three-valued facts: undeclared phase is advisory, so
   **nothing fails here yet by design**, and `save`/`promote`-style phase changes are a later step.
4. **Owner decisions pending, in order:**
   - **Declare a phase** (`make docs-hint` suggests `build`, from source plus a README). Until it
     is declared, every finding stays advisory and `make ci` cannot enforce any of it.
   - **Review the 24-type core list** and the phasing in `CATALOG-RULES.json`; then record the 12
     applicable core decisions with `[instantiated]`, `[satisfied_by]` or `[not_applicable]`
     reasons. Four of them rest on facts that are true only because `EXAMPLE-PROJECT` contains
     those files, so their reasons matter more than their answer.
   - **Kind inference is not implemented**, so declared `kinds` are inert and no predicate uses
     `kind:` yet; `audience` likewise. Do not describe them as working.
5. Done. Enforcement is one policy: `scripts/intelligence/enforce.py` runs obligations and the
   structural families at the severity the declared phase sets, with a baseline for adoption,
   documented exit codes, a pre-push hook and a dry-run branch-protection helper. `make ci` runs it.
6. Next: `init`, `adopt`, `promote` and `add` — scaffolding per phase, with `adopt` writing the
   baseline and `promote` showing the delta and an optional baseline before it writes the phase.
   Then render templates on demand instead of committing 780 variants, and dogfood on a
   repository that is not this one.
A heuristic generator may warn by default only if its output names what it cannot see.
