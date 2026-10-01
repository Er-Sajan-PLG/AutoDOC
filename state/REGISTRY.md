# REGISTRY — who is working here and what they own

**Last reconciled:** 2026-10-01T12:32Z

## Active — work in flight, or landed and awaiting the owner

| Agent ID | Model / type | Branch | Task (one line) | Started (UTC) | Claimed paths | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `A476` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Owner decision round: all six verdicts executed or recorded (P-003 `c7980f9`, P-001 `039e508`, P-002 `3ad5a57`, P-004 payload owner-run, P-005/P-006 records); awaiting the owner's close | 2026-10-01T12:42Z | released (round closed) | **PAUSED** (awaiting owner) |
| `A476` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Session-lifecycle correction: sessions close only on the owner's word; persist-before-present; handoff self-check | 2026-10-01T12:28Z | `state/**`, `docs/00-governance/MACP.md` (released) | **PAUSED** (awaiting owner) |
| `A476` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Cold-clone continuity test (verdict, gap fixes, the P-001…P-006 dossier) | 2026-10-01T12:19Z | `state/**` only | **PAUSED** (awaiting owner) |

## Landed — awaiting the owner's close (no claims held)

| Agent ID | Session | Model / type | Branch | Task | Landed (UTC) | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `A476` | `sessions/20261001-1110-A476-macp-adoption.md` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Adopt MACP: protocol in governance, bootstrap `state/`, register | 2026-10-01T11:13Z | landed — awaiting owner |
| `A476` | `sessions/20261001-1120-A476-bootstrap-audit.md` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Transcribe the full protocol; Section 7 audit; reconcile | 2026-10-01T11:29Z | landed — awaiting owner |
| `A476` | `sessions/20261001-1130-A476-decision-3.md` | Arena.ai Agent Mode | `arena/01a0f476-autodoc` | Close the open core decisions (11 of 12; 4/16 → 15/16) | 2026-10-01T11:44Z | landed — awaiting owner |

## Closed by the owner

None yet. Only the owner's word moves a row here (MACP local rule 8).

## Non-agent owner

| Who | Role | Scope |
| --- | --- | --- |
| `@Er-Sajan-PLG` | Repository owner and sole reviewer | Approves governed documents, records owner decisions, closes sessions, merges PRs. No backup reviewer is configured. |

## Rules in force here

- **Sessions close only on the owner's word** (local rule 8): agents mark `PAUSED (awaiting owner)`;
  `COMPLETED`/`CLOSED` are the owner's labels, and a session's plan stays until then.
- **Persist before presenting** (local rule 9): decision rounds live in `DECISIONS.md` § Pending,
  never only in chat.
- **Handoff self-check** (local rule 10): before handing off, read the state as a stranger; if the
  next actions cannot be executed from state alone, fix state first.
- An **active** claim wins; shared files (`Makefile`, `pyproject.toml`, workflows,
  `CONTROL/metadata/**`) need a `[COORDINATION]` note in both sessions.
- A claim held by an agent `INACTIVE` for **>24h** may be taken over; record the takeover.
- Only the owner records owner decisions. Agents propose and implement; the owner decides, and
  takes decisions one at a time.
