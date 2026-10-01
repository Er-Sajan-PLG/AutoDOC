# DECISIONS — record of settled choices

**Last reconciled:** 2026-10-01T11:29Z

Entries are append-only. An owner decision that is implemented but not yet recorded in the machine
files is marked **accepted — recording pending**; an agent never marks an owner decision recorded.

| ID | Decision | Decided by | Date | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| ADR-001 | License is **Apache-2.0**, including the NOTICE/Apache header conventions and the release-snapshot licence seam | Owner | 2026-10-01 | accepted, recorded | `LICENSE`, `pyproject.toml`, `docs/00-governance/LICENSE-DECISION.md`; commit `2454ea1` |
| ADR-002 | Core list + five profiles are hand-reviewed by the owner; the reviewer's flags are decided: **A** HTTP-specific rows move to a new `has_http_api` fact (`DOC-A22-004` stays on `has_public_api_surface`) with demo-fact cleanup; **B** `DEV-B08-001/002/003` become extended; **C** the dependency question splits between setup and policy | Owner | 2026-10-01 | accepted, recorded | `docs/00-governance/CORE-LIST-REVIEW.md` (approved); dated `owner_reviewed` notes in `CONTROL/metadata/CATALOG-RULES.json` + `PROFILES.json`; commits `f37d98a`, `c02d733` + the 2026-10-01 recording commit |
| ADR-009 | **Sessions close only on the owner's word.** Agents move a session to `PAUSED (awaiting owner)` at a handoff, keep its plan until then, and never write `COMPLETED`/`CLOSED` on their own judgment. Two companion rules from the same instruction: **persist before presenting** (decision rounds are written to `DECISIONS.md` § Pending in the same change that presents them) and the **handoff self-check** (read DASHBOARD → REGISTRY → BLOCKERS → § Pending as a stranger; if the next actions are not executable from state, fix state first). Root cause this corrects: the first decision round lived only in chat, which is what forced the owner to ask for a cold-clone test in the first place | Owner | 2026-10-01 | accepted, recorded | `docs/00-governance/MACP.md` local rules 8–10; this entry |
| ADR-008 | **Owner decision 3 executed**: the 12 open core decisions are closed at their existing homes (charter for the foundation rows, `[instantiated]` for README/SECURITY/conduct, `[satisfied_by]` for module contract, test strategy, dependency setup and policy), with one deviation — the ADR row uses a real ADR (`docs/adr/0001`) instead of the queued `[not_applicable]`, because a skip on an `always` row is reported as a permanent stale decision. Resolver: 4/16 → 15/16; `DOC-A05-001` waits on decision 4 | Owner (decision 3, "continue work") | 2026-10-01 | **accepted, recorded — the owner acknowledged the deviation and kept the real ADR (P-002, "proceed with recomendation")** | `autodoc.toml`, `docs/00-governance/PROJECT-CHARTER.md`, `docs/adr/0001-zero-runtime-dependencies.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `QUICK-START.md`; commit `1a65f5d` |
| ADR-003 | **MACP** is the coordination protocol for agents working on this repository: `state/` is the shared record, sessions and plans are mandatory, and the protocol composes with the owner's branch, tree-green and "owner records decisions" instructions. The protocol text is **fully transcribed** (Sections 1–7 + REMEMBER); the earlier reconstruction of Sections 8–10 was removed as superseded | Owner | 2026-10-01 | accepted, recorded | `docs/00-governance/MACP.md`; commits `868588e`, `d26d798` |
| ADR-004 | Enforcement is **one policy** keyed to the declared phase: undeclared → advisory only; per-check overrides; baseline for adoption, with deleted entries resurfacing and stale entries prunable | Owner | 2026-09-30/2026-10-01 | accepted, recorded | `autodoc.toml`, `scripts/intelligence/enforce.py`, `CONTROL/metadata/CONTEXT-MODEL.json`; commit `90478d4` |
| ADR-005 | Every generator is labeled **`exact` or `heuristic`**; a heuristic result carries its label and a warning instead of pretending to be exact | Owner | 2026-10-01 | accepted, recorded | `scripts/doc-sync/engine.py` (`GENERATOR_LABELS`), §6 commits `6d1c444`, `5d385cf` |
| ADR-006 | Facts are capability-named and three-valued; personal-data, payment and safety traits are **declaration-only, never inferred**; undeclared phase is advisory | Owner | standing | accepted, recorded | `CONTROL/metadata/CONTEXT-MODEL.json`, `PROFILES.json`, `autodoc.toml` |
| ADR-007 | Documentation is enforced at the declared phase — `build` (warn) for this repository — and the phase ladder is promoted by an explicit event (`promote <phase>`), not by inference | Owner | 2026-09-30 | accepted, recorded | `autodoc.toml` (`phase = "build"`), `docs/00-governance/CORE-LIST-REVIEW.md` Part 0 |
| ADR-010 | **Decision 4 (P-003) executed**: the demo-only facts are declared **false** with reasons (`has_persistent_state`, `has_env`, `has_ai`), and the `has_network_listener` self-match is fixed at its source — the detector excludes its own module, so no override was needed (a deliberate deviation from the "four overrides" wording, pinned by a regression test). The last open core decision `DOC-A05-001` closes as not applicable: readiness **15/15, 0 open**; beta cliff 4 → 2 | Owner | 2026-10-01 | accepted, recorded | `autodoc.toml`, `scripts/intelligence/profile.py`, `tests/test_profile.py`; commit `c7980f9` |
| ADR-011 | **Decision 5 (P-004)**: branch protection on `master` carries one required check — payload `{"strict": true, "contexts": ["AutoDOC guard / check"]}`, applied by the owner with `APPLY=1 make docs-require-check`; the check name is verified live on PR #2 | Owner | 2026-10-01 | accepted — application owner-run (attempted here: the session's identity has no repository-admin rights; the payload is printed and nothing was changed) | `Makefile` target `docs-require-check`, `docs/00-governance/BRANCH-PROTECTION.md` |
| ADR-012 | **Decision 6 (P-005)**: the declared phase stays `build`; after decision 4 the promotion delta is 2 core rows (License, Changelog), and promotion remains a deliberate event (`autodoc promote`'s delta view is not implemented, so it is a manual edit with those numbers) | Owner | 2026-10-01 | accepted, recorded | `autodoc.toml` (`phase = "build"` unchanged); this file, item P-005 |
| ADR-013 | **Decision 7 (P-006)**: the five smalls are deferred — `audience` consumer (D-004; first if any is picked), JS/TS + Rust toolchains (D-002), external dogfood repository (D-009), template rendering on demand (D-003), evidence signing (D-007); none gates anything | Owner | 2026-10-01 | accepted, recorded | `state/DEBT.md` |
## Pending — owner decisions awaiting a verdict

**Decided 2026-10-01 — the owner stated "proceed with recomendation", adopting all six
recommendations.** Execution is tracked in the table above: P-003 → ADR-010 (executed), P-004 →
ADR-011 (owner-run application; attempted, no admin rights in this session), P-005 → ADR-012,
P-006 → ADR-013, P-001 → ADR-002 (recorded), P-002 → ADR-008 (acknowledged). **All six are now
executed or recorded — the only open item is the owner-run protection apply.** The dossiers below
are kept as the record of what was presented.

**Added 2026-10-01 by the cold-clone continuity test** (session `20261001-1219-A476`): the round
below previously existed only in chat, so a new agent could see *that* decisions were pending but
not the substance needed to present or execute them. Each item states what it is, what it changes,
the options and the recommended one. No agent acts on an item until the owner states it, and the
owner takes them **one at a time**.

**P-001 — Confirm the core-list review (clears B-001).** The page
`docs/00-governance/CORE-LIST-REVIEW.md` (v1.3, `draft`) is reviewed and correct; what is missing is
the recorded verdict. On "confirmed": write dated `owner_reviewed` notes into
`CONTROL/metadata/CATALOG-RULES.json` and `PROFILES.json` naming the flagged rows and their
resolutions (A: `DOC-A08-001` → `has_http_api`, `DOC-A22-004` kept on `has_public_api_surface`,
demo overrides added; B: `DEV-B08-001/002/003` → extended; C: dependency question split); page →
`approved`; remove the caveat from `NEXT-ACTION.md` and `ADOPTION.md` and refresh their stale
figures (D-011). **Two repository-state figures on the page are pre-decision-3 and must be
refreshed in that commit**: "4/16 → 16/16 build-ready" is now **15/16 with 1 open decision**, and
the beta cliff "12 of 24" is now **4 of 24** (see P-005). Membership numbers are unchanged.
*Recommendation: confirm.*

**P-002 — Acknowledge the ADR-row deviation (clears B-002).** Decision 3 closed `DEV-B04-002` ADR
with a real record (`docs/adr/0001-zero-runtime-dependencies.md`) instead of the queued
`[not_applicable]`, because the resolver marks every skip on an `always` row as a permanent stale
decision. Options: keep the ADR (default), revert to `[not_applicable]` (accepting a permanent
warning), or edit the ADR's content/status. *Recommendation: keep.*

**P-003 — Decision 4: fact overrides and the detector self-match.** Four changes, all "the fact is
true only because of synthetic material, not because of AutoDOC":

| Fact | Detected from | Current consumers (of the fact) | After declaring `false` |
| --- | --- | --- | --- |
| `has_persistent_state` | only `EXAMPLE-PROJECT/db/schema.sql` (demo) | `DOC-A05-001` Data model (core), `DOC-A05-002/003` (extended), `DOC-A18-004` (extended), and the A05/A18 domain defaults | **closes the last open decision**: `DOC-A05-001` (and the A05/A18 rows) become not-applicable; readiness 15/16 → **15/15** |
| `has_env` | only the demo's `.env.example` + `config.schema.json` | `DOC-A14-005` Env var schema (core, off-until-beta), `DOC-A14-006` (extended) | `DOC-A14-005` not-applicable: beta cliff 4 → 2 |
| `has_ai` | only `examples/ai-agent-example` (synthetic) | the 12 `A21-AI-ML` rows (5 recommended, 7 contextual) | those rows not-applicable; no gate effect |
| `has_network_listener` | the detector's **own source** (`scripts/intelligence/profile.py` holds the pattern literals `gunicorn`, `ListenAndServe`) **and** `tests/fixtures/repos/go-service` | `DOC-A06-001` Threat model (extended) | row not-applicable; no gate effect |

Nuances: the engine *does* read ambient variables — `GITHUB_RUN_ID`/`GITHUB_SHA` for CI evidence,
`PATH`/`LANG` for toolchain probes — but that is not a configuration contract (configuration is
`autodoc.toml`), and the `has_env` reason should say so; declaring `true` instead would make
`DOC-A14-005` (Env var schema) an obligation at beta for an interface the project does not support.
The detector fix should exclude the detector's own module from its scan; whether `tests/fixtures/**`
is excluded from repository-level detection is a policy choice — the honest minimum is the
self-exclusion plus a reason naming the fixtures. *Recommendation: apply all four; it completes
12/12 decisions.*

**P-004 — Decision 5: branch protection.** `make docs-require-check` prints the payload;
`APPLY=1` PUTs it with `gh` (repository-admin rights, owner-run by design). Payload:
`{"strict": true, "contexts": ["AutoDOC guard / check"]}` on `master` — one required check, no
review or push restrictions. The check name is verified live on PR #2. *Recommendation: apply.*

**P-005 — Decision 6: phase.** Currently `build` (declared 2026-09-30): required docs warn,
structural breakage fails, drift/freshness off. If promoted to `beta` **today**, four core rows
would fail: `DOC-A05-001` Data model, `DOC-A10-008` License, `DOC-A14-005` Env var schema,
`DOC-A15-003` Changelog. After P-003, **two** remain (License, Changelog — both gated on
`is_public`, both potentially closeable later by mapping the existing `LICENSE`/`CHANGELOG.md`
files, subject to a mechanism check). The designed `autodoc promote` delta view is not implemented
yet, so promotion is a manual `phase`/`phase_declared` edit with these numbers as the delta.
*Recommendation: stay on `build` until P-003 and P-004 land.*

**P-006 — Decision 7: deferred smalls.** Each already lives in `DEBT.md`: `audience` declared but
unconsumed (D-004 — the remaining "declared without a consumer" hole), JS/TS + Rust toolchains
(D-002), external dogfood repository (D-009), template rendering on demand instead of 780 committed
variants (D-003), evidence signing (D-007). None gates anything. *Recommendation: defer all; if one
is picked now, `audience` first, toolchains second.*
