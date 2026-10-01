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

- **Sources of truth:** `CATALOG-*/INDEX.yaml` (JSON-compatible YAML) define document types and are
  **generated**: `CONTROL/metadata/CATALOG-RULES.json` holds the hand-seeded names plus every
  derived field (type, phase, maturity, `tier`, `applies_when`) and `build_catalogs.py` renders it,
  so classification is data a reviewer can diff rather than heuristics in Python.
  `CONTROL/metadata/CATALOG-SCHEMA.json` describes the index, and `check_catalog.py` validates it
  with an explicit keyword subset that fails on any keyword it does not implement, then cross-checks
  tiers, sentinels, templates and the flag vocabulary. `docs/.doc-sync-map.yaml` defines generated,
  human-review, living-state and changelog rules.
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
  Approved human documents must carry a section and content beyond their title; `stub_check.py`
  fails title-only index placeholders, while draft placeholders only warn.
- **Trust boundaries:** a sync map changed in a PR is code-like input. `safe_path` constrains
  generator targets to the checkout. Running user-supplied generator code in CI still executes
  untrusted PR code; use least-privilege `contents: read` and do not provide production secrets.
  No CI workflow pushes generated changes to a branch.
- **Freshness:** age checks block only overdue critical human-owned documents. Generated facts
  use drift checks instead. A draft status does not imply owner approval or branch protection.
- **Applicability is a decision, not an inference:**

      Obligations = Catalog x Context -> (applies?, severity, enforcement)

  `CONTROL/metadata/CONTEXT-MODEL.json` holds the phase ladder and the declared vocabularies
  (kinds, audiences, declared duties). `scripts/intelligence/context.py` reads `autodoc.toml`,
  applies the documented shorthands, and **fails on any unrecognised context**; a missing file is
  an empty context and an empty context is advisory-only. `scripts/intelligence/profile.py`
  records what files exist as fifteen **three-valued** facts (`true`, `false`, or `unknown`)
  and names three **declaration-only** traits, answered in `autodoc.toml` and never inferred.
  `unknown` is the honest answer when no configured source could be evaluated — a repository
  whose ecosystem has no reader, or one with no manifest at all — and it propagates: a predicate
  over an unknown fact yields **undetermined**, which is reported, never counted as satisfied and
  never failed. Every fact names its exactness (`exact` or `heuristic`) and its limits.

- **Severity scales with the declared phase, never with detection.** The phase sets what a
  violation *does*, family by family:

  | Phase | Missing required | Missing recommended | Structural breakage | Drift / freshness |
  | --- | --- | --- | --- | --- |
  | Idea, Prototype | Advisory | Advisory | Advisory | Off |
  | Build | Warn (baseline allowed) | Info | Fail | Off |
  | Beta | Fail | Warn | Fail | Warn |
  | Live, Mature | Fail | Warn | Fail | Fail |
  | Sunset | Only the sunset profile is active (status, license, security contact, deprecation or successor pointer, archive notes); everything else is off. | | | |

  An undeclared phase is advisory: nothing fails unless a pin says otherwise. Structural breakage means broken local links
  and unfilled placeholders. A core type also carries `phase_min`, so a type that is optional
  early and required later reads as `early` rather than as missing. Applicability and severity
  are separate: `recommend.py` decides whether a type applies, and the phase decides how hard
  that is enforced. A family at `off` is named in the report rather than silently skipped.

- **Kinds are declared, never inferred** (`scripts/intelligence/profile.py`,
  `scripts/intelligence/context.py`). `profile.py` holds a detector per detectable kind, each
  stating its exactness and limits, and the profile carries the evidence it found; kinds with no
  honest file evidence (`plugin`, `embedded`, `research`, `content`, `template`) carry a stated
  reason instead of a detector, so they can only ever be what an owner declares. `make docs-hint`
  shows the evidence; `kinds` in `autodoc.toml` is what counts. The two declaration-driven
  predicate tokens are three-valued for the same reason: `kind:<id>` is `unknown` until kinds are
  declared (then true or false), and `phase>=<id>` is `unknown` until a phase is declared (then a
  real comparison), so a repository whose owner has not answered yet gets *undetermined* — which
  is reported and never failed — rather than a verdict from a guess. A repository with no
  detector matches and no declaration is on the generic baseline: only requirements that do not
  depend on a kind or a phase apply.

- **Traits are declared, never inferred** (`scripts/intelligence/profile.py`). Three facts —
  `handles_personal_data`, `handles_payments`, `safety_critical` — describe the world, not the
  file tree, so no detector exists for them and none can be added: an `email` column may hold a
  business address, a table of hashes may still be personal data, and a `payments/` directory is
  code, not a live payment flow. They carry a stated reason instead of sources — the same honesty
  rule the declaration-only kinds follow — and `check_catalog.py` refuses a fact that claims both
  routes, claims neither, or has no catalog consumer. Until the owner answers in `autodoc.toml`
  `[facts]`, the value is `unknown` and every document that depends on it is **undetermined**;
  a declared `true` activates exactly those documents. The applicable report states each answer
  with its reason, `--hint` prints the open questions, and the catalog consumes the traits so the
  forms are exercised rather than merely allowed: the PII inventory, the new Cardholder data flow
  and Hazard analysis (each core, required once its trait is true), and the deeper privacy set.

- **The catalog states what it can and cannot verify** (`CATALOG-SCHEMA.json`, `CATALOG-RULES.json`).
  Each type carries the reader question it answers, who reads it, the lifecycle events that make
  it stale, the checks that apply to it, and a `support` level: `checked` (named checks run),
  `template-only` (a template exists and nothing is verified) or `human` (no detector is
  possible). An admission rule enforces the combination, so a type cannot claim to be checked
  without naming a check, and a type nothing can detect cannot be required of anyone.
  `severity_by_phase` is the authored answer to when a type lands; `phase_min` is derived from it
  by the generator, which is why the two can never disagree.

- **Which types are core is a declared profile, not a constant**
  (`CONTROL/metadata/PROFILES.json`). `default` is the hand-picked list in the catalog rules;
  `startup`, `oss-library`, `internal-service` and `regulated` are deltas of it, each addition
  carrying a reason and the phases it is off in. `profile` in `autodoc.toml` selects one, and the
  report states the resulting core set with its additions and removals. A removed type is off
  with the profile's reason rather than silently dropped, and a type that is off at the current
  phase is listed with the phase it lands at — an off check is a decision, never a silent skip.

- **Enforcement is one policy, applied once** (`scripts/intelligence/enforce.py`). Every check
  family — requirements, drift, stubs, placeholders, local links, committed key markers, tribal
  instructions and freshness — resolves its severity through the same precedence: an explicit
  `[severity]` override in `autodoc.toml`, then the declared phase's enforcement block, then
  `report`. An undeclared phase reports everything and fails nothing. This repository declares
  `phase = "build"` and keeps four pins that are deliberately stricter than that block (`stubs`,
  `tribal`, both `freshness.*`); a pin that merely repeated the phase default was removed as
  noise. Findings carry rule id, severity, location, reason, fix hint and the context that caused
  them ("phase=build and has_public_api_surface=true"); the machine output carries the same as
  `because`, `enforced` (true/false) and `enforced_reason`, and the report states the capability
  level that ran. Undetermined items are reported and never failed.

- **Adoption has a baseline** (`autodoc-baseline.json`, machine-generated, schema in
  `CONTROL/metadata/BASELINE-SCHEMA.json`). Findings recorded during adoption are suppressed and
  counted; findings that no longer occur are listed as stale so the ratchet can be pruned with
  `--write-baseline`. A new violation is never suppressed by an old entry, because entries are
  keyed by rule and location.

- **The resolver** (`scripts/intelligence/recommend.py`) joins profile, catalog and the recorded
  decisions in `autodoc.toml` — `[instantiated]`, `[satisfied_by]` (locations that count, local
  paths verified and URLs recorded but never fetched) and `[not_applicable]` (a reason is
  mandatory). A skip whose predicate is now true is reported as a **stale decision** and
  re-surfaced. `--check` fails only what the declared phase says must fail, and `--explain`
  prints the derivation chain for one requirement. `assess` marks the 81 types with no detectable
  predicate, so they are never auto-recommended. The fact vocabulary is closed: `check_catalog.py`
  fails on a predicate token nothing can detect, and on a fact no catalog entry consumes.

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
