"""Published airport-context bridge for the Beluga passenger API.

No ingestion database is read directly. A successful ingestion publish sends a
versioned, source-grounded snapshot to this service. The pre-existing composer,
flight booking, transport, and feedback routes remain independent.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import threading
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

AIRPORT_RE = re.compile(r"^[A-Z]{3}$")
STORE = Path(__file__).resolve().parent / ".beluga-cache" / "published-airports"
LOCK = threading.RLock()
MAX_IMAGE_BYTES = 2_500_000
MAX_EVIDENCE = 500
MAX_TEXT = 6000


class BridgeError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status
        self.message = message


def valid_airport(code: object) -> str:
    value = str(code or "").strip().upper()
    if not AIRPORT_RE.fullmatch(value):
        raise BridgeError("Airport must be an IATA code.", 400)
    return value


def _safe_https(url: object) -> str | None:
    if not isinstance(url, str) or len(url) > 1500:
        return None
    parsed = urlparse(url)
    return url if parsed.scheme == "https" and parsed.netloc and not parsed.username else None


def _clean_list(value: object, *, limit: int = 250) -> list[dict]:
    if not isinstance(value, list):
        return []
    output = []
    for row in value[:limit]:
        if not isinstance(row, dict):
            continue
        clean = {}
        for key in ("name", "title", "terminal", "concourse", "gate", "location",
                    "category", "description", "text", "hours", "checkpoint",
                    "code", "level", "offer", "expiration", "updated_at"):
            if isinstance(row.get(key), (str, int, float)):
                clean[key] = str(row[key])[:MAX_TEXT if key == "text" else 700]
        for key in ("source_url", "website", "map_url"):
            url = _safe_https(row.get(key))
            if url:
                clean[key] = url
        if clean:
            output.append(clean)
    return output


def _path(code: str) -> Path:
    return STORE / (valid_airport(code) + ".json")


def read_published(code: str) -> dict | None:
    path = _path(code)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except (OSError, ValueError, UnicodeError):
        return None


def published_codes() -> list[str]:
    if not STORE.is_dir():
        return []
    return sorted(p.stem for p in STORE.glob("???.json")
                  if AIRPORT_RE.fullmatch(p.stem) and read_published(p.stem))


def check_publish_authorization(received_key: str | None) -> None:
    expected = os.environ.get("BELUGA_INGESTION_PUBLISH_KEY", "")
    if not expected:
        raise BridgeError("Ingestion publishing is not configured.", 503)
    if not received_key or not hmac.compare_digest(received_key, expected):
        raise BridgeError("Unauthorized ingestion publish.", 403)


def publish(payload: dict) -> dict:
    """Accept only explicitly QA-approved published data; never ingest drafts."""
    if not isinstance(payload, dict):
        raise BridgeError("JSON object required.")
    code = valid_airport(payload.get("airport"))
    qa = payload.get("qa") or {}
    if (not isinstance(qa, dict) or qa.get("passed") is not True
            or not isinstance(qa.get("context_fingerprint"), str)
            or len(qa["context_fingerprint"]) < 12):
        raise BridgeError("Publication requires a passing QA check and fingerprint.", 409)
    revision = str(payload.get("revision") or "").strip()
    if not revision or len(revision) > 120:
        raise BridgeError("A versioned published revision is required.")
    if not isinstance(payload.get("evidence"), list):
        raise BridgeError("Original source evidence is required.", 409)
    image = payload.get("header_image")
    image_url = None
    image_bytes = None
    image_type = None
    if image is not None:
        if not isinstance(image, dict):
            raise BridgeError("Invalid header image.")
        if image.get("url"):
            image_url = _safe_https(image.get("url"))
            if not image_url:
                raise BridgeError("Header image URL must use HTTPS.")
        else:
            mime = image.get("mime_type")
            if mime not in ("image/png", "image/jpeg", "image/webp"):
                raise BridgeError("Only PNG, JPEG, or WebP header images are supported.")
            try:
                image_bytes = base64.b64decode(image.get("data_base64") or "", validate=True)
            except (ValueError, TypeError, base64.binascii.Error):
                raise BridgeError("Invalid base64 header image.") from None
            if not image_bytes or len(image_bytes) > MAX_IMAGE_BYTES:
                raise BridgeError("Header image must be under 2.5 MB.", 413)
            signatures = {
                "image/png": image_bytes.startswith(b"\x89PNG\r\n\x1a\n"),
                "image/jpeg": image_bytes.startswith(b"\xff\xd8\xff"),
                "image/webp": image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP",
            }
            if not signatures[mime]:
                raise BridgeError("Image content does not match MIME type.")
            image_type = mime
            fingerprint = hashlib.sha256(image_bytes).hexdigest()[:16]
            image_url = "/api/ingestion/image/" + code + "?v=" + fingerprint
    evidence = _clean_list(payload.get("evidence"), limit=MAX_EVIDENCE)
    # Original source passages MUST retain citations; semantic dossiers are only routing metadata.
    evidence = [e for e in evidence if e.get("text") and e.get("source_url")]
    snapshot = {
        "airport": code,
        "airport_name": str(payload.get("airport_name") or "")[:160],
        "revision": revision,
        "context_fingerprint": qa["context_fingerprint"],
        "published_at": str(payload.get("published_at") or "")[:80],
        "header_image_url": image_url,
        "header_image_mime": image_type,
        "concessions": _clean_list(payload.get("concessions")),
        "coupons": _clean_list(payload.get("coupons")),
        "checkpoints": _clean_list(payload.get("checkpoints")),
        "maps": _clean_list(payload.get("maps")),
        "gate_routes": _clean_list(payload.get("gate_routes"), limit=800),
        "facts": _clean_list(payload.get("facts"), limit=500),
        "evidence": evidence,
    }
    STORE.mkdir(parents=True, exist_ok=True)
    with LOCK:
        previous = read_published(code)
        if previous and previous.get("revision") == revision and previous != snapshot:
            raise BridgeError("Published revision is immutable. Increment revision after changing content.", 409)
        if image_bytes is not None:
            suffix = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}[image_type]
            file_path = STORE / (code + "." + suffix)
            temporary = STORE / (code + ".image.tmp")
            temporary.write_bytes(image_bytes)
            temporary.replace(file_path)
        temporary = STORE / (code + ".json.tmp")
        temporary.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
        temporary.replace(_path(code))
    return {"ok": True, "airport": code, "revision": revision,
            "context_fingerprint": qa["context_fingerprint"], "image": image_url,
            "evidence_count": len(evidence)}


def image_asset(code: str) -> tuple[bytes, str]:
    snapshot = read_published(code)
    if not snapshot or not snapshot.get("header_image_mime"):
        raise BridgeError("No published airport image.", 404)
    suffix = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}[snapshot["header_image_mime"]]
    try:
        return (STORE / (valid_airport(code) + "." + suffix)).read_bytes(), snapshot["header_image_mime"]
    except OSError:
        raise BridgeError("Published image is unavailable.", 404) from None


def public_profile(code: str) -> dict:
    snapshot = read_published(code)
    if not snapshot:
        raise BridgeError("Airport has no published ingestion context.", 404)
    return {k: v for k, v in snapshot.items() if k != "evidence" and k != "header_image_mime"}


def _retrieval_from_service(code: str, question: str, revision: str, limit: int) -> list[dict] | None:
    endpoint = os.getenv("BELUGA_INGESTION_RETRIEVE_URL", "").strip()
    if not endpoint:
        return None
    parsed = urlparse(endpoint)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    token = os.getenv("BELUGA_INGESTION_SERVICE_TOKEN", "")
    body = json.dumps({"airport": code, "question": question[:3000],
                       "published_revision": revision, "limit": limit}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request(endpoint, body, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=4) as response:
            data = response.read(350_000)
            raw = json.loads(data)
        # The ingestion semantic service returns ORIGINAL source passages, not generated dossiers.
        rows = raw.get("evidence") if isinstance(raw, dict) else None
        if not isinstance(rows, list):
            return None
        return [r for r in _clean_list(rows, limit=limit) if r.get("text") and r.get("source_url")]
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        return None


def retrieve(code: str, question: str, limit: int = 6) -> dict:
    code = valid_airport(code)
    snapshot = read_published(code)
    if not snapshot:
        return {"airport": code, "revision": None, "mode": "unavailable", "evidence": []}
    limit = max(1, min(int(limit), 12))
    live = _retrieval_from_service(code, question, snapshot["revision"], limit)
    if live is not None:
        return {"airport": code, "revision": snapshot["revision"], "mode": "semantic", "evidence": live}
    # Offline fallback: bounded lexical ranking over original published passages.
    # Does NOT misrepresent this as a semantic search or as live data.
    words = set(re.findall(r"[a-z0-9]{3,}", str(question).lower()))
    ranked = []
    for index, evidence in enumerate(snapshot.get("evidence") or []):
        text = evidence.get("text", "")
        terms = set(re.findall(r"[a-z0-9]{3,}", (text[:MAX_TEXT] + " " + evidence.get("title", "")).lower()))
        score = len(words.intersection(terms))
        if score:
            ranked.append((score, -index, evidence))
    ranked.sort(reverse=True)
    return {"airport": code, "revision": snapshot["revision"], "mode": "published-fallback",
            "evidence": [row for _, _, row in ranked[:limit]]}


def composer_context(code: str, question: str) -> tuple[dict | None, dict]:
    code = valid_airport(code)
    profile = read_published(code)
    return profile, retrieve(code, question)
