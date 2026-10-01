---
id: DOC-P3-GOV-005
title: "License decision record: Apache-2.0"
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
related: ["DOC-P3-GOV-004"]
criticality: medium
review_days: 180
last_verified: 2026-10-01
last_reviewed: 2026-10-01
last_updated: 2026-10-01
auto_generated: false
---
# License decision record: Apache-2.0

**Decision:** AutoDOC is licensed under the **Apache License, Version 2.0**.
**Decider:** repository owner (`@Er-Sajan-PLG`). **Date:** 2026-10-01.

## Context

The release gate (`scripts/doc-control/release_snapshot.py`) fails closed without a `LICENSE`
file, so no tagged release could snapshot controlled documents. The open question was not whether
to be permissive — the templates and scripts exist to be copied into other repositories — but
which permissive license answers the questions adopters actually ask.

## Options considered

The comparison is kept in [`LICENSE-CHOICE.md`](LICENSE-CHOICE.md). MIT was the runner-up;
AGPL-3.0, MPL-2.0, BSD-3-Clause and Unlicense were rejected for the reasons recorded there.

## Rationale

1. **Adopted through CI systems.** AutoDOC is meant to run inside other projects' pipelines. A
   permissive license keeps that path free of copyleft review.
2. **Patent clarity.** Apache-2.0 grants patent rights explicitly and terminates that grant for
   anyone who sues over the work — the clause corporate legal reviews look for before adding a
   checker to a build.
3. **Attribution without ambiguity.** The duties it imposes (keep notices, mark modified files)
   are the duties redistributors already expect; they are checked in the packaging metadata rather
   than asserted in prose.

## Consequences

- **Obligations travel with the code.** Redistributors keep `LICENSE` and copyright notices and
  state significant changes. There is no separate `NOTICE` file, so no extra notice duty applies
  beyond the license terms.
- **Release is unblocked.** The tag workflow proceeds when `LICENSE` is present, the `vX.Y.Z` tag
  exists and checks out the same commit, and generation/freshness checks pass.
- **Nothing is inferred retroactively.** The catalog's License inventory (DOC-A10-006) and SBOM
  (DOC-A10-002) remain documents a human answers; the engine reports only declared manifest data
  and never derives licenses from file contents.
- **Re-examination is cheap.** The choice is recorded once, in one page, with the alternatives and
  the reasons, so changing it later is an edit to two records plus packaging metadata.

## Verification

`LICENSE` contains the canonical text; `pyproject.toml` declares the SPDX expression
(`license = "Apache-2.0"`, `license-files = ["LICENSE"]`, built with setuptools ≥ 77 so the
generated metadata carries `License-Expression: Apache-2.0`); `release_snapshot.py` requires the
file; and `tests/test_agent_example.py` checks all three so the decision cannot silently drift
from the tree.

This is the repository's record of an owner decision. It is not legal advice.
