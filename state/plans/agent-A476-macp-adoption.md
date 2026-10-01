# Plan — A476 — adopt MACP

| Field | Value |
| --- | --- |
| Objective | Make MACP the operating protocol of this repository: the protocol text lives in governance, `state/` exists with real (not placeholder) content, and every future agent can start from it |
| Owner of the work | `A476` (session `20261001-1110-A476-macp-adoption.md`) |
| Status | **ACTIVE** — W1 complete on landing; W2 waits on the owner gate (B-001) |
| Opened (UTC) | 2026-10-01T11:10Z |

## Scope

**In:** `docs/00-governance/MACP.md` (protocol, transcribed + reconstructed bootstrap); the
`state/` tree and its seven files; pointers from `AGENTS.md`, `CLAUDE.md`, `AGENT-MEMORY.md`;
validation and landing of that set.

**Out:** any change to product behaviour, machine policy (`CONTROL/metadata/**`), the core-list
review gate, or the twelve open decisions. The next workstream (recording the owner's confirmation
and closing the open decisions) is *referenced* here, not started.

## Approach

1. Section 1 reconnaissance + recovery; confirm `state/` absence.
2. Scan the repository's checks for constraints on new files (controlled set, guards, pre-commit).
3. Write the protocol doc (verbatim where supplied, reconstructed sections flagged).
4. Seed the seven state files with sourced content; register the session; open this plan.
5. Add entry-point pointers; run `make generate`, tests, catalog check, `make ci`.
6. Commit + push; append validation and handoff entries to the session log; reconcile the dashboard.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| New files break the docs gate | Verified `state/**` is outside `engine.controlled()`; kept links resolvable for `guards.py`; full `make ci` before landing |
| State files drift from the real sources | Every file states its source (`NEXT-ACTION.md`, git history) and a `Last reconciled` line; the dashboard defers to NEXT-ACTION |
| Reconstructed protocol sections are mistaken for the owner's text | Clearly labelled *(reconstructed)* in place, with the paste's cut-off recorded at the top |
| Plans get deleted while session files still link to them | Rule 4 in `MACP.md`: reference plans as code spans, never as links |

## Rollback strategy

Revert the landing commit(s) with `git revert`; the change is additive (one new doc, one new
directory, one-line pointers in three existing docs). Nothing else depends on it, and reverting
removes `state/` from the tree without touching product code or machine policy.

## Success criteria

- [x] `docs/00-governance/MACP.md` exists, is valid controlled Markdown, and records its own completeness.
- [x] `state/` matches the specified structure with sourced content and no placeholders.
- [x] This session is registered in `REGISTRY.md` and summarised in `INDEX.md`.
- [ ] `make ci` exits 0 on the landing commit and the commit is pushed. *(in progress)*
- [x] A future agent can start from `AGENTS.md` → `MACP.md` → `state/DASHBOARD.md` without git archaeology.

When the owner confirms the v1.3 core-list page (B-001), this plan is superseded by the plan for
decision 3; at that point the file is deleted per MACP Section 7 and its outcome recorded in
`INDEX.md`.
