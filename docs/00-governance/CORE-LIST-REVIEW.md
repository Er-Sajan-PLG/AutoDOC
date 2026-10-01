---
id: DOC-P3-GOV-006
title: "Core list review — full context for the owner decision"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "1.1"
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
# Core list review — full context for the owner decision

The 27 core types in `CONTROL/metadata/CATALOG-RULES.json` and the five profile deltas in
`CONTROL/metadata/PROFILES.json` are authored policy: they decide which documents AutoDOC calls
required, recommended or not applicable for every project that uses it. They were written and
validated by tooling and have never been read end to end by the owner, so every report that trusts
them carries a "pending owner review" caveat.

This page exists to remove that caveat in one sitting, with enough context that no row is a
guess. Part 1 is the markable sheet; Parts 2–4 explain every row, every profile and the six places
where a reasonable owner could decide differently.

## How to read this page

**What "core" does, mechanically.** A core type is one of the 27 types the catalog calls part of the essential set. Being core does not make it required everywhere: two further switches decide that.

- **Applicability** — every type carries an `applies_when` predicate (`always`, `has_tests`, `is_public`, `has_deploy`, `handles_personal_data`, …). The predicate is evaluated against detected facts and your declarations, three-valued: `true` applies, `false` does not apply, and `unknown` leaves the type undetermined rather than silently satisfied.
- **Phase** — a type is required from its `phase_min` upward. Under the declared phase, a missing core type takes that phase's severity: **report** in idea/prototype, **warn** in build (a baseline is allowed), **fail** from beta onward. Extended types are one level softer (report → warn); contextual types are never enforced.

| Phase | Missing core type | Missing extended type | Structural checks (drift, stubs, links, secrets, freshness) |
| --- | --- | --- | --- |
| idea / prototype | report | report | report only; drift and freshness off |
| build (this repository) | **warn** | report | placeholders/links/secrets fail; drift and freshness off |
| beta | **fail** | warn | drift warns, freshness warns, the rest fail |
| live / mature | **fail** | warn | everything fails |
| sunset | fail | off | only the sunset documents are active |

**What the checks actually assert.** All 27 rows are `checked` with `human-review` mode: AutoDOC checks that the file exists, is not a stub, has no placeholder text, has resolving local links, and is not past its review date. It never judges whether the content is *good* — that stays with the human reviewer, and AutoDOC never certifies compliance.

**Your escapes.** Every open row can be answered without writing a new document: `[instantiated]` names the file that is that document, `[satisfied_by]` points where the content already lives (including a wiki or docs site), and `[not_applicable]` records a reasoned skip. Unknown ids are errors, a missing reason on a fact override is an error, and a skip is re-surfaced if the fact behind it later becomes true.

**What this review decides — and what it does not.** Approving means: the 27 rows and 5 profile deltas are what the owner intends, so the "pending owner review" caveat is removed and the list can be trusted as *declared policy* rather than tool output. Approving changes **no behaviour**: the same rows are enforced the same way tomorrow. Flagging a row turns it into a small data change (the rule, the profile or the predicate) plus re-validation. This review does **not** close the 12 open decisions — that is the next item, and it is what moves the repository from 7/19 to 19/19 build-ready.

**Common misreadings to avoid.**

- *"Core means required now here."* Only if the predicate is true and the phase has arrived: 9 rows are open here, 7 are closed, 6 are off until beta/live/mature, 5 are not applicable.
- *"Not applicable means the type is wrong."* It means the predicate is false for this project (`has_deploy = false`), or the owner declared the trait false — the question was answered, not dodged.
- *"A required document means a compliance claim."* AutoDOC checks records exist and are structured; it never asserts that the content satisfies an external standard.
- *"Approving adds work."* It adds none. The obligations already behave exactly as this page describes; approval removes the caveat that the policy itself was never read.

**The numbers behind the list:** 265 document types in the catalogs — 27 core, 46 extended, 192 contextual — plus 6 control artifacts in CATALOG-C that are not document types. The five profiles are deltas on the default core set, listed further down.

## Part 1 — the sheet: mark any row you would change

Everything blank is approved. The ✎ column is the only thing to edit.

| ✎ | ID | Name | Reader question | Why it is core | Applies when | Required from | In this repository today |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ☐ | `DEV-B01-001` | Problem statement | What problem does this project solve, and for whom? | Every project needs a stated reason to exist. | `always` | idea | Open here |
| ☐ | `DEV-B01-002` | Goals and non goals | What is this trying to achieve, and what is it deliberately not doing? | Non-goals prevent the scope creep that no check can detect. | `always` | idea | Open here |
| ☐ | `DEV-B01-003` | Scope | Where is the boundary of this system? | The boundary of what the system covers. | `always` | idea | Open here |
| ☐ | `DEV-B01-006` | README | What is this, why does it exist, and how do I know it works? | The first and most-read document: what it is, why it exists and whether it works. | `always` | idea | Open here |
| ☐ | `DEV-B04-001` | System overview | What are the parts of this system and how do they fit together? | One map of the parts, for newcomers and agents. | `always` | build | Closed here |
| ☐ | `DEV-B04-002` | ADR | Why was this decision made, and what did we give up? | Decisions are the highest-churn human knowledge in a repository. | `always` | build | Open here |
| ☐ | `DEV-B05-001` | Module contract | What does this module promise to its callers? | Module boundaries are where changes break neighbours. | `always` | build | Open here |
| ☐ | `DEV-B07-001` | Test strategy | How do we establish confidence that this works? | States how confidence is established; the canonical form of this type. | `has_tests` | build | Open here |
| ☐ | `DEV-B08-001` | Current state | What is true right now? | Working context; the substrate AutoDOC itself runs on. | `always` | build | Closed here |
| ☐ | `DEV-B08-002` | Next action | What is the next thing to do, and by whom? | Human priorities must be recorded, never inferred from Git. | `always` | build | Closed here |
| ☐ | `DEV-B08-003` | Recent changes | What changed lately, and why? | A short delta log beats reading raw commit history. | `always` | build | Closed here |
| ☐ | `DEV-B09-001` | AGENTS.md | What must an agent know before touching this repository? | The context file an agent reads first. | `uses_agents` | build | Closed here |
| ☐ | `DEV-B10-001` | Local setup | How do I get this running on my machine? | Nobody can run the project without it. | `always` | build | Closed here |
| ☐ | `DEV-B10-003` | Dependency setup | Which dependencies, at which versions, and how are they updated? | Direct dependencies and version policy; the most common onboarding failure. | `always` | build | Open here |
| ☐ | `DOC-A05-001` | Data model | What entities exist, how do they relate, and what do they mean? | Entities and relationships before schema detail. | `has_persistent_state` | build | Open here |
| ☐ | `DOC-A08-001` | OpenAPI | What is the machine-readable contract for this interface? | The machine-readable contract for a machine-callable interface. | `has_public_api_surface` | beta | Off here |
| ☐ | `DOC-A09-005` | Contributing guide | How do I contribute, and what will be expected of me? | Outside contributors need the contribution path. | `is_public` | live | Closed here |
| ☐ | `DOC-A10-008` | License | May I use, change and redistribute this, and on what terms? | Redistribution terms; without them nobody may legally reuse the work. | `is_public` | beta | Off here |
| ☐ | `DOC-A14-005` | Environment variable schema | Which environment variables exist, and what do they do? | Every environment variable and its meaning. | `has_env` | beta | Off here |
| ☐ | `DOC-A15-003` | Changelog | What changed between the version I have and the one I am upgrading to? | Consumers of a distributed project need a version delta. | `is_public` | beta | Off here |
| ☐ | `DOC-A15-006` | Rollback procedure | How do I undo this release if it goes wrong? | Reversing a bad release must be written before it is needed. | `has_deploy` | beta | Not applicable here |
| ☐ | `DOC-A16-003` | Runbook | What do I do when this alerts? | Operators need a procedure for the deployed service. | `has_deploy` | live | Not applicable here |
| ☐ | `DOC-A22-004` | API quickstart | How do I make my first successful call? | Shortest path to a first successful call. | `has_public_api_surface` | beta | Off here |
| ☐ | `DOC-A23-001` | Deprecation policy | What does this project promise before removing something? | Published interfaces need a removal promise before they are removed. | `is_public` | mature | Off here |
| ☐ | `DOC-A05-009` | PII inventory | What personal data does this hold, where did it come from, and who can see it? | Personal data nobody has mapped is data nobody can protect, delete or explain. | `handles_personal_data` | build | Not applicable here |
| ☐ | `DOC-A06-011` | Cardholder data flow | Where does card data live, move and stop, and what keeps it out of reach? | Card data has to be located before its flow can be limited, segmented or defended. | `handles_payments` | build | Not applicable here |
| ☐ | `DOC-A20-008` | Hazard analysis | What can this system do to a person or the world, and what stops it? | A hazard that is never written down is not controlled, and a safety claim without its failure modes is not a claim anyone can check. | `safety_critical` | prototype | Not applicable here |

## Part 2 — full context, row by row

Grouped by catalog domain, in the order of the sheet. "Needed" is the lifecycle the type serves: `when` is when the document matters, maturity is the state it belongs to, and the phase is when it stops being optional.

### B01-FOUNDATION

#### `DEV-B01-001` · Problem statement
- **What it is.** Record problem statement for context and goals.
- **It answers.** "What problem does this project solve, and for whom?" — read by **contributors**; the project owner owns it.
- **Required from** `idea` · needed during active development · maturity Project-Phase · life-cycle events: `direction-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* one `docs/00-governance/PROJECT-CHARTER.md` with three named sections can satisfy this row and its two siblings; then record `[satisfied_by]`.

#### `DEV-B01-002` · Goals and non goals
- **What it is.** Record goals and non goals for context and goals.
- **It answers.** "What is this trying to achieve, and what is it deliberately not doing?" — read by **contributors**; the project owner owns it.
- **Required from** `idea` · needed during active development · maturity Project-Phase · life-cycle events: `direction-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* same charter page, second section; record `[satisfied_by]`.

#### `DEV-B01-003` · Scope
- **What it is.** Record scope for context and goals.
- **It answers.** "Where is the boundary of this system?" — read by **contributors**; the project owner owns it.
- **Required from** `idea` · needed during active development · maturity Project-Phase · life-cycle events: `direction-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* same charter page, third section; record `[satisfied_by]`.

#### `DEV-B01-006` · README
- **What it is.** Record readme for context and goals.
- **It answers.** "What is this, why does it exist, and how do I know it works?" — read by **external-users**; the project owner owns it.
- **Required from** `idea` · needed during active development · maturity Project-Phase · life-cycle events: `release`, `onboarding`.
- **Checks that run on it:** `presence`, `links.local`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* `README.md` already exists — record `[instantiated] = "README.md"`.

### B04-ARCHITECTURE

#### `DEV-B04-001` · System overview
- **What it is.** Record system overview for early architecture.
- **It answers.** "What are the parts of this system and how do they fit together?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `api-change`, `direction-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `docs/05-architecture/AUTODOC-ARCHITECTURE.md` is the instance; keep it reviewed.

#### `DEV-B04-002` · ADR
- **What it is.** Record adr for early architecture.
- **It answers.** "Why was this decision made, and what did we give up?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `direction-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* either start `docs/adr/` with one real decision, or record `[not_applicable]` saying decisions live in ADOPTION.md (dated), the changelog (user-facing) and machine policy.

### B05-CONTRACTS

#### `DEV-B05-001` · Module contract
- **What it is.** Record module contract for implementation contracts.
- **It answers.** "What does this module promise to its callers?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `api-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* record `[satisfied_by]` the module-boundaries section of `docs/05-architecture/AUTODOC-ARCHITECTURE.md`.

### B07-TESTING

#### `DEV-B07-001` · Test strategy
- **What it is.** Record test strategy for validation.
- **It answers.** "How do we establish confidence that this works?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `release`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* record `[satisfied_by]` `docs/00-governance/ENGINE-COVERAGE.md` — what is verified, how, and the limits.

### B08-TRACKING

#### `DEV-B08-001` · Current state
- **What it is.** Record current state for handoff and tracking.
- **It answers.** "What is true right now?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `CURRENT-STATE.md` is the instance; keep it reviewed.

#### `DEV-B08-002` · Next action
- **What it is.** Record next action for handoff and tracking.
- **It answers.** "What is the next thing to do, and by whom?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `NEXT-ACTION.md` is the instance; keep it reviewed.

#### `DEV-B08-003` · Recent changes
- **What it is.** Record recent changes for handoff and tracking.
- **It answers.** "What changed lately, and why?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `RECENT-CHANGES.md` is the instance; keep it reviewed.

### B09-AGENT-CONTEXT

#### `DEV-B09-001` · AGENTS.md
- **What it is.** Record agents.md for ai agent context.
- **It answers.** "What must an agent know before touching this repository?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `onboarding`, `change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `AGENTS.md` is the instance; keep it reviewed.

### B10-SETUP

#### `DEV-B10-001` · Local setup
- **What it is.** Record local setup for project setup.
- **It answers.** "How do I get this running on my machine?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `onboarding`, `dependency-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `QUICK-START.md` is the instance; keep it reviewed.

#### `DEV-B10-003` · Dependency setup
- **What it is.** Record dependency setup for project setup.
- **It answers.** "Which dependencies, at which versions, and how are they updated?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `dependency-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* record `[satisfied_by]` `QUICK-START.md`, or add a short dependencies section to it.

### A05-DATA

#### `DOC-A05-001` · Data model
- **What it is.** Record data model for data and information management.
- **It answers.** "What entities exist, how do they relate, and what do they mean?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during pre-release · maturity Hardened · life-cycle events: `schema-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` (build warns, beta fails). *A path to close it:* the predicate fires only because the demo ships `db/schema.sql`; declaring `has_persistent_state = false` (the demo is a fixture) makes this row not applicable.

### A08-APIS

#### `DOC-A08-001` · OpenAPI
- **What it is.** Record openapi for apis and interfaces.
- **It answers.** "What is the machine-readable contract for this interface?" — read by **external-users**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during pre-release · maturity Hardened · life-cycle events: `api-change`, `release`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` (not required before beta).

### A09-DEVELOPMENT

#### `DOC-A09-005` · Contributing guide
- **What it is.** Record contributing guide for development process.
- **It answers.** "How do I contribute, and what will be expected of me?" — read by **contributors**; the project owner owns it.
- **Required from** `live` · off in `idea`, `prototype`, `build`, `beta` · needed during active development · maturity Hardened · life-cycle events: `onboarding`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `CONTRIBUTING.md` is the instance; keep it reviewed.

### A10-BUILD

#### `DOC-A10-008` · License
- **What it is.** Record license for build and supply chain.
- **It answers.** "May I use, change and redistribute this, and on what terms?" — read by **external-users**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during pre-release · maturity Hardened · life-cycle events: not tied to an event.
- **Checks that run on it:** `presence`, `links.local`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` (not required before beta).

### A14-CONFIGURATION

#### `DOC-A14-005` · Environment variable schema
- **What it is.** Record environment variable schema for configuration and change.
- **It answers.** "Which environment variables exist, and what do they do?" — read by **operators**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during pre-release · maturity Hardened · life-cycle events: `dependency-change`, `api-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.critical`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` (not required before beta).

### A15-RELEASE

#### `DOC-A15-003` · Changelog
- **What it is.** Record changelog for release and deployment.
- **It answers.** "What changed between the version I have and the one I am upgrading to?" — read by **external-users**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during post-release · maturity Product-Grade · life-cycle events: `release`.
- **Checks that run on it:** `presence`, `stubs`, `links.local`, `freshness.review`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` (not required before beta).

#### `DOC-A15-006` · Rollback procedure
- **What it is.** Record rollback procedure for release and deployment.
- **It answers.** "How do I undo this release if it goes wrong?" — read by **operators**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during post-release · maturity Product-Grade · life-cycle events: `release`, `incident`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.critical`.
- **In this repository:** **Not applicable here** — `has_deploy` is declared `false`; the answer is re-surfaced if the declaration changes.

### A16-OPERATIONS

#### `DOC-A16-003` · Runbook
- **What it is.** Record runbook for operations and observability.
- **It answers.** "What do I do when this alerts?" — read by **operators**; the project owner owns it.
- **Required from** `live` · off in `idea`, `prototype`, `build`, `beta` · needed during post-release · maturity Product-Grade · life-cycle events: `incident`, `dependency-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.critical`.
- **In this repository:** **Not applicable here** — `has_deploy` is declared `false`; the answer is re-surfaced if the declaration changes.

### A22-USER-SUPPORT

#### `DOC-A22-004` · API quickstart
- **What it is.** Record api quickstart for user and support.
- **It answers.** "How do I make my first successful call?" — read by **external-users**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during post-release · maturity Product-Grade · life-cycle events: `api-change`, `onboarding`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` (not required before beta).

### A23-LIFECYCLE

#### `DOC-A23-001` · Deprecation policy
- **What it is.** Record deprecation policy for lifecycle management.
- **It answers.** "What does this project promise before removing something?" — read by **external-users**; the project owner owns it.
- **Required from** `mature` · off in `idea`, `prototype`, `build`, `beta`, `live` · needed during post-release · maturity Product-Grade · life-cycle events: `retirement`, `api-change`.
- **Checks that run on it:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `mature` (not required before mature).

### A05-DATA

#### `DOC-A05-009` · PII inventory
- **What it is.** Record pii inventory for data and information management.
- **It answers.** "What personal data does this hold, where did it come from, and who can see it?" — read by **auditors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during pre-release · maturity Hardened · life-cycle events: `incident`, `release`.
- **Checks that run on it:** `presence`, `links.local`.
- **In this repository:** **Not applicable here** — `handles_personal_data` is declared `false`; the answer is re-surfaced if the declaration changes.
- **Why the trait gate matters:** This is the reason the row exists: the question is asked, not assumed. Answering the trait activates the type.

### A06-SECURITY

#### `DOC-A06-011` · Cardholder data flow
- **What it is.** Record cardholder data flow for security engineering.
- **It answers.** "Where does card data live, move and stop, and what keeps it out of reach?" — read by **auditors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during pre-release · maturity Hardened · life-cycle events: `api-change`, `incident`.
- **Checks that run on it:** `presence`, `links.local`.
- **In this repository:** **Not applicable here** — `handles_payments` is declared `false`; the answer is re-surfaced if the declaration changes.
- **Why the trait gate matters:** This is the reason the row exists: the question is asked, not assumed. Answering the trait activates the type.

### A20-GOVERNANCE

#### `DOC-A20-008` · Hazard analysis
- **What it is.** Record hazard analysis for governance risk and compliance.
- **It answers.** "What can this system do to a person or the world, and what stops it?" — read by **auditors**; the project owner owns it.
- **Required from** `prototype` · off in `idea` · needed during post-release · maturity Product-Grade · life-cycle events: `incident`.
- **Checks that run on it:** `presence`, `links.local`.
- **In this repository:** **Not applicable here** — `safety_critical` is declared `false`; the answer is re-surfaced if the declaration changes.
- **Why the trait gate matters:** Safety is the one area where asking beats assuming: a project with no hazard question never sees this row.

## Part 3 — the five profiles, in depth

A profile is a delta, not a second catalog: it adds or removes a handful of core types with a stated reason, and an addition can still be off in the early phases. A project picks one; this repository declares `oss-library`.

### `default` — Default
**What it is for.** The set that survives every project shape: the idea and build documents plus the ones already gated by a detected fact.

**Adds:** nothing — this profile is the default set.

**Removes:** nothing.

**Core types in effect:** 27.

### `startup` — Startup
**What it is for.** Small team, changing direction: a written roadmap earns its place, while lifecycle promises made before product-market fit are theatre.

**Adds:**
- `DOC-A01-004` **Roadmap** — Direction changes often and out loud; a written roadmap keeps the team pointing the same way. required from `idea`; read by contributors.

**Removes:**
- `DOC-A23-001` **Deprecation policy** — A deprecation promise is about consumers you do not have yet; it becomes real once there are users.

**Core types in effect:** 27.

### `oss-library` — Open-source library
**What it is for.** Consumers you will never meet, contributing strangers, and redistribution: the social documents are load-bearing.

**Adds:**
- `DOC-A09-009` **Code of conduct** — A public community needs a stated standard of behaviour and a way to report a breach. off in idea/prototype, required from `build`; read by contributors. **Open here** — a new `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1 plus a contact) closes it; record `[instantiated]`.
- `DOC-A06-008` **Vulnerability management** — A published package needs a disclosure route for vulnerabilities, as SECURITY.md. off in idea/prototype, required from `build`; read by external-users. **Open here** — a new `SECURITY.md` (private disclosure route, scope, expectations) closes it; record `[instantiated]`.
- `DOC-A09-006` **Dependency policy** — Dependency policy is the maintainer's stated answer to supply-chain questions. off in idea/prototype, required from `build`; read by contributors. **Open here** — a dependencies section in `CONTRIBUTING.md` closes it; record `[satisfied_by]`.

**Removes:**
- `DOC-A16-003` **Runbook** — A library is not operated; there is no on-call rotation for a package.

**Core types in effect:** 29.

### `internal-service` — Internal service
**What it is for.** Operated by the same organisation that owns it: operations documents are core, and distribution documents are not.

**Adds:**
- `DOC-A16-005` **On call policy** — Someone is on call; the rotation and its expectations must be written. off in idea/prototype/build/beta, required from `live`; read by operators.
- `DOC-A12-001` **SLI SLO SLA** — An internal service still needs a stated reliability target and the error budget it implies. off in idea/prototype/build/beta, required from `live`; read by operators.
- `DOC-A17-001` **Incident response** — Incidents happen to internal services too, and the response path should not be improvised. off in idea/prototype/build/beta, required from `live`; read by operators.

**Removes:**
- `DOC-A10-008` **License** — An internal service is not redistributed, so there are no external licence terms to state.

**Core types in effect:** 29.

### `regulated` — Regulated
**What it is for.** Personal data, auditors, and evidence: claims must be traceable to records that outlive the people who wrote them.

**Adds:**
- `DOC-A07-001` **ROPA** — Processing personal data requires a record of what is processed, why, and with whom it is shared. off in idea/prototype/build, required from `beta`; read by auditors.
- `DOC-A05-006` **Retention policy** — Retention must be decided before data accumulates, not after someone asks. off in idea/prototype/build, required from `beta`; read by auditors.
- `DOC-A20-002` **Control catalog** — Controls are only credible when they are catalogued and mapped to evidence. off in idea/prototype/build, required from `beta`; read by auditors.
- `DOC-A24-003` **Access review evidence** — Access reviews are the evidence auditors ask for first; the record is the deliverable. off in idea/prototype/build, required from `beta`; read by auditors.

**Removes:** nothing.

**Core types in effect:** 31.

Total: 11 additions and 4 removals across the five profiles, each re-checked by `check_catalog.py` against the admission rule.

## Part 4 — the six calls, with both sides

These are the rows where a reasonable owner could decide differently. My recommendation is first; if you pick the alternative, say so by number and the change becomes its own edit.

### Call 1 — `DEV-B10-003` Dependency setup overlaps `DEV-B10-001` Local setup
- **Context.** Both are core and always-applicable from build. Local setup answers "how do I get this running" (closed here by `QUICK-START.md`); Dependency setup answers "which dependencies, at which versions, and how are they updated" — the supply-chain question. Dependency setup is open here.
- **Recommended.** Keep both: they are read by different people on different days, and the dependency answer ages on every upgrade while the local-setup answer does not.
- **If you disagree.** Merge them: one core type disappears (26), the surviving type covers both questions, and `DEV-B10-003` is demoted to extended. It is a data edit plus re-validation, but it weakens the dependency-policy prompt — the row this repository currently answers with a profile addition.

### Call 2 — The `has_deploy` gate on `DOC-A15-006` Rollback procedure and `DOC-A16-003` Runbook
- **Context.** Both are core by default but apply only when `has_deploy` is true. Here it is false, so neither is asked; the oss-library profile also removes the runbook entirely. For a deployed service they become required from beta (rollback) and live (runbook).
- **Recommended.** Keep the gate: nothing that is not deployed has anything to roll back or operate. This gate is why the list does not demand a runbook from a library.
- **If you disagree.** Re-gate them on `has_ci` or `is_public`: then any library with continuous integration is told it needs a rollback plan for a release it cannot roll back — a false obligation, which is worse than a missing one.

### Call 3 — `startup` removes `DOC-A23-001` Deprecation policy and adds `DOC-A01-004` Roadmap
- **Context.** Deprecation policy stays core in default, oss-library, internal-service and regulated; only startup drops it. Roadmap is a startup-only addition. Both profiles keep 27 core types.
- **Recommended.** Approve the trade: a startup owes its users a direction far more than a removal promise for versions it does not have yet.
- **If you disagree.** Keep deprecation in startup: a pre-users project gets asked to promise how it will remove an API — the shape of obligation that makes a tool feel like paperwork and gets it uninstalled.

### Call 4 — `internal-service` removes `DOC-A10-008` License
- **Context.** License is core in default, startup, oss-library and regulated; the internal-service profile drops it, on the stated grounds that an internal service is not redistributed.
- **Recommended.** Approve, with one caveat to be aware of: if the code is ever distributed across legal entities or shipped in a product, the licence question returns. The removal expresses "not redistributed", not "licensing does not matter".
- **If you disagree.** Keep License in internal-service: adds a requirement many internal teams cannot answer meaningfully, and the rule returns the moment the code is published.

### Call 5 — `regulated` adds exactly ROPA, Retention policy, Control catalog and Access review evidence
- **Context.** The profile adds four records where the deliverable *is* the record: what is processed, how long it is kept, which controls exist, and who reviewed access. Each is off in idea/prototype and required from beta or live.
- **Recommended.** Approve the four. They are the documents a regulated project can be asked for from a repository alone, and `check_catalog.py` verifies each has a reader question, a predicate and its phases.
- **If you disagree.** Widen it (DPIA, vendor register, penetration-test reports, DR evidence): those are real obligations but their adequacy cannot be judged from file presence. They stay extended/contextual until a project wires real evidence sources — adding them to the profile would create paperwork, not assurance.

### Call 6 — Should anything be demoted from core? (`DOC-A15-003` Changelog is my only candidate)
- **Context.** Changelog is core, `is_public`, off at build and required from beta. There are 46 extended and 192 contextual types, so demotion has a home.
- **Recommended.** Keep it core. A changelog is the one document a user reads before upgrading, and "what changed between my version and yours" is exactly the question a distributed project must answer. Its beta phase already keeps it out of the way during build.
- **If you disagree.** Demote to extended: it becomes a recommendation (report at build, warn from beta) instead of a requirement — defensible, but it would make the upgrade path the only one of the guide's release documents that nobody is asked for.

## Part 5 — how to reply

- **Approve everything as written:** reply "approve all".
- **Change rows:** name the ids, e.g. "flag `DOC-A15-003` and `DEV-B10-003`".
- **Decide the calls:** answer by number, e.g. "call 3 → alternative".

Then I record the outcome: a dated `owner_reviewed` note in `CONTROL/metadata/CATALOG-RULES.json` and `CONTROL/metadata/PROFILES.json`, this page to `approved`, the pending-review caveat removed from `NEXT-ACTION.md` and `ADOPTION.md`, and any flagged row becomes its own change with catalog re-validation and a test where it has a consumer. Nothing changes before you answer.
