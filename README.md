# Beluga — V52.1

Beluga is a premium AI airport/travel assistant prototype.

## Current version
V52.1 — RouteStack hotel natural-language flow + restaurant logo correction.

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
