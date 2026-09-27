# Implementation guide

## Select, instantiate, connect

1. Filter the catalogs by project phase and risk; record exclusions rather than copying 260 empty docs.
2. Copy a `TEMPLATES/` blank or canonical file. Add full metadata per
   `CONTROL/metadata/FRONT-MATTER-SCHEMA.json` and a **new instance ID**, not the catalog ID.
   The built-in dependency-free parser accepts one scalar per line and JSON-compatible inline
   arrays for `related`; nested YAML and multiline scalar values need a custom parser.
3. Declare the authoritative source, generator and committed target in `docs/.doc-sync-map.yaml`.
   This file uses JSON syntax, which is valid YAML, so Python's standard library can parse it.
   Glob patterns are rooted in this repository. Source globs must match or generation fails.
4. For human-owned docs, add `review` mappings. A block-level rule fails PRs when mapped
   source paths change without a target change. A warn-level rule only logs a reminder.
5. Add project-specific generators to `GENERATORS` in `scripts/doc-sync/engine.py`, test both
   success and failure paths, and regenerate. Unsupported schemas must fail rather than emit
   apparently correct but incomplete documents.
6. On PRs, run generation in check mode and impact against the base SHA. Protected branch
   settings and real CODEOWNERS are required to actually prevent merging without approval.

## Example map rule

```json
{"id": "config", "sources": ["EXAMPLE-PROJECT/config.schema.json"],
 "target": "EXAMPLE-PROJECT/docs/CONFIG-REFERENCE.md", "generator": "config"}
```

Changing `config.schema.json` changes both the server default and the generated reference.
A generated target is committed in the same PR. `CURRENT-STATE.md`, `NEXT-ACTION.md`, and
`RECENT-CHANGES.md` require human review for mapped code changes; the state helper updates
only the observable file list, never invents priorities. Read the
[policy](CONTROL/policies/DOCUMENTATION-POLICY.md) for limitations.

## Self-adoption example

AutoDOC itself maps all three catalog indices and GitHub workflow files into generated
references in `docs/generated/`. Its source-to-human mappings require architecture and
adoption records to co-change with relevant implementation or catalog edits. The
`CONTROL/metadata/OWNERSHIP-MATRIX.yaml` file lists the actual primary document owner;
`check_ownership.py` checks path authority without pretending to supply an approver.
