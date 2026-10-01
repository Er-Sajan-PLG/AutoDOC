---
id: RECENT-CHANGES-MD
title: "Recent changes"
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
# Recent changes

- Replaced print-only scripts with deterministic generators, drift and impact checks.
- Added example API, configuration and SQLite schema with generated references.
- Added catalogs, template variants, metadata policy and tests.
- Integrated agent context in the demo and a scoped CI test evidence artifact.
- Made example SQL schema idempotent and added measured health reporting.
- Self-adopted catalogs and CI workflows, added architecture/adoption reviews and ownership checks.
- Added AST/Markdown/manifest inventories, 260-type catalog views, agent tool example and scoped evidence packaging.
- Tightened demo API, config and SQL extraction to fail on unsupported contracts.
- Added described environment/alert references, Mermaid graph, local tool policy demo and JUnit-derived unsigned evidence.

<!-- auto:start -->
## Last 20 Git commits

- d384d4e 2026-10-01 Correct the core-list review and answer the owner's three fact questions
- f06d5c0 2026-10-01 Expand the core-list review so no row can be approved by accident
- 5164b06 2026-10-01 Ask the owner to review the core list in one sitting, with every row reasoned
- 2454ea1 2026-10-01 License Apache-2.0: the owner decided, and the tree now says so
- a398dbd 2026-10-01 Declare when AutoDOC runs, and make the scheduled run triage instead of a second gate
- 5d385cf 2026-10-01 Regenerate the test inventory for the language tests
- 6d1c444 2026-10-01 Integrate each language's own tool, and label every generator with its exactness
- 5d3f155 2026-10-01 Refresh the living plan: the phase, kinds and traits are no longer pending
- 0fe3ec3 2026-10-01 Ask the facts no file can answer, and keep them undetermined until declared
- 74d0544 2026-10-01 Infer kinds as evidence and declare them as answers, never as guesses
- 58e1663 2026-10-01 Make the core set a declared profile and give every catalog type an admission
- 90478d4 2026-10-01 Enforce a phase-scaled contract: fingerprinted baselines, honest exits, golden fixtures
- 19ca0d4 2026-09-27 Merge pull request #1 from Er-Sajan-PLG/arena/01a0de49-autodoc

## Changed paths at update time

- `CATALOG-A/INDEX.yaml`
- `CATALOG-B/INDEX.yaml`
- `CONTROL/metadata/CATALOG-RULES.json`
- `README.md`
- `autodoc.toml`
- `docs/00-governance/CORE-LIST-REVIEW.md`
- `docs/01-catalogs/UNIVERSAL-DOCUMENT-CATALOG-A.md`
- `docs/01-catalogs/UNIVERSAL-DOCUMENT-CATALOG-B.md`
- `docs/META/CODE-INVENTORY.md`
- `docs/META/OUTLINE.md`
- `docs/META/TEST-INVENTORY.md`
- `scripts/doc-control/check_catalog.py`
- `scripts/intelligence/profile.py`
- `tests/test_catalog.py`
- `tests/test_profile.py`
- `tests/test_resolver.py`
<!-- auto:end -->
