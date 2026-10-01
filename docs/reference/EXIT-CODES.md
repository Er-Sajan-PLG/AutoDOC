---
id: DOC-REF-001
title: "Exit codes"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "0.1"
effective_date: 2026-10-01
next_review: 2027-03-30
source_of_truth: human
supersedes: null
related: ["DOC-ARC-001", "DOC-GOV-001"]
criticality: medium
review_days: 180
last_verified: 2026-10-01
last_reviewed: 2026-10-01
last_updated: 2026-10-01
auto_generated: false
---
# Exit codes

Every AutoDOC command uses the same three codes, so a hook, a workflow step or a wrapper can
branch on them without parsing output. `0` means nobody needs to act; `1` means the repository
has work to do; `2` means AutoDOC could not do its job and no conclusion about the repository
should be drawn from that run.

| Code | Meaning | What to do |
| --- | --- | --- |
| `0` | Success. Includes an advisory run with findings, and a run whose findings are all baseline-suppressed. | Nothing. Read the report to decide what to write next. |
| `1` | Findings at `error` severity under the declared phase, or the mapped checks (drift, freshness, stubs, links) failing. | Fix, or record a decision, or add the finding to the baseline during adoption. |
| `2` | Usage or configuration error: unknown catalog id, unreadable `autodoc.toml`, unknown rule or fact, malformed baseline, missing file. | Fix the input. An exit `2` is never a statement about documentation quality. |
| `3` | Internal error: AutoDOC itself failed. The message says "This is a tool failure, not a finding about this repository." | Report a bug. Nothing about the documentation is concluded from this run. |

`3` is deliberately not `1`: a crash in the tool must never be mistaken for a finding in the
repository, or a red build would read as "the docs are bad". A test forces a crash and asserts a
non-`1` exit (`tests/test_enforcement_contract.py`).

## Where each code comes from

| Command | `0` | `1` | `2` |
| --- | --- | --- | --- |
| `scripts/intelligence/enforce.py` | Nothing at `error` (advisory phases report and pass; stale baseline entries warn but do not fail) | New findings at `error` severity, or `--fail-on-stale` with a stale entry | Bad baseline, bad config, or a family that could not run; `3` if the tool itself fails |
| `scripts/intelligence/recommend.py --check` | Required set satisfied, or the phase is undeclared | Required types missing under a failing phase | Same as `enforce.py` |
| `scripts/doc-sync/engine.py drift` | Generated targets match their sources | Drift detected (targets are stale) | Generator source missing or unreadable |
| `scripts/doc-sync/engine.py freshness` | No critical review overdue | A critical document is overdue | Missing or invalid frontmatter |
| `scripts/doc-control/guards.py`, `stub_check.py` | Clean | Findings | — (a crash is not a code path, it is a bug) |
| `scripts/intelligence/context.py` | Declared context and model are valid | — | Any rejected declaration |

## What a code does not say

An exit `0` is not a statement that the documentation is good, complete or compliant. It says
the checks AutoDOC ran found nothing at failing severity, in the categories that ran, at the
capability level the report names. Unsupported ecosystems run at L0, and undetermined items are
reported rather than failed. AutoDOC checks that records exist and are structured; it never
certifies compliance.

## Baseline entries

`autodoc-baseline.json` records what was already broken when enforcement was switched on. Three
events are distinct and must not be confused:

| Event | What happens | Exit |
| --- | --- | --- |
| A recorded entry matches a current finding | The finding is suppressed, counted, and shown with the date it was recorded. | `0` |
| An entry's finding was fixed or removed | The entry is **stale**: printed as a warning, prunable with `--write-baseline`. | `0` (`1` with `--fail-on-stale`) |
| An entry was deleted by hand | The finding comes back and fails again. A baseline is a ratchet, not a blanket. | `1` |

Keys are `rule|path|fingerprint`, where the fingerprint is a digest of the finding's detail: two
different problems at one path are two entries, and moving a finding down a file does not change
its identity. `secrets.inline` findings are never recorded — a committed key stays in git history,
so an entry must not be able to hide it.

## Hooks and gates

The pre-push hook (`make hooks-install`, from `scripts/hooks/pre-push`) runs `make docs-enforce`
for convenience. It is bypassable with `git push --no-verify`, so it is not a gate. The
required CI check (`AutoDOC guard / check`, wired to `make ci`) is the gate that cannot be
skipped; see `docs/00-governance/BRANCH-PROTECTION.md` and `make docs-require-check`.
