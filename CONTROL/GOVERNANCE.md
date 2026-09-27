---
id: DOC-P2-004
title: "AutoDOC governance"
type: POL
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
# AutoDOC governance

The controlled metadata schema is `CONTROL/metadata/FRONT-MATTER-SCHEMA.json`. Review intervals
are per-file `review_days`; critical overdue human documents fail CI; other overdue docs warn.
Document changes go through PRs. Human approval requires repository settings, not merely
CODEOWNERS. See `CONTROL/policies/DOCUMENTATION-POLICY.md` and `docs/00-governance/DOCUMENT-CONTROL.md`.
No weekly issues or backups are claimed unless actually configured.
