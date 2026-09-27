"""Exercise the documented task routes over HTTP using an isolated SQLite database."""
import importlib.util
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('app', ROOT / 'EXAMPLE-PROJECT/src/app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class APIIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        app.Handler.db_path = str(Path(cls.folder.name) / 'test.db')
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.folder.cleanup()

    def test_registry_and_data(self):
        def fetch(path, method='GET', data=None):
            req = Request(self.base + path, method=method,
                          data=json.dumps(data).encode() if data is not None else None,
                          headers={'Content-Type': 'application/json'})
            with urlopen(req) as response:
                return response.status, json.load(response)
        self.assertEqual(fetch('/health')[1]['status'], 'ok')
        status, task = fetch('/tasks', 'POST', {'title': 'Write docs'})
        self.assertEqual(status, 201)
        self.assertIn(task, fetch('/tasks')[1])
        with self.assertRaises(HTTPError) as error:
            fetch('/tasks', 'POST', {'title': ''})
        self.assertEqual(error.exception.code, 400)
        with self.assertRaises(HTTPError) as error:
            fetch('/missing')
        self.assertEqual(error.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
