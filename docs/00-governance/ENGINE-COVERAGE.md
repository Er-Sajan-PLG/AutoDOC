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
| Python AST and ATX Markdown | Per-language code inventory and outline | Parsed declarations/headings, not behavior | `test_phase2.py`, `test_languages.py` |
| Declared toolchain (`go doc -all .`) | On-demand language reference (`make docs-languages SHOW=go`) | Runs the language's own tool inside the repository, offline and with a timeout; an absent tool is reported, never replaced | `test_languages.py` |
| Catalog rules file | `CATALOG-A/B/INDEX.yaml` | Seeds names; derives type, tier, `phase_min`, `applies_when`, maturity | `test_catalog.py` |
| Repository files | `profile.json` three-valued facts | File presence only; `unknown` when nothing could be read | `test_profile.py` |
| `autodoc.toml` `[facts]` traits | declared personal-data / payments / safety values | Declaration only; no detector exists, and unanswered is `unknown`, never false | `test_profile.py`, `test_resolver.py` |
| `autodoc.toml` + context model | Validated declared context | Declarations only; never inferred | `test_context.py` |
| Profile + catalog + context | Obligations with severity and `--check` | Phase-scaled; advisory without a declared phase | `test_resolver.py` |
| Fixture repositories | kind x phase x ecosystem matrix | Awkward cases: no manifest, unread ecosystem, docs-only | `test_profile.py` |
| Enforcement policy | severity per check family per phase | One precedence: override, phase default, report | `test_enforce.py` |
| Adoption baseline | suppressed findings and stale entries | Keyed by rule and location; never suppresses a new finding | `test_enforce.py` |
| Exit codes | `0`, `1`, `2` | Documented in `docs/reference/EXIT-CODES.md` | `test_enforce.py` |
| Catalogs/workflow files | Three views, CI inventory, completeness | Stable IDs and file hashes | `test_engine.py`, `test_phase3.py` |
| Frontmatter + sync map | Master/human inventories; JSON + Mermaid graph | References and actual mapped paths | `test_engine.py`, `test_phase3.py` |
| Local tool matrix/prompt files | Allowlist, prompt and model inventories | No LLM, shell or network tool execution | `test_local_tools.py`, `test_agent_example.py` |

## The generation contract
Every generator declares its exactness and its limits in one table in `scripts/doc-sync/engine.py`:
`exact` is the authoritative record of what it reads, `heuristic` is a bounded extraction that can
miss something of the kind it reports. The label and its limits are written into every generated
Markdown file, so a reader can judge the output without reading the generator; a heuristic
generator emits an advisory `generator.heuristic` finding by default, which the phase severity or
a `[severity]` pin can turn down but never turns into silent trust. No mapping may name a
generator without a label, and the label table is asserted to match the generator registry.

Per-language references follow the same rule and one more: a language gets a generator only where
its **own tool** can be integrated — AutoDOC never hand-rolls a parser for a language whose
toolchain exists — and a language with no generator is reported as **L0** (file and manifest facts
only) rather than guessed at. The runner executes the tool inside the repository with a scrubbed
environment, the toolchain's offline flags, no shell and a timeout, and a missing, failing or
hanging tool is reported with its reason. Python is extracted in-process with the interpreter's
own parser; Go integrates `go doc -all .`. A reference produced by an external toolchain is
printed on demand and never committed to a drift-checked target, because the same repository on
two machines would disagree.

## Implemented validators
Metadata (required fields, enums, unique IDs), relationship IDs and supersedes cycles,
ownership path authority, critical-date freshness, source/target mapping integrity, generator
byte drift, path-based human review impact, offline local links, key markers and tribal phrases.
`stub_check.py` also fails **approved** human documents with no section and no content beyond
their title, so a placeholder index cannot inflate the inventory or the health counts; drafts
warn instead. Generated targets are excluded because byte drift validates them, not prose volume.
The catalog index is validated against `CATALOG-SCHEMA.json` plus rule cross-checks (unknown
flags, mixed sentinels, core types without a reason or with an undetectable predicate, duplicate
ids, missing templates, and a vocabulary that no profiler detector backs). Predicate tokens are
checked against their own vocabularies too: `kind:<id>` must be a declared kind, `phase>=<id>` a
declared phase, and a kind is either detected from files by a detector that states its limits or
is explicitly declaration-only with a reason no file can tell.
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
