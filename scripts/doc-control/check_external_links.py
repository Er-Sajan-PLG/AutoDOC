#!/usr/bin/env python3
"""External link checks: the one network-touching check, kept in its own event.

AutoDOC is offline by default. This command is the exception, so it is scheduled, rate-limited and
warn-only, and it is deliberately absent from `make ci`: a flaky third-party host may never fail
someone's pull request. It opens one connection at a time, waits at least the declared interval
between requests to the same host, stops after the declared number of links, and gives every
request a timeout.

The report says what it skipped and why: templates are excluded because their links are
placeholders, generated files are excluded because a machine wrote them, and a run that stops at
the cap says so.

Exit codes: 0 warn-only (this is the default, even with broken links), 1 with `--strict` when
something is missing or errored, 2 usage or configuration error, 3 the tool itself failed.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = 'AutoDOC-link-check/1.0 (+https://github.com/STEMORG2026/AutoDOC)'
DEFAULTS = {'per_host_seconds': 1.0, 'max_links': 200, 'timeout_seconds': 10}
URL = re.compile(r'https?://[^\s<>)\]"\'`]+')
TRAILING = '.,;:!?'
FENCE = re.compile(r'^\s*(```|~~~)')
# Hosts that are documentation, not dependencies: loopback, reserved test names, canned examples.
PLACEHOLDER_HOSTS = ('localhost', '127.0.0.1', '0.0.0.0', '::1', 'host.docker.internal')
PLACEHOLDER_SUFFIXES = ('.local', '.invalid', '.test', '.example', '.localhost')
PLACEHOLDER_DOMAINS = ('example.com', 'example.net', 'example.org')


def model_defaults():
    """The rate limits declared in the trigger model; the CLI defaults must equal them."""
    path = ROOT / 'CONTROL/metadata/TRIGGERS.json'
    if not path.exists():
        return dict(DEFAULTS)
    for event in json.loads(path.read_text(encoding='utf-8')).get('events', []):
        if isinstance(event.get('rate_limit'), dict):
            return dict(event['rate_limit'])
    return dict(DEFAULTS)


def controlled_documents(root=ROOT):
    """The controlled Markdown set. Templates are excluded: their links are placeholders.

    Generated files are read too — they are what readers see, and byte drift keeps them stable.
    """
    sys.path.insert(0, str(root / 'scripts/doc-sync'))
    import engine  # the one definition of what a controlled document is
    kept, skipped = [], {'templates': 0}
    for path in engine.controlled():
        if 'templates' in path.parts:
            skipped['templates'] += 1
            continue
        kept.append(path)
    return kept, skipped


def extract(text):
    """(line, url) pairs from prose, not from fenced code blocks. Order preserved, deduped later."""
    found = []
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        for match in URL.finditer(line):
            url = match.group(0).rstrip(TRAILING)
            while url.endswith(')') and url.count('(') < url.count(')'):
                url = url[:-1]
            if url:
                found.append((number, url))
    return found


def targets(documents):
    """One entry per distinct URL, keeping where it was first seen."""
    seen, ordered = {}, []
    for path in documents:
        for line, url in extract(path.read_text(encoding='utf-8')):
            if url in seen:
                continue
            location = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
            seen[url] = {'url': url, 'file': str(location), 'line': line}
            ordered.append(seen[url])
    return ordered


def is_placeholder(url):
    """True for a URL that documents a local or reserved name, never a reachable dependency."""
    import urllib.parse
    host = (urllib.parse.urlsplit(url).hostname or '').lower()
    if host in PLACEHOLDER_HOSTS or host.endswith(PLACEHOLDER_SUFFIXES):
        return True
    return any(host == domain or host.endswith('.' + domain) for domain in PLACEHOLDER_DOMAINS)


def checkable(entries):
    """Split distinct URLs into what a scheduled run checks and what it skips, with the reason."""
    kept, skipped = [], []
    for entry in entries:
        if is_placeholder(entry['url']):
            skipped.append({**entry, 'reason': 'local or example host, documented not deployed'})
        else:
            kept.append(entry)
    return kept, skipped


def classify(status):
    """Four honest buckets; 'restricted' means the host answered but would not show the page."""
    if 200 <= status < 400:
        return 'ok'
    if status in (401, 403, 405, 429):
        return 'restricted'
    if status in (404, 410):
        return 'missing'
    return 'error'


def probe(url, timeout=DEFAULTS['timeout_seconds']):
    """One request: HEAD, then GET when the host refuses HEAD. Returns (status, error)."""
    for method in ('HEAD', 'GET'):
        request = urllib.request.Request(url, method=method, headers={'User-Agent': GUARD})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, None
        except urllib.error.HTTPError as error:
            if method == 'HEAD' and error.code in (403, 405, 501):
                continue  # some hosts refuse HEAD but serve GET; ask again before judging
            return error.code, None
        except Exception as error:  # noqa: BLE001 - any transport failure is one honest bucket
            return None, f'{type(error).__name__}: {error}'
    return None, 'no response'


def check_links(entries, probe_=probe, delay=DEFAULTS['per_host_seconds'], max_links=None,
                timeout=DEFAULTS['timeout_seconds'], clock=time.monotonic, sleep=time.sleep):
    """Check links, one at a time, at least `delay` seconds apart per host."""
    import urllib.parse
    selected = entries[:max_links] if max_links else entries
    last_host_time, results = {}, []
    for entry in selected:
        host = urllib.parse.urlsplit(entry['url']).hostname or ''
        waited = 0.0
        if host in last_host_time:
            waited = last_host_time[host] + delay - clock()
            if waited > 0:
                sleep(waited)
        last_host_time[host] = clock()
        status, error = probe_(entry['url'], timeout)
        bucket = classify(status) if status is not None else 'error'
        results.append({**entry, 'status': status, 'error': error, 'result': bucket,
                        'waited_seconds': round(max(waited, 0.0), 3)})
    return results


def report(entries, results, skipped, delay, max_links, timeout):
    counts = {}
    for item in results:
        counts[item['result']] = counts.get(item['result'], 0) + 1
    lines = ['# External link check', '',
             'Scheduled, rate-limited and warn-only. This command is not part of `make ci`: a '
             'third-party host may not fail a pull request. Anything but `ok` is for triage.', '',
             f"- Checked {len(results)} of {len(entries)} link(s); caps: {max_links} links, "
             f"{delay}s between requests to the same host, {timeout}s per request.",
             f"- Result: {counts.get('ok', 0)} ok, {counts.get('restricted', 0)} restricted "
             f"(auth or rate limit, treated as reachable), {counts.get('missing', 0)} missing, "
             f"{counts.get('error', 0)} errored.",
             f"- Skipped by design: {skipped['templates']} template file(s); their links are "
             f"placeholders."]
    lines.append(f"- Link extraction is line-based: fenced code is skipped, and indented code or "
                 f"HTML bodies are read as prose, which a template or a sample can surprise.")
    if len(entries) > len(results):
        lines.append(f"- {len(entries) - len(results)} link(s) not checked this run because of "
                     f"the cap; the cap is intentional, raise it in the scheduled workflow.")
    if skipped.get('placeholders'):
        lines.append(f"- Skipped {skipped['placeholders']} local or example URL(s): they document "
                     f"a local endpoint or a reserved name, so a scheduled runner cannot reach "
                     f"them by design.")
    print_lines = []
    for item in results:
        if item['result'] in ('missing', 'error'):
            detail = f"HTTP {item['status']}" if item['status'] is not None else item['error']
            print_lines.append(f"- {item['result']}: {item['url']} ({detail}) — {item['file']}:"
                               f"{item['line']}")
    if print_lines:
        lines.extend(['', '## Needs triage', ''] + print_lines)
    lines.extend(['', 'A red scheduled run is triage, never a gate.', ''])
    return '\n'.join(lines)


def main(argv=None, probe_=None, documents=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true', help='Print the links; no network access')
    parser.add_argument('--json', action='store_true', help='Print machine-readable output')
    parser.add_argument('--strict', action='store_true',
                        help='Exit 1 when a link is missing or errored (owner opt-in; default is warn-only)')
    defaults = model_defaults()
    parser.add_argument('--max', type=int, default=defaults['max_links'],
                        help=f"Most links to check (default {defaults['max_links']})")
    parser.add_argument('--delay', type=float, default=defaults['per_host_seconds'],
                        help=f"Seconds between requests to one host (default {defaults['per_host_seconds']})")
    parser.add_argument('--timeout', type=float, default=defaults['timeout_seconds'],
                        help=f"Seconds per request (default {defaults['timeout_seconds']})")
    args = parser.parse_args(argv)
    kept, skipped = controlled_documents() if documents is None else (list(documents), {'templates': 0})
    documents = kept
    entries, placeholders = checkable(targets(documents))
    skipped['placeholders'] = len(placeholders)
    if args.list:
        if args.json:
            print(json.dumps({'version': 1, 'links': entries, 'placeholder_links': placeholders,
                              'skipped': skipped}, indent=2))
        else:
            for entry in entries:
                print(f"{entry['file']}:{entry['line']} {entry['url']}")
        return 0
    results = check_links(entries, probe_=probe_ or probe, delay=args.delay, max_links=args.max,
                          timeout=args.timeout)
    if args.json:
        print(json.dumps({'version': 1, 'checked': len(results), 'of': len(entries),
                          'caps': {'max_links': args.max, 'delay': args.delay,
                                   'timeout': args.timeout},
                          'skipped': skipped, 'results': results}, indent=2))
    else:
        print(report(entries, results, skipped, args.delay, args.max, args.timeout), end='')
    if args.strict and any(item['result'] in ('missing', 'error') for item in results):
        return 1
    return 0


def cli(argv=None, probe_=None, documents=None):
    """The exit-code contract: 2 for a configuration problem, 3 for a tool failure, never 1."""
    try:
        return main(argv, probe_, documents)
    except (KeyboardInterrupt, SystemExit):
        raise
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print('External link check error:', error, file=sys.stderr)
        return 2
    except Exception as error:  # noqa: BLE001 - keep a crash off exit 1
        print(f'Internal error: {type(error).__name__}: {error}', file=sys.stderr)
        print('This is a tool failure, not a finding about this repository.', file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(cli())
