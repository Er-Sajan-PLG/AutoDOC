# Local tool authorization example

**This example uses deterministic, local-only tools. It does not call an LLM, does not use embeddings, and does not perform any external web requests.**

Run from the AutoDOC root: `python -m examples.local_tools_example` is not provided because
this directory contains a hyphen; instead `PYTHONPATH=examples/local-tools-example python -m src.tool_runner`
or run `python -m pytest -v tests/test_local_tools.py`. The AutoDOC root sync map generates
`docs/TOOL-AUTHORIZATION.md` from `config/tool-authorization.yaml`.

| Tool | Purpose | Arguments | Risk | Allowed | Confirmation |
| --- | --- | --- | --- | --- | --- |
| math.add | Pure integer addition | two integers | low | yes | no |
| text.upper | Pure bounded uppercase | <=1024 character string | low | yes | no |
| files.read | Read only data/ | simple file name <=8192 bytes | low | yes | no |
| shell.run_script | Not implemented | none | medium | no | required, no approval system |
| network.fetch | Not implemented | none | high | no | required, no approval system |

The real dispatcher rejects blocked/unknown tools and paths outside `data/`. It does not use
`subprocess`, `curl`, or arbitrary shell strings. Owner review is needed before adding a tool.
