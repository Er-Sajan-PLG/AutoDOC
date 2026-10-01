# DECISIONS — record of settled choices

**Last reconciled:** 2026-10-01T11:29Z

Entries are append-only. An owner decision that is implemented but not yet recorded in the machine
files is marked **accepted — recording pending**; an agent never marks an owner decision recorded.

| ID | Decision | Decided by | Date | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| ADR-001 | License is **Apache-2.0**, including the NOTICE/Apache header conventions and the release-snapshot licence seam | Owner | 2026-10-01 | accepted, recorded | `LICENSE`, `pyproject.toml`, `docs/00-governance/LICENSE-DECISION.md`; commit `2454ea1` |
| ADR-002 | Core list + five profiles are hand-reviewed by the owner; the reviewer's flags are decided: **A** HTTP-specific rows move to a new `has_http_api` fact (`DOC-A22-004` stays on `has_public_api_surface`) with demo-fact cleanup; **B** `DEV-B08-001/002/003` become extended; **C** the dependency question splits between setup and policy | Owner | 2026-10-01 | **accepted — recording pending** (owner confirmation of the v1.3 page + counts) | `docs/00-governance/CORE-LIST-REVIEW.md`; commits `f37d98a`, `c02d733` |
| ADR-003 | **MACP** is the coordination protocol for agents working on this repository: `state/` is the shared record, sessions and plans are mandatory, and the protocol composes with the owner's branch, tree-green and "owner records decisions" instructions. The protocol text is **fully transcribed** (Sections 1–7 + REMEMBER); the earlier reconstruction of Sections 8–10 was removed as superseded | Owner | 2026-10-01 | accepted, recorded | `docs/00-governance/MACP.md`; commits `868588e`, `d26d798` |
| ADR-004 | Enforcement is **one policy** keyed to the declared phase: undeclared → advisory only; per-check overrides; baseline for adoption, with deleted entries resurfacing and stale entries prunable | Owner | 2026-09-30/2026-10-01 | accepted, recorded | `autodoc.toml`, `scripts/intelligence/enforce.py`, `CONTROL/metadata/CONTEXT-MODEL.json`; commit `90478d4` |
| ADR-005 | Every generator is labeled **`exact` or `heuristic`**; a heuristic result carries its label and a warning instead of pretending to be exact | Owner | 2026-10-01 | accepted, recorded | `scripts/doc-sync/engine.py` (`GENERATOR_LABELS`), §6 commits `6d1c444`, `5d385cf` |
| ADR-006 | Facts are capability-named and three-valued; personal-data, payment and safety traits are **declaration-only, never inferred**; undeclared phase is advisory | Owner | standing | accepted, recorded | `CONTROL/metadata/CONTEXT-MODEL.json`, `PROFILES.json`, `autodoc.toml` |
| ADR-007 | Documentation is enforced at the declared phase — `build` (warn) for this repository — and the phase ladder is promoted by an explicit event (`promote <phase>`), not by inference | Owner | 2026-09-30 | accepted, recorded | `autodoc.toml` (`phase = "build"`), `docs/00-governance/CORE-LIST-REVIEW.md` Part 0 |
