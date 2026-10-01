---
id: DOC-P3-GOV-006
title: "Core list review — owner decision requested"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "1.0"
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
# Core list review — owner decision requested

The 27 core types in `CONTROL/metadata/CATALOG-RULES.json` and the five profile deltas in
`CONTROL/metadata/PROFILES.json` are authored policy, not measurements: they decide which documents
AutoDOC calls required, recommended or not applicable for every project that uses it. They were
written and validated by tooling, and they have never been read end to end by the owner. This page
exists to change that in one sitting.

**How to review it:** mark the ✎ column on any row you would change, and leave the rest blank.
Reply with the flagged rows (or "approve all"), and I record the outcome — a dated `owner_reviewed`
line in both machine files, this page going to `approved`, and the "pending owner review" claim
disappearing from the tree. Nothing in the proposal changes until you answer; the list stays exactly
as it is either way.

**What approval does not mean:** a core type is a *possible* document every project ought to have,
checked for existence, structure and drift. It is not a compliance claim, and AutoDOC checks that
records exist and are structured — it never certifies compliance.

## The 27 core types

Every row carries the reader question the type answers, why it is core, the fact that makes it apply, and the first phase it is required from. "In this repository today" is computed by the resolver against the declared `build` phase and the `oss-library` profile — it is where AutoDOC currently stands on that type, not part of the proposal.

| ✎ | ID | Name | Reader question | Why it is core | Applies when | Required from | In this repository today |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ☐ | `DEV-B01-001` | Problem statement | What problem does this project solve, and for whom? | Every project needs a stated reason to exist. | `always` | idea | **open** — required from idea (severity warn) |
| ☐ | `DEV-B01-002` | Goals and non goals | What is this trying to achieve, and what is it deliberately not doing? | Non-goals prevent the scope creep that no check can detect. | `always` | idea | **open** — required from idea (severity warn) |
| ☐ | `DEV-B01-003` | Scope | Where is the boundary of this system? | The boundary of what the system covers. | `always` | idea | **open** — required from idea (severity warn) |
| ☐ | `DEV-B01-006` | README | What is this, why does it exist, and how do I know it works? | The first and most-read document: what it is, why it exists and whether it works. | `always` | idea | **open** — required from idea (severity warn) |
| ☐ | `DEV-B04-001` | System overview | What are the parts of this system and how do they fit together? | One map of the parts, for newcomers and agents. | `always` | build | acknowledged → `docs/05-architecture/AUTODOC-ARCHITECTURE.md` |
| ☐ | `DEV-B04-002` | ADR | Why was this decision made, and what did we give up? | Decisions are the highest-churn human knowledge in a repository. | `always` | build | **open** — required from build (severity warn) |
| ☐ | `DEV-B05-001` | Module contract | What does this module promise to its callers? | Module boundaries are where changes break neighbours. | `always` | build | **open** — required from build (severity warn) |
| ☐ | `DEV-B07-001` | Test strategy | How do we establish confidence that this works? | States how confidence is established; the canonical form of this type. | `has_tests` | build | **open** — required from build (severity warn) |
| ☐ | `DEV-B08-001` | Current state | What is true right now? | Working context; the substrate AutoDOC itself runs on. | `always` | build | acknowledged → `CURRENT-STATE.md` |
| ☐ | `DEV-B08-002` | Next action | What is the next thing to do, and by whom? | Human priorities must be recorded, never inferred from Git. | `always` | build | acknowledged → `NEXT-ACTION.md` |
| ☐ | `DEV-B08-003` | Recent changes | What changed lately, and why? | A short delta log beats reading raw commit history. | `always` | build | acknowledged → `RECENT-CHANGES.md` |
| ☐ | `DEV-B09-001` | AGENTS.md | What must an agent know before touching this repository? | The context file an agent reads first. | `uses_agents` | build | acknowledged → `AGENTS.md` |
| ☐ | `DEV-B10-001` | Local setup | How do I get this running on my machine? | Nobody can run the project without it. | `always` | build | acknowledged → `QUICK-START.md` |
| ☐ | `DEV-B10-003` | Dependency setup | Which dependencies, at which versions, and how are they updated? | Direct dependencies and version policy; the most common onboarding failure. | `always` | build | **open** — required from build (severity warn) |
| ☐ | `DOC-A05-001` | Data model | What entities exist, how do they relate, and what do they mean? | Entities and relationships before schema detail. | `has_persistent_state` | build | **open** — required from build (severity warn) |
| ☐ | `DOC-A08-001` | OpenAPI | What is the machine-readable contract for this interface? | The machine-readable contract for a machine-callable interface. | `has_public_api_surface` | beta | off at build — needed from beta |
| ☐ | `DOC-A09-005` | Contributing guide | How do I contribute, and what will be expected of me? | Outside contributors need the contribution path. | `is_public` | live | acknowledged → `CONTRIBUTING.md` |
| ☐ | `DOC-A10-008` | License | May I use, change and redistribute this, and on what terms? | Redistribution terms; without them nobody may legally reuse the work. | `is_public` | beta | off at build — needed from beta |
| ☐ | `DOC-A14-005` | Environment variable schema | Which environment variables exist, and what do they do? | Every environment variable and its meaning. | `has_env` | beta | off at build — needed from beta |
| ☐ | `DOC-A15-003` | Changelog | What changed between the version I have and the one I am upgrading to? | Consumers of a distributed project need a version delta. | `is_public` | beta | off at build — needed from beta |
| ☐ | `DOC-A15-006` | Rollback procedure | How do I undo this release if it goes wrong? | Reversing a bad release must be written before it is needed. | `has_deploy` | beta | not applicable — `has_deploy` is false |
| ☐ | `DOC-A16-003` | Runbook | What do I do when this alerts? | Operators need a procedure for the deployed service. | `has_deploy` | live | not applicable — `has_deploy` is false |
| ☐ | `DOC-A22-004` | API quickstart | How do I make my first successful call? | Shortest path to a first successful call. | `has_public_api_surface` | beta | off at build — needed from beta |
| ☐ | `DOC-A23-001` | Deprecation policy | What does this project promise before removing something? | Published interfaces need a removal promise before they are removed. | `is_public` | mature | off at build — needed from mature |
| ☐ | `DOC-A05-009` | PII inventory | What personal data does this hold, where did it come from, and who can see it? | Personal data nobody has mapped is data nobody can protect, delete or explain. | `handles_personal_data` | build | not applicable — `handles_personal_data` is false |
| ☐ | `DOC-A06-011` | Cardholder data flow | Where does card data live, move and stop, and what keeps it out of reach? | Card data has to be located before its flow can be limited, segmented or defended. | `handles_payments` | build | not applicable — `handles_payments` is false |
| ☐ | `DOC-A20-008` | Hazard analysis | What can this system do to a person or the world, and what stops it? | A hazard that is never written down is not controlled, and a safety claim without its failure modes is not a claim anyone can check. | `safety_critical` | prototype | not applicable — `safety_critical` is false |

## The five profiles, as deltas of that list

A profile is a small delta, not a second catalog: each entry says why it is added or removed, and an addition can still be off in the early phases.

| Profile | Adds | Why | Removes | Why | Core types in effect |
| --- | --- | --- | --- | --- | ---: |
| **default** — Default | — | — | — | — | 27 |
| **startup** — Startup | `DOC-A01-004` Roadmap | Direction changes often and out loud; a written roadmap keeps the team pointing the same way. | `DOC-A23-001` Deprecation policy | A deprecation promise is about consumers you do not have yet; it becomes real once there are users. | 27 |
| **oss-library** — Open-source library | `DOC-A09-009` Code of conduct<br>`DOC-A06-008` Vulnerability management<br>`DOC-A09-006` Dependency policy | A public community needs a stated standard of behaviour and a way to report a breach.<br>A published package needs a disclosure route for vulnerabilities, as SECURITY.md.<br>Dependency policy is the maintainer's stated answer to supply-chain questions. | `DOC-A16-003` Runbook | A library is not operated; there is no on-call rotation for a package. | 29 |
| **internal-service** — Internal service | `DOC-A16-005` On call policy<br>`DOC-A12-001` SLI SLO SLA<br>`DOC-A17-001` Incident response | Someone is on call; the rotation and its expectations must be written.<br>An internal service still needs a stated reliability target and the error budget it implies.<br>Incidents happen to internal services too, and the response path should not be improvised. | `DOC-A10-008` License | An internal service is not redistributed, so there are no external licence terms to state. | 29 |
| **regulated** — Regulated | `DOC-A07-001` ROPA<br>`DOC-A05-006` Retention policy<br>`DOC-A20-002` Control catalog<br>`DOC-A24-003` Access review evidence | Processing personal data requires a record of what is processed, why, and with whom it is shared.<br>Retention must be decided before data accumulates, not after someone asks.<br>Controls are only credible when they are catalogued and mapped to evidence.<br>Access reviews are the evidence auditors ask for first; the record is the deliverable. | — | — | 31 |

That is 11 additions and 4 removals in total, every one of them re-checked by `check_catalog.py` against the admission rule (a reader question, a detectable predicate, its phases, and named checks or an explicit template-only label).

## The calls I would like you to make explicitly

Everything else I recommend approving as written. These are the rows where a reasonable owner could decide differently, with my recommendation:

| # | Call | My recommendation |
| --- | --- | --- |
| 1 | `DEV-B10-003` **Dependency setup** overlaps `DEV-B10-001` **Local setup**. Merge them, or keep both? | **Keep both.** One is "how do I run this", the other is "what may I depend on and how is it kept current" — they are read by different people on different days. |
| 2 | `DOC-A15-006` **Rollback procedure** and `DOC-A16-003` **Runbook** are core *by default* but gated by `has_deploy`. Is that the right gate? | **Yes.** Nothing that is not deployed has anything to roll back or operate; the gate is why the list does not demand a runbook from a library. |
| 3 | `startup` removes `DOC-A23-001` **Deprecation policy** and adds `DOC-A01-004` **Roadmap**. Right trade for a startup? | **Yes.** A startup owes its users a direction far more than a deprecation process it has no versions to apply. |
| 4 | `internal-service` removes `DOC-A10-008` **License**. | **Yes.** An internal service is not redistributed; the obligation to state redistribution terms follows publication, not use. |
| 5 | `regulated` adds ROPA, Retention policy, Control catalog and Access review evidence — no more, no less. | **Yes for AutoDOC's own scope**, with one caveat: this profile is a *prompt list*, never a certification. A real regulated project will also need documents no profile can name — vendor records, penetration tests, DR evidence — which is why they stay explicit gaps rather than rows here. |
| 6 | Anything you would demote from core outright? | **My one candidate: `DOC-A15-003` Changelog.** It becomes required at beta, which is right, but it is closer to "recommended" than "core". I would keep it: a changelog is the one document users read before upgrading. |

## What happens on approval

1. `CONTROL/metadata/CATALOG-RULES.json` and `CONTROL/metadata/PROFILES.json` gain a dated
   `owner_reviewed` note — the machine files stay machine files; the sentence is the record.
2. This page moves to `approved` with the date and any flagged row rewritten to the decided text.
3. `NEXT-ACTION.md` loses the "review the 27-type core list" item, and `ADOPTION.md` stops calling
   the membership unreviewed.
4. Any flagged row becomes its own change: an edit to the rule, the profile or the predicate, its
   catalog re-validation, and a test where the row has a consumer.

Nothing about this review retires the audit trail: the list, the profiles and the admission rule are
all diffable data, so the next review is a comparison, not an argument.
