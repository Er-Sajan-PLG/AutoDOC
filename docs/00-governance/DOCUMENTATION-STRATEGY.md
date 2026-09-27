---
id: DOC-P2-002
title: "Documentation strategy"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "0.1"
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
# Documentation strategy

AutoDOC prioritizes documentation needed while software is being built: decisions, module
boundaries, implementation notes, migration prose, tests, and working context. Mature projects
add operational policies and evidence as sources become real. Source-derived facts are regenerated;
human intent is reviewed, never inferred from Git history. The control loop is pre-commit checks,
PR drift/impact checks, a manual generation preview, release-tag artifacts when configured,
and scheduled staleness checks. See `ENGINE-COVERAGE.md` for actual enforcement limits.
