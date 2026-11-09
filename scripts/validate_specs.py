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
    schedule = read("schedule_tw.json")
    history = read("history_coverage_tw.json")
    assert schedule["adr"] == "ADR-005" and schedule["decision"] == "ACCEPTED"
    assert schedule["timezone"] == "Asia/Taipei"
    assert schedule["analysis_frequency"] == "DAILY"
    assert schedule["basis"] == "PROPOSED_POLL_SCHEDULE_NOT_EXCHANGE_SLA"
    assert schedule["intraday_trading_enabled"] is False
    times = [p["time"] for p in schedule["polls"]]
    assert times == sorted(set(times)), "poll times must be unique and sorted"
    assert {"07:30", "08:00", "13:50", "15:30", "20:30", "23:00"} <= set(times)
    assert schedule["critical_data_policy"] == "FAIL_CLOSED"
    assert schedule["unknown_publication_time"] == "NULL_AND_PIT_UNVERIFIED"
    assert schedule["reconcile_after_trading_days"] == [1, 2, 5, 20]
    assert {"PENDING", "PARTIAL", "READY", "STALE", "CORRECTED", "RESTRICTED", "UNAVAILABLE"} <= set(schedule["data_states"])
    assert history["adr"] == "ADR-006" and history["decision"] == "ACCEPTED"
    assert history["target_years"] == 10
    assert history["target_end_is_verified_completed_bar"] is False
    assert history["actual_latest_completed_trade_date"] is None
    assert (history["target_start"], history["target_end"]) == ("2016-11-09", "2026-11-09")
    assert len(history["instruments"]) == 10
    assert len(history["signals"]) == 14
    assert {x["symbol"] for x in history["instruments"]} == {x["symbol"] for x in instruments}
    assert {x["id"] for x in history["signals"]} == {x["id"] for x in signals}
    assert sum(x["ten_year_listing_eligible"] for x in history["instruments"]) == 7
    assert all(x["ten_year_listing_eligible"] == (x["listed_at"] <= history["target_start"]) for x in history["instruments"])
    assert all(x["actual_earliest_authorized_row"] is None and not x["pit_verified"] for x in history["instruments"] + history["signals"])
    assert not history["data_access_certified"] and not history["license_approved"] and not history["point_in_time_certified"]
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
        "docs/adr/ADR-005-daily-refresh.md",
        "docs/adr/ADR-006-ten-year-history.md",
        "docs/data/data-source-matrix.md",
        "docs/requirements/open-decisions.md",
    ]:
        assert (ROOT / path).is_file(), f"missing specification: {path}"
    print("PASS: R04 10+14 catalogs; R05 schedule; R06 10y listing/coverage contract; ADRs")
    print("NOT TESTED: actual ten-year vendor rows, license rights, PIT vintages, ARM64, headless recovery, live APIs")

if __name__ == "__main__":
    validate()
