---
id: DOC-P3-ADR-001
title: "ADR-0001: Keep the runtime dependency-free"
type: DEC
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "0.1"
effective_date: 2026-10-01
next_review: 2027-03-30
source_of_truth: human
supersedes: null
related: []
criticality: medium
review_days: 180
last_verified: 2026-10-01
last_reviewed: 2026-10-01
last_updated: 2026-10-01
auto_generated: false
---
# ADR-0001: Keep the runtime dependency-free

- **Status:** accepted — recorded 2026-10-01 during the core-list review (decision 3); the
  constraint has been in force since the engine was written and is stated here for the first time.
- **Decision owner:** repository owner (`@Er-Sajan-PLG`) as the accountable party for the policy.
- **Supersedes:** nothing. **Superseded by:** nothing.

## Context

AutoDOC is a tool people run *inside their own repositories*, usually inside CI, often offline.
Anything it imports at runtime becomes part of its adopters' supply chain, their install
instructions and their security review. The engine's work — parsing manifests, walking file trees,
generating Markdown, diffing in memory — is served by the Python standard library, and the
configuration formats were chosen accordingly (`autodoc.toml` is read with `tomllib`, catalogs are
JSON-compatible YAML read with the standard library, machine policy is JSON written by
`json_style.dumps`).

## Decision

Keep the **runtime** dependency set empty. `pyproject.toml` declares `dependencies = []`; the
engine imports only the standard library and its own modules. Third-party packages are allowed
only as **development** extras (`pytest`, `pre-commit`), declared as bounded ranges, installed by
`make setup`, and never imported by shipped code.

## Consequences

**Positive.** Adopters add no transitive dependencies; the tool installs and runs offline with
`python3`; there is no resolution drift between environments, and no runtime dependency can be
vulnerable in an adopter's tree because AutoDOC put it there.

**Negative, and accepted.** Format support is hand-written and will always be a documented subset:
the SQL parser reads simple `CREATE TABLE` statements and fails on anything else; there is no TOML
*writer*; YAML is restricted to the JSON-compatible subset. Features that other projects get from a
library — rich YAML, templating engines, CLI frameworks — are either implemented narrowly or
deliberately absent (`argparse` instead of `click`).

**Neutral.** This is a policy, not an automated gate: nothing fails a build if a runtime import
appears, and `check_catalog` does not read `pyproject.toml`. Enforcement is review plus the
documented process in `CONTRIBUTING.md` (a runtime dependency needs an owner decision recorded as
an ADR here).

## Alternatives considered

1. **Adopt PyYAML + tomli-w + click.** Rejected: convenience that shifts parsing fidelity and
   supply-chain exposure onto adopters, for a tool whose selling point is being inspectable.
2. **Vendor the small helpers.** Rejected: vendored code still needs licence tracking and updates
   while looking dependency-free; worse honesty for the same effort.
3. **Dev-only convenience libraries.** Kept where they earn their place (`pytest`, `pre-commit`),
   because they never ship to adopters.

## Verification and references

- `pyproject.toml` — `dependencies = []`; dev extras with bounded ranges.
- `CONTRIBUTING.md` § Dependencies — the process for changing either set.
- `docs/00-governance/ENGINE-COVERAGE.md` § Known environment constraints — what the offline,
  stdlib-only posture costs in supported scope.
