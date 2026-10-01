---
id: DOC-P3-GOV-006
title: "Core list review — full context for the owner decision"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "1.2"
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
them carries a "pending owner review" caveat. This page removes that caveat in one sitting.

## Review log

**2026-10-01 — owner reviewed v1.1.** Corrections requested and applied in this v1.2: the profile totals (3 removals, not 4), the source of the false predicate on not-applicable rows, the `has_public_api_surface` finding behind the two flagged rows, the enforcement block ahead of the table, the real escape names, the split of the open rows, the beta cliff, and rewritten rationales for calls 3 and 4. Four items are flagged and pending a decision (Part 5). The owner indicated approval of the remaining rows and calls subject to this revision. **No approval has been recorded:** both machine files are untouched and this page stays a draft until the owner confirms the revised page.

## Part 0 — How a row is enforced

Core decides that a type belongs to the essential set. Two further switches decide what happens to *your* repository:

- **Predicate.** Every row carries an `applies_when` fact (`always`, `has_tests`, `is_public`, `has_deploy`, `handles_personal_data`, …), evaluated three-valued: **true** applies, **false** does not apply, **unknown** leaves the row *undetermined* — asked and reported, never failed and never silently satisfied.
- **Phase.** A row is required from its `phase_min` upward, at the severity its enforcement block sets.

| Phase block | Core row | Extended row | Structural checks (drift, stubs, placeholders, links, secrets, freshness) |
| --- | --- | --- | --- |
| idea / prototype (advisory) | report | report | all report; drift and freshness off |
| build (warn) — this repository | warn | report | placeholders, links and secrets fail; drift and freshness off |
| beta (strict) | **fail** | warn | drift and freshness warn; the rest fail |
| live / mature (full) | **fail** | warn | everything fails |
| sunset | fail | off | only the sunset documents stay active |

**What the five checks actually assert.** Every one of the 27 rows runs the same family against the file it points at: the file **exists**, it is **not a stub** (beyond a title), it carries **no placeholder text**, its **local links resolve**, and it is **not past its review date**. Nothing checks whether the content is correct or adequate — a human reviewer does, and AutoDOC never certifies compliance.

**The three escapes, and how strong each is.**

| Escape | What it claims | How AutoDOC treats it |
| --- | --- | --- |
| `[instantiated]` | This file **is** that document. | Strongest: the file enters the controlled set, is checked and reviewed as that document, and a missing path is a configuration error. |
| `[satisfied_by]` | The content already **lives** somewhere else. | Weaker: a local path is existence-checked, a URL is recorded and never fetched (a human confirms it). The location is not checked as the document. |
| `[not_applicable]` | This question does not apply, for a stated reason. | The row is skipped and the reason is displayed. A reason is mandatory, and the skip is **re-surfaced** if the fact behind it later becomes true. |

**A false predicate has two sources, and the difference matters.** A **detected** fact is false because a detector ran and matched nothing (absence of evidence — it flips when the evidence appears). A **declared** fact is false because the owner answered the question in `autodoc.toml` with a reason (an answer, not an absence — it changes only when the owner changes it). A fact whose detector cannot run at all is `unknown`, which leaves the row undetermined rather than not applicable. This is why the five not-applicable rows rest on three declared traits and two detected facts.

**What this review does.** Approving changes **nothing behavioural** — the same rows behave the same way tomorrow; it removes the caveat that the policy itself was never read by its owner. It does **not** close the 12 open decisions: that is the next item, and it is what moves this repository from 7/19 to 19/19 build-ready. Flagging a row turns it into a small data change (the rule, the profile or the predicate) plus re-validation.

## Part 1 — The sheet: mark any row you would change

Quick read before the table: predicate **true / false / unknown** × phase (**report → warn → fail from beta**), extended rows one step softer; escapes **`[instantiated]`** (strongest), **`[satisfied_by]`** (content lives elsewhere), **`[not_applicable]`** (reasoned skip, reason mandatory). Everything blank is approved; the ✎ column is the only thing to edit.

| ✎ | ID | Name | Question | Why core | Applies when | Required from | State here |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ☐ | `DEV-B01-001` | Problem statement | What problem does this project solve, and for whom? | Every project needs a stated reason to exist. | `always` | idea | open — to author |
| ☐ | `DEV-B01-002` | Goals and non goals | What is this trying to achieve, and what is it deliberately not doing? | Non-goals prevent the scope creep that no check can detect. | `always` | idea | open — to author |
| ☐ | `DEV-B01-003` | Scope | Where is the boundary of this system? | The boundary of what the system covers. | `always` | idea | open — to author |
| ☐ | `DEV-B01-006` | README | What is this, why does it exist, and how do I know it works? | The first and most-read document: what it is, why it exists and whether it works. | `always` | idea | open — `[instantiated]` pending |
| ☐ | `DEV-B04-001` | System overview | What are the parts of this system and how do they fit together? | One map of the parts, for newcomers and agents. | `always` | build | [instantiated] → `docs/05-architecture/AUTODOC-ARCHITECTURE.md` |
| ☐ | `DEV-B04-002` | ADR | Why was this decision made, and what did we give up? | Decisions are the highest-churn human knowledge in a repository. | `always` | build | open — to author |
| ☐ | `DEV-B05-001` | Module contract | What does this module promise to its callers? | Module boundaries are where changes break neighbours. | `always` | build | open — `[satisfied_by]` pending |
| ☐ | `DEV-B07-001` | Test strategy | How do we establish confidence that this works? | States how confidence is established; the canonical form of this type. | `has_tests` | build | open — `[satisfied_by]` pending |
| ☐ | `DEV-B08-001` | Current state | What is true right now? | Working context; the substrate AutoDOC itself runs on. | `always` | build | [instantiated] → `CURRENT-STATE.md` |
| ☐ | `DEV-B08-002` | Next action | What is the next thing to do, and by whom? | Human priorities must be recorded, never inferred from Git. | `always` | build | [instantiated] → `NEXT-ACTION.md` |
| ☐ | `DEV-B08-003` | Recent changes | What changed lately, and why? | A short delta log beats reading raw commit history. | `always` | build | [instantiated] → `RECENT-CHANGES.md` |
| ☐ | `DEV-B09-001` | AGENTS.md | What must an agent know before touching this repository? | The context file an agent reads first. | `uses_agents` | build | [instantiated] → `AGENTS.md` |
| ☐ | `DEV-B10-001` | Local setup | How do I get this running on my machine? | Nobody can run the project without it. | `always` | build | [instantiated] → `QUICK-START.md` |
| ☐ | `DEV-B10-003` | Dependency setup | Which dependencies, at which versions, and how are they updated? | Direct dependencies and version policy; the most common onboarding failure. | `always` | build | open — `[satisfied_by]` pending |
| ☐ | `DOC-A05-001` | Data model | What entities exist, how do they relate, and what do they mean? | Entities and relationships before schema detail. | `has_persistent_state` | build | open — fact override pending |
| ☐ | `DOC-A08-001` | OpenAPI | What is the machine-readable contract for this interface? | The machine-readable contract for a machine-callable interface. | `has_public_api_surface` | beta | off — required from `beta` |
| ☐ | `DOC-A09-005` | Contributing guide | How do I contribute, and what will be expected of me? | Outside contributors need the contribution path. | `is_public` | live | [instantiated] → `CONTRIBUTING.md` |
| ☐ | `DOC-A10-008` | License | May I use, change and redistribute this, and on what terms? | Redistribution terms; without them nobody may legally reuse the work. | `is_public` | beta | off — required from `beta` |
| ☐ | `DOC-A14-005` | Environment variable schema | Which environment variables exist, and what do they do? | Every environment variable and its meaning. | `has_env` | beta | off — required from `beta` |
| ☐ | `DOC-A15-003` | Changelog | What changed between the version I have and the one I am upgrading to? | Consumers of a distributed project need a version delta. | `is_public` | beta | off — required from `beta` |
| ☐ | `DOC-A15-006` | Rollback procedure | How do I undo this release if it goes wrong? | Reversing a bad release must be written before it is needed. | `has_deploy` | beta | not applicable — `has_deploy` false (detected) |
| ☐ | `DOC-A16-003` | Runbook | What do I do when this alerts? | Operators need a procedure for the deployed service. | `has_deploy` | live | not applicable — `has_deploy` false (detected) |
| ☐ | `DOC-A22-004` | API quickstart | How do I make my first successful call? | Shortest path to a first successful call. | `has_public_api_surface` | beta | off — required from `beta` |
| ☐ | `DOC-A23-001` | Deprecation policy | What does this project promise before removing something? | Published interfaces need a removal promise before they are removed. | `is_public` | mature | off — required from `mature` |
| ☐ | `DOC-A05-009` | PII inventory | What personal data does this hold, where did it come from, and who can see it? | Personal data nobody has mapped is data nobody can protect, delete or explain. | `handles_personal_data` | build | not applicable — `handles_personal_data` false (declared) |
| ☐ | `DOC-A06-011` | Cardholder data flow | Where does card data live, move and stop, and what keeps it out of reach? | Card data has to be located before its flow can be limited, segmented or defended. | `handles_payments` | build | not applicable — `handles_payments` false (declared) |
| ☐ | `DOC-A20-008` | Hazard analysis | What can this system do to a person or the world, and what stops it? | A hazard that is never written down is not controlled, and a safety claim without its failure modes is not a claim anyone can check. | `safety_critical` | prototype | not applicable — `safety_critical` false (declared) |

**The beta cliff.** Under `build` this repository sees warnings; at `beta` the core requirement becomes `fail`. If the phase were promoted today, **14 of these 27** unresolved rows would start failing — the 9 open rows (warn → fail) plus the 5 off rows whose phase arrives at beta (`DOC-A08-001`, `DOC-A10-008`, `DOC-A14-005`, `DOC-A15-003`, `DOC-A22-004`). Counting the three profile additions this repository declares (`DOC-A06-008`, `DOC-A09-006`, `DOC-A09-009`, also open at build), the number is **17**. That is the argument for closing the 12 decisions before promoting, not after.

## Part 1b — The 12 open decisions, split three ways

These are the rows open *here* (9 of the 27 plus 3 profile additions). They are separate from this review: approving the list does not close them, and closing them is what moves the repository to 19/19.

| Group | Row | One-line closing path |
| --- | --- | --- |
| **Exists — needs `[instantiated]`** | `DEV-B01-006` README | [instantiated] = "README.md" — the file already is the document. |
| **Content exists — needs `[satisfied_by]`** | `DEV-B05-001` Module contract | [satisfied_by] the module-boundaries section of `docs/05-architecture/AUTODOC-ARCHITECTURE.md`. |
|  | `DEV-B07-001` Test strategy | [satisfied_by] `docs/00-governance/ENGINE-COVERAGE.md` (what is verified, how, and the limits). |
|  | `DEV-B10-003` Dependency setup | [satisfied_by] `QUICK-START.md` — flagged: see call 1 and flag C on the overlap with Dependency policy. |
|  | `DOC-A09-006` Dependency policy | [satisfied_by] a dependencies section in `CONTRIBUTING.md` — flagged: see flag C. |
| **Does not exist — to author** | `DEV-B01-001` Problem statement | one new `docs/00-governance/PROJECT-CHARTER.md` closes this row and its two siblings; then [satisfied_by]. |
|  | `DEV-B01-002` Goals and non goals | the same charter page, second section; then [satisfied_by]. |
|  | `DEV-B01-003` Scope | the same charter page, third section; then [satisfied_by]. |
|  | `DEV-B04-002` ADR | start `docs/adr/` with one real decision, or record [not_applicable] saying decisions live in ADOPTION.md (dated), the changelog (user-facing) and machine policy. |
|  | `DOC-A09-009` Code of conduct | a new `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1 plus a contact); then [instantiated]. |
|  | `DOC-A06-008` Vulnerability management | a new `SECURITY.md` (private disclosure route, scope, expectations); then [instantiated]. |
| **Fact override pending** | `DOC-A05-001` Data model | declare `has_persistent_state = false` in the demo-fact cleanup (the only schema is the demo fixture), which makes the row not applicable. |

The charter page is the cheapest win: one new `docs/00-governance/PROJECT-CHARTER.md` with problem, goals-and-non-goals, and scope as three named sections closes `DEV-B01-001`, `-002` and `-003` at once. `README.md` needs only a one-line mapping. The four `[satisfied_by]` rows need no new writing at all — only the declaration.

## Part 2 — Full context, row by row

Grouped by catalog domain, in the order of the sheet.

### B01-FOUNDATION

#### `DEV-B01-001` · Problem statement
- **What it is.** Record problem statement for context and goals.
- **It answers.** "What problem does this project solve, and for whom?" — read by **contributors**; the project owner owns it.
- **Required from** `idea` · needed during active development · maturity Project-Phase · life-cycle events: `direction-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* one new `docs/00-governance/PROJECT-CHARTER.md` closes this row and its two siblings; then [satisfied_by].

#### `DEV-B01-002` · Goals and non goals
- **What it is.** Record goals and non goals for context and goals.
- **It answers.** "What is this trying to achieve, and what is it deliberately not doing?" — read by **contributors**; the project owner owns it.
- **Required from** `idea` · needed during active development · maturity Project-Phase · life-cycle events: `direction-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* the same charter page, second section; then [satisfied_by].

#### `DEV-B01-003` · Scope
- **What it is.** Record scope for context and goals.
- **It answers.** "Where is the boundary of this system?" — read by **contributors**; the project owner owns it.
- **Required from** `idea` · needed during active development · maturity Project-Phase · life-cycle events: `direction-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* the same charter page, third section; then [satisfied_by].

#### `DEV-B01-006` · README
- **What it is.** Record readme for context and goals.
- **It answers.** "What is this, why does it exist, and how do I know it works?" — read by **external-users**; the project owner owns it.
- **Required from** `idea` · needed during active development · maturity Project-Phase · life-cycle events: `release`, `onboarding`.
- **Checks that run:** `presence`, `links.local`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* [instantiated] = "README.md" — the file already is the document.

### B04-ARCHITECTURE

#### `DEV-B04-001` · System overview
- **What it is.** Record system overview for early architecture.
- **It answers.** "What are the parts of this system and how do they fit together?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `api-change`, `direction-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `[instantiated]` → `docs/05-architecture/AUTODOC-ARCHITECTURE.md`. The file *is* the document; a missing path would be a configuration error.

#### `DEV-B04-002` · ADR
- **What it is.** Record adr for early architecture.
- **It answers.** "Why was this decision made, and what did we give up?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `direction-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* start `docs/adr/` with one real decision, or record [not_applicable] saying decisions live in ADOPTION.md (dated), the changelog (user-facing) and machine policy.

### B05-CONTRACTS

#### `DEV-B05-001` · Module contract
- **What it is.** Record module contract for implementation contracts.
- **It answers.** "What does this module promise to its callers?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `api-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* [satisfied_by] the module-boundaries section of `docs/05-architecture/AUTODOC-ARCHITECTURE.md`.

### B07-TESTING

#### `DEV-B07-001` · Test strategy
- **What it is.** Record test strategy for validation.
- **It answers.** "How do we establish confidence that this works?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `release`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* [satisfied_by] `docs/00-governance/ENGINE-COVERAGE.md` (what is verified, how, and the limits).

### B08-TRACKING

#### `DEV-B08-001` · Current state
- **What it is.** Record current state for handoff and tracking.
- **It answers.** "What is true right now?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `[instantiated]` → `CURRENT-STATE.md`. The file *is* the document; a missing path would be a configuration error.

#### `DEV-B08-002` · Next action
- **What it is.** Record next action for handoff and tracking.
- **It answers.** "What is the next thing to do, and by whom?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `[instantiated]` → `NEXT-ACTION.md`. The file *is* the document; a missing path would be a configuration error.

#### `DEV-B08-003` · Recent changes
- **What it is.** Record recent changes for handoff and tracking.
- **It answers.** "What changed lately, and why?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `[instantiated]` → `RECENT-CHANGES.md`. The file *is* the document; a missing path would be a configuration error.

### B09-AGENT-CONTEXT

#### `DEV-B09-001` · AGENTS.md
- **What it is.** Record agents.md for ai agent context.
- **It answers.** "What must an agent know before touching this repository?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `onboarding`, `change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `[instantiated]` → `AGENTS.md`. The file *is* the document; a missing path would be a configuration error.

### B10-SETUP

#### `DEV-B10-001` · Local setup
- **What it is.** Record local setup for project setup.
- **It answers.** "How do I get this running on my machine?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `onboarding`, `dependency-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `[instantiated]` → `QUICK-START.md`. The file *is* the document; a missing path would be a configuration error.

#### `DEV-B10-003` · Dependency setup
- **What it is.** Record dependency setup for project setup.
- **It answers.** "Which dependencies, at which versions, and how are they updated?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during active development · maturity Project-Phase · life-cycle events: `dependency-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* [satisfied_by] `QUICK-START.md` — flagged: see call 1 and flag C on the overlap with Dependency policy.

### A05-DATA

#### `DOC-A05-001` · Data model
- **What it is.** Record data model for data and information management.
- **It answers.** "What entities exist, how do they relate, and what do they mean?" — read by **contributors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during pre-release · maturity Hardened · life-cycle events: `schema-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Open here** — required now, severity `warn` at build and `fail` from beta. *Closing path:* declare `has_persistent_state = false` in the demo-fact cleanup (the only schema is the demo fixture), which makes the row not applicable.

### A08-APIS

#### `DOC-A08-001` · OpenAPI
- **What it is.** Record openapi for apis and interfaces.
- **It answers.** "What is the machine-readable contract for this interface?" — read by **external-users**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during pre-release · maturity Hardened · life-cycle events: `api-change`, `release`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` with fail severity.

### A09-DEVELOPMENT

#### `DOC-A09-005` · Contributing guide
- **What it is.** Record contributing guide for development process.
- **It answers.** "How do I contribute, and what will be expected of me?" — read by **contributors**; the project owner owns it.
- **Required from** `live` · off in `idea`, `prototype`, `build`, `beta` · needed during active development · maturity Hardened · life-cycle events: `onboarding`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Closed here** — `[instantiated]` → `CONTRIBUTING.md`. The file *is* the document; a missing path would be a configuration error.

### A10-BUILD

#### `DOC-A10-008` · License
- **What it is.** Record license for build and supply chain.
- **It answers.** "May I use, change and redistribute this, and on what terms?" — read by **external-users**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during pre-release · maturity Hardened · life-cycle events: not tied to an event.
- **Checks that run:** `presence`, `links.local`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` with fail severity.

### A14-CONFIGURATION

#### `DOC-A14-005` · Environment variable schema
- **What it is.** Record environment variable schema for configuration and change.
- **It answers.** "Which environment variables exist, and what do they do?" — read by **operators**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during pre-release · maturity Hardened · life-cycle events: `dependency-change`, `api-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.critical`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` with fail severity.

### A15-RELEASE

#### `DOC-A15-003` · Changelog
- **What it is.** Record changelog for release and deployment.
- **It answers.** "What changed between the version I have and the one I am upgrading to?" — read by **external-users**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during post-release · maturity Product-Grade · life-cycle events: `release`.
- **Checks that run:** `presence`, `stubs`, `links.local`, `freshness.review`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` with fail severity.

#### `DOC-A15-006` · Rollback procedure
- **What it is.** Record rollback procedure for release and deployment.
- **It answers.** "How do I undo this release if it goes wrong?" — read by **operators**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during post-release · maturity Product-Grade · life-cycle events: `release`, `incident`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.critical`.
- **In this repository:** **Not applicable here** — `has_deploy` is detected false: the detector ran and found no deployment evidence. It flips back to required when a deployment file appears (Dockerfile, compose, k8s/helm/terraform, or a deploy workflow). An unanswered declaration-only trait is `unknown`, which would leave the row *undetermined* (asked, reported, never silently not applicable).

### A16-OPERATIONS

#### `DOC-A16-003` · Runbook
- **What it is.** Record runbook for operations and observability.
- **It answers.** "What do I do when this alerts?" — read by **operators**; the project owner owns it.
- **Required from** `live` · off in `idea`, `prototype`, `build`, `beta` · needed during post-release · maturity Product-Grade · life-cycle events: `incident`, `dependency-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.critical`.
- **In this repository:** **Not applicable here** — `has_deploy` is detected false: the detector ran and found no deployment evidence. It flips back to required when a deployment file appears. An unanswered declaration-only trait is `unknown`, which would leave the row *undetermined* (asked, reported, never silently not applicable).

### A22-USER-SUPPORT

#### `DOC-A22-004` · API quickstart
- **What it is.** Record api quickstart for user and support.
- **It answers.** "How do I make my first successful call?" — read by **external-users**; the project owner owns it.
- **Required from** `beta` · off in `idea`, `prototype`, `build` · needed during post-release · maturity Product-Grade · life-cycle events: `api-change`, `onboarding`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `beta` with fail severity.

### A23-LIFECYCLE

#### `DOC-A23-001` · Deprecation policy
- **What it is.** Record deprecation policy for lifecycle management.
- **It answers.** "What does this project promise before removing something?" — read by **external-users**; the project owner owns it.
- **Required from** `mature` · off in `idea`, `prototype`, `build`, `beta`, `live` · needed during post-release · maturity Product-Grade · life-cycle events: `retirement`, `api-change`.
- **Checks that run:** `presence`, `stubs`, `placeholders`, `links.local`, `freshness.review`.
- **In this repository:** **Off here** — nothing is asked at build; it becomes required from `mature` with fail severity.

### A05-DATA

#### `DOC-A05-009` · PII inventory
- **What it is.** Record pii inventory for data and information management.
- **It answers.** "What personal data does this hold, where did it come from, and who can see it?" — read by **auditors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during pre-release · maturity Hardened · life-cycle events: `incident`, `release`.
- **Checks that run:** `presence`, `links.local`.
- **In this repository:** **Not applicable here** — `handles_personal_data` is declared false by the owner in `autodoc.toml`, with a reason. It flips back to required when the owner changes the declaration in `autodoc.toml`. An unanswered declaration-only trait is `unknown`, which would leave the row *undetermined* (asked, reported, never silently not applicable).

### A06-SECURITY

#### `DOC-A06-011` · Cardholder data flow
- **What it is.** Record cardholder data flow for security engineering.
- **It answers.** "Where does card data live, move and stop, and what keeps it out of reach?" — read by **auditors**; the project owner owns it.
- **Required from** `build` · off in `idea`, `prototype` · needed during pre-release · maturity Hardened · life-cycle events: `api-change`, `incident`.
- **Checks that run:** `presence`, `links.local`.
- **In this repository:** **Not applicable here** — `handles_payments` is declared false by the owner in `autodoc.toml`, with a reason. It flips back to required when the owner changes the declaration in `autodoc.toml`. An unanswered declaration-only trait is `unknown`, which would leave the row *undetermined* (asked, reported, never silently not applicable).

### A20-GOVERNANCE

#### `DOC-A20-008` · Hazard analysis
- **What it is.** Record hazard analysis for governance risk and compliance.
- **It answers.** "What can this system do to a person or the world, and what stops it?" — read by **auditors**; the project owner owns it.
- **Required from** `prototype` · off in `idea` · needed during post-release · maturity Product-Grade · life-cycle events: `incident`.
- **Checks that run:** `presence`, `links.local`.
- **In this repository:** **Not applicable here** — `safety_critical` is declared false by the owner in `autodoc.toml`, with a reason. It flips back to required when the owner changes the declaration in `autodoc.toml`. An unanswered declaration-only trait is `unknown`, which would leave the row *undetermined* (asked, reported, never silently not applicable).

## Part 3 — The five profiles, in depth

A profile is a delta on the default core set, not a second catalog: `core = (default ∪ added) − removed`. **A removal is not a soft downgrade** — it takes the row out of that profile's core set entirely, so the question is never asked, whatever the predicate says. A row left in place with an unknown predicate would be *undetermined* instead: AutoDOC would ask the question. That distinction is the point of the two removals that look surprising (a startup dropping a deprecation policy, an internal service dropping the licence).

| Profile | Adds | Removes | Core types |
| --- | ---: | ---: | ---: |
| **default** — Default | 0 | 0 | 27 |
| **startup** — Startup | 1 | 1 | 27 |
| **oss-library** — Open-source library | 3 | 1 | 29 |
| **internal-service** — Internal service | 3 | 1 | 29 |
| **regulated** — Regulated | 4 | 0 | 31 |

**Totals across the five profiles: 11 additions and 3 removals** (one removal each in `startup`, `oss-library` and `internal-service`; `regulated` removes nothing). Every change carries its own reason, and `check_catalog.py` re-checks each against the admission rule.

### `default` — Default
**What it is for.** The set that survives every project shape: the idea and build documents plus the ones already gated by a detected fact.

**Adds:** nothing — this profile is the default set.

**Removes:** nothing.

### `startup` — Startup
**What it is for.** Small team, changing direction: a written roadmap earns its place, while lifecycle promises made before product-market fit are theatre.

**Adds:**
- `DOC-A01-004` **Roadmap** — Direction changes often and out loud; a written roadmap keeps the team pointing the same way.

**Removes:**
- `DOC-A23-001` **Deprecation policy** — A deprecation promise is about consumers you do not have yet; it becomes real once there are users. *Effect: the profile never asks this question, even when its predicate is true or unknown.*

### `oss-library` — Open-source library
**What it is for.** Consumers you will never meet, contributing strangers, and redistribution: the social documents are load-bearing.

**Adds:**
- `DOC-A09-009` **Code of conduct** — off in `idea`, `prototype` — A public community needs a stated standard of behaviour and a way to report a breach. **Open here** — a new `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1 plus a contact); then [instantiated].
- `DOC-A06-008` **Vulnerability management** — off in `idea`, `prototype` — A published package needs a disclosure route for vulnerabilities, as SECURITY.md. **Open here** — a new `SECURITY.md` (private disclosure route, scope, expectations); then [instantiated].
- `DOC-A09-006` **Dependency policy** — off in `idea`, `prototype` — Dependency policy is the maintainer's stated answer to supply-chain questions. **Open here** — [satisfied_by] a dependencies section in `CONTRIBUTING.md` — flagged: see flag C.

**Removes:**
- `DOC-A16-003` **Runbook** — A library is not operated; there is no on-call rotation for a package. *Effect: the profile never asks this question, even when its predicate is true or unknown.*

### `internal-service` — Internal service
**What it is for.** Operated by the same organisation that owns it: operations documents are core, and distribution documents are not.

**Adds:**
- `DOC-A16-005` **On call policy** — off in `idea`, `prototype`, `build`, `beta` — Someone is on call; the rotation and its expectations must be written.
- `DOC-A12-001` **SLI SLO SLA** — off in `idea`, `prototype`, `build`, `beta` — An internal service still needs a stated reliability target and the error budget it implies.
- `DOC-A17-001` **Incident response** — off in `idea`, `prototype`, `build`, `beta` — Incidents happen to internal services too, and the response path should not be improvised.

**Removes:**
- `DOC-A10-008` **License** — An internal service is not redistributed, so there are no external licence terms to state. *Effect: the profile never asks this question, even when its predicate is true or unknown.*

### `regulated` — Regulated
**What it is for.** Personal data, auditors, and evidence: claims must be traceable to records that outlive the people who wrote them.

**Adds:**
- `DOC-A07-001` **ROPA** — off in `idea`, `prototype`, `build` — Processing personal data requires a record of what is processed, why, and with whom it is shared.
- `DOC-A05-006` **Retention policy** — off in `idea`, `prototype`, `build` — Retention must be decided before data accumulates, not after someone asks.
- `DOC-A20-002` **Control catalog** — off in `idea`, `prototype`, `build` — Controls are only credible when they are catalogued and mapped to evidence.
- `DOC-A24-003` **Access review evidence** — off in `idea`, `prototype`, `build` — Access reviews are the evidence auditors ask for first; the record is the deliverable.

**Removes:** nothing.

## Part 4 — The six calls

Calls 1, 2, 5 and 6 stand as recommended. Calls 3 and 4 have their rationale rewritten below, because the real mechanism is stronger than "not redistributed".

### Call 1 — `DEV-B10-003` Dependency setup overlaps `DEV-B10-001` Local setup
- **Context.** Both are core and always-applicable from build. Local setup answers "how do I get this running" (closed here by `QUICK-START.md`); Dependency setup answers "which dependencies, at which versions, and how are they updated". Dependency setup is open here, and it also overlaps `DOC-A09-006` Dependency policy — see flag C.
- **Recommended.** Keep both, and split the policy question from the setup question (flag C).
- **If you disagree.** Merge them: one core type disappears (26), the surviving type covers both, and `DEV-B10-003` is demoted to extended.

### Call 2 — The `has_deploy` gate on `DOC-A15-006` Rollback procedure and `DOC-A16-003` Runbook
- **Context.** Both are core but apply only when `has_deploy` is true; it is detected false here, so neither is asked. For a deployed service they become required from beta (rollback) and live (runbook).
- **Recommended.** Keep the gate: nothing that is not deployed has anything to roll back or operate. Re-gating on `has_ci` or `is_public` would demand a rollback plan for a release a library cannot roll back — a false obligation, worse than a missing one.

### Call 3 — `startup` removes `DOC-A23-001` Deprecation policy (rationale rewritten)
- **Context.** Deprecation policy is core in default, oss-library, internal-service and regulated, required from mature, and gated on `is_public`. Only `startup` removes it.
- **The real mechanism.** A removal is not a downgrade and not "not redistributed" in the generic sense: it deletes the row from that profile's core set, so a startup is **never asked the deprecation question** — even when `is_public` is true or unknown. Left in place, an unknown `is_public` would make the row *undetermined*, i.e. AutoDOC would ask, and a true `is_public` would eventually require the document. The removal is how the profile says "this question does not apply to you", explicitly and reviewably.
- **Recommended.** Approve the removal: a startup with no released versions has nothing to deprecate, and the row would otherwise nag it from build onward with a policy it cannot honestly write.
- **If you disagree.** Keep it in startup: the question is then asked and must be answered, either as `[not_applicable]` with a reason or, for a startup that already publishes versions, as a real deprecation policy — more honest for the second case, more noise for the first.

### Call 4 — `internal-service` removes `DOC-A10-008` License (rationale rewritten)
- **Context.** License is core in default, startup, oss-library and regulated, required from beta, and gated on `is_public`. Only `internal-service` removes it.
- **The real mechanism.** The removal forces the row off for that profile regardless of the predicate: an internal service is never asked the licence question even if `is_public` is unknown or even true. It is not that "licensing does not matter" — it is that this profile declares the question out of scope, visibly and with a reason, instead of leaving it undetermined.
- **Recommended.** Approve, with one caveat: if the code is ever redistributed across legal entities or shipped inside a product, the profile must change back to `default` or `oss-library`, because the removal actively suppresses the question.
- **If you disagree.** Keep License and let `is_public` decide: an internal service that also publishes a mirror keeps the row and is asked, at the cost of asking every purely internal team a question it cannot answer.

### Call 5 — `regulated` adds exactly ROPA, Retention policy, Control catalog and Access review evidence
- **Recommended.** Approve the four, and do not widen it. DPIA, vendor registers, penetration-test reports and DR evidence are real obligations, but their adequacy cannot be judged from file presence; they stay extended or contextual until a project wires real evidence sources.

### Call 6 — Should anything be demoted from core? (`DOC-A15-003` Changelog is the only candidate)
- **Recommended.** Keep it: a changelog is the one document a user reads before upgrading, its beta phase already keeps it out of the way during build, and demotion would leave the upgrade path as the only release document nobody is asked for.

## Part 5 — Your flags, with options

These are the four rows the 2026-10-01 review flagged. Each becomes a small data edit after you choose; none is applied yet.

### Flag A — `DOC-A08-001` OpenAPI and `DOC-A22-004` API quickstart
- **Finding.** The column does not ignore predicates. `has_public_api_surface` resolves **true** for this repository — evidence `EXAMPLE-PROJECT/routes.json` — so both rows are genuinely applicable and merely not yet reached: they switch on at beta with fail severity. For a project with no contract file the fact is false and the rows are not applicable, so the general mechanism is sound.
- **The real bug class.** The detector also counts `**/index.d.ts` and `**/api/*.ts` — a typed JavaScript/TypeScript library surface. Such a library has no HTTP interface, yet at beta it would be told it needs an OpenAPI document. `has_public_api_surface` is broader than the HTTP-specific rows that consume it, and this repository's own evidence is the *demo fixture*, not a surface AutoDOC ships.
- **Options.**
  1. **Split the predicate (recommended).** Add a detected fact `has_http_api` (openapi*, asyncapi*, `*.proto`, `schema.graphql`, `routes.json`, server/webhook markers) with stated limits, and re-gate the HTTP-specific rows on it — at minimum `DOC-A08-001`; decide whether `DOC-A22-004`, `DOC-A08-006` and `DOC-A08-009` stay on the broader surface fact. Cost: one detector, its limits, its consumers, a fixture and catalog re-validation — the machinery already exists.
  2. **Narrow the detector.** Drop the `index.d.ts`/`api/*.ts` patterns so the fact means "contract file exists". Cheapest, but loses the typed-library signal for every other row.
  3. **Leave the vocabulary.** Record `[not_applicable]` for `DOC-A08-001` when beta arrives (reason: no HTTP interface). Zero code, but the false prompt still appears first.
  4. **Repo-specific (part of the demo-fact cleanup).** The only evidence here is the demo fixture's `routes.json`; declaring the fact, or excluding the demo from that detector, removes the prompt for this repository without touching the vocabulary.
- **Recommendation.** Option 1 as its own small change, plus option 4 inside the demo-fact cleanup. Until then the two rows stay core and flagged.

### Flag B — `DEV-B08-001` Current state, `DEV-B08-002` Next action, `DEV-B08-003` Recent changes
- **The issue.** All three are `always` core and fail at beta, so every adopter — whatever their method — is required to keep three living-state files that are AutoDOC's own workflow, or fail the merge gate at beta.
- **Options.**
  1. **Leave as core.** AutoDOC insists on its own method: adopters keep the three files or fail at beta. Coherent with the tool's own practice, heavy-handed for a team that does not work that way.
  2. **Gate on a declared trait** (e.g. `maintains_living_state`): unknown → asked once, false → not applicable with a reason, true → required (a ratchet). Flexible, but it needs a fact about documentation practice, which the standing rule "facts describe code/infra, never docs" currently forbids — I would not do this without relaxing that rule.
  3. **Make the three extended (recommended).** Same prompts, one level softer: report at build, warn from beta, never fail. No new vocabulary, no gate on an adopter's workflow, and the advice survives. Demoting three rows is a one-line data edit each.
  4. **Keep core, require later** (`phase_min = live`): beta stays clean; a supported project is asked. A variant of option 1 with a later cliff.
- **Recommendation.** Option 3. If you want the ratchet later, option 2 becomes available the moment a documentation-practice fact is acceptable.

### Flag C — `DEV-B10-003` Dependency setup vs `DOC-A09-006` Dependency policy
- **The overlap.** `DEV-B10-003` currently says "which dependencies, at which versions, and how are they updated"; `DOC-A09-006` says "dependency policy is the maintainer's stated answer to supply-chain questions". Both are core, always-applicable from build, and would be satisfied by the same paragraph.
- **Options.**
  1. **Split by question (recommended).** `DEV-B10-003` (setup mechanics, read by contributors at build) owns: *how do I install and run the declared dependencies, and where are the versions pinned?* `DOC-A09-006` (policy, read by contributors, profile addition) owns: *how are dependencies chosen, updated and removed, and how do we respond to their vulnerabilities and licences?* Both stay core; the edit is the question text of `DEV-B10-003` plus its `purpose` line, then catalog re-validation.
  2. **Merge.** Fold version pinning into Dependency policy and demote `DEV-B10-003` to extended (or remove it), leaving setup without a dependency prompt.
  3. **`DEV-B10-003` owns versions explicitly.** Same split as option 1, but the pinning/update cadence stays with setup and the policy owns adoption, removal, vulnerability and licence criteria. Defensible; slightly less clean, because "how are they updated" is a policy question.
- **Recommendation.** Option 1. It keeps both rows honest, removes the duplicated sentence, and gives each document a reader and a moment (installing vs deciding).

## Part 6 — What happens on confirmation

Nothing is recorded until you confirm this revised page: both `CONTROL/metadata/CATALOG-RULES.json` and `CONTROL/metadata/PROFILES.json` stay untouched, and this page stays a draft.

On confirmation:

1. A dated `owner_reviewed` note is added to both machine files (machine files stay machine files; the note is the record), and this page moves to `approved`.
2. Flagged rows become their own change: flag A a predicate/detector change, flag B a tier change for three rows, flag C a question-text change for one row — each with catalog re-validation and a test where the row has a consumer.
3. `NEXT-ACTION.md` loses the "review the 27-type core list" item and `ADOPTION.md` stops calling the membership unreviewed.

Reply with anything you would change, or "confirmed" to record the review as approved.
