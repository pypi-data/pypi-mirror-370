import json
from datetime import datetime, timezone
from typing import Optional


def write_manifest(
    out_path: str,
    wm_id: str,
    mode: str,
    comment_prefix: str,
    meta: dict,
    manifest_path: Optional[str] = None
):
    """Writes a manifest file with watermark metadata."""
    manifest = {
        "id": wm_id,
        "mode": mode,
        "comment_prefix": comment_prefix,
        "embedded_at": datetime.now(timezone.utc).isoformat(),
        "metadata": meta
    }
    path = manifest_path or out_path + ".embedid.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def read_manifest(path: str) -> dict:
    """Reads and returns a manifest dictionary from file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_manifest(manifest: dict) -> bool:
    """Validates manifest structure for required fields."""
    required_keys = {"id", "mode", "comment_prefix", "embedded_at", "metadata"}
    return required_keys.issubset(manifest.keys())