# AutoDOC system

AutoDOC is a documentation operating system with four boundaries:

1. **Inventory:** the three catalogs list *possible* documents; each entry has a stable ID,
   intended owner, audience, purpose, required sections and template path.
2. **Facts:** the sync map generates selected targets deterministically from authoritative files.
   CI re-generates in memory and fails on differences; a changed source without a configured
   generator is not automatically documented.
3. **Judgment:** human-owned architecture, decisions, policy and working context are reviewed
   on relevant code changes and on a calendar SLA. Automation detects missing co-changes, not truth.
4. **Proof:** tests are run in CI. Audit evidence is outside the starter engine until a real
   evidence collection source, retention policy and verifier have been integrated.

The system documents itself through the generated automation reference, control metadata,
policy, tests and workflows. See [README.md](README.md) for commands.
