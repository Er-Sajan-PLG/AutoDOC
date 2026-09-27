---
id: DEV-AGENT-VIEW-008
title: "AutoDOC AI coding context"
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
related: ["DOC-ARC-001", "DOC-P2-001", "DEV-AGENT-001"]
criticality: medium
review_days: 180
last_verified: 2026-09-26
last_reviewed: 2026-09-26
last_updated: 2026-09-26
auto_generated: false
---
# AutoDOC AI coding context

AutoDOC maps source facts to generated references; humans own judgments, policy and next action.
The canonical instructions are [`AGENTS.md`](../../AGENTS.md), with limits in
[`ENGINE-COVERAGE.md`](../00-governance/ENGINE-COVERAGE.md). Python 3.11+ is required.

`make setup`, `make generate`, `make check`, `make test`, `make ci` and `make evidence`
are real commands; `make docs:verify` provides governed-doc validation. There is no separate
`make validate` target. `task ci` exists in `Taskfile.yaml` but requires go-task and may be
unavailable in minimal environments; `make ci` is canonical. No LLM or external service
is invoked by the examples. The agent must report unsupported sources rather than invent output.
