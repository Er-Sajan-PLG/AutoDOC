---
id: DOC-P3-GOV-007
title: "MACP — Multi-Agent Coordination Protocol"
type: PROC
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "1.0"
effective_date: 2026-10-01
next_review: 2027-03-30
source_of_truth: human
supersedes: null
related: []
criticality: high
review_days: 180
last_verified: 2026-10-01
last_reviewed: 2026-10-01
last_updated: 2026-10-01
auto_generated: false
---
# MACP — Multi-Agent Coordination Protocol

> **Read this before taking any action on this repository.** It is the agent workflow. The
> coordination state lives in [`state/`](../../state/DASHBOARD.md); the repository's own
> [agent instructions](../../AGENTS.md) point here first.

**Source and completeness.** Sections *Core philosophy*, *The state directory structure* and
*Section 1* (Steps 1–9) are transcribed from the owner's protocol text of 2026-10-01; only the
═══ separators were converted to Markdown headings and nothing else was changed. The paste ended
part-way through Section 7, so Sections 2–6 are not present in this document, and Section 7
(Bootstrap) plus Sections 8–10 (logging, handoff, conflicts) are **reconstructed** from the
directory specification and the three unbreakable rules. Reconstructed text is marked
*(reconstructed)*; it will be replaced verbatim when the owner supplies the remainder.

**Precedence and local reconciliation.** MACP states that it wins over other instructions unless
the user overrides it. On this repository the owner has standing instructions that qualify it;
they are recorded here so no agent has to guess:

1. **Branch.** Work on the branch the session was assigned. Never switch, rename or force-push
   branches. MACP is branch-agnostic; the assignment is the owner's instruction.
2. **"Clean" is defined by the repository's gate.** Tree-green means `make ci` exits 0 on the
   tip (tests, catalog check, document control), with docs co-changed and `make generate` run
   first after edits to metadata, catalogs, templates, doc sources or tests. That *is* MACP's
   "never leave broken state" made concrete; exit-code contract: 2 config/usage, 3 internal
   failure, 1 findings, never 1 on a crash.
3. **`state/**` is coordination data, not a controlled document.** It is outside
   `engine.controlled()`, so state files carry no frontmatter and are excluded from inventory,
   freshness and stub checks — but they are still scanned by `guards.py` (local links, tribal
   phrases, inline key markers) and are committed and pushed like any other file.
4. **Do not link to plan files.** Plans are deleted when done; `guards.py` would then report a
   broken local link. Reference plans and archives as code spans (`` `state/plans/…` ``).
5. **Only the owner records owner decisions.** No agent writes `owner_reviewed`, approves a
   page, or closes a decision the owner has not stated. Agents propose; the owner decides, one
   decision at a time.
6. **`NEXT-ACTION.md` is the priority source of truth.** `state/DASHBOARD.md` summarizes it and
   must never contradict it; when they disagree, NEXT-ACTION wins and the dashboard is
   reconciled in the same session.

═══════════════════════════════════════════════════════════════
                    CORE PHILOSOPHY
═══════════════════════════════════════════════════════════════

You are stateless. The repository is not. Other agents have worked here before you, and others
will work here after you. Your job is not just to complete the task — it's to leave a perfect
record so the next agent can continue seamlessly.

Three unbreakable rules:

1. ALWAYS start by reading state. NEVER assume you know the current situation.
2. ALWAYS log your work in real-time. NEVER wait until the end to document.
3. ALWAYS end clean. NEVER leave uncommitted changes, broken state, or ambiguous handoffs.

═══════════════════════════════════════════════════════════════
                 THE STATE DIRECTORY STRUCTURE
═══════════════════════════════════════════════════════════════

All coordination happens through a `state/` directory at the repo root:

```
state/
├── DASHBOARD.md          # Executive summary — ALWAYS read first
├── REGISTRY.md           # Who's actively working and what files they own
├── INDEX.md              # Searchable log of all past sessions
├── ARCHITECTURE.md       # Current system architecture (living document)
├── DECISIONS.md          # Architecture Decision Records
├── DEBT.md               # Technical debt tracker
├── BLOCKERS.md           # Active blockers and dependencies
├── sessions/             # One file per agent session (your workspace)
├── plans/                # Active plans (deleted when done)
├── conflicts/            # Documented conflicts needing coordination
└── archive/              # Old sessions compressed by month
```

If this directory does not exist, you must create it via the Bootstrap Protocol (Section 7 below).

═══════════════════════════════════════════════════════════════
              SECTION 1: STARTUP SEQUENCE (MANDATORY)
═══════════════════════════════════════════════════════════════

Before you do ANY work, execute these steps in order:

**STEP 1 — Git Reconnaissance**

Run (or request to run):

```
git status
git branch -vva
git log --oneline -10
git stash list
git fetch --all
```

Confirm:

- [ ] Working tree is clean (if not, document why)
- [ ] You know which branch you're on
- [ ] No unresolved merge conflicts exist
- [ ] You have the latest from remote

**STEP 2 — Check if state/ directory exists**

IF `state/` DOES NOT EXIST → Jump to Section 7 (Bootstrap Protocol)
IF `state/` EXISTS → Continue to Step 3

**STEP 3 — Read DASHBOARD.md**

This gives you the full picture in <60 seconds:

- What's the current state of the project?
- Which agents are active right now?
- What are the critical alerts and blockers?
- What was recently completed?

Check the "Last Reconciled" timestamp at the top:

- <24h old → Trust it, proceed
- 24-48h old → Verify against git log before trusting
- \>48h old → STALE. You must reconcile DASHBOARD.md before working (read recent session files and rebuild it)

**STEP 4 — Read REGISTRY.md**

Identify:

- Who else is active on this repo right now
- Which files/directories they have claimed ownership of
- Whether your intended work overlaps with their claims

File ownership rules:

- If another ACTIVE agent owns files you need to modify → STOP. Either coordinate (add note to their session file), choose a different approach, or wait.
- If owner is INACTIVE (>24h) → You may claim ownership.
- Shared files (config, package.json, etc.) require a `[COORDINATION]` note in both session files.

**STEP 5 — Check BLOCKERS.md (if it exists)**

Confirm your task is not blocked by something upstream.
Confirm your task does not block another agent's work.

**STEP 6 — Targeted History Reading via INDEX.md**

Search INDEX.md by keyword or file path relevant to your task.
Read ONLY the 2-3 most relevant past session files.
DO NOT read every session file — that wastes your context window.

**STEP 7 — Read ARCHITECTURE.md and DECISIONS.md (conditionally)**

- Only read ARCHITECTURE.md if your task touches system structure
- Only read DECISIONS.md if you're about to make a design choice (someone may have already decided it)

**STEP 8 — Register Yourself**

Create your session file:

```
state/sessions/YYYYMMDD-HHMM-<AGENT-ID>-<short-slug>.md
```

Example: `state/sessions/20250614-1530-C7A2-fix-login-bug.md`

Add yourself to REGISTRY.md with:

- Your agent ID (invent one: 4 alphanumeric characters)
- Your model/type (e.g., "Claude 3.5 Sonnet")
- Your branch
- Your task (one line)
- Current UTC timestamp
- Files/directories you claim ownership of

**STEP 9 — Create a Plan Entry**

Add `state/plans/agent-<YOUR-ID>-<slug>.md` with:

- Objective
- Scope (what's in and out)
- Approach (step by step)
- Risks and mitigations
- Rollback strategy
- Success criteria

Only after all 9 steps are complete may you begin the task.

═══════════════════════════════════════════════════════════════
              SECTION 7: BOOTSTRAP PROTOCOL *(reconstructed)*
═══════════════════════════════════════════════════════════════

The owner's paste ended before this section. The procedure below is the minimum that satisfies
the directory specification above and the three unbreakable rules; it is flagged as
reconstructed and will be replaced when the owner supplies the original text.

1. **Preconditions.** Section 1 Step 1 is complete: clean tree, known branch, no unresolved
   conflicts, fetched remote. If the tree is not clean, stop and document why first.
2. **Create the tree exactly as specified** in "The state directory structure". `archive/` and
   `conflicts/` are empty at bootstrap; each holds a `.gitkeep` so the directory survives a
   fresh clone. Do not add files that the specification does not name.
3. **Seed the seven files.** Every one starts with a `Last reconciled:` line (UTC) except
   `INDEX.md`, which is a table:
   - `DASHBOARD.md` — project, branch, declared phase, active agents, alerts, recently
     completed, next actions, and the timestamp.
   - `REGISTRY.md` — one row per agent: id, model/type, branch, task, UTC start, claimed paths,
     status (`ACTIVE` / `INACTIVE <timestamp>`).
   - `INDEX.md` — session table: file, agent, date (UTC), task, outcome, commits.
   - `ARCHITECTURE.md` — a short living summary plus a pointer to the authoritative
     architecture document. It describes the system, not the coordination layer.
   - `DECISIONS.md` — dated entries: id, decision, decided by, status, evidence. An owner
     decision that is implemented but not yet recorded is `accepted — recording pending`, never
     `recorded`.
   - `DEBT.md` — id, what, impact, location, fix, status. No wish list: only debt the
     maintainers would act on.
   - `BLOCKERS.md` — only real blockers, each with the gate it blocks and who can clear it.
     "None" is a valid, complete entry.
4. **Write nothing you cannot source.** Absent history is written as "none recorded", never
   guessed. Dates are UTC.
5. **Register the bootstrapping agent** per Step 8 and open its session file; the bootstrap is
   logged like any other task, with the recovery and reconnaissance findings that led to it.
6. **Validate and land.** Run the repository's gate (`make ci`) and commit + push the bootstrap,
   so every later clone sees the state directory. Record the commit in the session file.
7. **Reconcile `Last reconciled:`** on every close-out, and after any handoff.

═══════════════════════════════════════════════════════════════
                  SECTION 8: LOGGING *(reconstructed)*
═══════════════════════════════════════════════════════════════

1. The session file is **append-only** and updated at each milestone — reconnaissance, plan,
   each state transition, each validation result, commit/push, handoff. Never wait until the end.
2. Every entry: UTC time, what changed, and the evidence (command, result). Facts, not intentions.
3. Corrections are new entries that name the superseded entry. History is never silently rewritten;
   a wrong claim is struck by a later entry, not deleted.
4. At close, add the session's row to `INDEX.md` and reconcile `DASHBOARD.md`.
5. Secrets never appear in state files; link to the mechanism, never the value.

═══════════════════════════════════════════════════════════════
                  SECTION 9: HANDOFF *(reconstructed)*
═══════════════════════════════════════════════════════════════

1. The last entry of a session is a Handoff block: **Objective · Status (done / paused /
   blocked) · Verified · Not verified · Next actions · Files · Commits · Open gates**.
   "Not verified" is mandatory even when empty; an empty list is a claim.
2. Set the registry row to `INACTIVE <UTC>` and release claims the work no longer needs.
3. Update `BLOCKERS.md` (add or clear) and reconcile the dashboard's alerts and next actions.
4. Stop mid-task only as a committed green checkpoint or after reverting; never leave a partial tree.
5. A handoff that requires reading the whole session file to act on is a failed handoff.

═══════════════════════════════════════════════════════════════
              SECTION 10: CONFLICTS *(reconstructed)*
═══════════════════════════════════════════════════════════════

1. An **active** claim wins. Do not edit a file another active agent claimed; add a
   `[COORDINATION]` note to **both** session files and pick different work, or wait.
2. **Shared files** (build config, `Makefile`, `pyproject.toml`, workflow files, machine policy
   under `CONTROL/metadata/`) always require a `[COORDINATION]` note in both sessions before an edit.
3. Unresolvable contention is written to `state/conflicts/<YYYYMMDD>-<slug>.md` with both claims
   and a timeline, and the contested files are left untouched until the owner decides.
4. A claim whose agent has been `INACTIVE` for more than 24h may be taken over; record the
   takeover in the new agent's session and in `INDEX.md`.
