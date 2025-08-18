# iStampit CLI — Blockchain Timestamp Verification (OpenTimestamps)

<!-- badges: start -->
[![PyPI](https://img.shields.io/pypi/v/istampit-cli)](https://pypi.org/project/istampit-cli/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/istampit-cli)](https://pypi.org/project/istampit-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Publish to PyPI](https://github.com/SinAi-Inc/istampit-cli/actions/workflows/publish.yml/badge.svg)](https://github.com/SinAi-Inc/istampit-cli/actions/workflows/publish.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/SinAi-Inc/istampit-cli/badge)](https://securityscorecards.dev/viewer/?uri=github.com/SinAi-Inc/istampit-cli)
<!-- badges: end -->

Lightweight CLI around the official [OpenTimestamps](https://opentimestamps.org) client to **stamp, verify, upgrade, and inspect** cryptographic timestamp proofs (".ots" receipts) for your files — privacy‑first, Bitcoin‑anchored proof‑of‑existence.

---

## ✨ Features

* ✅ Free & open‑source (MIT wrapper, underlying libs LGPL-3.0)
* ✅ Privacy‑first — only hashes leave your machine
* ✅ Trustless & permanent — proofs anchor into Bitcoin
* ✅ Works offline — create receipts without network
* ✅ `--json` output for automation & CI

---

## 📦 Install

```bash
pip install istampit-cli
# or for isolated usage:
pipx install istampit-cli
```

---

## 🚀 Usage

```bash
# Create a timestamp receipt
istampit stamp path/to/file.pdf          # → creates file.pdf.ots

# Verify a receipt
istampit verify path/to/file.pdf.ots     # checks proof against Bitcoin

# Upgrade a receipt (fetch newer attestations)
istampit upgrade path/to/file.pdf.ots    # rewrites upgraded proof

# Inspect a receipt
istampit info path/to/file.pdf.ots       # shows operations/attestations

# Stamp a precomputed SHA-256 digest (detached, no file upload)
istampit stamp --hash 05c4f616a8e5310d19d938cfd769864d7f4ccdc2ca8b479b10af83564b097af9 \
	--out 05c4f616a8e5310d19d938cfd769864d7f4ccdc2ca8b479b10af83564b097af9.ots
```

Add `--json` to any command for machine‑readable output.

### JSON output (hash mode)

When using `--json` with `stamp --hash` the tool prints:

```json
{
	"receipts": ["<output-path>"],
	"hash": "<sha256-hex>",
	"upgraded": true | false
}
```

`upgraded` is `true` only if `--upgrade` was requested and at least one calendar attestation was successfully applied immediately.

---

## 🔢 Exit Codes

* `0` → success
* non‑zero → failure (error message on stderr)

---

## 📚 Resources

* 🌐 Website: <https://iStampit.io>
* 🧾 Public Ledger: <https://iStampit.io/ledger>
* 🐙 Source / Issues: <https://github.com/SinAi-Inc/istampit-cli>

---

## 📜 License

* Wrapper code: MIT
* OpenTimestamps libraries: LGPL-3.0

---

**Provable Innovation, Free for Everyone.**
Empowering developers, researchers, and creators with simple, reliable, and verifiable timestamp proofs.
