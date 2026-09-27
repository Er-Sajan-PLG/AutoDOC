# AutoDOC example: task API

A minimal Python standard-library HTTP/SQLite service plus a browser-side JavaScript client.
It does not need third-party dependencies. From this directory:

```sh
python src/app.py
# in another terminal:
curl http://localhost:8000/health
curl -H 'Content-Type: application/json' -d '{"title":"Try AutoDOC"}' http://localhost:8000/tasks
```

For an isolated database set `DB_PATH=/tmp/autodoc-tasks.db`; set `PORT=8080` to change the port.
Run the repository tests with `python -m unittest discover -s tests -v` from the repo root.
Generated documents are in `docs/`; regenerate with `python scripts/doc-sync/generate-all.py`.
The architecture file is human-owned and must be reviewed when API implementation changes.
This example is educational and **not** production hardened (no auth, TLS, backup, rate limit or concurrency guarantees).

Coding-agent users should read [AGENTS.md](AGENTS.md) and [agent context](docs/AI-CONTEXT.md).
This integrates structured agent instructions, not an LLM runtime.

The generated `.env.example` provides a preceding description for each key and drives
`docs/reference/ENVIRONMENT.md`. `monitoring/alerts.yaml` has a real local
[runbook](docs/HEALTH-RUNBOOK.md) and drives `docs/operations/ALERT-CATALOG.md`.
`pyproject.toml` declares no runtime dependencies; its reference is a declaration, not an SBOM.
