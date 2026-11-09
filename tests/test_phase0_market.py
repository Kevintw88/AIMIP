"""PH0-S02/S03。內嵌合成日曆、行情與事件，未下載任何資料。"""

import json
import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, date, datetime, time, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock, patch

from phase0a.data import (
    DatasetKey,
    LicenseDecision,
    LicenseRegistry,
    LicenseStatus,
    MockConnector,
    Observation,
    ObservationStore,
    Operation,
)
from phase0a.market import (
    CorporateAction,
    MarketSession,
    PollKey,
    PollState,
    Position,
    PriceBar,
    RetryAction,
    TradingCalendar,
    adjusted_close,
    paper_fill_at_next_open,
    poll_snapshot,
    position_after_actions,
    retry_advice,
)


TAIPEI_FIXTURE = timezone(timedelta(hours=8))
TRADE_DAY = date(2026, 1, 5)
HOLIDAY = date(2026, 1, 7)
DATASET = DatasetKey("mock:r05", "daily-close")
KEY = PollKey(DATASET, TRADE_DAY, "regular", sha256(b"synthetic close").hexdigest())
INSTRUMENTS = frozenset({"0050"})
SCHEDULE = Path(__file__).resolve().parents[1] / "specs" / "schedule_tw.json"


def taipei(day, hour, minute=0):
    return datetime.combine(day, time(hour, minute), TAIPEI_FIXTURE).astimezone(UTC)


def regular(day):
    return MarketSession(day, "regular", taipei(day, 9), taipei(day, 13, 30))


def cash_calendar():
    days = (TRADE_DAY + timedelta(days=i) for i in range(31))
    return TradingCalendar("TWSE_FIXTURE", tuple(regular(day) for day in days
                                                if day.weekday() < 5 and day != HOLIDAY))


def market_store(operations=None):
    if operations is None:
        operations = frozenset({Operation.DOWNLOAD, Operation.STORAGE, Operation.RETENTION, Operation.BACKTEST})
    decision = LicenseDecision(
        dataset=DATASET,
        decision_id="fixture-r05-only",
        status=LicenseStatus.APPROVED,
        allowed_operations=operations,
        checked_at=taipei(TRADE_DAY, 8),
        terms_reference="synthetic R05 unit fixture",
    )
    return ObservationStore(LicenseRegistry([decision]))


def row(released_at, revision="r1", value=100):
    return Observation(
        dataset=DATASET,
        instrument_id="0050",
        trade_date=TRADE_DAY,
        session_id="regular",
        observed_at=regular(TRADE_DAY).closes_at,
        published_at=released_at - timedelta(minutes=3),
        first_seen_at=released_at - timedelta(minutes=1),
        available_at=released_at,
        ingested_at=released_at,
        source_revision_id=revision,
        value=value,
    )


class R05Tests(unittest.TestCase):
    def setUp(self):
        self.calendar = cash_calendar()
        self.store = market_store()
        self.schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))

    def poll(self, now, *rows):
        return poll_snapshot(MockConnector(DATASET, rows), self.store, self.calendar, KEY, INSTRUMENTS, now=now)

    def test_holiday_and_overnight_have_exchange_specific_trade_date(self):
        after_holiday = date(2026, 1, 8)
        overnight = MarketSession(after_holiday, "night", taipei(date(2026, 1, 6), 15), taipei(HOLIDAY, 5))
        futures = TradingCalendar("TAIFEX_FIXTURE", (regular(after_holiday), overnight))
        overnight_observation = taipei(HOLIDAY, 2)
        self.assertEqual(futures.at(overnight_observation), overnight)
        self.assertEqual(futures.at(overnight_observation).trade_date, after_holiday)
        self.assertIsNone(self.calendar.at(overnight_observation))
        self.assertIsNone(self.calendar.at(taipei(HOLIDAY, 10)))
        holiday_key = replace(KEY, trade_date=HOLIDAY)
        with patch.object(MockConnector, "fetch") as fetch:
            result = poll_snapshot(MockConnector(DATASET), self.store, self.calendar, holiday_key,
                                   INSTRUMENTS, now=taipei(HOLIDAY, 20))
            self.assertEqual(result.state, PollState.NOT_DUE)
            fetch.assert_not_called()

    def test_reconciliation_uses_t1_t2_t5_t20_trading_days_and_watermark(self):
        offsets = tuple(self.schedule["reconcile_after_trading_days"])
        self.assertEqual(offsets, (1, 2, 5, 20))
        self.assertEqual(self.calendar.reconcile(TRADE_DAY, offsets), (
            date(2026, 1, 6), date(2026, 1, 8), date(2026, 1, 13), date(2026, 2, 3),
        ))
        with self.assertRaises(ValueError):
            self.calendar.reconcile(TRADE_DAY, (80,))
        missed = self.calendar.missed(taipei(TRADE_DAY, 23), taipei(date(2026, 1, 9), 13, 29))
        self.assertEqual(tuple(session.trade_date for session in missed), (date(2026, 1, 6), date(2026, 1, 8)))

    def test_empty_poll_and_unknown_availability_do_not_fabricate_ready(self):
        early = taipei(TRADE_DAY, 13, 50)
        late = taipei(TRADE_DAY, 20, 30)
        empty = self.poll(early)
        self.assertEqual(empty.state, PollState.PENDING)
        self.assertEqual(empty.rows, ())
        self.assertEqual(self.poll(late, replace(row(late), available_at=None)).state, PollState.PARTIAL)
        self.assertEqual(self.store.versions(DATASET, "0050", TRADE_DAY, "regular", now=late), ())
        release = self.poll(late, row(late))
        self.assertEqual(release.state, PollState.READY)
        self.assertEqual(release.rows, (row(late),))
        self.assertLess(release.rows[0].published_at, release.polled_at)
        self.assertEqual(empty.state, PollState.PENDING)

    def test_unknown_publication_or_first_seen_cannot_make_critical_data_ready(self):
        late = taipei(TRADE_DAY, 20, 30)
        for field in ("published_at", "first_seen_at", "ingested_at"):
            with self.subTest(field=field):
                incomplete = replace(row(late), **{field: None})
                result = self.poll(late, incomplete)
                self.assertIsNone(getattr(incomplete, field))
                self.assertEqual(result.state, PollState.PARTIAL)
                self.assertEqual(result.rows, ())
        self.assertIsNone(self.store.as_of(DATASET, "0050", TRADE_DAY, "regular", cutoff=late, now=late))

    def test_replay_cannot_make_an_unavailable_revision_ready(self):
        late = taipei(TRADE_DAY, 20, 30)
        available = taipei(TRADE_DAY, 23)
        original = replace(row(late), available_at=available)
        self.store.append(original, now=late)
        early_replay = self.poll(late, row(late))
        self.assertEqual(early_replay.state, PollState.PARTIAL)
        self.assertEqual(early_replay.rows, ())
        self.assertEqual(self.poll(available, original).rows, (original,))

    def test_snapshot_replay_deduplicates_and_t2_correction_preserves_prior_view(self):
        first_at = taipei(TRADE_DAY, 20, 30)
        repeated_at = taipei(TRADE_DAY, 23)
        _, t2 = self.calendar.reconcile(TRADE_DAY, (1, 2))
        corrected_at = taipei(t2, 20, 30)
        first_row = row(first_at)
        initial = self.poll(first_at, first_row)
        self.assertEqual(initial.state, PollState.READY)
        replay = replace(first_row, first_seen_at=repeated_at, ingested_at=repeated_at)
        self.assertEqual(self.poll(repeated_at, replay).rows, (first_row,))
        self.assertEqual(self.store.versions(DATASET, "0050", TRADE_DAY, "regular", now=repeated_at), (first_row,))

        corrected = row(corrected_at, revision="r2", value=101)
        amended = self.poll(corrected_at, corrected)
        self.assertEqual(amended.state, PollState.CORRECTED)
        self.assertEqual(amended.rows, (corrected,))
        self.assertNotEqual(first_row.payload_hash, corrected.payload_hash)
        self.assertEqual(self.store.versions(DATASET, "0050", TRADE_DAY, "regular", now=corrected_at),
                         (first_row, corrected))
        self.assertEqual(self.store.as_of(DATASET, "0050", TRADE_DAY, "regular", cutoff=first_at, now=corrected_at),
                         first_row)
        self.assertEqual(self.store.as_of(DATASET, "0050", TRADE_DAY, "regular", cutoff=corrected_at, now=corrected_at),
                         corrected)
        historical_replay = self.poll(first_at, first_row)
        self.assertEqual(historical_replay.state, PollState.READY)
        self.assertEqual(historical_replay.rows, (first_row,))
        self.assertEqual(initial.rows[0].value, 100)
        with self.assertRaises(FrozenInstanceError):
            initial.rows = amended.rows
        catch_up = self.poll(corrected_at + timedelta(days=3), first_row)
        self.assertEqual(catch_up.state, PollState.READY)
        self.assertEqual(catch_up.rows, (corrected,))
        self.assertEqual(self.store.versions(DATASET, "0050", TRADE_DAY, "regular", now=corrected_at),
                         (first_row, corrected))

    def test_bad_calendar_keys_or_missing_required_data_never_commit(self):
        late = taipei(TRADE_DAY, 20, 30)
        valid = row(late)
        other = replace(valid, instrument_id="2330", observed_at=taipei(TRADE_DAY, 14))
        required = frozenset({"0050", "2330"})
        for rows in ((valid,), (valid, valid, other), (valid, other)):
            with self.subTest(rows=len(rows)):
                result = poll_snapshot(MockConnector(DATASET, rows), self.store, self.calendar, KEY, required, now=late)
                self.assertEqual(result.state, PollState.PARTIAL)
                self.assertEqual(result.rows, ())
                self.assertEqual(self.store.versions(DATASET, "0050", TRADE_DAY, "regular", now=late), ())

    def test_download_or_storage_denial_and_non_mock_transport_stop_before_write(self):
        late = taipei(TRADE_DAY, 20, 30)
        for rights in (frozenset(), frozenset({Operation.DOWNLOAD, Operation.RETENTION})):
            with self.subTest(rights=rights):
                store = market_store(rights)
                result = poll_snapshot(MockConnector(DATASET, (row(late),)), store, self.calendar, KEY,
                                       INSTRUMENTS, now=late)
                self.assertEqual(result.state, PollState.RESTRICTED)
                self.assertEqual(result.rows, ())
        fake = Mock(dataset=DATASET)
        with self.assertRaises(ValueError):
            poll_snapshot(fake, self.store, self.calendar, KEY, INSTRUMENTS, now=late)
        fake.fetch.assert_not_called()

    def test_failures_respect_backoff_retry_after_and_quota(self):
        backoff = tuple(self.schedule["retries"]["transient_backoff_minutes"])
        self.assertEqual(backoff, (2, 5, 15))
        for count, status in enumerate((None, 500, 503)):
            with self.subTest(status=status):
                plan = retry_advice(status, count, backoff, jitter=timedelta(seconds=7))
                self.assertEqual(plan.action, RetryAction.RETRY)
                self.assertEqual(plan.delay, timedelta(minutes=backoff[count], seconds=7))
        self.assertEqual(retry_advice(503, 3, backoff).action, RetryAction.STOP_AND_ALERT)
        for status in (400, 401, 403, 429):
            with self.subTest(status=status):
                self.assertEqual(retry_advice(status, 0, backoff).action, RetryAction.STOP_AND_ALERT)
        for header, quota, expected in ((11, 8, 11), (8, 11, 11)):
            plan = retry_advice(429, 0, backoff, retry_after=timedelta(minutes=header), quota_wait=timedelta(minutes=quota))
            self.assertEqual(plan.action, RetryAction.RETRY)
            self.assertEqual(plan.delay, timedelta(minutes=expected))
        self.assertEqual(retry_advice(429, 3, backoff, retry_after=timedelta(minutes=30)).action,
                         RetryAction.STOP_AND_ALERT)
        self.assertEqual(retry_advice(204, 3, backoff).action, RetryAction.NEXT_POLL)


class CorporateActionTests(unittest.TestCase):
    def setUp(self):
        # 4:1 與生效日期取自 ADR-006，其餘數值、時間和交易時段皆是 fixture 假設。
        self.before = regular(date(2025, 6, 17))
        self.split_day = regular(date(2025, 6, 18))
        self.dividend_day = regular(date(2025, 6, 19))
        self.bar = PriceBar("0050", self.before, Decimal("159"), Decimal("160"))
        self.split = CorporateAction("0050", self.split_day.opens_at, self.before.opens_at,
                                     split_ratio=Decimal(4))
        self.dividend = CorporateAction("0050", self.dividend_day.opens_at, self.split_day.closes_at,
                                        cash_per_share=Decimal("1.50"))

    def test_split_has_no_future_leakage_and_preserves_raw_price(self):
        self.assertEqual(adjusted_close(self.bar, (self.split,), cutoff=self.before.closes_at), Decimal("160"))
        self.assertEqual(adjusted_close(self.bar, (self.split,), cutoff=self.split_day.opens_at), Decimal("40"))
        for available in (None, self.dividend_day.opens_at):
            with self.subTest(available=available):
                unproven = replace(self.split, available_at=available)
                self.assertEqual(adjusted_close(self.bar, (unproven,), cutoff=self.split_day.closes_at), Decimal("160"))
        self.assertEqual(self.bar.close, Decimal("160"))

    def test_position_uses_split_shares_and_separate_hypothetical_dividend_cash(self):
        initial = Position("0050", Decimal(25), Decimal(0))
        actions = (self.dividend, self.split, self.split)
        split_position = position_after_actions(initial, actions, held_after=self.before.closes_at,
                                                cutoff=self.split_day.closes_at)
        self.assertEqual(split_position, Position("0050", Decimal(100), Decimal(0)))
        self.assertEqual(split_position.shares * Decimal(40), initial.shares * self.bar.close)
        credited = position_after_actions(initial, actions, held_after=self.before.closes_at,
                                          cutoff=self.dividend_day.opens_at)
        self.assertEqual(credited, Position("0050", Decimal(100), Decimal("150.00")))

    def test_paper_fill_waits_for_next_mapped_open_uses_raw_price_and_fee(self):
        calendar = TradingCalendar("TWSE_FIXTURE", (self.before, self.split_day, self.dividend_day))
        next_bar = PriceBar("0050", self.split_day, Decimal("40.20"), Decimal("41.10"))
        later_bar = PriceBar("0050", self.dividend_day, Decimal("42"), Decimal("43"))
        fill = paper_fill_at_next_open(calendar, self.bar, (self.bar, next_bar, later_bar),
                                       signal_available_at=self.before.closes_at, shares=100, fee_rate=Decimal("0.001"))
        self.assertIsNotNone(fill)
        self.assertEqual(fill.execution_at, self.split_day.opens_at)
        self.assertEqual(fill.raw_price, Decimal("40.20"))
        self.assertEqual(fill.fee, Decimal("4.02"))
        self.assertEqual(fill.total_cost, Decimal("4024.02"))
        self.assertIsNone(paper_fill_at_next_open(calendar, self.bar, (self.bar, later_bar),
                                                signal_available_at=self.before.closes_at, shares=100,
                                                fee_rate=Decimal("0.001")))


if __name__ == "__main__":
    unittest.main()
