# BLOCKERS — active blockers and dependencies

**Last reconciled:** 2026-10-01T11:13Z

| ID | Blocker | Blocks | Owner who can clear it | Raised |
| --- | --- | --- | --- | --- |
| B-001 | Owner confirmation of `docs/00-governance/CORE-LIST-REVIEW.md` v1.3 and its final counts (24 core / 49 extended; build-ready 4/16; beta cliff 12 of 24) | Recording `owner_reviewed` in `CONTROL/metadata/CATALOG-RULES.json` + `PROFILES.json`, page → `approved`, caveat removal from `NEXT-ACTION.md` + `ADOPTION.md`, and the start of decision 3 | `@Er-Sajan-PLG` | 2026-10-01 |

No upstream dependency is blocking current work. Decision 3 (close the 12 open core decisions) is
*queued*, not blocked by anything else — it waits on B-001 because the owner works decisions one at
a time.

When a blocker clears: strike it here, record the clearing date in the session that saw it, and
reconcile `DASHBOARD.md`.
