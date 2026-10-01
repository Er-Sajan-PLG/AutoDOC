# DASHBOARD — AutoDOC

**Last reconciled:** 2026-10-01T14:08Z · **Reconciled by:** A476 (post-merge test session `20261001-1408-A476`, PAUSED awaiting owner) · **Tip at reconciliation:** `4d0c50f` on `master` (**PR #2 merged**, GitHub's merge commit) · session branch carries the record commit

## Project

| Field | Value |
| --- | --- |
| Repository | `STEMORG2026/AutoDOC` — a self-updating documentation engine, not a compliance certificate |
| Branch | `arena/01a0f476-autodoc` (session branch) — **PR #2 merged to `master`** at `4d0c50f` (2026-10-01T14:06:47Z); follow-up record commits are offered as a new PR |
| Declared phase | `build` (warn) — declared 2026-09-30, never inferred |
| Kinds / profile | `library` / `oss-library` (26 core types) |
| Catalog | 24 core · 49 extended · 265 types (prose still says 260 — D-001) · 16 detected facts · 3 declared traits |
| Build-ready | **15/15** · open core decisions **0** (owner decision 4 closed the last one, `DOC-A05-001` Data model, as not applicable) |
| Promotion cliff | Promoting to `beta` today would fail **2** core rows (License `DOC-A10-008`, Changelog `DOC-A15-003`); both gated on `is_public` |
| Stack | Python 3.11, **zero runtime dependencies**; pytest + pre-commit for dev; SQLite and a 3-route HTTP server only in the synthetic demo |
| Docs | 68 controlled (24 generated, 44 human-owned); 361 Markdown files tracked |
| Tests | 243 passed + 182 subtests, ~31 s (owner-round run, 2026-10-01) |
| CI | 5 workflows; required check `AutoDOC guard / check`; nightly freshness warn-only; tag-gated release |

## Active agents

`A476` — session `20261001-1408-A476` (**PAUSED (awaiting owner)**): merged PR #2 and ran the
post-merge continuity test on a cold clone of `master` (passed: state-only read, cold numbers,
`make ci` exit 0, `AutoDOC guard` green on `master`); the branch-protection apply is not possible
from this sandbox (App lacks Administration) and stays the owner's command.
`A476` — session `20261001-1242-A476` (**PAUSED (awaiting owner)**): the owner decision round — all
six verdicts executed or recorded (P-003 → `c7980f9`, P-001 → `039e508`, P-002 → `3ad5a57`, P-004
owner-run payload, P-005/P-006 records, shutdown/self-check → `5dd9112`…`ce4feba`); awaiting the
owner's close. Four sessions are
**PAUSED (awaiting owner)** (`20261001-1228` lifecycle, `20261001-1219` cold-clone, `20261001-1242`
decision round, `20261001-1408` post-merge test);
three are **landed — awaiting owner close** (`20261001-1110`, `-1120`, `-1130`). **No session is
complete** — only the owner closes one (ADR-009). Register yourself in `REGISTRY.md` before
starting work.

## Alerts

1. **B-001 cleared (2026-10-01)** — the owner confirmed the v1.3 page ("proceed with recomendation")
   and the recording landed: `owner_reviewed` in both machine files, page → `approved`, caveat off
   `NEXT-ACTION.md` + `ADOPTION.md`, D-011 fixed (commit `039e508`).
2. Nothing is failing: the gate is green (`make ci` exit 0), tests 243/243, catalog valid,
   resolver at **15/15 with zero open decisions**.
3. **B-002 cleared (2026-10-01)** — the owner acknowledged the decision-3 deviation and kept the
   real ADR; ADR-008 records it (commit `3ad5a57`). The ADR row was closed with a real ADR
   (`docs/adr/0001-zero-runtime-dependencies.md`) instead of the queued `[not_applicable]`, because
   the resolver reports every skip on an `always` row as a permanent stale-decision warning.
   Reversible; see the decision-3 session summary.
4. Environment resets recur (ten recoveries today, #11–#20: HEAD back to `19ca0d4`, wedged index,
   dirty-tree variant, venv deleted). #17 is logged in the lifecycle session; #18, #19 and #20 in
   the decision-round session. Recovery recipe is in the audit session's summary; never force-push.
5. **Continuity verified before and after the merge:** the merged `master` itself was tested cold
   (depth-1 clone, state-only read, cold `python3` numbers, `make ci` exit 0) — for the pre-merge
   check see `state/sessions/20261001-1219-A476-cold-clone-test.md`. A cold clone of this branch, read by a stranger, can state the position,
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
| 2026-10-01 | **PR #2 merged to `master`** (`4d0c50f`, 14:06:47Z) and the post-merge continuity test passed: cold clone of `master`, state-only read correct, cold numbers 15/15 · 0 open, `make ci` exit 0, `AutoDOC guard` green on the master push | merge commit `4d0c50f` + the record commit on the session branch |
| 2026-10-01 | Owner round executed: decision 4 landed; the review recorded (`owner_reviewed`, page → `approved`, caveat off, D-011 — **B-001 cleared**); the ADR deviation acknowledged (**B-002 cleared**); the branch-protection payload printed (owner-run application); shutdown reconcile + rule-10 self-check + session log ordered | `c7980f9`, `039e508`, `3ad5a57`, `5dd9112`, `e14135e`, `ce4feba` |
| 2026-10-01 | Owner decision 4 executed: the demo-only facts are declared false with reasons; the detector's self-match is fixed at its source (no override, regression-tested); the last open core decision closes — **15/15, 0 open**; beta cliff 4 → 2 | `c7980f9` |
| 2026-10-01 | Session-lifecycle correction (owner instruction): MACP local rules 8–10 + ADR-009 — sessions close only on the owner's word; persist-before-present; handoff self-check; all sessions/plans relabelled; deleted plans restored where possible | `c57b149` + handoff-log `14310ea` |
| 2026-10-01 | Cold-clone continuity test: verdict (a new agent can continue from `state/` alone), five gap fixes, and the pending-decision dossier P-001…P-006 in `DECISIONS.md` | `b3a4490` + reconcile commit |
| 2026-10-01 | Owner decision 3 executed: 11 of 12 open core decisions closed (charter, README, ADR, module contract, test strategy, dependency setup/policy, SECURITY.md, CODE_OF_CONDUCT.md); readiness 4/16 → **15/16** | `1a65f5d` + reconcile commit |
| 2026-10-01 | Full MACP transcription (Sections 2–7 + REMEMBER) and the Section 7 bootstrap audit | `d26d798` + the reconcile commit |
| 2026-10-01 | MACP adopted: protocol in governance, `state/` bootstrapped, agent pointers | `868588e`, `f417a8f` |
| 2026-10-01 | Owner flags A/B/C applied and re-validated; `CORE-LIST-REVIEW.md` v1.3 (24 core / 49 extended; build-ready 4/16; beta cliff 12 of 24) | `f37d98a`, `c02d733` |
| 2026-10-01 | Core-list review delivered; license decided (Apache-2.0); enforcement layer; §3–§7 lanes | `5164b06`…`2454ea1`, `90478d4` |
| Earlier | Catalog, profiles, facts, triggers, evidence and language work | see `RECENT-CHANGES.md` |

## Next actions (source of truth: `NEXT-ACTION.md`)

1. **Owner: apply the required check** — `APPLY=1 make docs-require-check`, or Settings → Branches
   with the status check `AutoDOC guard / check`. Two attempts from this sandbox failed on
   permissions (403 read / 404 write; nothing changed) — the connection's GitHub App has no
   Administration permission, so this stays owner-run.
2. **Owner: merge the follow-up record PR** that carries this reconcile (post-merge test result,
   sessions and counters) into `master`, if you want it there.
3. **Owner: close the sessions you consider done** (ADR-009, rule 8). Four are
   `PAUSED (awaiting owner)` and three are `landed — awaiting owner close`; none is closed by an
   agent.
4. Nothing is failing: `make ci` exit 0 on the merged `master` clone; **B-001 and B-002 cleared**;
   P-001…P-006 executed or recorded. Resets and the recovery recipe are in Alerts above; never
   force-push.

This dashboard summarizes; it never overrides `NEXT-ACTION.md` or an owner instruction. Sessions
are closed only by the owner.
