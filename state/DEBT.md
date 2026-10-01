# DEBT — technical debt worth acting on

**Last reconciled:** 2026-10-01

Only debt the maintainers would actually fix; a wish list belongs elsewhere. Statuses: `open`,
`queued (<decision>)`, `accepted (by design)`, `fixed (<commit>)`.

| ID | What | Impact | Where | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| D-001 | Catalog count drift: prose says "260 types" while the indexes hold 265 (209 A + 56 B) | Credibility; every number in this repo is supposed to be checkable | `README.md`, `CURRENT-STATE.md`, `QUICK-START.md`, `CONTEXT-SNAPSHOT.md`, `IMPLEMENTATION-GUIDE.md`, `docs/META/CODE-INVENTORY.md`, ~15 more | Regenerate the numbers from `CATALOG-*/INDEX.yaml`, or make the count a generated fact | open |
| D-002 | JavaScript/TypeScript and Rust toolchains are not integrated; those languages run at L0 | Readers are unimplemented for two of the languages this repo touches | `scripts/doc-sync/languages.py` | Wire canonical tools behind the existing probe | queued (decision 7) |
| D-003 | 780 template variants (260 types × canonical/blank/example) are committed rather than rendered on demand | Repository weight; drift risk between variants | `TEMPLATES/**` | Render on demand into `build/`; keep one source per type | queued (decision 7) |
| D-004 | `audience` is declared and displayed but no predicate consumes it | Vocabulary carried without a consumer — the project's own rule says every fact needs one | `CONTROL/metadata/CONTEXT-MODEL.json`, `recommend.py` | Either wire it or mark it explicitly as display-only | queued (decision 7) |
| D-005 | `has_network_listener` matches the detector's own pattern text in `scripts/intelligence/profile.py` | A false positive on this repository; erodes trust in detectors | `scripts/intelligence/profile.py` | Exclude detector source files from the scan, or tighten the pattern | queued (decision 4) |
| D-006 | Two facts are true here only because the synthetic demo fixture contains the files: `has_persistent_state`, `has_env` | Their rows look applicable for the wrong reason; the owner asked for human reasons | `autodoc.toml`, `EXAMPLE-PROJECT/**` | Declare both false with reasons (the two API facts were already cleaned) | queued (decision 4) |
| D-007 | Evidence is verified as hashes only — unsigned | Cannot prove who produced a passing run | `scripts/doc-control/evidence_pack.py`, `docs/00-governance/EVIDENCE-SIGNING.md` | Signing design, then implementation | queued (decision 7) |
| D-008 | `state/` archive rotation is manual; no script compresses old sessions by month | Sessions will accumulate; INDEX stays small only if rotation happens | `state/archive/` | Add a small rotation step when the first month closes | accepted (by design, for now) |
| D-009 | No external dogfood repository yet; AutoDOC is verified mostly on itself and fixtures | Semantic claims about other projects are untested | — | Adopt one real external repository | queued (decision 7) |
