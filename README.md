# Beluga — V52.2

Beluga is a premium AI airport/travel assistant prototype.

## Current version
V52.2 — canonical airport place cards from the ingestion architecture, with Yelp consumer enrichment flowing into the passenger app.

## Start locally

```bash
cp .env.example .env
# Add your server-side keys to .env
python3 beluga_server.py
```

Then open `http://127.0.0.1:8790`.

## Server-side providers
- OpenAI
- Aviationstack
- WeatherAPI
- Duffel
- RouteStack

Secrets belong in `.env` and must never be committed.

## Main files
- `index.html` — current V52.1 frontend
- `beluga_full_demo_v52_1.html` — versioned frontend source
- `beluga_server.py` — local API/backend boundary
- `airport_context/` — airport context data
- `assets/` — local visual assets


## Airport place cards / Yelp enrichment

The passenger server now proxies the canonical place feed from the Beluga Airport Ingestion service:

```text
GET /api/passenger/airports/{CODE}/places/{category}
```

The default ingestion service is `http://127.0.0.1:8787` and can be changed with `BELUGA_INGESTION_BASE_URL`.

Beluga's ingestion architecture remains the authority for airport inventory and physical location. Yelp is never called from the browser and never creates a restaurant, lounge, shop or other airport entity. It only enriches an already-known canonical place with consumer metadata such as rating, review count, price, highlights, image and profile URL.

The passenger composer receives a bounded snapshot of Dining, Lounges and Retail from the same normalized feed. The Airport Hub uses the same endpoint and falls back to its existing demo catalog if the ingestion service is offline. Existing prototype pickup menus remain orderable only for the restaurants already supported by Beluga's demo order flow.
