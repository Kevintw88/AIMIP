"""PH0-S01 的固定種子識別碼與十年資格契約。"""

import unittest

from scripts.validate_specs import read


class CatalogTests(unittest.TestCase):
    def test_stable_instrument_and_signal_ids(self):
        instruments = read("instruments.json")
        signals = read("signals.json")
        self.assertCountEqual(
            [(row["id"], row["symbol"]) for row in instruments],
            [
                ("TW-ETF-0050", "0050"), ("TW-ETF-006208", "006208"),
                ("TW-ETF-00631L", "00631L"), ("TW-ETF-00685L", "00685L"),
                ("TW-ETF-00632R", "00632R"), ("TW-ETF-00406A", "00406A"),
                ("TW-ETF-00878", "00878"), ("TW-EQ-2330", "2330"),
                ("TW-EQ-2317", "2317"), ("TW-EQ-2454", "2454"),
            ],
        )
        self.assertCountEqual(
            [row["id"] for row in signals],
            [
                "TAIEX", "TAIWAN50", "TPEX_INDEX", "CASH_TURNOVER", "MARKET_BREADTH",
                "MARGIN_FINANCING", "MARGIN_SHORT", "INSTITUTIONAL_CASH", "TAIEX_FUTURES",
                "FOREIGN_FUTURES_POSITION", "OPTIONS_VOLUME_PCR", "OPTIONS_OI_PCR",
                "ETF_UNITS_FLOW", "ETF_NAV_PREMIUM",
            ],
        )
        self.assertTrue(all(row["license_status"] == "PENDING" for row in instruments + signals))

    def test_listing_eligibility_does_not_certify_coverage_or_rights(self):
        history = read("history_coverage_tw.json")
        instruments = history["instruments"]
        self.assertEqual(sum(row["ten_year_listing_eligible"] for row in instruments), 7)
        self.assertCountEqual(
            [row["symbol"] for row in instruments if not row["ten_year_listing_eligible"]],
            ["00685L", "00406A", "00878"],
        )
        self.assertFalse(history["license_approved"])
        self.assertFalse(history["data_access_certified"])
        self.assertFalse(history["point_in_time_certified"])
        for row in instruments + history["signals"]:
            self.assertIsNone(row["actual_earliest_authorized_row"])
            self.assertIs(row["pit_verified"], False)
