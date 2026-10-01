# DASHBOARD — AutoDOC

**Last reconciled:** 2026-10-01T11:56Z · **Reconciled by:** A476 (last active agent) · **Tip at reconciliation:** `407d3d4` + the state note recording it

## Project

| Field | Value |
| --- | --- |
| Repository | `STEMORG2026/AutoDOC` — a self-updating documentation engine, not a compliance certificate |
| Branch | `arena/01a0f476-autodoc` (session branch; PR #2 open) |
| Declared phase | `build` (warn) — declared 2026-09-30, never inferred |
| Kinds / profile | `library` / `oss-library` (26 core types) |
| Catalog | 24 core · 49 extended · 265 types (prose still says 260 — D-001) · 16 detected facts · 3 declared traits |
| Build-ready | **15/16** · open core decisions **1** (`DOC-A05-001` Data model — waits on decision 4's fact override) |
| Stack | Python 3.11, **zero runtime dependencies**; pytest + pre-commit for dev; SQLite and a 3-route HTTP server only in the synthetic demo |
| Docs | 68 controlled (24 generated, 44 human-owned); 361 Markdown files tracked |
| Tests | 242 passed + 182 subtests, ~27 s (audit run, 2026-10-01) |
| CI | 5 workflows; required check `AutoDOC guard / check`; nightly freshness warn-only; tag-gated release |

## Active agents

None. `A476` completed three sessions today (adoption; transcription + audit; decision 3).
Register yourself in `REGISTRY.md` before starting work.

## Alerts

1. **Owner confirmation pending (B-001)** on `docs/00-governance/CORE-LIST-REVIEW.md` v1.3 and its
   final counts. Recording `owner_reviewed`, page → `approved`, and caveat removal are **gated on the
   owner's confirmation**; no agent may record it.
2. Nothing is failing: the gate is green (`make ci` exit 0), tests 242/242, catalog valid,
   resolver at 15/16 with one open decision.
3. **Decision-3 deviation needs acknowledgement:** the ADR row was closed with a real ADR
   (`docs/adr/0001-zero-runtime-dependencies.md`) instead of the queued `[not_applicable]`, because
   the resolver reports every skip on an `always` row as a permanent stale-decision warning.
   Reversible; see the decision-3 session summary.
4. Environment resets recur (five recoveries today, #11–#15: HEAD back to `19ca0d4`, wedged index,
   venv deleted). Recovery recipe is in the audit session's summary; never force-push.

## Recently completed

| Date | Work | Commits |
| --- | --- | --- |
| 2026-10-01 | Owner decision 3 executed: 11 of 12 open core decisions closed (charter, README, ADR, module contract, test strategy, dependency setup/policy, SECURITY.md, CODE_OF_CONDUCT.md); readiness 4/16 → **15/16** | `1a65f5d` + reconcile commit |
| 2026-10-01 | Full MACP transcription (Sections 2–7 + REMEMBER) and the Section 7 bootstrap audit | `d26d798` + the reconcile commit |
| 2026-10-01 | MACP adopted: protocol in governance, `state/` bootstrapped, agent pointers | `868588e`, `f417a8f` |
| 2026-10-01 | Owner flags A/B/C applied and re-validated; `CORE-LIST-REVIEW.md` v1.3 (24 core / 49 extended; build-ready 4/16; beta cliff 12 of 24) | `f37d98a`, `c02d733` |
| 2026-10-01 | Core-list review delivered; license decided (Apache-2.0); enforcement layer; §3–§7 lanes | `5164b06`…`2454ea1`, `90478d4` |
| Earlier | Catalog, profiles, facts, triggers, evidence and language work | see `RECENT-CHANGES.md` |

## Next actions (source of truth: `NEXT-ACTION.md`)

1. **Owner: confirm or correct** the v1.3 core-list page and counts (B-001), and acknowledge the
   ADR-row deviation from decision 3.
2. On confirmation: record `owner_reviewed` in `CATALOG-RULES.json` + `PROFILES.json` (note names the
   flagged rows and their resolutions), page → `approved`, remove the caveat from NEXT-ACTION and
   ADOPTION, clear B-001, and refresh the stale statements D-011.
3. **Decision 4** — fact overrides (`has_persistent_state`, `has_ai`, `has_env` false), which closes
   `DOC-A05-001`, plus the `has_network_listener` self-match fix. **Decision 5** — branch protection
   `APPLY=1`. **Decision 6** — stay on `build`. **Decision 7** — defer smalls.

This dashboard summarizes; it never overrides `NEXT-ACTION.md` or an owner instruction.
