# Quick start

AutoDOC is a self-updating, self-documenting documentation engine with **truthful, verifiable
automation and explicit limits**. Install Python 3.11+, make, and optionally go-task.

```sh
make setup          # isolated development dependencies and pre-commit hooks
make ci             # canonical local verification
make docs:drift     # read-only generator check (IN SYNC on success)
make evidence       # actual tests + unsigned run evidence
```

`Taskfile.yaml` is available for [go-task](https://taskfile.dev/) users. The binary is not
installed in this environment; use the same `make` targets instead of treating task absence
as a documentation-engine failure.

## Adopt an existing project

1. Run `python scripts/adopt.py --project-path /path/to/project` for **heuristic suggestions**;
   it does not modify the project or establish regulatory applicability.
2. Browse [the 260-type catalog](docs/01-catalogs/CATALOG-INDEX.md), select relevant types,
   assign real owners and record non-applicability. Do not copy 260 empty documents.
3. Copy/adapt the engine and `docs/.doc-sync-map.yaml` to actual sources, generate only factual
   references with supported extractors, and create human-owned records for design decisions.
4. Run `make docs:verify`, `make test`, then enable required checks/CODEOWNERS approval manually
   in repository settings. AutoDOC cannot observe an unrelated project until configured there.

## New project and new documents

`python scripts/init-project.py --name "My App" --type web-api --output /existing/project`
creates ten **draft** foundations without overwrites. `1970-01-01` means unverified.
For a single type, copy its `TEMPLATES/*/*.md.blank` variant, assign a new *instance* ID,
real owner/reviewer, actual review dates and project-specific facts; then add a source/review
mapping. Catalog IDs name *types*, not deployed artifacts. To add a type, append a stable ID
under `CATALOG-A/INDEX.yaml` or `CATALOG-B/INDEX.yaml` and run
`python scripts/doc-control/library.py` to regenerate its three template variants.

## Add a deterministic extractor

Implement a scoped parser in `engine/extractors/`, render facts in `scripts/doc-sync/engine.py`,
add a mapped source/target in `docs/.doc-sync-map.yaml`, and test accepted and rejected inputs.
Run `make generate && make ci`; update [engine coverage](docs/00-governance/ENGINE-COVERAGE.md).
Unsupported formats must fail or be documented as not implemented, never silently pass.

## Interpret a failure

- `Generated documentation drift: path`: inspect its map sources, run `make generate` and
  commit source with target. Do **not** hand-edit an AUTO-GENERATED file.
- `review <target>` or `Living state not updated`: have a human review the listed document,
  update it and stage it. Co-change does not certify accuracy.
- `overdue review (critical)`: obtain a real review; do not simply reset a date.
- `Missing source` or `Unsupported SQL`: fix the map/source or add a tested extractor.
- `Release blocked`: read `docs/00-governance/LICENSE-CHOICE.md`; only the owner chooses a license.

Run `make help` for all aliases. Use `make docs:staged` for staged changes; `make docs:impact`
compares committed HEAD to `BASE=origin/master` and does **not** include uncommitted edits.
