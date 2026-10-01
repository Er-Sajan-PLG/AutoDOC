# Contributing

Keep the AutoDOC name and stable catalog IDs. Add catalog entries without renumbering old IDs.
After editing the catalog, run `python scripts/doc-control/library.py` to update template variants.
After editing source maps, generators or example sources, run
`python scripts/doc-sync/generate-all.py`. Review source-to-human impact and update living-state
files when code changes. Run `python -m unittest discover -s tests -v` and the commands in README.
Do not claim external evidence (audits, tests or backups) without actual artifacts.

## Dependencies

AutoDOC's runtime is the Python standard library only (`dependencies = []` in
`pyproject.toml`); the reasoning and the trade-offs are recorded in
[docs/adr/0001-zero-runtime-dependencies.md](docs/adr/0001-zero-runtime-dependencies.md).

- **Adding a runtime dependency** is a decision, not a commit: it needs the repository owner's
  agreement and a new ADR under `docs/adr/` that states what it buys and what it costs adopters.
  Until that exists, a runtime import from a third-party package is a defect.
- **Development dependencies** live in `[project.optional-dependencies].dev` as bounded ranges
  (`pytest>=8,<10`, `pre-commit>=3,<5`). They are installed by `make setup` and never imported by
  shipped code. Widen or narrow a range in the same change that uses it, and run `make ci`.
- **Updating** is manual: there is no automated updater and no bot pull requests. Bump the range,
  run `make ci`, and include the reason in the commit message.
- **Removing** a dependency means deleting it from `pyproject.toml` and from any import, then
  running `make generate && make ci`. Nothing else records it, so the manifest is the source of
  truth.
- **Vulnerabilities** are handled through [SECURITY.md](SECURITY.md). No scanner is wired into CI —
  the runtime set is empty, and the tool runs offline by default; if that changes, the scanner and
  its schedule belong in the trigger model rather than in an implied policy.
- **Licences**: this project is Apache-2.0. A dependency whose licence is incompatible with
  redistribution under Apache-2.0 must not be added at all, and one that requires attribution
  must be recorded where that attribution is visible.
