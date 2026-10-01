# Plan — A476 — cold-clone continuity test

| Field | Value |
| --- | --- |
| Objective | Answer the owner's question with evidence: can a brand-new agent continue this work from a cold clone using `state/` alone? Then make the answer yes by closing any gap found |
| Owner of the work | `A476` (session `20261001-1219-A476`) |
| Status | ACTIVE |
| Opened (UTC) | 2026-10-01T12:19Z |

## Scope

**In:** a scratch clone of `arena/01a0f476-autodoc` from GitHub under `/tmp/cold-agent-test`; a
state-only read of it; a written verdict (what a cold reader knows, what it cannot know); state-file
fixes for any gap found; re-test on a second fresh clone; commit + push.

**Out:** product code, catalog, machine policy, and any owner decision. This test changes `state/**`
only.

## Approach

1. `git clone --branch arena/01a0f476-autodoc` from GitHub into `/tmp/cold-agent-test` (true stranger's
   view: only what is pushed).
2. Read nothing but the files MACP tells a new agent to read, and write down what they imply:
   current state, next work, pending owner decisions.
3. Diff that against what is actually needed to continue (the six-item decision round) and list gaps.
4. Fix the gaps in `state/**` (details, not narrative).
5. Re-clone and re-read the fixed state; confirm the gaps are closed.
6. Validate (`guards.py`, `make ci`), commit, push, shutdown per Section 4.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| The author (me) knows things the cold reader cannot — self-fulfilling test | Read only the clone's state files for the verdict; every claim in the verdict cites a state file and line |
| The clone tests the pushed state, not the worktree — a gap in one but not the other | That is the point: the clone is what a stranger gets |
| Fixing gaps by adding prose that nobody will read | Keep it in the files a cold reader already opens (DASHBOARD next actions, DECISIONS pending section, BLOCKERS) |

## Rollback strategy

Revert the landing commit; the change is `state/**` only.

## Success criteria

- [ ] A written verdict, evidence-based, from a real cold clone.
- [ ] Any gap found is fixed in state and re-verified on a second cold clone.
- [ ] `make ci` exit 0; commits pushed; PR checks green; Section 4 shutdown complete.
