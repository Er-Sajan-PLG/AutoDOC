---
id: CURRENT-STATE-MD
title: "Current state"
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
# Current state

AutoDOC has a working sync map, standard-library runtime, three authoritative catalog indices,
260 template triples, a task API demo and two local tool-policy demonstrations without an LLM or web calls.
Its checks validate controlled-document metadata, generated drift, age and source-to-human-review impact.
A catalog entry represents a possible document, not a completed compliance obligation.

The demo includes structured agent context and CI can retain actual test-run evidence as an artifact.

A health command measures catalog template triples, instantiated docs, deadlines and drift.
The human inventory, relationship graph, catalog views and code/test/dependency outlines are generated.
CI packages actual test-run evidence without claiming a signed build or license approval.
The release-tag workflow fails closed while `LICENSE-CHOICE.md` remains pending.

AutoDOC now self-hosts its catalog and workflow inventories. Catalog and control-code changes
are mapped to human adoption or architecture review; declared ownership is checked in CI.

<!-- auto:start -->
- Catalog types: 260 (not necessarily instantiated).
- Controlled docs: 92 (23 generated, 69 human-owned).
- Overdue human-owned docs: 0.
- Open gaps: see `docs/00-governance/ENGINE-COVERAGE.md`; this block does not infer intent.
<!-- auto:end -->
