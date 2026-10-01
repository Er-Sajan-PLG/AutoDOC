# ARCHITECTURE — coordination-layer view

**Last reconciled:** 2026-10-01 (audit-complete; same day)

This file is the agent's orientation map, not the authoritative design. When they disagree, the
authoritative documents win: `docs/05-architecture/AUTODOC-ARCHITECTURE.md` (system),
`docs/00-governance/ENGINE-COVERAGE.md` (what is verified, and its limits),
`CONTROL/metadata/CONTEXT-MODEL.json` (phases, enforcement, facts).

## Components

| Piece | Where | Role |
| --- | --- | --- |
| Sync engine | `scripts/doc-sync/*` | Sources → deterministic generators → mapped targets; drift, impact, freshness checks |
| Intelligence | `scripts/intelligence/*` | `profile` (facts) → `context` (declarations) → `recommend` (applicability) → `enforce` (severity at the declared phase) → `triggers` (when CI runs what) |
| Doc control | `scripts/doc-control/*` | Catalog build/check, guards, health, evidence packing, release snapshot, link checks, hooks |
| Machine policy | `CONTROL/metadata/*` | Rules, profiles under review, context model, triggers, schemas — machine-written JSON |
| Catalog + templates | `CATALOG-A/B/C`, `TEMPLATES/**` | 265 document types, 24 core, 49 extended; templates per type |
| Governed docs | `docs/**` + named root files | Human-owned controlled Markdown with frontmatter, review dates, ownership |
| Coordination | `state/**` | This protocol's workspace. **Not** part of the product architecture and excluded from `engine.controlled()` |

## Flows

- **Documentation:** mapped source → generator (labeled `exact` or `heuristic`) → target; `docs-drift` fails the build when a target is stale.
- **Applicability:** three-valued facts → profile → `recommend` → decision states (`[instantiated]`, `[satisfied_by]`, `[not_applicable]`, open, off, undetermined) at the declared phase's severity.
- **Gating:** `CONTROL/metadata/TRIGGERS.json` declares which events run what; one blocking event, one required status check (`AutoDOC guard / check`), network checks scheduled and warn-only.

## Invariants worth knowing before touching anything

1. Facts are capability-named (`has_cli`), three-valued (true / false / **unknown** — never silently false), and either detector-backed (with stated limits and fixtures) or declaration-only with a reason.
2. Phase, kinds, obligations and personal-data/payment/safety traits are **declared, never inferred**; evidence is only a hint. Undeclared phase → advisory only.
3. Human edits TOML; machines write JSON; never round-trip TOML. Use `json_style.dumps()` for machine JSON.
4. Exit-code contract: 2 config/usage, 3 internal failure, 1 findings; a crash never exits 1.
5. Docs co-change with behavior; `make generate` first, then tests and `make ci`.

## Audit facts (Section 7 Step 1, 2026-10-01)

- **Runtime:** Python 3.11.2, **zero runtime dependencies** (stdlib only); dev extras `pytest>=8,<10` and `pre-commit>=3,<5`; build `setuptools>=77`.
- **Scale:** 1015 tracked files = 64 `.py`, 361 `.md`, and 265 catalog types × 3 template variants; 68 controlled docs (24 generated, 44 human-owned).
- **Demo surface:** SQLite (`EXAMPLE-PROJECT/db/schema.sql`, single `tasks` table, no migrations) and a stdlib threaded HTTP server with three routes (`GET/POST /tasks`, `GET /health`), **no auth**, 1–4096-byte body cap, JSON 400/404 errors.
- **Readers:** Python only (exact, in-process). No reader for JavaScript/TypeScript, Rust or Go (L0, reported as such).
- **Gates:** pytest (242 tests), catalog check, guards, drift, drift-impact, evidence hashing; required CI check `AutoDOC guard / check`; nightly freshness warn-only.
- **Known-issue markers:** none inline (0 TODO/FIXME/XXX/HACK); the known surface is `LIMITATIONS.md` and `ENGINE-COVERAGE.md`.

## Change log

| Date | Change |
| --- | --- |
| 2026-10-01 | Full MACP transcription landed (Sections 2–7 + REMEMBER verbatim) and the Section 7 Step 1 audit completed; `state/` files reconciled at `d26d798`. |
| 2026-10-01 | `state/` added as the MACP coordination layer (`docs/00-governance/MACP.md`). It is deliberately outside the controlled-document set; `guards.py` still scans its Markdown for links, tribal phrases and key markers. |
