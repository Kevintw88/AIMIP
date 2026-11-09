"""R05 排程與公司行動的離線契約，所有時間與價格皆由測試 fixture 提供。"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from .data import DatasetKey, MockConnector, Observation, ObservationStore, require_utc


@dataclass(frozen=True)
class MarketSession:
    trade_date: date
    session_id: str
    opens_at: datetime
    closes_at: datetime

    def __post_init__(self) -> None:
        require_utc(self.opens_at)
        require_utc(self.closes_at)
        if self.opens_at >= self.closes_at:
            raise ValueError("invalid session window")


@dataclass(frozen=True)
class TradingCalendar:
    market: str
    sessions: tuple[MarketSession, ...]

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.sessions, key=lambda session: session.opens_at))
        keys = {(session.trade_date, session.session_id) for session in ordered}
        if len(keys) != len(ordered):
            raise ValueError("duplicate calendar session")
        if any(left.closes_at >= right.opens_at for left, right in zip(ordered, ordered[1:])):
            raise ValueError("overlapping calendar sessions")
        object.__setattr__(self, "sessions", ordered)

    def session(self, trade_date: date, session_id: str) -> MarketSession | None:
        return next((session for session in self.sessions
                     if (session.trade_date, session.session_id) == (trade_date, session_id)), None)

    def at(self, instant: datetime) -> MarketSession | None:
        require_utc(instant)
        return next((session for session in self.sessions
                     if session.opens_at <= instant <= session.closes_at), None)

    def reconcile(self, trade_date: date, offsets: tuple[int, ...]) -> tuple[date, ...]:
        days = sorted({session.trade_date for session in self.sessions})
        if trade_date not in days:
            raise ValueError("unknown reconciliation trade date")
        start = days.index(trade_date)
        if any(type(offset) is not int or offset <= 0 or start + offset >= len(days)
               for offset in offsets):
            raise ValueError("reconciliation exceeds fixture calendar")
        return tuple(days[start + offset] for offset in offsets)

    def missed(self, watermark: datetime, through: datetime) -> tuple[MarketSession, ...]:
        require_utc(watermark)
        require_utc(through)
        if through < watermark:
            raise ValueError("invalid catch-up window")
        return tuple(session for session in self.sessions if watermark < session.closes_at <= through)


class PollState(StrEnum):
    NOT_DUE = "NOT_DUE"
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    READY = "READY"
    CORRECTED = "CORRECTED"
    RESTRICTED = "RESTRICTED"


@dataclass(frozen=True)
class PollKey:
    dataset: DatasetKey
    trade_date: date
    session_id: str
    query_hash: str


@dataclass(frozen=True)
class PollResult:
    key: PollKey
    polled_at: datetime
    state: PollState
    rows: tuple[Observation, ...] = ()


def _complete_timeline(row: Observation) -> bool:
    return all(timestamp is not None for timestamp in (
        row.published_at, row.first_seen_at, row.available_at, row.ingested_at,
    ))


def poll_snapshot(
    connector: MockConnector,
    store: ObservationStore,
    calendar: TradingCalendar,
    key: PollKey,
    required_instruments: frozenset[str],
    *,
    now: datetime,
) -> PollResult:
    """檢查單一已結束交易時段的合成快照，驗證完成後才附加資料版本。"""
    require_utc(now)
    if type(connector) is not MockConnector or connector.dataset != key.dataset:
        raise ValueError("matching offline mock connector required")
    if not required_instruments:
        raise ValueError("required instrument keys must be declared")
    session = calendar.session(key.trade_date, key.session_id)
    if session is None or now < session.closes_at:
        return PollResult(key, now, PollState.NOT_DUE)

    try:
        rows = connector.fetch(store.registry, key.trade_date, key.session_id, now=now)
        if not rows:
            return PollResult(key, now, PollState.PENDING)
        instruments = {row.instrument_id for row in rows}
        if (instruments != required_instruments or len(instruments) != len(rows)
                or any(calendar.at(row.observed_at) != session or not _complete_timeline(row) for row in rows)):
            return PollResult(key, now, PollState.PARTIAL)

        def versions(row: Observation) -> tuple[Observation, ...]:
            return store.versions(row.dataset, row.instrument_id, row.trade_date, row.session_id, now=now)

        rows = tuple(sorted(rows, key=lambda row: row.instrument_id))
        before = [len(versions(row)) for row in rows]
        try:
            store.append_many(rows, now=now)
        except ValueError:
            return PollResult(key, now, PollState.PARTIAL)
        after = [versions(row) for row in rows]
    except PermissionError:
        return PollResult(key, now, PollState.RESTRICTED)

    latest_rows = tuple(revisions[-1] for revisions in after)
    if not all(_complete_timeline(row) for row in latest_rows):
        return PollResult(key, now, PollState.PARTIAL)
    corrected = any(old and len(new) > old for old, new in zip(before, after))
    state = PollState.CORRECTED if corrected else PollState.READY
    return PollResult(key, now, state, latest_rows)


class RetryAction(StrEnum):
    RETRY = "RETRY"
    NEXT_POLL = "NEXT_POLL"
    STOP_AND_ALERT = "STOP_AND_ALERT"


@dataclass(frozen=True)
class RetryAdvice:
    action: RetryAction
    delay: timedelta | None = None


def retry_advice(
    status: int | None,
    retries_used: int,
    backoff_minutes: tuple[int, ...],
    *,
    retry_after: timedelta | None = None,
    quota_wait: timedelta = timedelta(0),
    jitter: timedelta = timedelta(0),
) -> RetryAdvice:
    """規劃離線重試，None 表示傳輸失敗，204 表示尚無資料。"""
    if retries_used < 0 or any(minutes <= 0 for minutes in backoff_minutes):
        raise ValueError("invalid retry configuration")
    if quota_wait < timedelta(0) or not timedelta(0) <= jitter <= timedelta(minutes=1):
        raise ValueError("invalid quota wait or jitter")
    if status == 204:
        return RetryAdvice(RetryAction.NEXT_POLL)
    if retries_used >= len(backoff_minutes):
        return RetryAdvice(RetryAction.STOP_AND_ALERT)

    delay = timedelta(minutes=backoff_minutes[retries_used]) + jitter
    if status == 429 and retry_after is not None and retry_after >= timedelta(0):
        return RetryAdvice(RetryAction.RETRY, max(delay, retry_after, quota_wait))
    if status is None or 500 <= status <= 599:
        return RetryAdvice(RetryAction.RETRY, max(delay, quota_wait))
    return RetryAdvice(RetryAction.STOP_AND_ALERT)


@dataclass(frozen=True)
class PriceBar:
    instrument_id: str
    session: MarketSession
    open: Decimal
    close: Decimal

    def __post_init__(self) -> None:
        if any(not price.is_finite() or price <= 0 for price in (self.open, self.close)):
            raise ValueError("positive finite executable prices required")


@dataclass(frozen=True)
class CorporateAction:
    instrument_id: str
    effective_at: datetime
    available_at: datetime | None
    split_ratio: Decimal = Decimal(1)
    cash_per_share: Decimal = Decimal(0)

    def __post_init__(self) -> None:
        require_utc(self.effective_at)
        if self.available_at is not None:
            require_utc(self.available_at)
        if not self.split_ratio.is_finite() or self.split_ratio <= 0:
            raise ValueError("positive finite split ratio required")
        if not self.cash_per_share.is_finite() or self.cash_per_share < 0:
            raise ValueError("non-negative finite cash distribution required")
        if (self.split_ratio == 1) == (self.cash_per_share == 0):
            raise ValueError("a fixture action is either a split or a cash distribution")


def _known_actions(
    instrument_id: str,
    after: datetime,
    cutoff: datetime,
    actions: tuple[CorporateAction, ...],
) -> tuple[CorporateAction, ...]:
    require_utc(after)
    require_utc(cutoff)
    if cutoff < after:
        raise ValueError("as-of cutoff precedes input")
    return tuple(sorted({action for action in actions
                         if action.instrument_id == instrument_id
                         and after < action.effective_at <= cutoff
                         and action.available_at is not None and action.available_at <= cutoff},
                        key=lambda action: (action.effective_at, action.split_ratio, action.cash_per_share)))


def adjusted_close(bar: PriceBar, actions: tuple[CorporateAction, ...], *, cutoff: datetime) -> Decimal:
    price = bar.close
    for action in _known_actions(bar.instrument_id, bar.session.closes_at, cutoff, actions):
        price /= action.split_ratio
    return price


@dataclass(frozen=True)
class Position:
    instrument_id: str
    shares: Decimal
    cash: Decimal


def position_after_actions(
    position: Position,
    actions: tuple[CorporateAction, ...],
    *,
    held_after: datetime,
    cutoff: datetime,
) -> Position:
    shares, cash = position.shares, position.cash
    for action in _known_actions(position.instrument_id, held_after, cutoff, actions):
        cash += shares * action.cash_per_share
        shares *= action.split_ratio
    return Position(position.instrument_id, shares, cash)


@dataclass(frozen=True)
class PaperFill:
    execution_at: datetime
    shares: int
    raw_price: Decimal
    fee: Decimal

    @property
    def total_cost(self) -> Decimal:
        return self.raw_price * self.shares + self.fee


def paper_fill_at_next_open(
    calendar: TradingCalendar,
    signal_bar: PriceBar,
    bars: tuple[PriceBar, ...],
    *,
    signal_available_at: datetime,
    shares: int,
    fee_rate: Decimal,
) -> PaperFill | None:
    require_utc(signal_available_at)
    if signal_bar.session not in calendar.sessions or signal_available_at < signal_bar.session.closes_at:
        raise ValueError("a completed and mapped signal session is required")
    if type(shares) is not int or shares <= 0 or not fee_rate.is_finite() or fee_rate < 0:
        raise ValueError("invalid fixture quantity or fee rate")
    next_session = next((session for session in calendar.sessions
                         if session.session_id == signal_bar.session.session_id
                         and session.opens_at > signal_available_at), None)
    candidates = [bar for bar in bars if bar.instrument_id == signal_bar.instrument_id
                  and bar.session == next_session]
    if len(candidates) != 1:
        return None
    raw_price = candidates[0].open
    return PaperFill(next_session.opens_at, shares, raw_price, raw_price * shares * fee_rate)
