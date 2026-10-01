---
id: DOC-P3-GOV-002
title: "Branch protection requirements (not configured)"
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
# Branch protection requirements (not configured)

A repository administrator should configure the protected default branch. Require the check
`AutoDOC guard / check` (as named by GitHub Actions), require CODEOWNERS approval, and prohibit
direct pushes if that fits the team's workflow. Optional signed commits/linear history are
owner decisions. `AutoDOC self-documentation / impact` is path-filtered and **cannot** be the
sole required check (it may not run on unrelated PRs). The nightly freshness workflow is
scheduled and not a PR required check. Verify current check names in GitHub before enabling;
this document does not change repository settings or assert they are enabled.

`make docs-require-check` prints the exact payload and the `gh api` command for the required
status check, and changes nothing; `make docs-require-check APPLY=1` performs the update and
must be run by a repository owner with admin rights. It is dry-run by default because it edits
repository settings, not files.

The pre-push hook (`make hooks-install`) runs the same enforcement locally. It is a convenience
that `git push --no-verify` bypasses, so the required check above remains the real gate.
