"""Contract tests: python3 -m unittest discover -s tests -v"""
import base64
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import beluga_ingestion_bridge as bridge


def snapshot(code="IAD", version="iad-2026-10-17"):
    return {
        "airport": code, "revision": version,
        "qa": {"passed": True, "context_fingerprint": "f" * 64},
        "airport_name": "Dulles International Airport",
        "published_at": "2026-10-17T20:00:00Z",
        "concessions": [{"name": "Coffee Counter", "gate": "C12",
                         "website": "https://example.org/cafe"}],
        "facts": [{"text": "C gates are served by the AeroTrain.",
                   "source_url": "https://example.org/dulles"}],
        "evidence": [{"title": "Terminal guide",
                      "text": "The coffee counter is located at Gate C12.",
                      "source_url": "https://example.org/airport/coffee"},
                     {"text": "Departures level has TSA screening checkpoints.",
                      "source_url": "https://example.org/airport/security"}],
    }


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self._store = bridge.STORE
        bridge.STORE = Path(self.directory.name)

    def tearDown(self):
        bridge.STORE = self._store
        self.directory.cleanup()

    def test_qa_is_mandatory(self):
        payload = snapshot()
        payload["qa"]["passed"] = False
        with self.assertRaises(bridge.BridgeError):
            bridge.publish(payload)
        self.assertEqual(bridge.published_codes(), [])

    def test_version_and_grounded_evidence(self):
        result = bridge.publish(snapshot())
        self.assertEqual(result["airport"], "IAD")
        profile = bridge.public_profile("IAD")
        self.assertNotIn("evidence", profile)
        self.assertEqual(profile["concessions"][0]["gate"], "C12")
        with patch.dict(os.environ, {"BELUGA_INGESTION_RETRIEVE_URL": ""}):
            answer = bridge.retrieve("IAD", "Where is coffee near gate C12?")
        self.assertEqual(answer["mode"], "published-fallback")
        self.assertIn("coffee", answer["evidence"][0]["text"].lower())
        self.assertEqual(answer["evidence"][0]["source_url"], "https://example.org/airport/coffee")

    def test_airport_scope_does_not_leak(self):
        bridge.publish(snapshot("IAD"))
        self.assertEqual(bridge.retrieve("EWR", "coffee")["evidence"], [])
        with self.assertRaises(bridge.BridgeError):
            bridge.public_profile("EWR")

    def test_untrusted_external_url_is_dropped(self):
        payload = snapshot()
        payload["evidence"][0]["source_url"] = "javascript:alert(1)"
        bridge.publish(payload)
        with patch.dict(os.environ, {"BELUGA_INGESTION_RETRIEVE_URL": ""}):
            response = bridge.retrieve("IAD", "coffee")
        self.assertFalse(response["evidence"])

    def test_failed_revision_rewrite_is_rejected(self):
        bridge.publish(snapshot())
        newer = snapshot()
        newer["qa"]["context_fingerprint"] = "a" * 64
        with self.assertRaises(bridge.BridgeError):
            bridge.publish(newer)

    def test_image_publish_and_serve(self):
        payload = snapshot()
        payload["header_image"] = {
            "mime_type": "image/png",
            "data_base64": base64.b64encode(b"\x89PNG\r\n\\x1a\n" + b"x" * 16).decode()
        }
        # Python bytes literals above intentionally contain the PNG signature.
        result = bridge.publish(payload)
        self.assertIn("/api/ingestion/image/IAD", result["image"])
        content, mime = bridge.image_asset("IAD")
        self.assertEqual(mime, "image/png")
        self.assertTrue(content.startswith(b"\x89PNG"))

    def test_key_requirement(self):
        with patch.dict(os.environ, {"BELUGA_INGESTION_PUBLISH_KEY": "secret-key"}):
            with self.assertRaises(bridge.BridgeError):
                bridge.check_publish_authorization("wrong-key")
            bridge.check_publish_authorization("secret-key")


if __name__ == "__main__":
    unittest.main()
