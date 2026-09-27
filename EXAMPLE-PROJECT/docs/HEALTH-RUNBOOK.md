---
id: EX-HEALTH-RUNBOOK-001
title: "Local demo health runbook"
type: PROC
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "0.1"
effective_date: 2026-09-26
next_review: 2027-03-25
source_of_truth: human
supersedes: null
related: ["EX-API-001"]
criticality: medium
review_days: 180
last_verified: 2026-09-26
last_reviewed: 2026-09-26
last_updated: 2026-09-26
auto_generated: false
---
# Local demo health runbook

This is an educational local procedure, not an on-call SLA or production response plan.
If `/health` returns non-200, confirm the local server is listening and review its stderr.
Restart `python src/app.py` from `EXAMPLE-PROJECT`; verify with
`curl http://localhost:8000/health`. Do not delete task data or claim an incident resolved
without checking the actual running service.
