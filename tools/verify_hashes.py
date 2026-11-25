"""Fail the build when a frozen input differs from its recorded SHA256.

Record once with `python tools/verify_hashes.py --record`, commit the lock file,
and let continuous integration compare every later run against it.

Author: Armin Kajevic
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

FILES = [
    "protocol/p01_protocol.yaml",
    "protocol/p01_protocol.tsr",
    "data/panel/p01_registrations_panel.csv",
    "data/raw/destatis_pkw_neuzulassungen_jahre.csv",
    "data/reference/geo/ne_110m_countries.geojson",
    "lean_p01/ProtocolCausal.lean",
]
LOCK = Path("hashes.lock.json")


def digest(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main() -> int:
    if "--record" in sys.argv:
        LOCK.write_text(json.dumps({f: digest(f) for f in FILES}, indent=2) + "\n")
        print("recorded", len(FILES), "files")
        return 0
    if not LOCK.exists():
        print("no lock file, nothing to verify")
        return 0
    recorded = json.loads(LOCK.read_text())
    bad = [f for f, value in recorded.items() if digest(f) != value]
    if bad:
        print("HASH MISMATCH:", ", ".join(bad))
        return 1
    print("all", len(recorded), "hashes verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
