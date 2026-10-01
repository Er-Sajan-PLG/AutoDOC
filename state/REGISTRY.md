# REGISTRY — who is working here and what they own

**Last reconciled:** 2026-10-01T11:29Z

## Active

None. Agent `A476` completed both sessions; no other agent has ever registered. The next agent
starts by opening a new session file and adding itself here (Section 1 Step 8).

| Agent ID | Model / type | Branch | Task (one line) | Started (UTC) | Claimed paths | Status |
| --- | --- | --- | --- | --- | --- | --- |
| — | — | — | — | — | — | — |

## Completed

| Agent ID | Session | Model / type | Branch | Task | Completed (UTC) | Claims released |
| --- | --- | --- | --- | --- | --- | --- |
| `A476` | `sessions/20261001-1110-A476-macp-adoption.md` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Adopt MACP: protocol in governance, bootstrap `state/`, register | 2026-10-01T11:13Z | `state/**`, `docs/00-governance/MACP.md`, `AGENTS.md`, `CLAUDE.md`, `AGENT-MEMORY.md` |
| `A476` | `sessions/20261001-1120-A476-bootstrap-audit.md` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Transcribe the full protocol (Sections 2–7 + REMEMBER), complete the Section 7 bootstrap audit, reconcile state | 2026-10-01T11:29Z | `state/**`, `docs/00-governance/MACP.md` |

No inactive agent needs removing — the table above is the whole history.

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
- Step 8 registration is the one startup write to this file; Section 2 forbids further writes until
  shutdown (Section 4 reconciles).
