---
id: DOC-P3-GOV-004
title: "License choice — Apache-2.0 selected"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: approved
version: "1.0"
effective_date: 2026-10-01
next_review: 2027-03-30
source_of_truth: human
supersedes: null
related: ["DOC-P3-GOV-005"]
criticality: medium
review_days: 180
last_verified: 2026-10-01
last_reviewed: 2026-10-01
last_updated: 2026-10-01
auto_generated: false
---
# License choice — Apache-2.0 selected

**Status: SELECTED — Apache-2.0 (owner decision, 2026-10-01).** The authoritative text is the
repository's [`LICENSE`](../../LICENSE) file, and the full record with consequences is
[`LICENSE-DECISION.md`](LICENSE-DECISION.md). This page keeps the comparison that was weighed, so
the choice can be re-examined rather than re-argued.

| Option | Consideration for AutoDOC | Outcome |
| --- | --- | --- |
| **Apache-2.0** | Permissive for templates and scripts, with an explicit patent grant and a patent-retaliation clause; attribution and change notices are duties a redistributor expects to keep. | **Selected.** |
| MIT | Shortest permissive text; no patent language, so corporate adoption asks more questions than it answers here. | Runner-up. |
| AGPL-3.0 | Network copyleft; substantially larger obligations for anyone reusing the templates or the checker in a pipeline. | Rejected: this tool is adopted by being copied into other repos and CI systems. |
| MPL-2.0 | File-level copyleft; unnecessary complexity for a repository that ships whole files for reuse. | Rejected. |
| BSD-3-Clause | Permissive with a non-endorsement clause, but no patent grant. | Rejected: Apache-2.0 covers the same reuse with clearer patent terms. |
| Unlicense | Public-domain style; recognition varies between jurisdictions. | Rejected: unacceptable uncertainty for redistributors. |

## What the choice obliges

- Redistributors keep the license text and the copyright notices, and state significant changes to
  the files they modify (Apache-2.0 §4).
- The license includes a patent grant, and it terminates for anyone who brings a patent suit over
  the work.
- AutoDOC still never infers licences: the catalog's License inventory and SBOM documents remain
  human answers about what is *used*, and the engine reports only declared manifest data.

## Where the choice lives

`LICENSE` (canonical text) · `pyproject.toml` (`license = "Apache-2.0"`,
`license-files = ["LICENSE"]`) · `README.md` · the release gate in
`scripts/doc-control/release_snapshot.py`, which fails closed if `LICENSE` is ever missing.

This page records a decision and its scope. It is not legal advice; a redistribution plan that
raises patent or trademark questions should get a lawyer's read.
