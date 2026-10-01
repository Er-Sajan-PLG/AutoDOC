# Plan — A476 — owner decision round (walkthrough)

| Field | Value |
| --- | --- |
| Objective | Present P-001…P-006 one at a time and execute each stated verdict; record each decision in the commit that implements it |
| Owner of the work | `A476` (session `20261001-1242-A476`) |
| Status | **PAUSED (awaiting owner)** — the round is executed (P-001…P-006; P-004's apply is owner-run); kept until the owner closes the session (MACP local rule 8) |
| Opened (UTC) | 2026-10-01T12:42Z |

## Scope

**In:** the six pending items exactly as dossiered in `state/DECISIONS.md` § Pending, plus the work a
stated verdict implies — P-001: dated `owner_reviewed` notes in `CATALOG-RULES.json` and
`PROFILES.json`, the review page → `approved`, caveat removal from `NEXT-ACTION.md` and
`ADOPTION.md`, the two stale page figures refreshed, D-011; P-002: acknowledge or edit the ADR row;
P-003: the four fact overrides in `autodoc.toml` + the detector self-exclusion fix + the consumer
effects, then the resolver re-run (15/16 → 15/15); P-004: print/apply the branch-protection payload
(owner-run by design); P-005: the phase call — no edit if `build` stays; P-006: deferrals stay
recorded in `DEBT.md`. Validation (`make ci`) and push per change.

**Out:** merging PR #2 (the owner merges); any item the owner has not stated; implementing the P-006
deferrals.

## Approach

1. Startup reconcile — done: session registered, two dashboard defects fixed, restore #18 logged.
2. Present the round from the dossier; wait for the owner's pick and verdict.
3. Execute a stated verdict as its own commit; `make ci` exit 0; push; the decision recorded in the
   same commit via `state/DECISIONS.md`.
4. Repeat per item; hand off under rule 10; the session stays open until the owner closes it.

## Progress

- 2026-10-01: executed P-003 (`c7980f9`), P-001 (`039e508`), P-002 (`3ad5a57`), recorded P-004…P-006,
  reconciled and handed off (`5dd9112`, `e14135e`). Rule-10 self-check passed on a fresh clone.
