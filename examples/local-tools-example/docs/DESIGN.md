---
id: EX-LOCAL-DES-001
title: "Local tool policy design"
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
# Local tool policy design

The matrix is allow-by-name with fixed supported handlers. Network and shell tools are explicitly
blocked; approval is a documented concept, not an implemented bypass. `files.read` confines
resolved paths to `data/`, rejects traversal and symlinks outside it, and limits file size.
No LLM or network integration exists. Review this document on policy or handler changes.
