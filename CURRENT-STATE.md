---
id: CURRENT-STATE-MD
title: "Current state"
type: REF
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
criticality: medium
review_days: 180
last_verified: 2026-09-26
last_reviewed: 2026-09-26
last_updated: 2026-09-26
auto_generated: false
---
# Current state

AutoDOC has a working sync map, standard-library runtime, three authoritative catalog indices,
260 template triples, a task API demo and two local tool-policy demonstrations without an LLM or web calls.
Its checks validate controlled-document metadata, generated drift, age and source-to-human-review impact.
A catalog entry represents a possible document, not a completed compliance obligation.

The demo includes structured agent context and CI can retain actual test-run evidence as an artifact.

A health command measures catalog template triples, instantiated docs, deadlines and drift.
The human inventory, relationship graph, catalog views and code/test/dependency outlines are generated.
CI packages actual test-run evidence without claiming a signed build or license approval.
The release-tag workflow fails closed while `LICENSE-CHOICE.md` remains pending.

AutoDOC now self-hosts its catalog and workflow inventories. Catalog and control-code changes
are mapped to human adoption or architecture review; declared ownership is checked in CI.

The catalog is generated from `CONTROL/metadata/CATALOG-RULES.json` and validated against
`CATALOG-SCHEMA.json`, so document type, tier, phase, maturity and applicability are data a
reviewer can diff. `priority` is gone: it came from three domain prefixes and classified UAT as
core for every project. It is replaced by 24 hand-picked core types — including `README`, which
was missing from all 260 — each with a recorded reason, a detectable `applies_when` predicate
and an authored `severity_by_phase` (the phases it is off in; `phase_min` is derived, never a
second source), over 45 extended and 194 contextual types.

Which of those types count as core is now a profile, not a constant: `CONTROL/metadata/PROFILES.json`
holds `default`, `startup`, `oss-library`, `internal-service` and `regulated` as small deltas of
the default set, each addition carrying a reason and its own phases. This repository declares
`profile = "oss-library"`, which adds the code of conduct, the vulnerability-disclosure route and
the dependency policy, and drops the runbook; the addition of `License` (DOC-A10-008) states the
redistribution terms the license decision still owes. Every type any profile can list passes the
admission rule — a reader question, a detectable predicate, its phases, and named checks or an
explicit template-only/human label — and `check_catalog.py` fails when one does not.

Requirements resolve as Catalog x Context: a declared context in `autodoc.toml` (phase, audience,
kinds, declared duties) against fifteen three-valued facts, so a fact that cannot be read makes a
type **undetermined** rather than silently satisfied. Severity scales with phase, per column:
`build` warns about required docs and fails structural breakage with drift and freshness off;
`beta` adds drift and freshness as warnings; `live` and `mature` fail all four; `sunset` shrinks
to the sunset profile. This repository declares `build` (2026-09-30), so its 16 applicable
core types are surveyed against that phase: 7 are acknowledged, and the missing required ones
warn rather than fail. Kind inference is not
implemented, so declared kinds are inert and no predicate uses `kind:` yet.

<!-- auto:start -->
- Catalog types: 263 (not necessarily instantiated).
- Controlled docs: 65 (23 generated, 42 human-owned).
- Overdue human-owned docs: 0.
- Open gaps: see `docs/00-governance/ENGINE-COVERAGE.md`; this block does not infer intent.
<!-- auto:end -->
