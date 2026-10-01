# DASHBOARD — AutoDOC

**Last reconciled:** 2026-10-01T11:13Z · **Reconciled by:** A476 · **Tip at reconciliation:** `868588e` (MACP bootstrap landing)

## Project

| Field | Value |
| --- | --- |
| Repository | `STEMORG2026/AutoDOC` — a self-updating documentation engine, not a compliance certificate |
| Branch | `arena/01a0f476-autodoc` (session branch; PR #2 open) |
| Declared phase | `build` (warn) — declared 2026-09-30, never inferred |
| Kinds / profile | `library` / `oss-library` (26 core types) |
| Catalog | 24 core · 49 extended · 265 types · 16 detected facts · 3 declared traits |
| Build-ready | **4/16** · open core decisions **12** |

## Active agents

| Agent | Status | Task | Since |
| --- | --- | --- | --- |
| A476 (Arena.ai Agent Mode) | ACTIVE | Adopt MACP: bootstrap `state/`, write the protocol, register this session | 2026-10-01T11:10Z |

No other agent is active. Details and file claims: [REGISTRY.md](REGISTRY.md). The human owner is
`@Er-Sajan-PLG` (approver for every governed change).

## Alerts

1. **Owner confirmation is pending** on `docs/00-governance/CORE-LIST-REVIEW.md` v1.3 and its
   final counts (24 core / 49 extended; build-ready 4/16; beta cliff 12 of 24). Recording
   `owner_reviewed` in `CATALOG-RULES.json` and `PROFILES.json`, moving the page to `approved`,
   and removing the caveat from `NEXT-ACTION.md` / `ADOPTION.md` are **gated on that confirmation**.
   No agent may record it on the owner's behalf.
2. Nothing is failing: `make ci` was green on `c02d733` (guard job on PR #2: pass).
3. Recovery event: restore #12 was detected and repaired during this session (wedged index at
   `19ca0d4`; recovered by fetch → sha256 verification → `reset --hard` to `c02d733`; venv rebuilt).

## Recently completed

| Date | Work | Commit |
| --- | --- | --- |
| 2026-10-01 | Core-list review: v1.1 → v1.2 dossier, then the owner's flags A/B/C applied and re-validated (`CORE-LIST-REVIEW.md` v1.3) | `5164b06`, `f06d5c0`, `d384d4e`, `f37d98a`, `c02d733` |
| 2026-10-01 | License decided: Apache-2.0, landed with release-snapshot seam and doc co-changes | `2454ea1` |
| 2026-10-01 | §7 triggers/thresholds: scheduler declares itself, network checks warn-only | `a398dbd` |
| 2026-10-01 | §6 language integrations + `exact|heuristic` generator labels; §5.2/§3/§4 lanes | `6d1c444`, `5d385cf`, `58e1663`, `74d0544`, `0fe3ec3`, `5d3f155` |
| 2026-10-01 | Enforcement-layer review fixes (exit-code contract, baseline semantics, golden matrix) | `90478d4` |
| 2026-10-01 | MACP adopted: protocol in governance (`DOC-P3-GOV-007`), `state/` bootstrapped, agent pointers added | `868588e` |

## Next actions (source of truth: `NEXT-ACTION.md`)

1. **Await the owner's "confirmed"** on the v1.3 page + counts → then record `owner_reviewed` in
   both machine files (note: which rows were flagged and how resolved), page → `approved`,
   remove the caveat from NEXT-ACTION and ADOPTION.
2. **Decision 3** — close the 12 open core decisions via the Part 1b closing paths (charter page,
   `[satisfied_by]` declarations, SECURITY.md, CODE_OF_CONDUCT.md, ADR or reason).
3. **Decision 4** — fact overrides (`has_persistent_state`, `has_ai`, `has_env` false) and the
   `has_network_listener` self-match fix.
4. **Decision 5** — branch protection `APPLY=1` (require only "AutoDOC guard / check").
5. **Decision 6** — stay on `build`; promotion later. **Decision 7** — defer smalls (audience
   wiring, JS/TS + Rust toolchains, external dogfood repo, template rendering, evidence signing).

This dashboard summarizes; it never overrides `NEXT-ACTION.md` or an owner instruction.
