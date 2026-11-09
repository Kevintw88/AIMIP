"""離線資料讀取、逐用途授權及 PIT 版本契約。"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from hashlib import sha256
import json
from threading import Lock
from typing import Iterable


def require_utc(value: datetime) -> None:
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise ValueError("時間必須明確標記為 UTC")


@dataclass(frozen=True)
class DatasetKey:
    provider_id: str
    dataset_id: str


class Operation(Enum):
    DOWNLOAD = "download"
    STORAGE = "storage"
    RETENTION = "retention"
    BACKTEST = "backtest"
    AI_INFERENCE = "ai_inference"
    ML_TRAINING = "ml_training"
    REDISTRIBUTION = "redistribution"
    BACKUP = "backup"


class LicenseStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    RESTRICTED = "RESTRICTED"
    DENIED = "DENIED"


@dataclass(frozen=True)
class LicenseDecision:
    dataset: DatasetKey
    decision_id: str
    status: LicenseStatus
    allowed_operations: frozenset[Operation]
    checked_at: datetime
    terms_reference: str
    retention_until: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "allowed_operations", frozenset(self.allowed_operations))
        require_utc(self.checked_at)
        if self.retention_until is not None:
            require_utc(self.retention_until)


class LicenseRegistry:
    def __init__(self, decisions: Iterable[LicenseDecision] = ()) -> None:
        self._decisions: dict[DatasetKey, LicenseDecision] = {}
        for decision in decisions:
            if decision.dataset in self._decisions:
                raise ValueError("同一資料集存在重複授權決策")
            self._decisions[decision.dataset] = decision

    def require(self, dataset: DatasetKey, operation: Operation, *, now: datetime) -> str:
        require_utc(now)
        decision = self._decisions.get(dataset)
        if (
            not dataset.provider_id.startswith("mock:")
            or len(dataset.provider_id) <= len("mock:")
            or not dataset.dataset_id.strip()
            or decision is None
            or decision.status is not LicenseStatus.APPROVED
            or not isinstance(operation, Operation)
            or operation is Operation.AI_INFERENCE
            or operation not in decision.allowed_operations
            or not isinstance(decision.decision_id, str)
            or not decision.decision_id.strip()
            or not isinstance(decision.terms_reference, str)
            or not decision.terms_reference.strip()
            or now < decision.checked_at
            or (decision.retention_until is not None and now >= decision.retention_until)
        ):
            raise PermissionError("資料集或用途未獲 Phase 0A 授權")
        return decision.decision_id


@dataclass(frozen=True)
class Observation:
    dataset: DatasetKey
    instrument_id: str
    trade_date: date
    session_id: str
    observed_at: datetime
    published_at: datetime | None
    first_seen_at: datetime | None
    available_at: datetime | None
    ingested_at: datetime | None
    source_revision_id: str | None
    value: int | str

    def __post_init__(self) -> None:
        require_utc(self.observed_at)
        if type(self.value) not in (int, str):
            raise ValueError("合成資料值限整數或字串")
        for timestamp in (self.published_at, self.first_seen_at, self.available_at, self.ingested_at):
            if timestamp is not None:
                require_utc(timestamp)
                if timestamp < self.observed_at:
                    raise ValueError("資料時間早於觀測時間")
        if self.published_at is not None:
            for timestamp in (self.first_seen_at, self.available_at):
                if timestamp is not None and timestamp < self.published_at:
                    raise ValueError("首次觀察或可用時間早於來源發布時間")
        if self.first_seen_at is not None and self.ingested_at is not None:
            if self.ingested_at < self.first_seen_at:
                raise ValueError("入庫時間早於首次觀察時間")

    @property
    def payload_hash(self) -> str:
        return sha256(json.dumps(self.value).encode("utf-8")).hexdigest()

    @property
    def _source_content(self) -> tuple[datetime, datetime | None, int | str]:
        # 重複輪詢會更新平台時間，去重時保留首次確認的資料版本。
        return (self.observed_at, self.published_at, self.value)

    def visible_at(self, now: datetime) -> bool:
        """保留明確的未知值，只隱藏已知在未來的資料。"""
        timestamps = (self.observed_at, self.published_at, self.first_seen_at, self.available_at, self.ingested_at)
        return all(timestamp is None or timestamp <= now for timestamp in timestamps)


@dataclass(frozen=True)
class MockConnector:
    dataset: DatasetKey
    _rows: tuple[Observation, ...]

    def __init__(self, dataset: DatasetKey, rows: Iterable[Observation] = ()) -> None:
        object.__setattr__(self, "dataset", dataset)
        object.__setattr__(self, "_rows", tuple(rows))
        if any(row.dataset != dataset for row in self._rows):
            raise ValueError("資料列不屬於 connector 的資料集")

    def fetch(
        self, registry: LicenseRegistry, trade_date: date, session_id: str, *, now: datetime
    ) -> tuple[Observation, ...]:
        registry.require(self.dataset, Operation.DOWNLOAD, now=now)
        return tuple(
            row
            for row in self._rows
            if row.trade_date == trade_date
            and row.session_id == session_id
            and row.visible_at(now)
        )


ObservationKey = tuple[DatasetKey, str, date, str]


class ObservationStore:
    """以記憶體保存不可變資料版本，供離線驗證。"""

    def __init__(self, registry: LicenseRegistry) -> None:
        self._registry = registry
        self._observations: dict[ObservationKey, tuple[Observation, ...]] = {}
        self._revision_ids: dict[tuple[ObservationKey, str], Observation] = {}
        self._lock = Lock()

    @property
    def registry(self) -> LicenseRegistry:
        return self._registry

    def append(self, observation: Observation, *, now: datetime) -> Observation:
        return self.append_many((observation,), now=now)[0]

    def append_many(
        self, observations: Iterable[Observation], *, now: datetime
    ) -> tuple[Observation, ...]:
        pending: dict[ObservationKey, tuple[Observation, ...]] = {}
        revision_ids: dict[tuple[ObservationKey, str], Observation] = {}
        results: list[Observation] = []
        with self._lock:
            for row in observations:
                self.registry.require(row.dataset, Operation.STORAGE, now=now)
                self.registry.require(row.dataset, Operation.RETENTION, now=now)
                if row.ingested_at is None or row.ingested_at > now:
                    raise ValueError("入庫時間須為已發生且明確的時間")
                key = (row.dataset, row.instrument_id, row.trade_date, row.session_id)
                versions = pending.get(key, self._observations.get(key, ()))
                latest = versions[-1] if versions else None
                source_id = row.source_revision_id
                if source_id is not None:
                    revision_key = (key, source_id)
                    prior = revision_ids.get(revision_key, self._revision_ids.get(revision_key))
                    if prior is not None:
                        if row._source_content != prior._source_content:
                            raise ValueError("同一來源版本 ID 的內容不一致")
                        if not prior.visible_at(now):
                            raise ValueError("重放時不得使用尚未可見的版本")
                        results.append(prior)
                        continue
                if latest is not None and row._source_content == latest._source_content:
                    if not latest.visible_at(now):
                        raise ValueError("去重時不得使用尚未可見的版本")
                    stored = latest
                else:
                    if latest is not None and (
                        row.ingested_at < latest.ingested_at
                        or (
                            row.first_seen_at is not None
                            and latest.first_seen_at is not None
                            and row.first_seen_at < latest.first_seen_at
                        )
                    ):
                        raise ValueError("修訂不得回填較早的首次觀察或入庫時間")
                    stored = row
                    pending[key] = (*versions, stored)
                if source_id is not None:
                    revision_ids[(key, source_id)] = stored
                results.append(stored)
            self._observations.update(pending)
            self._revision_ids.update(revision_ids)
        return tuple(results)

    def versions(
        self, dataset: DatasetKey, instrument_id: str, trade_date: date, session_id: str, *, now: datetime
    ) -> tuple[Observation, ...]:
        self.registry.require(dataset, Operation.RETENTION, now=now)
        with self._lock:
            versions = self._observations.get((dataset, instrument_id, trade_date, session_id), ())
        return tuple(row for row in versions if row.visible_at(now))

    def as_of(
        self,
        dataset: DatasetKey,
        instrument_id: str,
        trade_date: date,
        session_id: str,
        *,
        cutoff: datetime,
        now: datetime,
    ) -> Observation | None:
        self.registry.require(dataset, Operation.BACKTEST, now=now)
        require_utc(cutoff)
        if cutoff > now:
            raise ValueError("PIT 截止時間不得晚於查詢時間")
        versions = self.versions(dataset, instrument_id, trade_date, session_id, now=now)
        for row in reversed(versions):
            if not row.visible_at(cutoff):
                continue
            timestamps = (row.published_at, row.first_seen_at, row.available_at)
            if any(timestamp is None for timestamp in timestamps):
                return None
            return row
        return None
