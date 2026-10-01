# Security policy

AutoDOC is a static documentation engine: it reads a repository, generates and checks Markdown, and
writes findings. It has no accounts, no telemetry, no network calls by default, and no runtime
service. This policy says how to report a problem with the tool or this repository, and what you
can expect back. It applies to the code in this repository; it is not a claim that any adopter's
project is secure.

## Supported versions

AutoDOC is pre-1.0 (`0.x`). There are no long-term support branches and no backports: security
fixes land on the default branch (`master`) and are included in the next tagged snapshot.
Release-tag snapshots are produced only when the `release.yml` gate passes.

## Reporting a vulnerability

- **Preferred:** use GitHub's private vulnerability reporting for this repository
  (*Security* tab → *Report a vulnerability*). Then GitHub gives us a private channel and a
  private advisory for the fix.
- **If that form is unavailable:** open a regular issue that asks for a private channel **without
  including any vulnerability details**, exploit steps, or secrets. A maintainer will reply with a
  private route.
- Do not put credentials, tokens or reproduction secrets in any report, issue or pull request.

Please include: affected version or commit, the command or workflow involved, what happens, what
you expected, and the smallest reproduction you can give. A failing test case is the most useful
report.

## What to expect

| Stage | Commitment |
| --- | --- |
| Acknowledgement | Best effort within **7 days**; this is a small project, not a staffed security team |
| Assessment | A written answer on impact and severity, or an honest “we could not reproduce / out of scope” |
| Fix | For accepted reports, a fix on the default branch, or a documented decision not to fix with the reason |
| Disclosure | Coordinated: we ask for **90 days** or until a fix ships, whichever comes first, before public detail |
| Credit | Named in the release notes if you want, or anonymous — your choice |
| Bounty | **No monetary bounty.** There is no funded program. |

## Scope: what is security-relevant here

1. **The engine's behaviour on untrusted repositories.** Parsers, file walking, generators, the
   sandboxed executable-documentation path (opt-in, timed out, no network by default), and the
   pre-commit/CI hooks.
2. **Secret handling.** AutoDOC reads configuration that may contain secrets. It is designed
   **never to print secret values**: findings name the file, the rule and the location, never the
   matched line (`scripts/doc-control/guards.py`). A leak through a report, a baseline, evidence or
   a log is in scope.
3. **Writes and overwrites.** Anything that lets a run modify files outside the intended targets,
   or follow a path out of the repository, is in scope.
4. **CI workflows.** Credential exposure, unexpected network access, or a workflow that runs
   untrusted code with elevated permissions.
5. **The synthetic examples.** `EXAMPLE-PROJECT` includes a small HTTP server **with no
   authentication, by design**, because it is a local demonstration fixture, not a deployable
   service (`docs/00-governance/LIMITATIONS.md`). Running it on a public interface is out of
   scope — the documentation says so, and it is never presented as a product.

## Out of scope

- Vulnerabilities in third parties' tools that AutoDOC invokes or documents (report them upstream).
- Findings that a generated or human document is *wrong about the world*; that is a documentation
  defect, handled as a normal issue.
- Anything requiring a compromised maintainer machine or GitHub account.
- Requests to certify compliance or to perform attestation: AutoDOC never certifies compliance and
  its evidence is unsigned by design (`docs/00-governance/EVIDENCE-SIGNING.md`).

## References

- `CONTRIBUTING.md` — dependency policy, including how a runtime dependency is added or removed.
- `docs/00-governance/LIMITATIONS.md`, `docs/00-governance/ENGINE-COVERAGE.md` — what the tool
  verifies and what it explicitly does not.
- `docs/00-governance/EVIDENCE-SIGNING.md` — why evidence is unsigned, and what that means.
