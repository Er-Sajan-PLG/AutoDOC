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
- Made project kinds a declaration with evidence behind it (§3): `profile.py` gained a detector
  per detectable kind with stated exactness and limits (packaging shape, entry points, web/data/AI
  dependencies, UI dependencies, deployment and infrastructure files, workspace markers), and the
  kinds no file can honestly separate — `plugin`, `embedded`, `research`, `content`, `template` —
  are marked `declaration-only` with a reason instead of a guess. `make docs-hint` prints the
  evidence for phases and kinds; the declaration in `autodoc.toml` is what counts. Two predicate
  tokens became three-valued: `kind:<id>` is undetermined until kinds are declared, `phase>=<id>`
  until a phase is; both are now consumed by catalog entries (SDK guide, model registry, ETL
  specification, observability strategy, postmortem) so the forms are exercised rather than merely
  allowed. Kind-gated documents and kinds with no supporting evidence are reported, and a
  repository with no evidence at all gets the generic baseline — reported as such, never guessed.
  This repository declares `kinds = ["library"]`; `docs-hint` also suggested `application`, which
  came from an example inside the repository, and that difference is exactly why kinds are asked
  for rather than inferred.
- Moved the core-set decision into data: `CONTROL/metadata/PROFILES.json` holds `default`,
  `startup`, `oss-library`, `internal-service` and `regulated` as deltas of the hand-picked core
  list, each addition carrying a reason and the phases it is off in; `profile` in `autodoc.toml`
  selects one and the report states the resulting set with its additions and removals. Catalog
  entries gained the §5.1 fields — `question` (the reader question), `reader`, `support`
  (`checked` / `template-only` / `human`), `checks`, `events`, and `severity_by_phase`, which
  subsumes the authored `phase_min` (now derived by the generator, so the two cannot disagree).
  An admission rule in `check_catalog.py` requires every type any profile can list to state the
  reader question it answers, a detectable predicate, its phases and named checks or an explicit
  label; a type nothing can detect cannot be required. Two types were reconciled for the
  profiles: `License` (DOC-A10-008) is added as the project's redistribution terms, while the
  old `License inventory` becomes extended (dependency licensing belongs with the SBOM), and
  `Code of conduct` (DOC-A09-009) joins the oss-library profile. A type that is off at the
  current phase is now listed with its reason and the phase it lands at, in both text and JSON.
- Added a declared context: phases with phase-scaled enforcement (undeclared is advisory and
  nothing fails), declared kinds, audiences and obligations, and a validated `autodoc.toml` with
  `[facts]`, `[satisfied_by]`, `[not_applicable]` and `[severity]`. Facts became three-valued
  (`true` / `false` / `unknown`) with stated exactness and limits, and an unknown fact now makes
  an obligation **undetermined** instead of silently satisfied. Predicates gained `kind:<id>`,
  `obligation:<id>` and `{all, any}` forms. Added `README` as the 261st catalog type — the
  every-phase document that was missing — plus a fixture matrix of awkward repositories,
  `make docs-hint`, and `make docs-explain`.
- Made personal data, payments and safety declared traits (§4): `handles_personal_data`,
  `handles_payments` and `safety_critical` are facts about the world, so the vocabulary now names
  its two routes — fifteen facts read from files with stated limits, and three that are
  declaration-only with a stated reason why no detector can exist. `check_catalog.py` follows the
  same honesty rule it applies to kinds: a fact that claims both routes, claims neither, or has no
  consumer is refused. The catalog consumes the traits — the PII inventory plus the new
  `Cardholder data flow` and `Hazard analysis` are core types required only once their trait is
  true, and the deeper privacy set moves to the personal-data trait — so an unanswered trait
  leaves exactly those documents **undetermined**, reported and never read as `false`. Both
  reports state each trait's answer, `--hint` prints the open questions, and this repository
  answers all three `false` with reasons.
