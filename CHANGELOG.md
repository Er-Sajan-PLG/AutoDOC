# Changelog

## Unreleased

- Implemented AutoDOC's deterministic sync, drift, human-review impact and freshness checks.
- Added three catalogs, generated template variants, governed metadata, CI and a task API example.
- Made task API SQLite setup idempotent; added scoped test evidence and health reporting.
- Added self-documenting catalog and CI workflow references plus human architecture/adoption records.
- Added declared owner-scope validation to local and CI checks.
- Added deterministic Python/Markdown/dependency inventories and three catalog navigation views.
- Added checked agent context and a local tool-dispatch example with explicit unsupported web search.
- Added derived human inventory/relationship graph, offline guards and an unsigned run-evidence pack.
- Added a fail-closed release snapshot workflow pending an owner-selected license.
- Reject unsupported demo route, config and SQL changes instead of generating partial references.
- Added described environment and alert extraction with runbook validation.
- Added the local-only allowlisted tool-policy demo, relationship visualization and measured JUnit evidence.
- Hardened ownership/supersedes checks and made Makefile the canonical harness.
- Added an approved-stub check; it failed on 28 title-only `docs/*/_index.md` placeholders, which
  were then retired from the controlled inventory. Health now reports substantive versus stub docs.
- Moved every catalog classification rule out of Python into `CATALOG-RULES.json` (a
  behavior-preserving refactor: 260 ids, names, types and template paths unchanged), added
  `CATALOG-SCHEMA.json` and a validator with an explicit keyword subset, and replaced the
  domain-prefix `priority` with a hand-picked core tier plus detectable `applies_when`
  predicates. Added a file-presence profiler and an applicability report that joins the profile
  with the decisions recorded in `autodoc.toml`.
- Aligned enforcement with the refined phase table: five blocks (advisory, build, beta,
  live+mature, sunset), drift and freshness off until beta, warning at beta, failing from live,
  and sunset reduced to its profile with every other family off. Report-level findings are now
  emitted as informational instead of being dropped, `off` families are named in the report so a
  skipped check is never mistaken for a clean one, the report carries a maturity score relative
  to the declared phase, and the declared context accepts `schema = 1` and `phase_declared`, with
  name-slug keys resolved to catalog ids (ambiguity is an error, and every substitution is
  recorded).
- Added the enforcement layer: `scripts/intelligence/enforce.py` resolves one severity per check
  family (obligations, drift, stubs, placeholders, local links, committed key markers, tribal
  instructions, freshness) from `[severity]`, then the declared phase, then `report`, and reports
  each finding with rule id, severity, location, reason, fix hint and the context that caused it.
  Added the adoption baseline (`autodoc-baseline.json`, schema-checked, keyed by rule and
  location, with stale-entry reporting so it can ratchet down), documented exit codes
  (`0`/`1`/`2`, `docs/reference/EXIT-CODES.md`), a pre-push hook, a dry-run-by-default
  branch-protection helper, and the capability level in every report. The checker functions the
  enforcement layer calls now return structured findings, so severity, baseline and exit codes
  come from one place rather than from printed strings.
- Added a declared context: phases with phase-scaled enforcement (undeclared is advisory and
  nothing fails), declared kinds, audiences and obligations, and a validated `autodoc.toml` with
  `[facts]`, `[satisfied_by]`, `[not_applicable]` and `[severity]`. Facts became three-valued
  (`true` / `false` / `unknown`) with stated exactness and limits, and an unknown fact now makes
  an obligation **undetermined** instead of silently satisfied. Predicates gained `kind:<id>`,
  `obligation:<id>` and `{all, any}` forms. Added `README` as the 261st catalog type — the
  every-phase document that was missing — plus a fixture matrix of awkward repositories,
  `make docs-hint`, and `make docs-explain`.
