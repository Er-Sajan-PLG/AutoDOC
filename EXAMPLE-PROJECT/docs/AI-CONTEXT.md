---
id: EX-AGENT-001
title: "Task API agent context"
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
related: ["EXAMPLE-PROJECT-DOCS-ARCHITECTURE-MD"]
criticality: medium
review_days: 180
last_verified: 2026-09-26
last_reviewed: 2026-09-26
last_updated: 2026-09-26
auto_generated: false
---
# Task API agent context

This example does not call an LLM or silently run an autonomous agent. It demonstrates the
agent-context contract: a coding agent reads `EXAMPLE-PROJECT/AGENTS.md`, this context,
the human architecture review and the generated factual references before changing code.

## Constraints
- SQLite is local demo storage; no auth, backup or multi-tenant isolation.
- Use `routes.json` for the route registry, `config.schema.json` for defaults, and
  `db/schema.sql` for persistent shape.
- Test against a temporary database. Do not commit task data or secrets.
- Source changes require regenerated docs; API implementation changes need architecture review.

## Agent workflow
1. Read current state and next action at the repository root.
2. Inspect source files, tests and the sync map; make the smallest change.
3. Run tests, regenerate, review human-owned context, and report what remains unverified.
