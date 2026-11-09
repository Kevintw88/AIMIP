#!/usr/bin/env python3
"""Validate *static specifications only*: no network, no paid API, no runtime claims."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(name: str):
    return json.loads((ROOT / "specs" / name).read_text(encoding="utf-8"))

def validate():
    instruments = read("instruments.json")
    signals = read("signals.json")
    assert len(instruments) == 10, "R04 must have exactly 10 research instruments"
    assert len(signals) == 14, "R04 must have exactly 14 signal categories"
    assert len({x["id"] for x in instruments}) == len(instruments)
    assert len({x["symbol"] for x in instruments}) == len(instruments)
    assert len({x["id"] for x in signals}) == len(signals)
    assert all(x["market"] == "TW" for x in instruments + signals)
    assert all(x["license_status"] == "PENDING" for x in instruments + signals)
    assert all(x["metadata_verified"] is False for x in instruments)
    assert all(x["dataset_verified"] is False for x in signals)
    assert set(x["priority"] for x in instruments) <= {"P0", "P1"}
    assert {x["symbol"] for x in instruments} == {
        "0050", "006208", "00631L", "00685L", "00632R",
        "00406A", "00878", "2330", "2317", "2454"
    }
    for path in [
        "AGENTS.md",
        "docs/adr/ADR-001-personal-use.md",
        "docs/adr/ADR-002-mac-mini-headless.md",
        "docs/adr/ADR-003-market-order.md",
        "docs/adr/ADR-003A-openbb-conditional.md",
        "docs/adr/ADR-004-balanced-universe.md",
        "docs/data/data-source-matrix.md",
        "docs/requirements/open-decisions.md",
    ]:
        assert (ROOT / path).is_file(), f"missing specification: {path}"
    print("PASS: R04 static catalog 10 instruments / 14 signals; ADR files present")
    print("NOT TESTED: licenses, exchange metadata, ARM64, headless recovery, live APIs")

if __name__ == "__main__":
    validate()
