"""Tiny task API; routes and configuration are read from the documented SSOTs."""
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {(r['method'], r['path']) for r in json.loads((ROOT / 'routes.json').read_text())['routes']}
if ROUTES != {('GET', '/tasks'), ('POST', '/tasks'), ('GET', '/health')}:
    raise ValueError('Route registry differs from implemented HTTP handlers')
SCHEMA = json.loads((ROOT / 'config.schema.json').read_text())['properties']


def setting(key):
    value = os.environ.get(key, SCHEMA[key]['default'])
    return int(value) if SCHEMA[key]['type'] == 'integer' else value


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript((ROOT / 'db/schema.sql').read_text())
    return conn


class Handler(BaseHTTPRequestHandler):
    db_path = None

    def respond(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if ('GET', self.path) not in ROUTES:
            return self.respond(404, {'error': 'not found'})
        if self.path == '/health':
            return self.respond(200, {'status': 'ok'})
        with connect(self.db_path) as db:
            return self.respond(200, [{'id': row[0], 'title': row[1]} for row in db.execute('SELECT id, title FROM tasks ORDER BY id')])

    def do_POST(self):
        if ('POST', self.path) not in ROUTES:
            return self.respond(404, {'error': 'not found'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size > 4096 or size < 1:
                raise ValueError('invalid length')
            title = json.loads(self.rfile.read(size))['title']
            if not isinstance(title, str) or not title.strip():
                raise ValueError('invalid title')
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return self.respond(400, {'error': 'expected nonempty title'})
        with connect(self.db_path) as db:
            cursor = db.execute('INSERT INTO tasks (title) VALUES (?)', (title.strip(),))
            return self.respond(201, {'id': cursor.lastrowid, 'title': title.strip()})


def serve(host='0.0.0.0', port=None, db_path=None):
    Handler.db_path = db_path or str(ROOT / setting('DB_PATH'))
    server = ThreadingHTTPServer((host, port if port is not None else setting('PORT')), Handler)
    server.serve_forever()


if __name__ == '__main__':
    serve()
