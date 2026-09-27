---
id: DEV-AGENT-001
title: "AutoDOC agent instructions"
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
# AutoDOC agent instructions

## Project overview
AutoDOC is a self-updating, self-documenting documentation engine, not a compliance certificate.

## Working sequence
1. Read `CURRENT-STATE.md`, `NEXT-ACTION.md`, `RECENT-CHANGES.md`, and `CONTEXT-SNAPSHOT.md`.
2. Consult `docs/.doc-sync-map.yaml` for the source-to-target contract; inspect source and tests.
3. Make the smallest source change, add tests, regenerate, and review human-owned impact.
4. Run `make check` and `make test`; report remaining unverified behavior.

## Hard constraints
Never rename AutoDOC, edit generated docs by hand, fabricate evidence, or overwrite human
priorities. Controlled files need metadata and ownership. See `ANTI-PATTERNS-FOR-AGENT.md`.
