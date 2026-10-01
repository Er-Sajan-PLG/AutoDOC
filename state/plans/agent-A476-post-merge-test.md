# Plan — A476 — post-merge continuity test

| Field | Value |
| --- | --- |
| Objective | Merge PR #2, then prove the merged repository still works from the outside: a stranger's read of `state/` and the full gate on a cold clone of `master` |
| Owner of the work | `A476` (session `20261001-1408-A476`) |
| Status | **PAUSED (awaiting owner)** — kept until the owner closes the session (MACP local rule 8) |
| Opened (UTC) | 2026-10-01T14:08Z |

## Scope

**In:** the branch-protection apply attempt (owner-instructed), the PR #2 merge, a depth-1 clone of
`master` under `/tmp/postmerge-test`, the state-only read, the cold numeric checks with system
`python3`, `make ci` on the clone, the `master` workflow runs, and the state record of all of it.

**Out:** any product change; pushing to `master` (work stays on the session branch, recorded in
state and offered as a follow-up pull request).

## Approach

1. Attempt `APPLY=1 make docs-require-check` on the owner's instruction; record the permission
   result honestly (403 read / 404 write, nothing changed).
2. Merge PR #2 with a merge commit; keep the branch.
3. Cold clone `master`; read `state/` as a stranger; verify the numbers with system `python3`.
4. Run the full gate (`make ci`) on the clone and check the `master` push runs.
5. Record results here and in `state/**`; land as the record commit, offered as its own PR.

## Progress

- 2026-10-01: apply attempted (not possible from this sandbox); PR #2 merged (`4d0c50f`); cold clone
  test passed (`make ci` exit 0; `AutoDOC guard` green on `master`).
