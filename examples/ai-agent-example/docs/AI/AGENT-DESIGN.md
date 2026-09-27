---
id: EX-AGENT-DES-001
title: "Example tool dispatcher design"
type: DES
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
# Example tool dispatcher design

## Purpose and scope
Demonstrate an agent project's tool-authorization boundary without requiring a model service.
This example is a local dispatcher, **not** an AI agent with LLM inference.

## Details and decisions
`src/tools.json` declares authorized name/module/function pairs. The runtime refuses unknown
names or modules outside its hardcoded implementation allowlist. Calculator is bounded to two
integers; prompt reader allows only simple filenames under its prompt directory. Search raises
`NOT_IMPLEMENTED`. There is no secret, external network call or write-capable tool.

## Verification and references
Run `python -m pytest -v` from the repository root. The generated tool/prompt/model registries
are derived from versioned JSON, source code and prompt files. Review this design when tool
semantics or authorization change; a generated registry cannot verify safety reasoning.
