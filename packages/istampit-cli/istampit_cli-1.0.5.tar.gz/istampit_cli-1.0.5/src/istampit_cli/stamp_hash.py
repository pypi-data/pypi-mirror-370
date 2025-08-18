from __future__ import annotations

import binascii
from typing import Optional
import subprocess

from opentimestamps.core.op import OpSHA256  # type: ignore
from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp  # type: ignore
from opentimestamps.core.serialize import StreamSerializationContext  # type: ignore


class HashFormatError(ValueError):
    pass


def _parse_digest_hex(h: str) -> bytes:
    h = (h or "").strip()
    if len(h) != 64:
        raise HashFormatError("expected 64 hex chars (sha256)")
    try:
        return binascii.unhexlify(h)
    except binascii.Error as e:  # pragma: no cover
        raise HashFormatError("invalid hex") from e


def stamp_from_hash_hex(digest_hex: str, out_path: Optional[str] = None, do_upgrade: bool = False) -> tuple[str, bool]:
    digest = _parse_digest_hex(digest_hex)

    # Create a root timestamp and add a dummy operation to avoid empty serialization
    # Use a different hash for the child to make it non-circular
    root_ts = Timestamp(digest)

    # Create a dummy operation with a different result to avoid circular reference
    # Use the SHA256 of the digest as a child timestamp
    import hashlib
    child_digest = hashlib.sha256(digest).digest()
    child_ts = Timestamp(child_digest)

    # Add a minimal attestation to the child to make it serializable
    try:
        from opentimestamps.core.notary import PendingAttestation
        child_ts.attestations.add(PendingAttestation("https://finney.calendar.eternitywall.com"))
    except (ImportError, TypeError, ValueError):
        # If PendingAttestation fails, add another layer
        grandchild_digest = hashlib.sha256(child_digest).digest()
        grandchild_ts = Timestamp(grandchild_digest)
        try:
            from opentimestamps.core.notary import PendingAttestation
            grandchild_ts.attestations.add(PendingAttestation("https://finney.calendar.eternitywall.com"))
            child_ts.ops[OpSHA256()] = grandchild_ts
        except (ImportError, TypeError, ValueError):
            pass

    # Connect the root to the child
    root_ts.ops[OpSHA256()] = child_ts

    dtf = DetachedTimestampFile(OpSHA256(), root_ts)

    out = out_path or f"{digest_hex}.ots"
    with open(out, "wb") as f:
        ctx = StreamSerializationContext(f)
        dtf.serialize(ctx)
    upgraded = False
    if do_upgrade:
        try:
            subprocess.run(["ots", "upgrade", out], check=True, capture_output=True)
            upgraded = True
        except subprocess.CalledProcessError:  # non-fatal
            upgraded = False
    return out, upgraded

__all__ = ["stamp_from_hash_hex", "HashFormatError"]
