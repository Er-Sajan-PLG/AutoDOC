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

> **Acknowledge that you have read and understood this protocol before beginning any task.** It is
> the agent workflow. The coordination state lives in [`state/`](../../state/DASHBOARD.md); the
> repository's own [agent instructions](../../AGENTS.md) point here first.

**Source and completeness.** The full protocol below (core philosophy, the state directory
structure, and Sections 1–7 plus REMEMBER) is transcribed from the owner's text of 2026-10-01.
Only the `═══` separators were converted to Markdown headings and the checkboxes kept as Markdown
task lists; the words are unchanged. An earlier revision of this file, written before the owner
supplied Sections 2–7, contained *reconstructed* Sections 7–10; those reconstructions are removed
and were replaced by the owner's actual text (recorded in
`state/sessions/20261001-1120-A476-bootstrap-audit.md`).

**Precedence and local reconciliation.** MACP states that it wins over other instructions unless
the user overrides it. On this repository the owner has standing instructions that qualify it;
they are recorded here so no agent has to guess:

1. **Branch.** Work on the branch the session was assigned. Never switch, rename or force-push
   branches. MACP is branch-agnostic; the assignment is the owner's instruction.
2. **"Clean" is defined by the repository's gate.** Tree-green means `make ci` exits 0 on the tip
   (tests, catalog check, document control), with docs co-changed and `make generate` run first
   after edits to metadata, catalogs, templates, doc sources or tests. That *is* MACP's "never
   leave broken state" made concrete; exit-code contract: 2 config/usage, 3 internal failure,
   1 findings, never 1 on a crash.
3. **`state/**` is coordination data, not a controlled document.** It is outside
   `engine.controlled()`, so state files carry no frontmatter and are excluded from inventory,
   freshness and stub checks — but they are still scanned by `guards.py` (local links, tribal
   phrases, inline key markers) and are committed and pushed like any other file.
4. **Do not link to plan files.** Plans are deleted when done; `guards.py` would then report a
   broken local link. Reference plans and archives as code spans (`` `state/plans/…` ``).
5. **Only the owner records owner decisions.** No agent writes `owner_reviewed`, approves a page,
   or closes a decision the owner has not stated. Agents propose; the owner decides, one decision
   at a time.
6. **`NEXT-ACTION.md` is the priority source of truth.** `state/DASHBOARD.md` summarizes it and
   must never contradict it; when they disagree, NEXT-ACTION wins and the dashboard is reconciled
   in the same session.
7. **Step 8 registers; Section 2 then freezes.** Step 8's write to `REGISTRY.md` happens during
   startup, before Step 9's work begins. From then on, Section 2 applies: `DASHBOARD.md`,
   `REGISTRY.md` and `INDEX.md` are not touched during active work — Section 4's shutdown sequence
   and its reconciliation step update them.

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

Only after all 9 steps are complete may you begin actual work.

═══════════════════════════════════════════════════════════════
             SECTION 2: DURING WORK (LIVE LOGGING)
═══════════════════════════════════════════════════════════════

While working, maintain a running log in YOUR session file. Write ONLY to your own session file
during active work. Do not touch DASHBOARD.md, REGISTRY.md, or INDEX.md until shutdown.

Log every significant event using these tags:

```
[START]         — Beginning a work phase
[PROGRESS]      — Completed a milestone
[DISCOVERY]     — Found something unexpected
[PIVOT]         — Changing approach from the original plan
[DECISION]      — Chose between alternatives (document rationale)
[BLOCKER]       — Cannot proceed, need resolution
[COORDINATION]  — Need to notify or sync with another agent
[DEBT]          — Introducing known technical debt
[BUG FOUND]     — Found unrelated bug (log it, don't fix unless blocking)
[SECURITY]      — Security-relevant consideration
[SCOPE EXPANSION] — Doing something beyond original plan (must justify)
[DISCREPANCY]   — State files don't match reality
```

Example entries:

```
`15:45` [DISCOVERY] Found that auth.ts exports changed in last session.
        Adjusted my refactor to preserve backward compatibility.
`16:12` [PIVOT] Redis approach won't work — Redis isn't in the stack.
        Switching to DB-backed solution.
`16:30` [COORDINATION] Modified shared config.ts. Notified agent B3K1
        via note in their session file.
```

Scope discipline:

- If a "quick fix" reveals a deeper issue → log [BUG FOUND], stay focused.
- If you must expand scope → log [SCOPE EXPANSION] with justification.
- Never silently refactor unrelated code.
- Never fix unrelated bugs unless they block your current work.

═══════════════════════════════════════════════════════════════
         SECTION 3: VALIDATION (BEFORE DECLARING DONE)
═══════════════════════════════════════════════════════════════

Nothing is "done" until verified. Run and confirm:

- [ ] All tests pass (full suite, not just yours)
- [ ] Linter passes with no new violations
- [ ] Type checker passes (if applicable)
- [ ] Build succeeds (if applicable)
- [ ] No secrets, credentials, or .env files in your diff
- [ ] No debug/console statements left in production code
- [ ] Error handling exists for all IO, network, and parsing operations
- [ ] Documentation updated if behavior changed
- [ ] Database migrations are reversible (if applicable)

If any check fails and you cannot fix it in scope:

→ Log it in your session file with severity and remediation plan
→ Do NOT silently skip it

═══════════════════════════════════════════════════════════════
              SECTION 4: SHUTDOWN SEQUENCE (MANDATORY)
═══════════════════════════════════════════════════════════════

**STEP 1 — Finalize Your Session File**

Add a complete summary section:

- Outcome: COMPLETED | PARTIAL | BLOCKED | PIVOTED
- What was accomplished
- What was NOT accomplished and why
- Files changed (table: path, action, summary)
- Key decisions made and rationale
- Technical debt introduced (if any)
- Bugs discovered but not fixed (with location)
- Risks and warnings for the next agent
- Prioritized next steps

**STEP 2 — Update REGISTRY.md**

Change your status from IN-PROGRESS to COMPLETED.
Release your file ownership claims.

**STEP 3 — Clean Up state/plans/**

If your plan is complete, delete your plan file.
If partially complete, update it with current status.

**STEP 4 — Add Entry to INDEX.md**

One row with: session ID, your agent, date, title, files touched, status, branch.

**STEP 5 — Git Cleanup**

Verify:

- [ ] Working tree is clean
- [ ] All changes committed with descriptive messages
- [ ] Branch pushed to remote
- [ ] No orphan files or forgotten artifacts

**STEP 6 — Reconciliation (IF applicable)**

If you are the last active agent OR if you merged branches:

You are the RECONCILER. You must:

- Rebuild DASHBOARD.md to reflect current merged reality
- Update REGISTRY.md (remove inactive agents)
- Resolve any conflicts in state/conflicts/
- Update ARCHITECTURE.md if structure changed
- Add any new ADRs to DECISIONS.md
- Commit: "chore(state): reconcile after <description>"

═══════════════════════════════════════════════════════════════
            SECTION 5: CONFLICT HANDLING RULES
═══════════════════════════════════════════════════════════════

If you discover a conflict (overlapping files, contradictory plans, stale ownership, merge issues):

1. STOP active work.
2. Create a file in `state/conflicts/` describing:
   - What the conflict is
   - Which agents/sessions are involved
   - Proposed resolution
3. If the other agent is active (<24h), add a `[COORDINATION REQUEST]` note in their session file.
4. If the other agent is inactive, document your takeover and proceed.
5. If the conflict is unresolvable without human input, mark it `[NEEDS HUMAN]` in BLOCKERS.md and halt.

Never silently overwrite another agent's work. Never resolve a conflict by just "going first and
hoping."

═══════════════════════════════════════════════════════════════
          SECTION 6: ANTI-PATTERNS (NEVER DO THESE)
═══════════════════════════════════════════════════════════════

- ❌ Starting work without reading DASHBOARD.md and REGISTRY.md
- ❌ Reading every single file in state/sessions/ (wastes context)
- ❌ Modifying files owned by an active agent without coordination
- ❌ Writing to DASHBOARD.md, REGISTRY.md, or INDEX.md during active work
- ❌ Leaving uncommitted changes at session end
- ❌ Fixing unrelated bugs without logging them first
- ❌ Silently expanding scope beyond the original plan
- ❌ Catching errors without logging or re-throwing
- ❌ Committing secrets, API keys, or .env files
- ❌ Trusting a DASHBOARD.md that's >48h stale without verification
- ❌ Skipping tests because they're "probably fine"
- ❌ Making handoff notes assuming the next agent has your context

═══════════════════════════════════════════════════════════════
          SECTION 7: BOOTSTRAP PROTOCOL (NO state/ EXISTS)
═══════════════════════════════════════════════════════════════

If the `state/` directory does not exist, you are the first agent under this protocol. Perform a
full repository audit before any other work:

**STEP 1 — Comprehensive Audit**

Investigate and document:

- Directory structure (tree, depth 3-4, exclude node_modules/.git)
- Technology stack (languages, frameworks, versions)
- Entry points and main modules
- Database type and migration state
- API surface (endpoints, auth mechanism)
- Testing framework and current test status (run them!)
- CI/CD configuration
- Dependencies (outdated, vulnerable)
- Documentation state (README accuracy, inline docs)
- Known issues visible in code (TODOs, FIXMEs, broken areas)
- Current working features vs broken features

**STEP 2 — Create state/ Structure**

Create the directory and these initial files:

- DASHBOARD.md     — summary of your audit findings
- REGISTRY.md      — empty table, ready for agents
- INDEX.md         — empty, ready for sessions
- ARCHITECTURE.md  — architecture summary from audit
- DECISIONS.md     — empty, ready for ADRs
- DEBT.md          — list all tech debt found in audit
- BLOCKERS.md      — list any blockers found
- sessions/        — directory with your first session file
- plans/           — empty directory
- conflicts/       — empty directory
- archive/         — empty directory

**STEP 3 — Create Your Bootstrap Session File**

Document the audit itself as your first session.
Filename: `state/sessions/YYYYMMDD-HHMM-<ID>-bootstrap-audit.md`

**STEP 4 — Commit the Bootstrap**

Commit message:

```
chore(state): bootstrap MACP protocol with repository audit
```

**STEP 5 — Now Proceed to Normal Startup (Section 1)**

Treat the bootstrap as complete and proceed with your actual task.

═══════════════════════════════════════════════════════════════
                      REMEMBER
═══════════════════════════════════════════════════════════════

- You are one of many agents. Act like it.
- The `state/` directory is the shared brain. Keep it accurate.
- When in doubt: document more, assume less.
- A clean handoff is more valuable than a clever shortcut.
- If you break the protocol, document why — don't hide it.
