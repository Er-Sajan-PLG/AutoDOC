# Plan — A476 — decision 3: close the open core decisions

| Field | Value |
| --- | --- |
| Objective | Execute the owner's decision 3: close the open core decisions in this repository using the Part 1b closing paths, so `recommend.py` stops reporting them as open |
| Owner of the work | `A476` (session `20261001-1130-A476`) |
| Status | ACTIVE |
| Opened (UTC) | 2026-10-01T11:30Z |

## Scope

**In (11 rows):**

| Row | Closing path |
| --- | --- |
| `DEV-B01-001` Problem statement, `DEV-B01-002` Goals and non-goals, `DEV-B01-003` Scope | one new `docs/00-governance/PROJECT-CHARTER.md` with those three named sections; rows become `[satisfied_by]` |
| `DEV-B01-006` README | `[instantiated]` → `README.md` |
| `DEV-B04-002` ADR | `[not_applicable]` with a stated reason (the owner's chosen path), **subject to a mechanism check**: a skip on an `always` row may be re-surfaced as stale by design |
| `DEV-B05-001` Module contract | `[satisfied_by]` the module-boundaries content of `docs/05-architecture/AUTODOC-ARCHITECTURE.md` |
| `DEV-B07-001` Test strategy | `[satisfied_by]` `docs/00-governance/ENGINE-COVERAGE.md` |
| `DEV-B10-003` Dependency setup | `[satisfied_by]` `QUICK-START.md` (install + pinning) |
| `DOC-A09-006` Dependency policy | `[satisfied_by]` a Dependencies section in `CONTRIBUTING.md` |
| `DOC-A06-008` Vulnerability management | new `SECURITY.md` → `[instantiated]` |
| `DOC-A09-009` Code of conduct | new `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1 + contact) → `[instantiated]` |

**Out:** `DOC-A05-001` Data model (waits on decision 4's `has_persistent_state` override); the v1.3
review recording (B-001); any product behaviour change; machine policy beyond `autodoc.toml`
declarations; `NEXT-ACTION.md`/`ADOPTION.md` caveat removal (gated).

## Approach

1. Read the declaration formats (`autodoc.toml`, `context.py`, `recommend.py`, `enforce.py`) and the
   mechanism question for `[not_applicable]` on an `always` row; also how root files without
   frontmatter behave under the checks.
2. Write the content the declarations point at: charter, `SECURITY.md`, `CODE_OF_CONDUCT.md`
   (canonical text fetched, not paraphrased), a Dependencies section in `CONTRIBUTING.md`, and any
   missing section the `[satisfied_by]` targets need.
3. Add the declarations to `autodoc.toml`; never round-trip it with a generator.
4. Regenerate, run the full gate, and verify in `recommend.py` output that the rows left the open
   group and the readiness number moved as expected.
5. Shutdown per MACP: session summary, registry, plans, index, dashboard, commits, push, PR checks.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| An `always` row with `[not_applicable]` is surfaced as stale (mechanism), so the "closing" is not clean | Verify with the real tool before writing; if stale, choose the page's other sanctioned option (a real ADR under `docs/adr/`) and log the deviation as [PIVOT] for the owner |
| New root files break ownership/frontmatter/stub checks | Check `check_ownership.py` rules first; add matrix entries or metadata only as the checks require |
| Content invented rather than sourced (charter, security policy) | Draft only from existing repo documents and name the contact/route the owner already uses; no fabricated commitments |
| Writing `owner_reviewed` or touching gated files by accident | Declarations only in `autodoc.toml`; the gated files are listed in Scope "Out" and are checked at shutdown |

## Rollback strategy

Each item is a declaration plus a document. Reverting the landing commit restores the previous
`autodoc.toml` and removes the new sections/files; the repository returns to 12 open decisions with
no other effect.

## Success criteria

- [ ] `recommend.py` reports the 11 rows as closed and the open count drops from 12 to 1
      (`DOC-A05-001`, reserved for decision 4).
- [ ] `check_catalog` valid; `make ci` exit 0; full suite green.
- [ ] The declared closing points exist and actually answer the row's question.
- [ ] MACP shutdown complete: session summary, registry, plan deleted, INDEX row, dashboard
      reconciled, commits pushed, PR checks green.
