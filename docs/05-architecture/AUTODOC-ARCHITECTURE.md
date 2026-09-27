---
id: DOC-ARC-001
title: "AutoDOC architecture"
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
related: ["DOC-AUTO-001", "DOC-CI-001", "DOC-CAT-001"]
criticality: high
review_days: 180
last_verified: 2026-09-26
last_reviewed: 2026-09-26
last_updated: 2026-09-26
auto_generated: false
---
# AutoDOC architecture

## Purpose and scope
AutoDOC is a dependency-free Python documentation control system for this repository and
a task API and two educational local tool-authorization examples. It indexes possible documents, generates a bounded set of factual
references and checks source-to-document impact. It does **not** execute controls listed in a catalog.

## Details and decisions

```text
Authoritative catalogs / source files / Markdown metadata
                 |              |                |
                 v              v                v
           library.py      docs/.doc-sync-map   frontmatter_validator.py
                 |              |                |
                 v              v                v
          TEMPLATES/        engine.py          MASTER-INDEX
                                |
              generation / drift / PR impact / freshness
                                |
                       pre-commit and CI
```

- **Sources of truth:** `CATALOG-*/INDEX.yaml` (JSON-compatible YAML) define document types;
  `docs/.doc-sync-map.yaml` defines generated, human-review, living-state and changelog rules.
  The task API routes, config, described environment, bounded SQL and alert declaration have
  separate sources; tool examples have explicit authorization sources and no LLM or network.
- **Generated facts:** `engine.py` renders in memory for drift checks. Generator outputs are
  deterministic and checked into the branch. Catalog and workflow references are derived from
  their version-controlled sources; workflow hashes make edits visible without a YAML parser.
- **Human reasoning:** architecture, adoption decisions, policy and next-action text are reviewed
  by a person. A path-based PR impact check can require a co-change, not certify its correctness.
- **Additional bounded extractors:** `engine/extractors/facts.py` parses Python AST declarations
  and tests, ATX Markdown headings and PEP 621 manifests. It does not infer behavior, installed
  dependencies or parse arbitrary TypeScript/OpenAPI. The three catalog views are derived from
  the original 260 stable IDs, not a duplicated catalog. The task route/SQLite/config
  renderers reject unsupported records rather than producing a deceptively complete reference.
- **Evidence and release:** CI runs tests and uploads an unsigned, hash-verifiable pack to a run
  artifact. No pack or timestamps are committed. The release-tag snapshot workflow fails closed
  until a license is selected; snapshot artifacts are not permanent external retention.
- **Metadata and ownership:** the frontmatter schema and ownership matrix validate instantiated
  controlled docs. The master index, human-owned inventory and relationship graph come from frontmatter.
  The Mermaid reference adds concrete source-to-target and catalog-to-template edges.
  Template examples are synthetic. The agent working-state helper only changes observable blocks.
- **Trust boundaries:** a sync map changed in a PR is code-like input. `safe_path` constrains
  generator targets to the checkout. Running user-supplied generator code in CI still executes
  untrusted PR code; use least-privilege `contents: read` and do not provide production secrets.
  No CI workflow pushes generated changes to a branch.
- **Freshness:** age checks block only overdue critical human-owned documents. Generated facts
  use drift checks instead. A draft status does not imply owner approval or branch protection.

## Verification and references
Run `make ci` (or `python -m unittest discover -s tests -v` offline), `python scripts/doc-sync/check-doc-drift.py`,
`python scripts/doc-control/library.py --check`, and the metadata, ownership and freshness checks.
The actual workflow names and fingerprints are in `docs/generated/WORKFLOW-REFERENCE.md`.
Review `CONTROL/policies/DOCUMENTATION-POLICY.md` for the enforcement matrix and limits.

## Phase 3 trust boundaries
`make ci` is the canonical local harness; go-task delegates to make if installed. Strict
`env_alerts.py` rejects undocumented environment keys and alerts without an existing runbook.
`local-tools-example` uses a closed JSON-compatible YAML policy, pure functions, and confined
read-only files; blocked network/shell tools do not execute. CI evidence records real JUnit
counts and hashes but is unsigned. A green check cannot configure protected branches.
