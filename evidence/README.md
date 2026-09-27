# Actual-run evidence only

`python scripts/doc-control/test_evidence.py --output evidence/out/test-evidence.json`
executes the test suite. If it passes, run
`python scripts/doc-control/evidence_pack.py --test evidence/out/test-evidence.json --output-dir evidence/out`.
The pack records declared runtime dependencies, hashes of source materials, document health
and the test command's actual output. Generated run artifacts are ignored by Git and uploaded
by CI, not committed. Timestamps intentionally make runtime evidence non-deterministic;
source-derived documentation remains deterministic.

**Limits:** this is an unsigned provenance *record*, not an attestation. The SBOM contains
only the declared AutoDOC component and **does not** resolve installed/transitive dependencies
or infer licenses/suppliers. No external audit, build, backup or compliance control is claimed.
