---
id: DOC-P2-001
title: "Engine coverage and honest limits"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "0.2"
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
# Engine coverage and honest limits

## Implemented and tested
All outputs below have concrete sources in `docs/.doc-sync-map.yaml`; `make generate` writes,
`make docs:drift` checks without writing, and tests cover accepted and rejected inputs.

| Source format | Generator/output | Supported scope | Tests |
| --- | --- | --- | --- |
| Demo `routes.json` | Task API reference | Exactly three implemented routes | `test_phase2.py`, `test_example.py` |
| Demo config JSON | Config reference + described `.env.example` | `integer`/`string` defaults | `test_phase2.py` |
| Described `.env.example` | `docs/reference/ENVIRONMENT.md` | `KEY=value`, preceding comment | `test_phase3.py` |
| Demo SQLite DDL | Data dictionary | Simple CREATE TABLE columns only | `test_phase2.py` |
| Example alert JSON-compatible YAML | Alert catalog | Condition, severity, existing runbook required | `test_phase3.py` |
| PEP 621 manifests | Declared dependency references | Direct declarations, no resolution | `test_phase2.py` |
| Python AST and ATX Markdown | Code/test inventory and outline | Parsed declarations/headings, not behavior | `test_phase2.py` |
| Catalogs/workflow files | Three views, CI inventory, completeness | Stable IDs and file hashes | `test_engine.py`, `test_phase3.py` |
| Frontmatter + sync map | Master/human inventories; JSON + Mermaid graph | References and actual mapped paths | `test_engine.py`, `test_phase3.py` |
| Local tool matrix/prompt files | Allowlist, prompt and model inventories | No LLM, shell or network tool execution | `test_local_tools.py`, `test_agent_example.py` |

## Implemented validators
Metadata (required fields, enums, unique IDs), relationship IDs and supersedes cycles,
ownership path authority, critical-date freshness, source/target mapping integrity, generator
byte drift, path-based human review impact, offline local links, key markers and tribal phrases.
CI artifacts contain actual test output; `make evidence` packages a scoped **unsigned** hash-
verifiable record. `make ci` also checks staged impact locally, or compares HEAD with `BASE`
when there is no staged change (CI supplies the PR base SHA). It uses pytest; no
line-coverage plugin/percentage is configured.

## Mapped but template-only
The 260 types have canonical/blank/synthetic-example templates, but a type is **not** an
instantiated document. A human-authored instance is checked for ownership/freshness only once
created under a controlled path; source-change review requires an explicit map rule. There is
no deterministic extractor for ADR rationale, risk acceptance, user guides, incident analysis,
security policies or other judgment-heavy catalog entries. Do not treat template completeness
as production documentation coverage.

## Partially supported
The task API source is a JSON registry, **not** OpenAPI. SQL is a deliberately narrow SQLite
subset; unsupported DDL fails. The alert file is not connected to production monitoring.
Dependencies are declared requirements, not installed packages, licenses or transitive SBOM.
External links are not checked offline. Local agent demos have no LLM or network provider.
Git-derived living-state blocks cannot infer a human next action. Code inventory cannot
establish runtime semantics or guarantee every dynamic symbol is represented.

## Explicitly not implemented

| Input | Status and reason |
| --- | --- |
| OpenAPI / AsyncAPI | `NOT_IMPLEMENTED`: no checked-in contract or parser mapping. |
| General YAML alerts or tool policies | `NOT_IMPLEMENTED`: examples accept only the JSON-compatible YAML subset; YAML syntax without a bounded parser fails. |
| Arbitrary SQL dialects and DDL | `NOT_IMPLEMENTED`: the SQLite demo parser only handles its declared CREATE TABLE subset; it refuses partial dictionaries. |
| TypeScript, Docker, Kubernetes and vendor APIs | `NOT_IMPLEMENTED`: no tested extractor or authoritative input/credential integration is configured. |
| External link reachability, live monitoring, signed evidence | `NOT_IMPLEMENTED`: offline guard only checks local links; there are no monitors, signing keys or approval policy. |

## Not supported / integration needed
OpenAPI/AsyncAPI and CLI parsing need real contracts plus tests. TypeScript/Docker/Kubernetes
extractors need project-specific parsers. Cloud cost, deployed services and vendor APIs need
scoped credentials and owners. Signed provenance requires key management and a verification
policy; GitHub issue creation and CODEOWNERS branch protection need owner approval. No
semantic prose correctness, line coverage or audit certification is claimed. Scope and effort
are project-dependent; do not quote estimates as measured facts.

## Known environment constraints
The go-task binary is not installed in this sandbox. The Taskfile delegates to Make but
`task ci` was not executable here; `make ci` is the canonical local verification path.
Python 3.11+ and pytest for development are declared in `pyproject.toml`; runtime extraction
uses the standard library. The owner has not selected a license, so release snapshots block.
