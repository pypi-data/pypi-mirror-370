from __future__ import annotations

import argparse
import importlib.metadata
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_ERR = 1

OTS_CMD = shutil.which("ots")  # if None we'll fallback to python -m invocation

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def run_ots(*args: str) -> subprocess.CompletedProcess:
    """Run ots CLI; if not installed, fallback to python -m opentimestamps.client.cmd."""
    base_cmd: list[str]
    if OTS_CMD:
        base_cmd = [OTS_CMD]
    else:
        # Fallback: python -m opentimestamps.client.cmd <args>
        base_cmd = [sys.executable, "-m", "opentimestamps.client.cmd"]
    try:
        return subprocess.run([*base_cmd, *args], check=True, capture_output=True, text=True)
    except (FileNotFoundError, ModuleNotFoundError):
        print(
            "error: OpenTimestamps client not available; install opentimestamps-client",
            file=sys.stderr,
        )
        sys.exit(EXIT_ERR)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip() or e.stdout.strip() or str(e)) from e

def cmd_stamp_paths(paths: list[str], json_out: bool):
    receipts: list[str] = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"warn: missing {p}", file=sys.stderr)
            continue
        try:
            run_ots("stamp", str(path))
            receipts.append(str(path) + ".ots")
        except (RuntimeError, OSError, ValueError) as e:
            print(f"error stamping {p}: {e}", file=sys.stderr)
    if json_out:
        print(json.dumps({"receipts": receipts}, indent=2))


def cmd_stamp_hash(digest_hex: str, out_path: str | None, json_out: bool, do_upgrade: bool = False):
    """Stamp a precomputed SHA-256 digest (detached mode).

    Produces a receipt whose commitment matches the provided digest, allowing
    later verification against the original file whose sha256 equals digest_hex.
    """
    from .stamp_hash import stamp_from_hash_hex, HashFormatError  # local import to avoid import cost if unused

    try:
        receipt_path, upgraded = stamp_from_hash_hex(digest_hex, out_path, do_upgrade)
    except HashFormatError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERR)
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERR)
    if json_out:
        print(json.dumps({"receipts": [receipt_path], "hash": digest_hex, "upgraded": upgraded}, indent=2))
    else:
        print(receipt_path)

def _parse_bitcoin_attestation(text: str):
    # Heuristic: look for 'Bitcoin block <height>' pattern.
    m = re.search(r'Bitcoin block (\d+)', text, re.IGNORECASE)
    if not m:
        return None
    height = int(m.group(1))
    # Try to parse a unix timestamp (10-digit epoch >=1600000000) in same or following line
    tm = re.search(
        r'(?:^|\D)(1[6-9]\d{8}|2\d{9})(?:\D|$)',
        text,
    )  # 10-digit timestamp 1600000000+
    block_time = int(tm.group(1)) if tm else None
    return {"blockHeight": height, "blockTime": block_time}

def cmd_verify(receipt: str, json_out: bool):
    try:
        cp = run_ots("verify", receipt)
        out = cp.stdout.strip()
        bitcoin = _parse_bitcoin_attestation(out)
        status = "confirmed" if bitcoin else "pending"
        calendars = []
        if status == "pending":
            try:
                info_cp = run_ots("info", receipt)
                lines = info_cp.stdout.splitlines()
                calendars = [
                    ln.split(maxsplit=1)[1]
                    for ln in lines
                    if ln.lower().startswith("calendar ")
                ]
            except (RuntimeError, OSError, ValueError):
                pass
        if json_out:
            print(json.dumps({
                "status": status,
                "bitcoin": bitcoin,
                "calendars": calendars,
                "detail": out
            }, indent=2))
        else:
            print(out)
    except (RuntimeError, OSError, ValueError) as e:
        # Treat incomplete / pending timestamps as a non-fatal pending status.
        msg = str(e)
        lower = msg.lower()
        if "not complete" in lower or "pending" in lower:
            status = "pending"
            bitcoin = None
            calendars: list[str] = []
            try:
                info_cp = run_ots("info", receipt)
                lines = info_cp.stdout.splitlines()
                calendars = [
                    ln.split(maxsplit=1)[1]
                    for ln in lines
                    if ln.lower().startswith("calendar ")
                ]
            except (RuntimeError, OSError, ValueError):
                pass
            if json_out:
                print(json.dumps({
                    "status": status,
                    "bitcoin": bitcoin,
                    "calendars": calendars,
                    "detail": msg
                }, indent=2))
            else:
                print(msg)
            return
        if json_out:
            print(json.dumps({"status": "error", "error": msg}))
        else:
            print(f"error: {msg}", file=sys.stderr)
        sys.exit(EXIT_ERR)

def cmd_upgrade(receipt: str, json_out: bool):
    try:
        cp = run_ots("upgrade", receipt)
        out = cp.stdout.strip()
        # After upgrade attempt, re-verify for status
        try:
            v_cp = run_ots("verify", receipt)
            v_out = v_cp.stdout.strip()
            bitcoin = _parse_bitcoin_attestation(v_out)
            status = "confirmed" if bitcoin else "pending"
        except (RuntimeError, OSError, ValueError):
            bitcoin = None
            status = "unknown"
        if json_out:
            print(
                json.dumps(
                    {
                        "upgraded": True,
                        "status": status,
                        "bitcoin": bitcoin,
                        "detail": out,
                    },
                    indent=2,
                )
            )
        else:
            print(out)
    except (RuntimeError, OSError, ValueError) as e:
        if json_out:
            print(json.dumps({"upgraded": False, "error": str(e)}))
        else:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERR)

def cmd_upgrade_all(root: str, json_out: bool):
    root_path = Path(root)
    if not root_path.exists():
        print(f"error: {root} not found", file=sys.stderr)
        sys.exit(EXIT_ERR)
    receipts = list(root_path.rglob("*.ots")) if root_path.is_dir() else [root_path]
    results = []
    for r in receipts:
        try:
            run_ots("upgrade", str(r))
            v_cp = run_ots("verify", str(r))
            v_out = v_cp.stdout.strip()
            bitcoin = _parse_bitcoin_attestation(v_out)
            status = "confirmed" if bitcoin else "pending"
            results.append({"receipt": str(r), "status": status, "bitcoin": bitcoin})
        except (RuntimeError, OSError, ValueError) as e:
            results.append({"receipt": str(r), "status": "error", "error": str(e)})
    if json_out:
        print(json.dumps({"results": results}, indent=2))
    else:
        for r in results:
            line = f"{r['receipt']}: {r['status']}"
            if r.get('bitcoin'):
                line += f" (block {r['bitcoin']['blockHeight']})"
            if r.get('error'):
                line += f" error={r['error']}"
            print(line)

def cmd_info(receipt: str, json_out: bool):
    try:
        cp = run_ots("info", receipt)
        out = cp.stdout.strip()
        if json_out:
            lines = out.splitlines()
            calendars = [
                ln.split(maxsplit=1)[1]
                for ln in lines
                if ln.lower().startswith("calendar ")
            ]
            print(json.dumps({"raw": out, "calendars": calendars}, indent=2))
        else:
            print(out)
    except (RuntimeError, OSError, ValueError) as e:
        if json_out:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERR)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="istampit",
        description="iStampit CLI – Proof-of-Existence with OpenTimestamps",
    )
    p.add_argument("--json", action="store_true", dest="json_out", help="JSON output")
    p.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {importlib.metadata.version('istampit-cli')}",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("stamp", help="Stamp file(s) OR a precomputed SHA-256 digest to create .ots receipts")
    # Mutually exclusive: either positional file paths OR --hash
    sp.add_argument("paths", nargs="*", help="File paths to stamp")
    mx = sp.add_mutually_exclusive_group()
    mx.add_argument("--hash", dest="digest_hex", help="SHA-256 hex digest to stamp (detached)")
    sp.add_argument("--out", dest="out", help="Output .ots path when using --hash (defaults to <hash>.ots)")
    sp.add_argument("--upgrade", action="store_true", dest="upgrade", help="Attempt immediate upgrade (calendar attestations) after stamping")
    sp.add_argument("--json", action="store_true", dest="json_out", help="JSON output")

    sp = sub.add_parser("verify", help="Verify a .ots receipt")
    sp.add_argument("receipt", help="Receipt file (.ots)")
    sp.add_argument("--json", action="store_true", dest="json_out", help="JSON output")

    sp = sub.add_parser("upgrade", help="Upgrade a .ots receipt (fetch attestations)")
    sp.add_argument("receipt", help="Receipt file (.ots)")
    sp.add_argument("--json", action="store_true", dest="json_out", help="JSON output")

    sp = sub.add_parser("info", help="Show receipt operations/attestations")
    sp.add_argument("receipt", help="Receipt file (.ots)")
    sp.add_argument("--json", action="store_true", dest="json_out", help="JSON output")

    sp = sub.add_parser(
        "upgrade-all", help="Upgrade all .ots receipts under a directory (recursive)"
    )
    sp.add_argument("root", help="Directory to scan (or a single .ots file)")
    sp.add_argument("--json", action="store_true", dest="json_out", help="JSON output")

    return p

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # json_out may be provided either globally or per-subcommand; already unified in args.json_out
    if args.cmd == "stamp":
        # Hash mode
        if getattr(args, "digest_hex", None):
            if args.paths:
                print("error: --hash cannot be combined with file paths", file=sys.stderr)
                return EXIT_ERR
            cmd_stamp_hash(args.digest_hex, args.out, args.json_out, getattr(args, "upgrade", False))
            return EXIT_OK
        if not args.paths:
            print("error: provide at least one file path OR --hash <digest>", file=sys.stderr)
            return EXIT_ERR
        cmd_stamp_paths(args.paths, args.json_out)
        return EXIT_OK
    if args.cmd == "verify":
        cmd_verify(args.receipt, args.json_out)
        return EXIT_OK
    if args.cmd == "upgrade":
        cmd_upgrade(args.receipt, args.json_out)
        return EXIT_OK
    if args.cmd == "info":
        cmd_info(args.receipt, args.json_out)
        return EXIT_OK
    if args.cmd == "upgrade-all":
        cmd_upgrade_all(args.root, args.json_out)
        return EXIT_OK
    return EXIT_ERR

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
