PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
BASE ?= origin/master
.PHONY: help setup lint generate check test ci docs-verify docs-drift docs-metadata docs-ownership docs-inventory docs-freshness docs-sync docs-health docs-stubs docs-catalog docs-profile docs-recommend docs-hint docs-languages docs-triggers docs-links-external docs-explain docs-enforce docs-baseline docs-require-check hooks-install docs-staged-impact evidence check-evidence self-doc report

help: ## Show available commands and their purposes
	@awk '$$0 !~ /^[[:space:]]/ && $$0 !~ /^#/ && index($$0, "## " ) {i=index($$0, "## " ); n=substr($$0,1,i-1); sub(/:[^:]*$$/,"",n); gsub(/\\:/,":",n); gsub(/[[:space:]]+$$/,"",n); printf "%-22s %s\n",n,substr($$0,i+3)}' $(MAKEFILE_LIST)

setup: ## Create a local venv, install test/pre-commit dependencies and generate mapped docs
	python3 -m venv .venv
	.venv/bin/python -m pip install -e '.[dev]'
	.venv/bin/pre-commit install
	$(MAKE) generate

lint: ## Check local Markdown links/tribal phrases/key markers and frontmatter (not external markdownlint)
	$(PYTHON) scripts/doc-control/guards.py
	$(PYTHON) scripts/validate/frontmatter_validator.py

generate: ## Regenerate all mapped factual targets and catalog templates
	$(PYTHON) scripts/doc-sync/generate-all.py
	$(PYTHON) scripts/doc-control/library.py

docs-drift: ## Check all generated targets without writing (IN SYNC on success)
	$(PYTHON) scripts/doc-sync/generate-all.py --check
	@echo 'IN SYNC'

docs-metadata: ## Validate controlled Markdown frontmatter
	$(PYTHON) scripts/validate/frontmatter_validator.py

docs-inventory: ## Validate human inventory against current frontmatter
	$(PYTHON) scripts/doc-sync/generate-all.py --check --only human-inventory

docs-ownership: ## Validate declared owner path coverage
	$(PYTHON) scripts/doc-control/check_ownership.py

docs-freshness: ## Fail overdue critical docs, warn for other overdue human docs
	$(PYTHON) scripts/doc-sync/engine.py freshness

docs-sync: ## Validate mapped source paths, targets, generators and review rules
	$(PYTHON) scripts/doc-control/check_sync_map.py

docs-health: ## Measure health and template coverage without claiming semantic correctness
	$(PYTHON) scripts/doc-control/health.py

docs-stubs: ## Fail approved human docs with no section or content beyond the title
	$(PYTHON) scripts/doc-control/stub_check.py

docs-catalog: ## Validate catalog schema, rules, index and declared context
	$(PYTHON) scripts/doc-control/check_catalog.py
	$(PYTHON) scripts/doc-control/build_catalogs.py --check
	$(PYTHON) scripts/intelligence/context.py --config autodoc.toml

docs-profile: ## Detect project facts (flags) from file presence
	$(PYTHON) scripts/intelligence/profile.py

docs-recommend: ## List catalog types that apply here, with reasons and recorded decisions
	$(PYTHON) scripts/intelligence/recommend.py

docs-languages: ## Show which generator each code language gets; SHOW=<language> renders one
	$(PYTHON) scripts/doc-sync/languages.py $(if $(SHOW),--show "$(SHOW)",)

docs-hint: ## Suggest a phase and kinds from evidence; a hint never sets enforcement
	$(PYTHON) scripts/intelligence/recommend.py --hint

docs-explain: ## Explain one catalog type (usage: make docs-explain DOC=DOC-A08-001)
	@test -n "$(DOC)" || { echo 'set DOC=<catalog type id>'; exit 2; }
	$(PYTHON) scripts/intelligence/recommend.py --explain "$(DOC)"

docs-enforce: ## Enforce obligations and structural checks at the declared phase's severity
	$(PYTHON) scripts/intelligence/enforce.py

docs-triggers: ## Show which event runs what, and what the required gate actually blocks
	$(PYTHON) scripts/intelligence/triggers.py

docs-links-external: ## Check external links the scheduled way: rate-limited and warn-only (opens the network)
	$(PYTHON) scripts/doc-control/check_external_links.py

docs-baseline: ## Record current findings as the adoption baseline (machine-generated JSON)
	$(PYTHON) scripts/intelligence/enforce.py --write-baseline

docs-require-check: ## Print (or with APPLY=1 set) the required branch-protection check
	@test -z "$(APPLY)" || echo 'APPLY=1: this changes repository settings.'
	$(PYTHON) $(if $(APPLY),scripts/doc-control/require-docs-check.py --apply,scripts/doc-control/require-docs-check.py)

hooks-install: ## Install the pre-push enforcement hook (convenience; CI is the real gate)
	@test -d .git || { echo 'not a git worktree'; exit 2; }
	@ln -sf "$(CURDIR)/scripts/hooks/pre-push" .git/hooks/pre-push
	@echo 'Installed .git/hooks/pre-push. Bypassable with git push --no-verify; the required CI check is the real gate.'

docs-staged-impact: ## Verify staged source changes have mapped human-doc co-changes
	$(PYTHON) scripts/intelligence/change_analyzer.py --staged

docs-verify: docs-metadata docs-inventory docs-ownership docs-freshness docs-sync docs-drift docs-stubs docs-catalog ## Validate governed docs and mapped facts
	$(PYTHON) scripts/doc-control/library.py --check
	$(PYTHON) scripts/doc-control/completeness.py
	$(PYTHON) scripts/doc-control/guards.py

check: docs-verify ## PR-equivalent local checks (use staged-impact separately for staged changes)

self-doc: ## Check map, inventory, triggers, ownership, and staged (or BASE-to-HEAD) impact
	$(PYTHON) scripts/doc-control/check_sync_map.py
	$(PYTHON) scripts/intelligence/triggers.py --check
	$(PYTHON) scripts/doc-control/check_ownership.py
	$(PYTHON) scripts/doc-sync/generate-all.py --check --only catalog
	@if git diff --cached --quiet; then $(PYTHON) scripts/intelligence/change_analyzer.py --base "$(BASE)"; else $(PYTHON) scripts/intelligence/change_analyzer.py --staged; fi

test: ## Run the complete pytest suite
	$(PYTHON) -m pytest -v

ci: check docs-enforce self-doc test evidence ## Run canonical docs, enforcement, self-documentation, tests and unsigned evidence verification

evidence: ## Run actual tests and package scoped unsigned evidence in evidence/out/
	mkdir -p evidence/out
	$(PYTHON) scripts/doc-control/test_evidence.py --output evidence/out/test-evidence.json
	$(PYTHON) scripts/doc-control/evidence_pack.py --test evidence/out/test-evidence.json --output-dir evidence/out
	$(MAKE) check-evidence

check-evidence: ## Verify stored evidence artifact hashes (NOT a signature)
	$(PYTHON) scripts/doc-control/evidence_pack.py --verify --output-dir evidence/out

report: docs-health ## Display current health measurements

# Go-task delegates to these same commands; colon targets preserve the documented API.
docs\:generate: generate ## Alias for make generate
docs\:drift: docs-drift ## Alias for drift check
docs\:metadata: docs-metadata ## Alias for metadata check
docs\:inventory: docs-inventory ## Alias for inventory check
docs\:ownership: docs-ownership ## Alias for ownership check
docs\:freshness: docs-freshness ## Alias for freshness check
docs\:sync: docs-sync ## Alias for sync-map check
docs\:impact: ## Compare committed HEAD with BASE (default origin/master); use docs:staged for local edits
	$(PYTHON) scripts/intelligence/change_analyzer.py --base "$(BASE)"
docs\:staged: docs-staged-impact ## Alias for staged change impact check
docs\:index: ## Rebuild the controlled frontmatter index
	$(PYTHON) scripts/doc-sync/generate-all.py --only index
docs\:health: docs-health ## Alias for health report
docs\:stubs: docs-stubs ## Alias for approved-stub check
docs\:catalog: docs-catalog ## Alias for catalog schema/rules check
docs\:profile: docs-profile ## Alias for project profile
docs\:recommend: docs-recommend ## Alias for applicability report
docs\:hint: docs-hint ## Alias for phase suggestion
docs\:explain: docs-explain ## Alias for one obligation explanation
docs\:enforce: docs-enforce ## Alias for the enforcement gate
docs\:baseline: docs-baseline ## Alias for recording the adoption baseline
docs\:verify: docs-verify ## Alias for full governed-doc verification
docs\:check: check ## Alias for PR-equivalent local check
docs\:self-doc: self-doc ## Alias for self-documentation check
