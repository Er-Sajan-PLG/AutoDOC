#!/usr/bin/env python3
"""Detect project facts from file presence, as three-valued facts with stated limits.

A fact is `true`, `false`, or `unknown`. `unknown` is the honest answer when no configured
source could be evaluated — typically because the repository's ecosystem has no reader
implemented — and it propagates: a requirement that depends on an unknown fact is *undetermined*,
never silently satisfied. A fact never describes documentation content, and a detector never
prints a secret value, only the file that names a credential.

Each source is:
  {"patterns": [...]}                      path check, always applicable
  {"patterns": [...], "requires": "go"}    path check that only means something in that ecosystem
  {"pack": "python", "probe": "..."}       manifest probe, needs the ecosystem and a reader
  {"globs": [...], "match": "<regex>"}     bounded content scan, heuristic
`exactness` is `exact` when the check is exhaustive for what it claims, `heuristic` when it can
miss things; `limits` says what it cannot see, and is printed with the fact. Generated, vendored
and test-input directories are skipped, and the document records which ones were skipped, so a
fact is never quietly answered from a fixture corpus.
"""
import argparse
import fnmatch
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IGNORED_DIRS = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build',
                'target', '.mypy_cache', '.pytest_cache', '.ruff_cache', '.tox', '.next'}
INPUT_DIRS = {'fixtures', 'testdata'}  # test inputs, not the project's own code
CONTENT_FILE_LIMIT = 400
ECOSYSTEMS = {
    'python': ['pyproject.toml', 'requirements.txt', 'setup.py', 'setup.cfg'],
    'javascript': ['package.json'],
    'go': ['go.mod'],
    'rust': ['Cargo.toml'],
    'jvm': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
    'dotnet': ['*.csproj', '*.fsproj', '*.sln'],
    'ruby': ['Gemfile'],
    'php': ['composer.json'],
    'swift': ['Package.swift'],
    'elixir': ['mix.exs'],
    'terraform': ['*.tf'],
    'cpp': ['CMakeLists.txt', 'meson.build'],
}
PACKS = ('python', 'javascript')
LANGUAGES = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.tsx': 'typescript',
             '.jsx': 'javascript', '.go': 'go', '.rs': 'rust', '.java': 'java', '.rb': 'ruby',
             '.cs': 'csharp', '.c': 'c', '.h': 'c', '.cpp': 'cpp', '.sh': 'shell',
             '.sql': 'sql', '.yaml': 'yaml', '.yml': 'yaml', '.json': 'json', '.md': 'markdown',
             '.toml': 'toml', '.tf': 'terraform'}
# The languages that are code, as opposed to the data and prose formats LANGUAGES also counts.
# One vocabulary, used by the phase hint here and by the per-language generator registry, so a
# language cannot be "code" in one place and a data format in another.
CODE_LANGUAGES = ('python', 'javascript', 'typescript', 'go', 'rust', 'java', 'csharp', 'c',
                  'cpp', 'ruby', 'shell', 'sql', 'terraform')
AI_DEPENDENCIES = {'openai', 'anthropic', '@anthropic-ai/sdk', 'langchain', 'llama-index',
                   'transformers', 'llama-cpp-python', 'google-generativeai', 'ollama', 'ai'}
WEB_DEPENDENCIES = {'fastapi', 'flask', 'django', 'starlette', 'uvicorn', 'gunicorn', 'aiohttp',
                    'tornado', 'sanic', 'bottle', 'express', 'koa', 'fastify', 'nest', 'hapi',
                    'restify', '@nestjs/core', 'sails'}
DATA_DEPENDENCIES = {'pandas', 'polars', 'pyspark', 'dbt-core', 'apache-airflow', 'airflow',
                     'duckdb', 'dask', 'pyarrow', 'great-expectations', 'dagster', 'prefect',
                     'kafka-python', 'confluent-kafka'}
UI_DEPENDENCIES = {'react', 'vue', 'svelte', 'next', 'nuxt', 'angular', '@angular/core'}

DETECTORS = {
    'has_tests': {
        'exactness': 'exact',
        'limits': 'A tests/ directory with no runnable test still counts.',
        'sources': [{'patterns': ['tests/**', 'test/**', 'spec/**', '**/tests/**', 'test_*.py',
                                  '*_test.py', '**/test_*.py', '*_test.go', '*.test.ts', '*.spec.ts']}]},
    'has_ci': {
        'exactness': 'exact',
        'limits': 'Recognises common CI definition files only.',
        'sources': [{'patterns': ['.github/workflows/*.yml', '.github/workflows/*.yaml',
                                  '.gitlab-ci.yml', '.circleci/config.yml', 'azure-pipelines.yml',
                                  'Jenkinsfile']}]},
    'has_public_api_surface': {
        'exactness': 'heuristic',
        'limits': 'Contract files, route registries and typed JavaScript/TypeScript surfaces; '
                  'a public API described in prose, or in another language, is not seen.',
        'sources': [{'patterns': ['openapi.yaml', 'openapi.yml', 'openapi.json', '**/openapi*.yaml',
                                  '**/openapi*.json', 'asyncapi*.yaml', '**/*.proto',
                                  'schema.graphql', 'routes.json', '**/routes.json']},
                    {'patterns': ['**/index.d.ts', '**/api/*.ts'], 'requires': 'javascript'}]},
    'has_http_api': {
        'exactness': 'heuristic',
        'limits': 'HTTP contract files and route registries only; an API served without a '
                  'contract, described in prose, or in another ecosystem is not seen. Wider '
                  'contract shapes (protobuf, GraphQL, typed surfaces) stay with '
                  'has_public_api_surface.',
        'sources': [{'patterns': ['openapi.yaml', 'openapi.yml', 'openapi.json',
                                  '**/openapi*.yaml', '**/openapi*.json', 'swagger.yaml',
                                  '**/swagger*.yaml', '**/swagger*.json', 'asyncapi*.yaml',
                                  '**/asyncapi*.yaml', 'routes.json', '**/routes.json']}]},
    'has_cli': {
        'exactness': 'heuristic',
        'limits': 'Declared entry points and conventional paths; a CLI built ad hoc is not seen, '
                  'and ecosystems without a reader make this fact unknown rather than false.',
        'sources': [{'pack': 'python', 'probe': 'entry_points'},
                    {'patterns': ['**/__main__.py', '**/cli.py', '**/cli/*.py'], 'requires': 'python'},
                    {'pack': 'javascript', 'probe': 'bin'},
                    {'patterns': ['cmd/**', '**/main.go'], 'requires': 'go'},
                    {'patterns': ['src/main.rs', 'src/bin/**'], 'requires': 'rust'}]},
    'has_ui': {
        'exactness': 'heuristic',
        'limits': 'Browser assets and common UI dependencies; server-rendered markup is not seen.',
        'sources': [{'patterns': ['web/**', '**/index.html', '**/*.tsx', '**/*.vue', '**/*.svelte',
                                  'public/**', 'static/**']},
                    {'pack': 'javascript', 'probe': 'ui_dependencies'}]},
    'has_env': {
        'exactness': 'exact',
        'limits': 'Described or schematised environment configuration only.',
        'sources': [{'patterns': ['.env.example', '.env.sample', '.env.template',
                                  'config.schema.json', '**/config.schema.json']}]},
    'has_docker': {
        'exactness': 'exact',
        'limits': 'Container build files only.',
        'sources': [{'patterns': ['Dockerfile', 'Dockerfile.*', '**/Dockerfile',
                                  'docker-compose.yml', 'docker-compose.yaml']}]},
    'has_persistent_state': {
        'exactness': 'heuristic',
        'limits': 'Schema and migration files; state kept only in code is not seen.',
        'sources': [{'patterns': ['**/*.sql', 'migrations/**', '**/migrations/**', 'alembic.ini',
                                  'prisma/schema.prisma', '**/schema.prisma']}]},
    'has_deploy': {
        'exactness': 'heuristic',
        'limits': 'Declared deployment directories and workflows; a hand-run deploy is not seen.',
        'sources': [{'patterns': ['k8s/**', 'kubernetes/**', 'helm/**', 'deploy/**', 'terraform/**',
                                  '**/*.tf', 'fly.toml', 'Procfile', 'render.yaml', 'ansible/**']},
                    {'patterns': ['.github/workflows/deploy*.yml']}]},
    'has_ai': {
        'exactness': 'heuristic',
        'limits': 'Model, prompt and agent files plus dependencies in supported manifests; '
                  'other ecosystems are not read.',
        'sources': [{'patterns': ['prompts/**', '**/prompts/**', 'models.json', '**/models.json',
                                  'tools.json', '**/tools.json', 'agents/**']},
                    {'pack': 'python', 'probe': 'ai_dependencies'},
                    {'pack': 'javascript', 'probe': 'ai_dependencies'}]},
    'is_public': {
        'exactness': 'heuristic',
        'limits': 'A license file or an explicit published marker; a private repo with a license '
                  'file still reads as public.',
        'sources': [{'patterns': ['LICENSE', 'LICENSE.*', 'COPYING', 'COPYING.*']},
                    {'pack': 'javascript', 'probe': 'published'}]},
    'uses_agents': {
        'exactness': 'exact',
        'limits': 'Recognises common agent instruction files.',
        'sources': [{'patterns': ['AGENTS.md', '**/AGENTS.md', 'CLAUDE.md', '**/CLAUDE.md',
                                  '.cursor/rules', '.cursor/**',
                                  '.github/copilot-instructions.md']}]},
    'has_third_party_deps': {
        'exactness': 'exact',
        'limits': 'Declared dependencies in a supported manifest (runtime or development); '
                  'vendored or transitive dependencies are not seen, and other ecosystems '
                  'are unread, which makes this fact unknown rather than false.',
        'sources': [{'pack': 'python', 'probe': 'dependencies'},
                    {'pack': 'javascript', 'probe': 'dependencies'}]},
    'has_network_listener': {
        'exactness': 'heuristic',
        'limits': f'Bounded content scan of at most {CONTENT_FILE_LIMIT} files; listeners that '
                  'arrive from a framework, configuration or dependency are not seen.',
        'sources': [{'globs': ['**/*.py', '**/*.js', '**/*.ts', '**/*.go', '**/*.rb', '**/*.rs',
                               'Dockerfile', '**/Dockerfile', '**/*.yaml', '**/*.yml'],
                     'match': r'(\.listen\(|ListenAndServe|uvicorn\.run\(|gunicorn|EXPOSE\s+\d+|'
                              r'http\.createServer|app\.run\(|bind\(|listen\()'}]},
    'has_secrets_or_credentials_config': {
        'exactness': 'heuristic',
        'limits': 'Names, never values: only the file that mentions a credential is recorded. '
                  'Bounded content scan of at most '
                  f'{CONTENT_FILE_LIMIT} files; externally managed secrets are not seen.',
        'sources': [{'patterns': ['secrets.*', '**/secrets.*', '**/*.pem']},
                    {'globs': ['.env.example', '.env.sample', '.env.template', '**/config.schema.json'],
                     'match': r'([A-Z][A-Z0-9_]*(SECRET|TOKEN|PASSWORD|API_KEY|CREDENTIAL|PRIVATE_KEY)[A-Z0-9_]*)'}]},
}


DECLARED_FACTS = {
    # Declaration-only facts. No detector exists for these on purpose, and the reason why is part
    # of the vocabulary: each one is a fact about the world that no file tree can answer. The
    # owner declares them in autodoc.toml `[facts]`; until then the honest value is `unknown`, so
    # the documents they gate are undetermined — reported, never silently not applicable.
    'handles_personal_data': {
        'label': 'handles personal data',
        'why_declared_only': 'Whether data identifies a person is a fact about the world, not about '
                             'the file tree: a column named `email` may hold a business address, and '
                             'a table of hashes may still be personal data.',
    },
    'handles_payments': {
        'label': 'handles payments',
        'why_declared_only': 'Only the owner knows whether money moves through the system and which '
                             'parts touch card or account data; a `payments/` directory is evidence '
                             'of code, not of a live payment flow.',
    },
    'safety_critical': {
        'label': 'safety-critical',
        'why_declared_only': 'Harm depends on what the system controls, not on what it imports; '
                             'nothing in a file tree can tell whether a wrong answer hurts someone.',
    },
}


def fact_specs():
    """Every fact in the vocabulary, with its detection route.

    A fact is either readable from files (a detector with exactness, limits and sources) or
    declaration-only (a stated reason why no detector can exist). The two sets are disjoint, and
    the catalog gate rejects a fact that claims both, claims neither, or has no consumer.
    """
    facts = {name: {**spec, 'detection': 'files'} for name, spec in DETECTORS.items()}
    for name, spec in DECLARED_FACTS.items():
        if name in facts:
            raise ValueError(f'{name}: fact cannot be both detectable and declaration-only')
        facts[name] = {**spec, 'detection': 'declaration-only'}
    return facts


def tracked_files(root):
    """Tracked files when Git is available (honors .gitignore); otherwise a pruned walk."""
    try:
        output = subprocess.check_output(['git', '-C', str(root), 'ls-files'], text=True,
                                         stderr=subprocess.DEVNULL)
        names = [line for line in output.splitlines() if line.strip()]
        if names:
            return sorted(names)
    except (subprocess.CalledProcessError, OSError):
        pass
    found = []
    for path in root.rglob('*'):
        if not path.is_file() or skipped_dir(path.relative_to(root)):
            continue
        found.append(str(path.relative_to(root)))
    return sorted(found)


def skipped_dir(relative):
    """A path inside a generated, vendored or test-input directory is not project evidence."""
    return any(part in IGNORED_DIRS or part in INPUT_DIRS for part in Path(relative).parts[:-1])


def skipped_dirs(root, files):
    """The directories this profile ignored, so the report can say what it did not look at."""
    found = set()
    for name in files:
        parts = Path(name).parts
        for index, part in enumerate(parts[:-1]):
            if part in INPUT_DIRS:
                found.add('/'.join(parts[:index + 1]))
    for name in sorted(IGNORED_DIRS):
        if (root / name).exists():
            found.add(name)
    return sorted(found)


def matches(relative, pattern):
    """fnmatch has no recursive `**`; a leading `**/` also has to match the bare name."""
    if fnmatch.fnmatchcase(relative, pattern) or fnmatch.fnmatchcase(Path(relative).name, pattern):
        return True
    if pattern.startswith('**/'):
        stripped = pattern[3:]
        return (fnmatch.fnmatchcase(relative, stripped)
                or fnmatch.fnmatchcase(Path(relative).name, stripped))
    return False


def read_manifest(root, name, cache):
    if name in cache:
        return cache[name]
    path = root / name
    if not path.is_file():
        cache[name] = {}
        return cache[name]
    try:
        if name.endswith('.toml'):
            cache[name] = tomllib.loads(path.read_text(encoding='utf-8'))
        elif name.endswith('.json'):
            cache[name] = json.loads(path.read_text(encoding='utf-8'))
        else:
            cache[name] = {'__lines__': [line.strip() for line in
                                         path.read_text(encoding='utf-8').splitlines()]}
    except (tomllib.TOMLDecodeError, json.JSONDecodeError, OSError, UnicodeDecodeError):
        cache[name] = {}
    return cache[name]


def dependency_names(data):
    """Declared dependency names, normalised enough to compare against a vocabulary."""
    project = data.get('project', {})
    declared = list(project.get('dependencies') or [])
    declared += [item for group in (project.get('optional-dependencies') or {}).values()
                 for item in group]
    return {item.split('[')[0].split('>')[0].split('=')[0].split('<')[0].split(';')[0]
            .strip().lower() for item in declared if item}


def probe(root, pack, name, cache):
    """Return True, False, or None when the probe cannot be evaluated."""
    if pack == 'python':
        if name == 'entry_points':
            data = read_manifest(root, 'pyproject.toml', cache)
            return bool(data.get('project', {}).get('scripts'))
        if name == 'packaged_library':
            data = read_manifest(root, 'pyproject.toml', cache)
            project = data.get('project', {})
            # Declares a distribution but installs no command: the shape of a library.
            return bool(project.get('name')) and not bool(project.get('scripts'))
        if name == 'web_dependencies':
            names = dependency_names(read_manifest(root, 'pyproject.toml', cache))
            names |= {line.split('[')[0].split('>')[0].split('=')[0].split('<')[0].strip().lower()
                      for line in read_manifest(root, 'requirements.txt', cache).get('__lines__', [])
                      if line and not line.startswith('#')}
            return bool(names & WEB_DEPENDENCIES)
        if name == 'data_dependencies':
            names = dependency_names(read_manifest(root, 'pyproject.toml', cache))
            names |= {line.split('[')[0].split('>')[0].split('=')[0].split('<')[0].strip().lower()
                      for line in read_manifest(root, 'requirements.txt', cache).get('__lines__', [])
                      if line and not line.startswith('#')}
            return bool(names & DATA_DEPENDENCIES)
        if name == 'dependencies':
            data = read_manifest(root, 'pyproject.toml', cache)
            project = data.get('project', {})
            declared = list(project.get('dependencies') or [])
            declared += [item for group in (project.get('optional-dependencies') or {}).values()
                         for item in group]
            requirements = read_manifest(root, 'requirements.txt', cache).get('__lines__', [])
            declared += [line for line in requirements if line and not line.startswith('#')]
            return bool(declared)
        if name == 'ai_dependencies':
            data = read_manifest(root, 'pyproject.toml', cache)
            project = data.get('project', {})
            declared = list(project.get('dependencies') or [])
            return bool({item.split('[')[0].split('>')[0].split('=')[0].split('<')[0].strip().lower()
                         for item in declared} & AI_DEPENDENCIES)
    if pack == 'javascript':
        data = read_manifest(root, 'package.json', cache)
        if name == 'bin':
            return bool(data.get('bin'))
        if name == 'published':
            return data.get('private') is False
        names = set(data.get('dependencies') or {}) | set(data.get('devDependencies') or {})
        if name == 'dependencies':
            return bool(names)
        if name == 'ai_dependencies':
            return bool(names & AI_DEPENDENCIES)
        if name == 'ui_dependencies':
            return bool(names & UI_DEPENDENCIES)
        if name == 'packaged_library':
            # An entry point means it is run; `exports`/`main` without `private` means it is
            # imported. A private package with `main` is still a library inside its own repo, so
            # the probe is deliberately only about publishing shape.
            return bool(data.get('main') or data.get('exports')) and data.get('private') is not True
        if name == 'web_dependencies':
            return bool(names & WEB_DEPENDENCIES)
        if name == 'data_dependencies':
            return bool(names & DATA_DEPENDENCIES)
        if name == 'workspaces':
            return bool(data.get('workspaces'))
    return None


KIND_DETECTORS = {
    'library': {
        'exactness': 'heuristic',
        'limits': 'Packaging shape only: a CLI that is also installed as a library reads as an '
                  'application, and a library published from a separate release repo reads as '
                  'unknown here.',
        'sources': [{'pack': 'python', 'probe': 'packaged_library'},
                    {'pack': 'javascript', 'probe': 'packaged_library'},
                    {'patterns': ['*.gemspec', 'Package.swift', 'lib/**/*.rb']}]},
    'application': {
        'exactness': 'heuristic',
        'limits': 'Entry points and desktop/mobile manifest files; a program that is only ever '
                  'run by another program is not seen.',
        'sources': [{'pack': 'python', 'probe': 'entry_points'},
                    {'pack': 'javascript', 'probe': 'bin'},
                    {'patterns': ['main.py', 'app.py', 'manage.py', 'cli.py', 'cmd/**',
                                  'src/main.rs', '*.desktop', 'Info.plist', 'AndroidManifest.xml',
                                  'electron-builder.*', 'tauri.conf.json']}]},
    'service': {
        'exactness': 'heuristic',
        'limits': 'Web-framework dependencies and deployment definitions; a service written on a '
                  'bare socket, or a batch job with a Dockerfile, is classified wrong or not at '
                  'all.',
        'sources': [{'pack': 'python', 'probe': 'web_dependencies'},
                    {'pack': 'javascript', 'probe': 'web_dependencies'},
                    {'patterns': ['Dockerfile', 'Dockerfile.*', 'docker-compose*.yml',
                                  'docker-compose*.yaml', 'Procfile', 'fly.toml', 'render.yaml',
                                  'serverless.yml', 'openapi.yaml', 'openapi.json']}]},
    'frontend': {
        'exactness': 'heuristic',
        'limits': 'UI dependencies and client build configuration; a server-rendered site with no '
                  'client build is not seen.',
        'sources': [{'pack': 'javascript', 'probe': 'ui_dependencies'},
                    {'patterns': ['index.html', 'public/index.html', 'src/App.vue',
                                  'src/App.svelte', 'angular.json', 'next.config.*',
                                  'vite.config.*', 'nuxt.config.*', 'astro.config.*']}]},
    'data': {
        'exactness': 'heuristic',
        'limits': 'Data libraries and pipeline layouts; SQL files alone are deliberately not '
                  'enough, because migrations look the same.',
        'sources': [{'pack': 'python', 'probe': 'data_dependencies'},
                    {'patterns': ['dbt_project.yml', 'dagster.yaml', 'prefect.yaml', 'dags/**',
                                  'notebooks/**', 'pipelines/**', '*.ipynb']}]},
    'ml': {
        'exactness': 'heuristic',
        'limits': 'AI libraries and model artifacts; a service that calls a hosted model API '
                  'through a thin client may not be seen as ML.',
        'sources': [{'pack': 'python', 'probe': 'ai_dependencies'},
                    {'pack': 'javascript', 'probe': 'ai_dependencies'},
                    {'patterns': ['prompts/**', 'evals/**', '**/*.safetensors', '**/*.onnx',
                                  '**/*.pt', 'models/**/*.json']}]},
    'infrastructure': {
        'exactness': 'exact',
        'limits': 'Declared infrastructure-as-code and cluster layout files; hand-run '
                  'infrastructure leaves no file to find.',
        'sources': [{'patterns': ['*.tf', '**/*.tfvars', 'terraform/**', 'helm/**', 'charts/**',
                                  'k8s/**', 'kubernetes/**', 'ansible/**', 'playbooks/**',
                                  'Pulumi.yaml', 'cdk.json']}]},
    'platform': {
        'exactness': 'heuristic',
        'limits': 'Monorepo workspace markers; several unrelated projects in one repository '
                  'without a workspace file are not seen.',
        'sources': [{'pack': 'javascript', 'probe': 'workspaces'},
                    {'patterns': ['pnpm-workspace.yaml', 'lerna.json', 'nx.json', 'turbo.json',
                                  'go.work', 'packages/*/package.json', 'apps/*/package.json',
                                  'services/*/package.json']}]},
}
# A kind with no reliable file evidence is declared, never guessed: the model says why.
DECLARATION_ONLY_LIMITS = ('No file distinguishes this kind from an application or a library, so '
                           'AutoDOC asks instead of inferring.')


def kind_specs(model=None):
    """The three-valued kind detectors: what each kind is detected from, and what that misses."""
    return KIND_DETECTORS


def detect_kinds(files, ecosystems, cache, root):
    """Return {kind: {'value': .., 'evidence': ..}} for every kind with a detector."""
    found = {}
    for kind, spec in KIND_DETECTORS.items():
        value, evidence = evaluate(spec, files, set(ecosystems), cache, root, {})
        found[kind] = {'value': value, 'exactness': spec['exactness'],
                       'evidence': evidence, 'limits': spec['limits']}
    return found


def content_hits(root, source, files, cache):
    """Bounded content scan; returns matching paths only, never matched text."""
    pattern = re.compile(source['match'])
    hits, scanned = [], 0
    for name in files:
        if not any(matches(name, glob) for glob in source['globs']):
            continue
        if scanned >= CONTENT_FILE_LIMIT:
            break
        path = root / name
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        scanned += 1
        if pattern.search(text):
            hits.append(name)
    return hits


def evaluate(spec, files, ecosystems, cache, root, evidence):
    """Three-valued evaluation: true if anything matched, unknown if nothing could run."""
    applicable, matched = 0, []
    for source in spec['sources']:
        if 'pack' in source:
            if source['pack'] in ecosystems and source['pack'] in PACKS:
                applicable += 1
                result = probe(root, source['pack'], source['probe'], cache)
                if result:
                    matched.append(f"{source['probe']} in {source['pack']} manifest")
        elif 'globs' in source:
            applicable += 1
            hits = content_hits(root, source, files, cache)
            if hits:
                matched.extend(hits[:5])
        else:
            required = source.get('requires')
            if required and required not in ecosystems:
                continue
            applicable += 1
            hits = [name for name in files if any(matches(name, p) for p in source['patterns'])]
            if hits:
                matched.extend(hits[:5])
    if matched:
        return 'true', sorted(set(matched))[:5]
    if applicable:
        return 'false', []
    return 'unknown', []


def profile(root, declared=None):
    """Return a deterministic three-valued profile of the repository rooted at `root`."""
    root = Path(root).resolve()
    tracked = tracked_files(root)
    files = [name for name in tracked if not skipped_dir(name)]
    ecosystems = sorted(name for name, manifests in ECOSYSTEMS.items()
                        if any(matches(item, pattern) for item in files for pattern in manifests))
    cache, facts = {}, {}
    for flag, spec in fact_specs().items():
        if spec['detection'] == 'declaration-only':
            # Never inferred: with no declaration the honest value is "not answered", which the
            # resolver reports as undetermined. Absence is not a negative fact about the project.
            facts[flag] = {'value': 'unknown', 'detection': 'declaration-only', 'exactness': None,
                           'evidence': [], 'limits': spec['why_declared_only'],
                           'label': spec['label']}
            continue
        value, evidence = evaluate(spec, files, set(ecosystems), cache, root, {})
        facts[flag] = {'value': value, 'detection': 'files', 'exactness': spec['exactness'],
                       'evidence': evidence, 'limits': spec['limits']}
    for name in sorted(declared or {}):
        if name not in facts:
            raise ValueError('Unknown declared fact: ' + name)
        entry = declared[name]
        facts[name] = {**facts[name], 'value': entry['value'], 'evidence': ['declared'],
                       'declared_reason': entry['reason']}
    languages = {}
    for name in files:
        language = LANGUAGES.get(Path(name).suffix.lower())
        if language:
            languages[language] = languages.get(language, 0) + 1
    return {'version': 2, 'repo': root.name, 'file_count': len(files),
            'languages': dict(sorted(languages.items(), key=lambda item: (-item[1], item[0]))),
            'ecosystems': {'present': ecosystems,
                           'readers': [name for name in ecosystems if name in PACKS],
                           'unread': [name for name in ecosystems if name not in PACKS]},
            'facts': facts,
            'kinds': detect_kinds(files, ecosystems, cache, root),
            'excluded': skipped_dirs(root, tracked),
            'note': 'File-presence facts with stated limits, never behavior. `unknown` means no '
                    'configured source could be evaluated; it never means false. Facts with '
                    '`detection` `declaration-only` (the declared traits) have no detector at all '
                    'and stay `unknown` until the owner answers in autodoc.toml. `kinds` holds '
                    'evidence for the project kinds that have a detector; it is a hint, never a '
                    'declaration, and the requirements are driven by the declared `kinds` in '
                    'autodoc.toml. `excluded` lists the generated, vendored and test-input '
                    'directories not looked at.'}


def summary(document):
    """Boolean projection for callers that only need the values that are true."""
    return {name: entry['value'] for name, entry in document['facts'].items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT, help='Repository to profile')
    parser.add_argument('--output', type=Path, help='Write profile JSON here instead of stdout')
    args = parser.parse_args()
    try:
        document = json.dumps(profile(args.repo), indent=2) + '\n'
    except (ValueError, OSError) as error:
        raise SystemExit(f'Profile error: {error}')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document, encoding='utf-8')
        print('Wrote', args.output)
    else:
        print(document, end='')
