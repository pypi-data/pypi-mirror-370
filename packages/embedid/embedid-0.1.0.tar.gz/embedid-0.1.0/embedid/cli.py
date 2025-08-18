import argparse
import base64
import hashlib
import json
import subprocess
import os
from functools import wraps
from datetime import datetime, timezone

from embedid.core import (
    descramble_metadata,
    embed_watermark,
    extract_watermark,
    remove_watermark,
    scramble_metadata,
    get_watermark_id,
)
from embedid.manifest import (
    write_manifest,
    read_manifest,
    validate_manifest,
)

def check_file_exists(func):
    """Decorator that checks if the file from args exists before running the handler."""
    @wraps(func)
    def wrapper(args):
        if not os.path.exists(args.file):
            print(f"[ERROR] File not found: {args.file}")
            return
        return func(args)
    return wrapper

@check_file_exists
def handle_add(args):
    meta = {
        "author": args.author,
        "tool": args.tool,
        "remix_of": args.remix_of,
        "agent": args.agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    meta = {k: v for k, v in meta.items() if v is not None}

    wm_id, encoded = scramble_metadata(meta)
    success = embed_watermark(args.file, encoded, args.comment_prefix)
    if success:
        print(f"[+] Watermark embedded: id={wm_id}")
        write_manifest(args.file, wm_id, "add", args.comment_prefix, meta)
    else:
        print("[!] Watermark already exists or failed to embed.")


@check_file_exists
def handle_verify(args):
    encoded = extract_watermark(args.file, args.comment_prefix)
    if not encoded:
        print("[!] No watermark found.")
        return
    try:
        meta = descramble_metadata(encoded)
        wm_id = get_watermark_id(args.file, args.comment_prefix)
        if args.json:
            print(json.dumps({"id": wm_id, **meta}, indent=2))
        else:
            print(f"[OK] Verified EmbedID: id={wm_id}")
            if args.verbose:
                for k, v in meta.items():
                    print(f"  {k}: {v}")
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")


def handle_test(args):
    print("[-] Running unit tests...")
    cmd = ["pytest", "tests/"]
    if args.fail_fast:
        cmd.append("-x")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("[!] Tests failed.")
        print(result.stderr)
    else:
        print("[+] All tests passed.")


@check_file_exists
def handle_remove(args):
    success = remove_watermark(args.file, args.comment_prefix)
    if success:
        print("[+] Watermark removed.")
    else:
        print("[!] Failed to remove watermark.")


@check_file_exists
def handle_id(args):
    wm_id = get_watermark_id(args.file, args.comment_prefix)
    if wm_id:
        print(f"[ID] {wm_id}")
    else:
        print("[!] No watermark ID found.")


def handle_inspect(args):
    try:
        manifest = read_manifest(args.path)
        if not manifest:
            print(f"[ERROR] Manifest not found or is empty: {args.path}")
            return
        print(json.dumps(manifest, indent=2))
    except Exception as e:
        print(f"[ERROR] Failed to read manifest: {e}")


def handle_validate(args):
    try:
        manifest = read_manifest(args.path)
        if not manifest:
            print(f"[ERROR] Manifest not found or is empty: {args.path}")
            return
        if validate_manifest(manifest):
            print("[+] Manifest is valid.")
        else:
            print("[!] Manifest is missing required fields.")
    except Exception as e:
        print(f"[ERROR] Failed to validate manifest: {e}")


def main():
    parser = argparse.ArgumentParser(description="EmbedID Free Edition")
    parser.add_argument("--version", action="version", version="EmbedID 0.1.0")
    subp = parser.add_subparsers(dest="command", required=True, help="Available commands")

    addp = subp.add_parser("add", help="Embed watermark into a file")
    addp.add_argument("file", help="Target file path")
    addp.add_argument("--author", required=True)
    addp.add_argument("--tool", default="EmbedID")
    addp.add_argument("--remix-of")
    addp.add_argument("--agent")
    addp.add_argument("--comment-prefix", default="#")
    addp.set_defaults(func=handle_add)

    verifyp = subp.add_parser("verify", help="Verify and extract watermark from a file")
    verifyp.add_argument("file")
    verifyp.add_argument("--comment-prefix", default="#")
    verifyp.add_argument("--verbose", action="store_true")
    verifyp.add_argument("--json", action="store_true")
    verifyp.set_defaults(func=handle_verify)

    testp = subp.add_parser("test", help="Run unit tests")
    testp.add_argument("--fail-fast", action="store_true")
    testp.set_defaults(func=handle_test)

    removep = subp.add_parser("remove", help="Erase watermark from a file")
    removep.add_argument("file")
    removep.add_argument("--comment-prefix", default="#")
    removep.set_defaults(func=handle_remove)

    idp = subp.add_parser("id", help="Extract watermark ID from a file")
    idp.add_argument("file")
    idp.add_argument("--comment-prefix", default="#")
    idp.set_defaults(func=handle_id)

    inspectp = subp.add_parser("inspect", help="View manifest contents")
    inspectp.add_argument("path", help="Path to .embedid.json file")
    inspectp.set_defaults(func=handle_inspect)

    validatep = subp.add_parser("validate", help="Validate manifest structure")
    validatep.add_argument("path", help="Path to .embedid.json file")
    validatep.set_defaults(func=handle_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()