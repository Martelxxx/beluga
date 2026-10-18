"""HTTP smoke tests for the ingestion publication and passenger routes."""
import base64
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

import beluga_ingestion_bridge as bridge
from beluga_server import Handler


class IngestionAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = "http://127.0.0.1:" + str(cls.server.server_address[1])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.original = bridge.STORE
        bridge.STORE = Path(self.temporary.name)
        self.environment = patch.dict(os.environ, {
            "BELUGA_INGESTION_PUBLISH_KEY": "http-test-publish-key",
            "BELUGA_INGESTION_RETRIEVE_URL": ""
        })
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        bridge.STORE = self.original
        self.temporary.cleanup()

    def request(self, method, path, payload=None, key=None):
        headers = {"Content-Type": "application/json"}
        if key:
            headers["X-Beluga-Publish-Key"] = key
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=5) as response:
                body = response.read()
                return response.status, response.headers, body
        except HTTPError as e:
            return e.code, e.headers, e.read()

    def fixture(self):
        return {
            "airport": "EWR", "revision": "ewr-v10-001",
            "qa": {"passed": True, "context_fingerprint": "a" * 64},
            "airport_name": "Newark Liberty International Airport",
            "concessions": [{"name": "Cafe near C", "terminal": "C",
                             "source_url": "https://example.org/ewr-dining"}],
            "evidence": [{"text": "Cafe near Terminal C",
                          "source_url": "https://example.org/ewr-dining"}],
            "header_image": {"mime_type":"image/png",
                             "data_base64":base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"X" * 12).decode()},
        }

    def test_end_to_end_publish_profile_image_and_retrieve(self):
        snapshot = self.fixture()
        status, _, _ = self.request("POST", "/api/ingestion/publish", snapshot)
        self.assertEqual(status, 403)
        status, _, raw = self.request("POST", "/api/ingestion/publish", snapshot, "http-test-publish-key")
        self.assertEqual(status, 201, raw)
        status, _, raw = self.request("GET", "/api/ingestion/airport/EWR")
        self.assertEqual(status, 200)
        profile = json.loads(raw)
        self.assertEqual(profile["revision"], "ewr-v10-001")
        self.assertEqual(profile["concessions"][0]["name"], "Cafe near C")
        status, headers, body = self.request("GET", "/api/ingestion/image/EWR")
        self.assertEqual(status, 200)
        self.assertEqual(headers.get_content_type(), "image/png")
        self.assertTrue(body.startswith(b"\x89PNG"))
        status, _, raw = self.request("POST", "/api/ingestion/retrieve",
                                      {"airport":"EWR", "question":"cafe at terminal C"})
        self.assertEqual(status, 200)
        retrieval = json.loads(raw)
        self.assertEqual(retrieval["mode"], "published-fallback")
        self.assertEqual(retrieval["evidence"][0]["source_url"], "https://example.org/ewr-dining")
        status, _, raw = self.request("GET", "/api/ingestion/airports")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)["airports"], ["EWR"])
        status, _, _ = self.request("GET", "/api/ingestion/airport/IAD")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
