# Contributing

Keep the AutoDOC name and stable catalog IDs. Add catalog entries without renumbering old IDs.
After editing the catalog, run `python scripts/doc-control/library.py` to update template variants.
After editing source maps, generators or example sources, run
`python scripts/doc-sync/generate-all.py`. Review source-to-human impact and update living-state
files when code changes. Run `python -m unittest discover -s tests -v` and the commands in README.
Do not claim external evidence (audits, tests or backups) without actual artifacts.
