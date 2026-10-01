---
id: DOC-P3-GOV-008
title: "Project charter — problem, goals and scope"
type: REF
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
# Project charter — problem, goals and scope

## Purpose and scope

This charter states, in one place, why AutoDOC exists, what it is trying to achieve and where its
boundary lies. It is the document the catalog types `DEV-B01-001` Problem statement,
`DEV-B01-002` Goals and non-goals and `DEV-B01-003` Scope are satisfied by
(`[satisfied_by]` in `autodoc.toml`). It records intent; the enforceable detail lives in
`AUTODOC.md`, `docs/05-architecture/AUTODOC-ARCHITECTURE.md` and `CONTROL/metadata/*`.

## Problem statement

Documentation in software repositories decays in a predictable way. The documents a project owes
depend on what kind of project it is and how mature it is, but that dependency is rarely written
down; documents are produced once and then drift from the code; and the checks that exist are ad
hoc, so nobody can say which obligations were verified, which were skipped, and why. Tools in this
space tend to add one of two failure modes of their own: generators that silently produce stale
output, or checkers that assert far more than they can prove — including, at worst, “compliance”
nobody demonstrated.

AutoDOC is built for a maintainer who wants four things from one tool: a catalog of the document
*types* that can apply, facts about the repository that decide which of them actually apply,
enforcement at a severity that matches the project's declared phase, and an honest record — in the
tool's own output — of what was checked, what was skipped, and what cannot be verified at all.

## Goals and non-goals

**Goals.**

1. Make documentation obligations **declarative**: types, phases, facts and decisions are data a
   reviewer can diff (`CATALOG-A/B`, `CONTROL/metadata/*`, `autodoc.toml`), not heuristics in code.
2. Be **phase-aware and proportional**: a prototype is advised, a beta is warned, a live project is
   failed — the same repository, different enforcement, decided by a declared phase
   (`docs/00-governance/CORE-LIST-REVIEW.md` Part 0).
3. Stay **truthful about its own limits**: every generator is labeled `exact` or `heuristic`, every
   skipped check carries a reason, and evidence is described as unsigned when it is
   (`docs/00-governance/LIMITATIONS.md`, `docs/00-governance/ENGINE-COVERAGE.md`).
4. **Integrate rather than reimplement**: use each language's own toolchain where one exists, and
   say so when nothing does (L0), instead of hand-rolled parsers.
5. Remain **local and dependency-free at runtime**: the engine runs offline from the standard
   library (`docs/adr/0001-zero-runtime-dependencies.md`), so adopting it does not add a supply
   chain to the adopter's repository.

**Non-goals.**

1. **Not a compliance certificate.** AutoDOC checks that records exist and are structured; it never
   certifies that a document is true, that a control works, or that a project is compliant — say
   so in every report, and never let a green run be presented as more than it is.
2. **Not a judge of prose.** Semantic correctness, adequacy and architecture rationale are human
   review, only ever detected as *missing co-changes*, never proven.
3. **Not a hosted service and not a network tool by default.** No accounts, no telemetry; the one
   network check is scheduled, rate-limited and warn-only.
4. **Not an inference engine for intent.** Phase, kinds, obligations, profiles and sensitive-data
   traits are declarations; evidence is a hint the owner may accept or reject.
5. **Not a replacement for a project's own governance.** Ownership, approvals and branch protection
   stay with the repository's owners and its platform settings.

## Scope

**In scope:** this repository's engine, catalog, rules and metadata; the enforcement and reporting
it performs on a repository that has adopted it; its own governance, evidence and examples; and the
documented checks it declares (presence, structure, placeholders, local links, review dates,
generator drift, triggers, catalog consistency).

**Out of scope:** the correctness of a project's code or infrastructure; security scanning of
dependencies; legal or regulatory advice; any claim about an external system that a configured
extractor does not read; and documentation of a repository that has not adopted AutoDOC and
configured its `docs/.doc-sync-map.yaml` and sources.

**Boundary rule.** When a fact, a decision or an enforcement outcome cannot be established from the
repository's own files and declarations, the correct behavior is to say so — `unknown`, `undetermined`
or “reported, not checked” — never to guess.

## Verification and references

- `AUTODOC.md` — the four boundaries (inventory, facts, judgment, proof).
- `docs/05-architecture/AUTODOC-ARCHITECTURE.md` — module contracts and trust boundaries.
- `docs/00-governance/LIMITATIONS.md`, `docs/00-governance/ENGINE-COVERAGE.md` — what is verified
  and what is not.
- `docs/00-governance/ADOPTION.md` — which catalog types this repository itself instantiates.
