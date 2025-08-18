import os, subprocess, shutil, sys, pytest

OTS = shutil.which("ots")
DIGEST = "05c4f616a8e5310d19d938cfd769864d7f4ccdc2ca8b479b10af83564b097af9"

@pytest.mark.skipif(OTS is None, reason="ots client not installed in test environment")
def test_stamp_hash_creates_receipt(tmp_path):
    out = tmp_path / f"{DIGEST}.ots"
    proc = subprocess.run([
        sys.executable, "-m", "istampit_cli.__main__", "stamp", "--hash", DIGEST, "--out", str(out), "--json"
    ], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert out.exists() and out.stat().st_size > 0

@pytest.mark.parametrize("bad", ["", "zz", "abcd", "0"*63, "0"*65])
def test_stamp_hash_rejects_invalid(bad, tmp_path):
    proc = subprocess.run([
        sys.executable, "-m", "istampit_cli.__main__", "stamp", "--hash", bad
    ], capture_output=True, text=True)
    assert proc.returncode != 0
