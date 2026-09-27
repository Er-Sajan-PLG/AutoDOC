---
id: DOC-P3-GOV-004
title: "License choice — pending owner approval"
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
# License choice — pending owner approval

**Status: NOT SELECTED.** Choose a license before publishing. The release gate fails until
an owner-approved `LICENSE` file is added. No license text or SPDX claim is supplied here.

| Option | Consideration for AutoDOC |
| --- | --- |
| MIT | Short, permissive for templates and scripts; limited patent language. |
| Apache-2.0 | Permissive with explicit patent terms and notice duties. |
| AGPL-3.0 | Network copyleft; substantial obligations for reuse. |
| MPL-2.0 | File-level copyleft; narrower reuse obligations than AGPL. |
| BSD-3-Clause | Permissive with attribution and non-endorsement. |
| Unlicense | Public-domain style; acceptance varies by jurisdiction. |

Evaluate template redistribution, automation-script reuse, patent clarity and the owner's
desired contribution obligations. **Recommendation: pending the owner's goals.** After approval,
add the selected text in `LICENSE`, update README, and review the release workflow.
