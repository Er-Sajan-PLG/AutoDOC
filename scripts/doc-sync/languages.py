#!/usr/bin/env python3
"""Per-language references: integrate the language's own tool, never reimplement one.

A language gets a generator only where integrating its canonical tool is honest. Each entry
declares the tool, how it runs, its `exactness` and its `limits` — the same shape the fact
detectors use. The runner is sandboxed on purpose: the tool runs inside the repository, with a
scrubbed environment (never the caller's), the toolchain's offline flags, no shell and a timeout.
A missing or failing tool is reported with its reason; it is never replaced by a hand-rolled
parser, an empty document, or silence. A language with no declared generator is reported as L0 —
file and manifest facts only — and never guessed at.

Committed generated content must be reproducible, so a reference produced by an external
toolchain is printed on demand (`--show`) and never written to a drift-checked target: the same
repository on two machines would otherwise disagree. Committed per-language inventory is limited
to in-process extraction, which is deterministic.

Exit codes: 0 success, 1 the requested reference could not be generated, 2 usage error.
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILER = ROOT / 'scripts/intelligence/profile.py'
sys.path.insert(0, str(ROOT / 'engine'))
from extractors.facts import python_api  # noqa: E402 - path is set up above

DEFAULT_TIMEOUT = 30

# The registry. `probe` is the executable that must exist for the generator to run; an
# in-process generator ships with AutoDOC and needs no probe. `env` is what the toolchain needs
# to work offline: AutoDOC never installs a toolchain, fetches modules or opens a network path.
GENERATORS = {
    'python': {
        'tool': 'ast (the CPython parser)',
        'mode': 'in-process',
        'probe': None,
        'exactness': 'exact',
        'limits': 'Module-level declarations, signatures and first docstring lines from parsed '
                  'source: definitions created at runtime, generated code and non-module sources '
                  'are invisible.',
    },
    'go': {
        'tool': 'go doc -all .',
        'mode': 'subprocess',
        'argv': ['go', 'doc', '-all', '.'],
        'probe': 'go',
        'exactness': 'exact',
        'limits': 'The exported API of packages the toolchain can read; a module that does not '
                  'resolve yields no reference, and AutoDOC never installs a toolchain or fetches '
                  'modules.',
        'env': {'GOPROXY': 'off', 'GOFLAGS': '-mod=readonly', 'GOTOOLCHAIN': 'local',
                'GOTELEMETRY': 'off'},
    },
}

NO_GENERATOR = ('No generator is declared for this language: it is read at L0 — file and '
                'manifest facts only — because AutoDOC integrates a language\'s own tool and '
                'never hand-rolls a parser for it.')


def profiler_module():
    """The language vocabulary lives in the profiler; this module never keeps a second copy."""
    spec = importlib.util.spec_from_file_location('autodoc_languages_profiler', PROFILER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generator(language):
    """The declared generator for a language, or None when the language is L0."""
    return GENERATORS.get(language)


def available(language, path=None):
    """Return (True, None) when the generator can run here, else (False, reason)."""
    spec = GENERATORS.get(language)
    if spec is None:
        return False, NO_GENERATOR
    if spec['mode'] == 'in-process':
        return True, None
    found = shutil.which(spec['probe'], path=path if path is not None else os.environ.get('PATH'))
    if not found:
        return False, f'`{spec["probe"]}` is not on PATH'
    return True, None


def runner_env(spec, sandbox, path=None):
    """A scrubbed environment: no inherited variables, offline flags, caches in a temp sandbox."""
    env = {'PATH': path if path is not None else os.environ.get('PATH', ''),
           'HOME': str(sandbox), 'TMPDIR': str(sandbox),
           'LANG': os.environ.get('LANG', 'C.UTF-8')}
    env.update(spec.get('env', {}))
    return env


def run(language, root, files=None, timeout=DEFAULT_TIMEOUT, path=None, env=None):
    """Run one language's generator. Returns a result record; never raises for tool failure.

    Statuses: `generated` (text is the reference), `unavailable` (no generator, or its tool is
    not installed), `timed_out`, `no-files` (generator exists, nothing to read), `failed`.
    """
    root = Path(root)
    spec = GENERATORS.get(language)
    result = {'language': language, 'files': len(files or []), 'timeout': timeout,
              'status': None, 'reason': None, 'text': None,
              'tool': spec['tool'] if spec else None,
              'exactness': spec['exactness'] if spec else None,
              'limits': spec['limits'] if spec else NO_GENERATOR}
    ok, reason = available(language, path)
    if not ok:
        return {**result, 'status': 'unavailable', 'reason': reason}
    if spec['mode'] == 'in-process':
        if not files:
            return {**result, 'status': 'no-files', 'reason': 'no files of this language were read'}
        return {**result, 'status': 'generated', 'text': reference(language, files, root)}
    if not files:
        # A toolchain asked to document nothing would either fail or print an empty page, and
        # neither is a reference. Say there was nothing to read instead of running the tool.
        return {**result, 'status': 'no-files', 'reason': 'no files of this language were matched'}
    sandbox = Path(tempfile.mkdtemp(prefix='autodoc-language-'))
    try:
        proc = subprocess.run(spec['argv'], cwd=root, env=env or runner_env(spec, sandbox, path),
                              timeout=timeout, shell=False, capture_output=True, text=True,
                              check=False)
    except subprocess.TimeoutExpired:
        return {**result, 'status': 'timed_out',
                'reason': f'`{spec["tool"]}` did not finish within {timeout}s'}
    except OSError as error:
        return {**result, 'status': 'failed', 'reason': f'could not run `{spec["tool"]}`: {error}'}
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)
    if proc.returncode != 0:
        tail = [line for line in (proc.stderr or proc.stdout or '').strip().splitlines() if line]
        return {**result, 'status': 'failed',
                'reason': f'`{spec["tool"]}` exited {proc.returncode}'
                          + (f': {tail[-1].strip()}' if tail else '')}
    if not proc.stdout.strip():
        return {**result, 'status': 'failed', 'reason': f'`{spec["tool"]}` printed nothing'}
    return {**result, 'status': 'generated', 'text': proc.stdout}


def reference(language, files, root):
    """Render one language's reference in Markdown. Only in-process renderers exist today."""
    if language != 'python':
        raise ValueError(f'No in-process renderer for {language}; run its toolchain instead')
    lines = ['## Python declarations (exact, in-process)', '',
             'Extracted with the interpreter\'s own parser. Signatures and first docstring lines '
             'only; nothing here is executed, and a definition that exists only at runtime is not '
             'in the source tree to be seen.', '',
             '| Source | Line | Kind | Symbol | Signature | Summary |',
             '| --- | ---: | --- | --- | --- | --- |']
    vocabulary = profiler_module().LANGUAGES
    for path in sorted(Path(item) for item in files):
        if vocabulary.get(path.suffix.lower()) != language:
            continue  # a mixed source list: only this language's files are read here
        relative = path.relative_to(root) if path.is_absolute() else path
        for line, kind, name, signature, summary in python_api(path):
            lines.append(f'| `{relative}` | {line} | {kind} | `{name}` | `{signature}` | {summary} |')
    return '\n'.join(lines) + '\n'


def declarations(entry, root=None):
    """The language counts of a set of files, from the one shared vocabulary."""
    root = Path(root or ROOT)
    counts = {}
    for item in entry:
        path = Path(item)
        language = profiler_module().LANGUAGES.get(path.suffix.lower())
        if language:
            counts[language] = counts.get(language, 0) + 1
    return counts


def rows(counts, path=None, probe=False):
    """Per-language rows for the code languages present.

    `probe=False` is deterministic — the registry's declared tool, exactness and limits, and the
    L0 statement for languages with no generator. `probe=True` adds whether this machine can
    actually run it, which is a fact about the machine, never about the repository.
    """
    code = profiler_module().CODE_LANGUAGES
    result = []
    for language in sorted(counts):
        if language not in code:
            continue
        spec = GENERATORS.get(language)
        row = {'language': language, 'files': counts[language],
               'generator': language if spec else None,
               'tool': spec['tool'] if spec else None,
               'exactness': spec['exactness'] if spec else None,
               'limits': spec['limits'] if spec else NO_GENERATOR}
        if probe:
            ok, reason = available(language, path)
            row['available'] = ok
            row['reason'] = reason
        result.append(row)
    return result


def line(rows_):
    """One report line: what each code language gets here, and what it does not get today."""
    parts = []
    for row in rows_:
        if not row['generator']:
            parts.append(f"{row['language']} (L0 — no generator declared, facts only)")
        elif row.get('available', True):
            parts.append(f"{row['language']} ({row['exactness']} via {row['tool']})")
        else:
            parts.append(f"{row['language']} (declared {row['exactness']} via {row['tool']}; "
                         f"{row['reason']} — L0 in this run)")
    return '- Languages: ' + ('; '.join(parts) or 'none with a generator')


def tracked_language_files(root):
    """Tracked files that are project evidence: generated, vendored and test inputs are skipped.

    The same rule the profiler applies, so the command and the report cannot disagree about what
    the repository contains — a fixture toolchain or a vendored bundle is not the project's code.
    """
    profiler = profiler_module()
    return [name for name in profiler.tracked_files(root) if not profiler.skipped_dir(name)]


def report(root=ROOT, path=None, probe=True):
    """The terminal view: one line per code language, with the limits spelled out."""
    counts = declarations(tracked_language_files(root), root)
    lines = ['# Language coverage', '',
             'A language gets a generator only where its own tool can be integrated. A language '
             'with no generator is read at L0 — file and manifest facts only — and said so, never '
             'guessed at.', '']
    for row in rows(counts, path=path, probe=probe):
        status = 'L0 — no generator declared'
        if row['generator']:
            status = (f"available ({row['exactness']} via {row['tool']})" if row.get('available')
                      else f"declared, but {row['reason']}")
        lines.append(f"- **{row['language']}** — {row['files']} file(s), {status}")
        lines.append(f"  - what it can and cannot see: {row['limits']}")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT, help='Repository to read')
    parser.add_argument('--show', metavar='LANGUAGE', help='Print one generated reference')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT,
                        help=f'Seconds before a toolchain is stopped (default {DEFAULT_TIMEOUT})')
    parser.add_argument('--json', action='store_true', help='Print machine-readable coverage')
    args = parser.parse_args()
    files = tracked_language_files(args.repo)
    counts = declarations(files, args.repo)
    if args.show:
        matched = [path for path in files
                   if profiler_module().LANGUAGES.get(Path(path).suffix.lower()) == args.show]
        result = run(args.show, args.repo, files=matched, timeout=args.timeout)
        if result['status'] != 'generated':
            print(f"{args.show}: {result['status']} — {result['reason']}", file=sys.stderr)
            return 1
        print(result['text'], end='')
        return 0
    data = rows(counts, probe=True)
    if args.json:
        print(json.dumps({'version': 1, 'languages': data}, indent=2))
        return 0
    print(report(args.repo), end='')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ValueError as error:
        raise SystemExit(f'Language coverage error: {error}')
