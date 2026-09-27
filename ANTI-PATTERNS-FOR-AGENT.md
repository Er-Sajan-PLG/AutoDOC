---
id: DEV-AGENT-004
title: "Agent anti-patterns"
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
# Agent anti-patterns

- Do not rename AutoDOC or hand-edit a generated document.
- Do not claim support for SQL dialects, TypeScript parsing, cryptographic signing or an LLM
  runtime merely because a catalog lists them.
- Do not invent review dates, owners, dependency licenses, secrets or test results.
- Do not delete human-authored records or rewrite priorities from Git metadata.
- Do not add source patterns that recursively include their own generated target.
- Do not suppress failures from missing sources, unsupported constructs or path escapes.
- Do not push CI-generated commits or change repository protections without owner approval.
