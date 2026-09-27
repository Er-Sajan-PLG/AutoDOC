# Generated document shells

Do not hand-edit generated facts. Set an authoritative source and generator in
`docs/.doc-sync-map.yaml`, add a regression test, then run `generate-all.py`.
The example's API, configuration, environment and SQLite schema outputs demonstrate this pattern.
Use the canonical A/B templates for human-owned documents; generated targets have their
own frontmatter emitted by the generator.
