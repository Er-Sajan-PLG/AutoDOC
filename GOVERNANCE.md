# Governance

Maintainers review changes to the sync map, generator code, catalog IDs, and templates.
Changes to controlled docs need a named human owner and reviewer in frontmatter.
Real CODEOWNERS approval and CI merge blocking require protected branch settings; a file alone
is insufficient. Critical reviews overdue by `review_days` fail the CI freshness check;
other severities produce warnings for maintainers to triage.
See [documentation policy](CONTROL/policies/DOCUMENTATION-POLICY.md).
