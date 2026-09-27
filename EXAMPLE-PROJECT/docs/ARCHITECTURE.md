---
id: EXAMPLE-PROJECT-DOCS-ARCHITECTURE-MD
title: "Task service architecture"
type: REF
owner: "@Er-Sajan-PLG"
reviewer: "@Er-Sajan-PLG"
classification: public
status: draft
version: "1.0"
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
# Task service architecture

## Purpose and scope
This is a deliberately small local demo, not a hardened multi-tenant service. Python's HTTP server
accepts requests; SQLite stores tasks; the JavaScript module calls the API with relative URLs.

## Details and decisions
`routes.json` is the route registry consulted by the server and the reference generator.
Both fail when the registry differs from the three handlers this demo implements.
`config.schema.json` contains defaults used by the server and the config/env generators.
`db/schema.sql` seeds the database and produces the data dictionary. The small SQL parser
rejects unsupported DDL (for example indexes, ALTER or complex constraints).
The SQLite connection is per request. There is no authentication, production deployment, or backup.

## Verification and references
Run `python -m unittest discover -s tests -v` at the repository root; the tests exercise HTTP routes
and check generated documentation against the three authoritative example sources.
