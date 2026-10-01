# AutoDOC

**AutoDOC is a self-updating, self-documenting documentation engine. It keeps project documentation in sync with code through detection, generation, validation, drift checks, and enforced governance.** Its automation is truthful and verifiable, with explicit limits.

```text
Pre-commit ──> PR check ──> Merge preview ──> Release gate ──> Nightly health
   staged       tests +       generated-only      blocked pending     drift + age
   impact       drift         diff artifact       owner license       + report
```

## What it does
- Detects which mapped human documents are affected by source changes.
- Generates supported factual references from authoritative files and fails on unsupported inputs.
- Checks metadata, ownership, review dates, local links, relationships and generated drift.
- Makes required checks fail on missing co-changes; protected-branch enforcement needs admin setup.
- Can snapshot controlled docs at release **after** the owner chooses a license (currently blocked).

## Quick start (Python 3.11+)

```sh
git clone https://github.com/Er-Sajan-PLG/AutoDOC.git && cd AutoDOC
make setup
make ci
```

`make docs-recommend` reports which catalog types apply to this repository, why, and which
decisions are recorded in `autodoc.toml`; `make docs-catalog` validates the catalog rules,
schema and declared context; `make docs-hint` suggests a phase from history; and
`make docs-explain DOC=DEV-B01-006` prints the derivation chain for one requirement.

**Profile and phase are declarations.** `profile` in `autodoc.toml` picks which document types
count as core for this kind of project (`default`, `startup`, `oss-library`, `internal-service`,
`regulated`); each addition states the phases it is off in, and the report shows the resulting
core set. **Phase is a declaration.** With no `phase` the output is advisory and nothing fails, unless a
`[severity]` pin says otherwise. This repository declares `phase = "build"`: missing required
documents warn (a baseline is allowed), recommended ones are informational, structural breakage
fails, and drift and freshness are off. `beta` adds drift and freshness as warnings; `live` and
`mature` fail all four columns; `sunset` shrinks to the sunset profile.

`make docs-enforce` is the single gate: requirements, drift, stubs, placeholders, local links,
committed key markers, tribal instructions and freshness each resolve their severity from
`[severity]` in `autodoc.toml`, then from the declared phase, then to `report`. `make docs-baseline`
records current findings so an adopted repository enforces only what is new and can ratchet down.
`make hooks-install` adds a bypassable pre-push hook; the required CI check is the real gate
(`make docs-require-check` prints the branch-protection payload and changes nothing). Exit codes
are documented in `docs/reference/EXIT-CODES.md`. AutoDOC checks that records exist and are
structured; it never certifies compliance.

## Status

| State | Reality |
| --- | --- |
| ✅ Working | 260 catalog types with declarative rules, a 23-type core tier and a detectable `applies_when` predicate per type; file-presence profile and applicability report; bounded generators; ownership/inventory/graph; two local tool examples; pytest, Makefile, hooks and CI checks; unsigned actual-run evidence |
| 🚧 Partial | Route registry is not OpenAPI; SQLite/manifest/alert parsers are bounded; human-review impact proves a co-change, not quality |
| 📋 Not implemented | Arbitrary language/SQL parsers, external link/network monitoring, LLM, semantic prose verification and signed attestations |
| 🔒 Blocked | License choice blocks release; branch protection needs repository-admin configuration |

`make ci` is canonical. The repository also includes `Taskfile.yaml` for [go-task](https://taskfile.dev/)
users; if go-task is not installed, use the equivalent `make` targets. `make evidence` runs
actual tests and saves **unsigned** artifacts under ignored `evidence/out/`.

## Navigate

[Quick start](QUICK-START.md) · [Engine coverage](docs/00-governance/ENGINE-COVERAGE.md) ·
[Limitations](docs/00-governance/LIMITATIONS.md) ·
[Draft adoption](docs/00-governance/ADOPTION.md) ·
[Architecture](docs/05-architecture/AUTODOC-ARCHITECTURE.md) ·
[Catalog navigation](docs/01-catalogs/CATALOG-INDEX.md) ·
[Tool policy demo](examples/local-tools-example/README.md)

`docs/.doc-sync-map.yaml` is the **single authoritative map**. `TEMPLATES/` has three
synthetic variants for each catalog type, not 260 implemented project documents. See
[license choice](docs/00-governance/LICENSE-CHOICE.md) and
[manual branch requirements](docs/00-governance/BRANCH-PROTECTION.md). AutoDOC is not renamed.
