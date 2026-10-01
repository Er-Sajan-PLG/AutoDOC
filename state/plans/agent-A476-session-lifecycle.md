# Plan — A476 — session-lifecycle correction

| Field | Value |
| --- | --- |
| Objective | Correct the two process mistakes the owner identified: (1) sessions were closed by the agent instead of the owner; (2) a decision round reached chat before it existed in state, which forced the owner to ask for a cold-clone test. Fix the cause so neither recurs |
| Owner of the work | `A476` (session `20261001-1228-A476`) |
| Status | ACTIVE (work in flight) |
| Opened (UTC) | 2026-10-01T12:28Z |

## Scope

**In:** three local rules in `MACP.md` (8: sessions close only on the owner's word; 9: persist before
presenting; 10: handoff self-check); `ADR-009` recording the owner's instruction; relabelling every
session and plan to `landed — awaiting owner close`; restoring the plans that were deleted early;
the continuity self-check performed by the agent (not the owner).

**Out:** any decision. P-001…P-006 stay exactly as they are, waiting for the owner.

## Approach

1. Correct the labels and restore the plans (done in this session's first pass).
2. Record the rules and the ADR; reconcile DASHBOARD/REGISTRY/INDEX.
3. Perform the handoff self-check per new rule 10 and record the result.
4. Validate (`guards`, `make ci`), commit, push; leave the session `PAUSED (awaiting owner)`.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Relabelling looks like rewriting history | Every label change is named in an append-only correction note in the affected session file |
| A rule that exists on paper but is not followed | Rule 10 makes the agent perform the check at every handoff, and this session demonstrates it |
| The owner reads "PAUSED" as "work stopped" | PAUSED means *the ball is with the owner*, not that anything is unfinished |

## Rollback strategy

Revert the landing commit; the change set is `state/**` plus one block in `MACP.md`.

## Success criteria

- [ ] No file in `state/` says `COMPLETED` for an unclosed session; plans are present.
- [ ] Rules 8–10 and ADR-009 exist and are referenced from REGISTRY.
- [ ] A stranger's-eye self-check passes and is recorded.
- [ ] `make ci` exit 0; commits pushed; session left `PAUSED (awaiting owner)`.
