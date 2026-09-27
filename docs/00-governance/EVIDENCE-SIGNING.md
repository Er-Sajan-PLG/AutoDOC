---
id: DOC-P3-GOV-003
title: "Evidence signing (pending decision)"
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
# Evidence signing (pending decision)

Current `make evidence` captures an actual test run, material hashes and documentation health;
its outputs explicitly say `unsigned: true`. SHA-256 verifies integrity of locally retained
artifacts, **not** identity or approval. Signing would require an owner-selected tool (e.g.
GPG or a scoped CI identity), key custody/rotation, signing and verification ceremonies,
artifact retention and a revocation procedure. No signing key, secret or trust policy exists
in this repository. Never call these JSON records certified provenance.
