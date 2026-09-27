# Local agent-like tool dispatch example

From this directory: `python src/agent.py` prints 5. `tools.json` is the explicit authorization
registry. `models.json` says there is **no model** and `web_search.py` raises
`NOT_IMPLEMENTED`; no network search, autonomous planning or LLM inference is claimed.
`src/prompts/system.md` is versioned context for a *future* opt-in model integration.
AutoDOC generates tool, prompt and model registries in `docs/AI/`; human design is separate.
Run all repo checks with `make ci` at the AutoDOC root.
