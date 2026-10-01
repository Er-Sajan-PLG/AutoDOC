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

- 5d385cf 2026-10-01 Regenerate the test inventory for the language tests
- 6d1c444 2026-10-01 Integrate each language's own tool, and label every generator with its exactness
- 5d3f155 2026-10-01 Refresh the living plan: the phase, kinds and traits are no longer pending
- 0fe3ec3 2026-10-01 Ask the facts no file can answer, and keep them undetermined until declared
- 74d0544 2026-10-01 Infer kinds as evidence and declare them as answers, never as guesses
- 58e1663 2026-10-01 Make the core set a declared profile and give every catalog type an admission
- 90478d4 2026-10-01 Enforce a phase-scaled contract: fingerprinted baselines, honest exits, golden fixtures
- 19ca0d4 2026-09-27 Merge pull request #1 from Er-Sajan-PLG/arena/01a0de49-autodoc

## Changed paths at update time

- `.github/workflows/docs-staleness.yml`
- `CHANGELOG.md`
- `CONTROL/metadata/MASTER-INDEX.json`
- `CONTROL/policies/DOCUMENTATION-POLICY.md`
- `Makefile`
- `README.md`
- `docs/.doc-sync-map.yaml`
- `docs/00-governance/BRANCH-PROTECTION.md`
- `docs/00-governance/ENGINE-COVERAGE.md`
- `docs/00-governance/LIMITATIONS.md`
- `docs/04-guides/HOW-AUTODOC-WORKS.md`
- `docs/05-architecture/AUTODOC-ARCHITECTURE.md`
- `docs/META/CODE-INVENTORY.md`
- `docs/META/COMPLETENESS-REPORT.md`
- `docs/META/OUTLINE.md`
- `docs/META/TEST-INVENTORY.md`
- `docs/generated/AUTOMATION-REFERENCE.md`
- `docs/generated/WORKFLOW-REFERENCE.md`
- `docs/reference/DOC-RELATIONSHIPS.md`
- `docs/reference/EXIT-CODES.md`
- … and 2 more; use git diff --cached --name-only.
<!-- auto:end -->
