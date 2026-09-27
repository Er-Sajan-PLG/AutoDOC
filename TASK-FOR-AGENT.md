---
id: DEV-AGENT-006
title: "Task for an AutoDOC agent (fillable template)"
type: TPL
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
# Task for an AutoDOC agent (fillable template)

## Context
Describe the specific source, catalog entry and documentation mapping involved.

## Task
State a bounded outcome with source and target paths.

## Files to read first
`AGENTS.md`, `CURRENT-STATE.md`, `NEXT-ACTION.md`, `docs/.doc-sync-map.yaml`, and relevant tests.

## Constraints
Never invent evidence. Add extractor tests and regenerate mapped targets. Human decisions remain human.

## Verification
Run `make check` and `make test`; report unsupported formats explicitly.
