---
id: DEV-AGENT-002
title: "AutoDOC coding-agent context"
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
last_updated: 2026-10-01
auto_generated: false
---
# AutoDOC coding-agent context

Provider-specific entry point; the canonical rules are [AGENTS.md](AGENTS.md).

Agent workflow protocol: [docs/00-governance/MACP.md](docs/00-governance/MACP.md) — read it before
acting, then start from [state/DASHBOARD.md](state/DASHBOARD.md) and register a session.

Current work is hardening bounded extractors and review processes. See `NEXT-ACTION.md` for the current
human-owned priority and `CONTEXT-SNAPSHOT.md` for session recovery. Use `make generate`,
`make check`, `make test`. Sources and generators are in `docs/.doc-sync-map.yaml` and
`scripts/doc-sync/engine.py`. Do not claim the task API is an OpenAPI extractor or a production API.
