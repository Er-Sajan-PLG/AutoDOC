---
id: DOC-P3-GOV-001
title: "AutoDOC limitations"
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
# AutoDOC limitations

AutoDOC has 260 *possible* document types, but only configured, tested extractors generate
facts. All other types are templates and human-owned instances subject to metadata, ownership,
review-path and freshness checks **when instantiated and mapped**; templates alone are not
inventoried human documents. There is no semantic proof of prose accuracy or architecture
rationale, diagram rendering, external link availability, approval or compliance.

The demo API uses a three-route JSON registry, **not** OpenAPI. SQL accepts only the documented
SQLite CREATE TABLE subset; unknown statements fail. Dependencies are declared PEP 621
requirements, not installed/transitive packages or known license information. Alerts are
versioned example declarations, not live monitoring. The agent examples have no LLM or network.
Cloud costs, Kubernetes state, SaaS/vendor APIs, real model behavior and signed attestations
require independent project-owned integrations and credentials. GitHub branch protection is
not configured by a checked-in file; release-tag snapshots block until an owner selects a license.
Generated graph edges are factual references, not proof of architecture semantics.
