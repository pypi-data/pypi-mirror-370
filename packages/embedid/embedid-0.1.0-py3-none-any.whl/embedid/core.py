import base64
import hashlib
import json
import os
from typing import Optional, Tuple


def scramble_metadata(meta: dict, salt: Optional[bytes] = None) -> Tuple[str, str]:
    """Scrambles metadata into a salted, encoded watermark string."""
    raw = json.dumps(meta, separators=(",", ":")).encode("utf-8")
    salt = salt or os.urandom(8)
    salted = salt + raw
    digest = hashlib.sha256(salted).digest()
    wm_id = base64.urlsafe_b64encode(digest[:12]).decode("utf-8").rstrip("=")
    encoded = base64.urlsafe_b64encode(salted).decode("utf-8").rstrip("=")
    return wm_id, encoded


def descramble_metadata(encoded: str) -> dict:
    """Decodes watermark string back into metadata dictionary."""
    padded = encoded + "=" * (-len(encoded) % 4)
    raw = base64.urlsafe_b64decode(padded)
    return json.loads(raw[8:].decode("utf-8"))


def embed_watermark(file_path: str, encoded: str, comment_prefix: str, allow_multiple: bool = False) -> bool:
    """Embeds watermark into file. Rejects if one exists unless allow_multiple=True."""
    try:
        with open(file_path, "r+", encoding="utf-8") as f:
            lines = f.readlines()
            marker = f"{comment_prefix} EmbedID: {encoded}\n"
            if not allow_multiple and any("EmbedID:" in line for line in lines):
                return False
            f.seek(0)
            f.write(marker)
            f.writelines(lines)
        return True
    except Exception:
        return False


def extract_watermark(file_path: str, comment_prefix: str) -> Optional[str]:
    """Extracts the first watermark from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(comment_prefix) and "EmbedID:" in line:
                    return line.strip().split("EmbedID:")[1].strip()
    except Exception:
        pass
    return None


def remove_watermark(file_path: str, comment_prefix: str) -> bool:
    """Removes all watermark lines from a file."""
    try:
        with open(file_path, "r+", encoding="utf-8") as f:
            lines = [line for line in f if "EmbedID:" not in line]
            f.seek(0)
            f.truncate()
            f.writelines(lines)
        return True
    except Exception:
        return False


def get_watermark_id(file_path: str, comment_prefix: str) -> Optional[str]:
    """Returns the watermark ID from a file, if present."""
    encoded = extract_watermark(file_path, comment_prefix)
    if not encoded:
        return None
    try:
        padded = encoded + "=" * (-len(encoded) % 4)
        salted_data = base64.urlsafe_b64decode(padded)
        digest = hashlib.sha256(salted_data).digest()
        return base64.urlsafe_b64encode(digest[:12]).decode("utf-8").rstrip("=")
    except Exception:
        return None