---
id: DOC-P2-003
title: "Document control"
type: POL
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
# Document control

## Numbering and lifecycle
Catalog IDs name *types*. Give each instantiated document a unique stable ID and owner. Keep
superseded records, link replacements and do not edit an approved ADR in place; add a new one
with `supersedes`, then set the prior record's status/superseded-by when schema support exists.
Draft does not mean approved. `last_verified` must reflect real review, not a generator run.

## Merge controls
Require the AutoDOC guard check on the protected default branch and enable CODEOWNERS approval
in GitHub settings. A checked-in CODEOWNERS file alone cannot enforce approvals. Generated files
must travel with their source changes; a CI bot never pushes over human work. Do not grant write
permissions or release credentials to untrusted PR checks.

## Evidence and release
Only record executed tests/builds and actual materials, with a commit and digests. An unsigned
record is not a cryptographic attestation. The license is Apache-2.0 (owner decision,
2026-10-01; `LICENSE`), so a release now requires a `vX.Y.Z` tag at the same commit and a clean
tree rather than a licensing decision.
