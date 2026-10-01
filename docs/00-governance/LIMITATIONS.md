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

Enforcement is only as strong as the declared phase. While no phase is declared every finding
is advisory and the exit code is `0`; a baseline suppresses findings recorded during adoption, so
`0` can mean "nothing new" rather than "nothing wrong". The report separates new findings,
baseline-suppressed findings and stale baseline entries so those two states are never conflated.
This repository pins its pre-existing structural checks (`drift`, `stubs`, `placeholders`,
`links.local`, `secrets.inline`, `tribal`, freshness) to `error` so that the policy layer did not
lower them; that choice lives in `autodoc.toml` and can be deleted to let the phase decide. The
reference integrity and manifest-aware checks (L1) cover two ecosystems only, and no L2
code-aware check exists yet, so a clean run does not mean the reference documentation is correct.

Applicability predicates come from `scripts/intelligence/profile.py`, which records **file
presence only**: a `has_public_api_surface` fact means a contract file exists, not that an
interface works, and a `false` fact means "no evidence found" rather than proof of absence.
Facts are three-valued: `unknown` is returned when no configured source could be evaluated —
an ecosystem with no reader, or no manifest at all — and a predicate over an unknown fact makes
a type **undetermined**, which is reported separately and never silently satisfied. Generated,
vendored and test-input directories (`fixtures/`, `testdata/`, `node_modules/`, virtualenvs) are
skipped and the profile lists what it skipped; a project whose shipped corpus *is* its product
would need those paths declared instead. Example and demo directories are **not** skipped, so
this repository still reports `has_public_api_surface` from `EXAMPLE-PROJECT/routes.json`. Only Python
and JavaScript have manifest readers today, so dependency questions in other ecosystems are
`unknown` rather than false. The four heuristic content scans are bounded and name their limits;
the credential scan records file paths and never values. Phase is a declaration: an undeclared
phase means advisory-only output, and the phase hint never sets enforcement. Kinds and audiences
are validated and displayed but no predicate consumes them yet, so declaring them is inert until
kind inference lands. Profiling this repository reports `has_public_api_surface`,
`has_persistent_state`, `has_env` and `has_ai` because the synthetic examples contain those
files, which is exactly why the report demands a recorded decision instead of assuming the
project owns an API or a database. The catalog tiers are a reviewable proposal, not a
measurement of any project's obligations, and a member of a tier is a *possible* document.
