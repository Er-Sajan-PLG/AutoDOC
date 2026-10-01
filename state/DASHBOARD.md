# DASHBOARD — AutoDOC

**Last reconciled:** 2026-10-01T12:43Z · **Reconciled by:** A476 (decision-round session `20261001-1242-A476`, ACTIVE) · **Tip at reconciliation:** `14310ea`

## Project

| Field | Value |
| --- | --- |
| Repository | `STEMORG2026/AutoDOC` — a self-updating documentation engine, not a compliance certificate |
| Branch | `arena/01a0f476-autodoc` (session branch; PR #2 open — the owner merges, and only after the decision round is worked through) |
| Declared phase | `build` (warn) — declared 2026-09-30, never inferred |
| Kinds / profile | `library` / `oss-library` (26 core types) |
| Catalog | 24 core · 49 extended · 265 types (prose still says 260 — D-001) · 16 detected facts · 3 declared traits |
| Build-ready | **15/16** · open core decisions **1** (`DOC-A05-001` Data model — waits on decision 4's fact override) |
| Promotion cliff | Promoting to `beta` today would fail **4** core rows (`DOC-A05-001`, License, Env var schema, Changelog); **2** after decision 4 |
| Stack | Python 3.11, **zero runtime dependencies**; pytest + pre-commit for dev; SQLite and a 3-route HTTP server only in the synthetic demo |
| Docs | 68 controlled (24 generated, 44 human-owned); 361 Markdown files tracked |
| Tests | 242 passed + 182 subtests, ~27 s (audit run, 2026-10-01) |
| CI | 5 workflows; required check `AutoDOC guard / check`; nightly freshness warn-only; tag-gated release |

## Active agents

`A476` — session `20261001-1242-A476` (**ACTIVE**): owner decision round — walk P-001…P-006 and
record each verdict only when the owner states it. Two earlier sessions are
**PAUSED (awaiting owner)** (`20261001-1228` lifecycle, `20261001-1219` cold-clone); three are
**landed — awaiting owner close** (`20261001-1110`, `-1120`, `-1130`). **No session is complete** —
only the owner closes one (ADR-009). Register yourself in `REGISTRY.md` before starting work.

## Alerts

1. **Owner confirmation pending (B-001)** on `docs/00-governance/CORE-LIST-REVIEW.md` v1.3 and its
   final counts. Recording `owner_reviewed`, page → `approved`, and caveat removal are **gated on the
   owner's confirmation**; no agent may record it.
2. Nothing is failing: the gate is green (`make ci` exit 0), tests 242/242, catalog valid,
   resolver at 15/16 with one open decision.
3. **Decision-3 deviation needs acknowledgement:** the ADR row was closed with a real ADR
   (`docs/adr/0001-zero-runtime-dependencies.md`) instead of the queued `[not_applicable]`, because
   the resolver reports every skip on an `always` row as a permanent stale-decision warning.
   Reversible; see the decision-3 session summary.
4. Environment resets recur (eight recoveries today, #11–#18: HEAD back to `19ca0d4`, wedged index,
   dirty-tree variant, venv deleted). #17 is logged in the lifecycle session, #18 in the
   decision-round session. Recovery recipe is in the audit session's summary; never force-push.
5. **Continuity verified:** a cold clone of this branch, read by a stranger, can state the position,
   the gates and the whole pending decision round, and can verify the numbers with system `python3`
   and no install (`state/sessions/20261001-1219-A476-cold-clone-test.md`).

6. **Sessions await the owner's close** (ADR-009, MACP local rule 8): no `A476` session is complete.
   Two are `PAUSED (awaiting owner)` (lifecycle, cold-clone), three are `landed — awaiting owner
   close`, and one is ACTIVE (this decision round); their plans are kept.
   Only the owner's word moves a session to CLOSED. Two companion rules came with this correction:
   **persist before presenting** (decision rounds live in `DECISIONS.md` § Pending, never only in
   chat) and the **handoff self-check** (local rule 10) — performed on the pushed branch this time,
   not requested from the owner.

## Recently landed (sessions await the owner's close)

| Date | Work | Commits |
| --- | --- | --- |
| 2026-10-01 | Session-lifecycle correction (owner instruction): MACP local rules 8–10 + ADR-009 — sessions close only on the owner's word; persist-before-present; handoff self-check; all sessions/plans relabelled; deleted plans restored where possible | `c57b149` + handoff-log `14310ea` |
| 2026-10-01 | Cold-clone continuity test: verdict (a new agent can continue from `state/` alone), five gap fixes, and the pending-decision dossier P-001…P-006 in `DECISIONS.md` | `b3a4490` + reconcile commit |
| 2026-10-01 | Owner decision 3 executed: 11 of 12 open core decisions closed (charter, README, ADR, module contract, test strategy, dependency setup/policy, SECURITY.md, CODE_OF_CONDUCT.md); readiness 4/16 → **15/16** | `1a65f5d` + reconcile commit |
| 2026-10-01 | Full MACP transcription (Sections 2–7 + REMEMBER) and the Section 7 bootstrap audit | `d26d798` + the reconcile commit |
| 2026-10-01 | MACP adopted: protocol in governance, `state/` bootstrapped, agent pointers | `868588e`, `f417a8f` |
| 2026-10-01 | Owner flags A/B/C applied and re-validated; `CORE-LIST-REVIEW.md` v1.3 (24 core / 49 extended; build-ready 4/16; beta cliff 12 of 24) | `f37d98a`, `c02d733` |
| 2026-10-01 | Core-list review delivered; license decided (Apache-2.0); enforcement layer; §3–§7 lanes | `5164b06`…`2454ea1`, `90478d4` |
| Earlier | Catalog, profiles, facts, triggers, evidence and language work | see `RECENT-CHANGES.md` |

## Next actions (source of truth: `NEXT-ACTION.md`)

1. **Owner: confirm or correct** the v1.3 core-list page and counts (B-001), and acknowledge the
   ADR-row deviation from decision 3.
2. On confirmation: record `owner_reviewed` in `CATALOG-RULES.json` + `PROFILES.json` (note names the
   flagged rows and their resolutions), page → `approved`, remove the caveat from NEXT-ACTION and
   ADOPTION, clear B-001, and refresh the stale statements D-011.
3. **The owner decision round is written up in full in `state/DECISIONS.md` § Pending** —
   P-001 (confirm the review), P-002 (ADR deviation), P-003 (decision 4: the four fact
   overrides/self-match, with the consumer table and the consumer-level effects), P-004 (branch
   protection payload), P-005 (phase and the promotion cliff), P-006 (deferred smalls). Present and
   execute one item at a time; only the owner states each decision. **Being walked with the owner
   now** (session `20261001-1242-A476`, ACTIVE). (Resets and the recovery recipe are in Alerts
   above.)

This dashboard summarizes; it never overrides `NEXT-ACTION.md` or an owner instruction. Sessions
are closed only by the owner.
