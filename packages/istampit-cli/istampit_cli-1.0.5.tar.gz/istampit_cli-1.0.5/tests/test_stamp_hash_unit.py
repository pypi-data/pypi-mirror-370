from pathlib import Path
from istampit_cli.stamp_hash import stamp_from_hash_hex

def test_stamp_from_hash_hex_writes_non_empty_file(tmp_path: Path):
    # Known 64-char SHA-256 hex
    digest = "05c4f616a8e5310d19d938cfd769864d7f4ccdc2ca8b479b10af83564b097af9"
    out_path = tmp_path / f"{digest}.ots"
    out, upgraded = stamp_from_hash_hex(digest, str(out_path), do_upgrade=False)
    assert Path(out).exists(), "Receipt file was not created"
    size = Path(out).stat().st_size
    assert size > 0, f"Receipt file is empty (size={size})"
    assert upgraded is False
