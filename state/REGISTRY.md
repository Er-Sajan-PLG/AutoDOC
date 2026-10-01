# REGISTRY — who is working here and what they own

**Last reconciled:** 2026-10-01T11:13Z

## Active

| Agent ID | Model / type | Branch | Task (one line) | Started (UTC) | Claimed paths | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `A476` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Adopt MACP: write the protocol, bootstrap `state/`, register this session | 2026-10-01T11:10Z | `state/**` (retained); `docs/00-governance/MACP.md`, `AGENTS.md`, `CLAUDE.md`, `AGENT-MEMORY.md` (released on landing) | INACTIVE 2026-10-01T11:13Z — paused on B-001, owner reply resumes |

## Inactive / expired claims

None recorded. `state/` was bootstrapped on 2026-10-01; no earlier agent sessions exist in this
protocol. Sessions before that date live in git history and `docs/00-governance/`.

## Non-agent owner

| Who | Role | Scope |
| --- | --- | --- |
| `@Er-Sajan-PLG` | Repository owner and sole reviewer | Approves governed documents, records owner decisions, merges PRs. No backup reviewer is configured. |

## Rules in force here

- An **active** claim wins: do not edit claimed paths; add a `[COORDINATION]` note to both session
  files and choose different work, or wait.
- **Shared files** (build config, `Makefile`, `pyproject.toml`, workflows, `CONTROL/metadata/**`)
  always require a `[COORDINATION]` note in both sessions before an edit.
- A claim held by an agent `INACTIVE` for **>24h** may be taken over; record the takeover in your
  session and in `INDEX.md`.
- Only the owner records owner decisions. Agents propose and implement; the owner confirms.
