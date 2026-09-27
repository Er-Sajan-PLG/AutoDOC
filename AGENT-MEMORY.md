---
id: DEV-AGENT-003
title: "Agent memory"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "0.1"
effective_date: 2026-09-26
next_review: 2027-03-25
source_of_truth: human
supersedes: null
related: []
criticality: medium
review_days: 180
last_verified: 2026-09-26
last_reviewed: 2026-09-26
last_updated: 2026-09-26
auto_generated: false
---
# Agent memory

## Patterns that work
- Sources are listed in `docs/.doc-sync-map.yaml`; renderers return bytes determined by those sources.
- Compare in memory before writing. Run `python scripts/doc-sync/generate-all.py --check` in CI.
- Use Python AST for Python symbols; avoid regex-based parsing of arbitrary programming languages.
- Preserve human-owned intent and decisions; a changed-path check cannot verify semantics.

## Past pitfalls
- An import named `engine` can resolve the sync script instead of the Python package. Import
  scoped extractor helpers from `engine/extractors` via an explicit search path.
- A generated report that scans itself is recursive; constrain sources to human-owned inputs.
- A synthetic sample date or evidence file is not a real review or signed attestation.

## Next review
Review when extractors, map conventions, or the CI contract change.
