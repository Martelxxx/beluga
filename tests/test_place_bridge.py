import unittest
from unittest.mock import patch

import beluga_server as beluga


class PassengerPlaceBridgeTests(unittest.TestCase):
    def setUp(self):
        with beluga.PLACE_CACHE_LOCK:
            beluga.PLACE_CACHE.clear()

    def test_normalizer_keeps_canonical_location_separate_from_yelp(self):
        row = {
            "canonical": {
                "id": "iad-dining-42",
                "name": "Example Coffee",
                "terminal": "Concourse B",
                "zone": "B Gates",
                "level": "Departures",
                "coordinates": {"latitude": 38.95, "longitude": -77.45},
                "source": "airport-map",
            },
            "consumer": {
                "provider": "Yelp",
                "business_id": "yelp-123",
                "rating": 4.6,
                "review_count": 318,
                "price": "$$",
                "highlights": ["Coffee & Tea", "Breakfast"],
                "image_url": "https://example.test/coffee.jpg",
                "url": "https://example.test/yelp",
                "phone": "+1 555 555 0100",
                "match_confidence": 0.94,
                "match_distance_m": 21,
            },
        }
        card = beluga._normalize_passenger_place(row, "IAD", "dining")
        self.assertEqual(card["name"], "Example Coffee")
        self.assertEqual(card["terminal"], "Concourse B")
        self.assertEqual(card["zone"], "B Gates")
        self.assertEqual(card["physical_location_source"], "airport-map")
        self.assertEqual(card["consumer"]["provider"], "Yelp")
        self.assertEqual(card["consumer"]["rating"], 4.6)
        self.assertEqual(card["consumer"]["price"], "$$")
        self.assertEqual(card["consumer"]["business_id"], "yelp-123")

    def test_bridge_accepts_cards_response_shape(self):
        payload = {
            "airport": "IAD",
            "category": "dining",
            "cards": [
                {
                    "canonical": {"id": "1", "name": "Known Airport Cafe", "zone": "Concourse C"},
                    "consumer": {"provider": "Yelp", "rating": 4.2, "price": "$"},
                }
            ],
        }
        with patch.object(beluga, "_ingestion_json", return_value=payload):
            result = beluga.passenger_place_cards("IAD", "dining", allow_stale=False)
        self.assertTrue(result["available"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["name"], "Known Airport Cafe")
        self.assertEqual(result["items"][0]["consumer"]["rating"], 4.2)

    def test_bridge_does_not_create_inventory_from_empty_enrichment(self):
        with patch.object(beluga, "_ingestion_json", return_value={"cards": []}):
            result = beluga.passenger_place_cards("IAD", "dining", allow_stale=False)
        self.assertTrue(result["available"])
        self.assertEqual(result["items"], [])
        self.assertEqual(result["count"], 0)

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(beluga.APIError):
            beluga.passenger_place_cards("IAD", "nearby_everything", allow_stale=False)


if __name__ == "__main__":
    unittest.main()
