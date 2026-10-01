---
id: DEV-AGENT-005
title: "AutoDOC context snapshot"
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
# AutoDOC context snapshot

## What works
AutoDOC's versioned map generates references for the example API/config/schema, its own
catalogs/workflows, a Python AST symbol/test inventory, Markdown outline, declared dependencies
the filtered 260-type catalog views, two local tool-authorization examples, a described env and checked alert catalog, an unsigned
test-evidence pack and a template completeness report. Generation is deterministic. CI checks drift, metadata,
ownership, freshness, templates, human review impact, and actual test results.

## Boundaries
`EXAMPLE-PROJECT` is not a production service. The task API's route registry is not OpenAPI.
TypeScript, arbitrary SQL, signed build provenance, external compliance and LLM execution
are not implemented. Root `NEXT-ACTION.md` is human-owned; a Git-derived state block cannot
invent the next human priority. Branch protection still needs a repository-admin decision; the license is Apache-2.0 (`LICENSE`), so release snapshots require only a `vX.Y.Z` tag at the same commit.

## Commands
`make generate`, `make check`, `make test`; see `docs/.doc-sync-map.yaml` and `README.md`.
