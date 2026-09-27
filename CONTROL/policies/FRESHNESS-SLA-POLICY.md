---
id: CONTROL-POLICIES-FRESHNESS-SLA-POLICY-MD
title: "Freshness SLA policy"
type: POL
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "1.0"
effective_date: 2026-09-26
next_review: 2027-03-25
source_of_truth: human
supersedes: null
related: []
criticality: high
review_days: 180
last_verified: 2026-09-26
last_reviewed: 2026-09-26
last_updated: 2026-09-26
auto_generated: false
---
# Freshness SLA policy

`review_days` is counted from `last_verified`, not from a Git timestamp. Critical overdue
human-owned documents fail the freshness check; high/medium/low overdue documents emit warnings.
Generated documents are governed by deterministic drift checks instead of calendar age.

Default guidance: critical 30 days, high 90 days, medium 180 days, low 365 days.
`last_verified` only changes after a real review; running a generator is not a review.
`next_review` is an explicit planning date and should agree with the chosen SLA.
A scheduled CI workflow checks all controlled files; create an issue from a warning only
when issue permissions and triage ownership are explicitly configured.
