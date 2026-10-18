#!/usr/bin/env python3
"""Publish an approved airport snapshot into a running Beluga passenger backend.

Example:
  BELUGA_INGESTION_PUBLISH_KEY=... python3 tools/publish_airport.py \
    approved-IAD.json --image /path/to/dulles-header.png --url http://127.0.0.1:8790
The source ingestion admin must export a QA-passed snapshot with original-page evidence.
"""
import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="QA-approved passenger snapshot JSON")
    parser.add_argument("--image", type=Path, help="Optional image selected in ingestion admin")
    parser.add_argument("--url", default="http://127.0.0.1:8790", help="Beluga passenger API URL")
    args = parser.parse_args()
    token = os.environ.get("BELUGA_INGESTION_PUBLISH_KEY")
    if not token:
        parser.error("Set BELUGA_INGESTION_PUBLISH_KEY in the publisher environment.")
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.image:
        mime = mimetypes.guess_type(args.image.name)[0]
        if mime not in ("image/png", "image/jpeg", "image/webp"):
            parser.error("Image must be PNG, JPEG or WebP.")
        data = args.image.read_bytes()
        if len(data) > 2_500_000:
            parser.error("Image cannot exceed 2.5 MB.")
        payload["header_image"] = {"mime_type": mime, "data_base64": base64.b64encode(data).decode("ascii")}
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        args.url.rstrip("/") + "/api/ingestion/publish",
        data=raw,
        method="POST",
        headers={"Content-Type": "application/json", "X-Beluga-Publish-Key": token},
    )
    try:
        with urlopen(req, timeout=25) as response:
            result = json.loads(response.read())
    except HTTPError as exc:
        print("Publication rejected:", exc.code, exc.read().decode("utf-8", errors="replace"))
        raise SystemExit(1)
    except URLError as exc:
        print("Cannot connect to passenger backend:", exc.reason)
        raise SystemExit(1)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
