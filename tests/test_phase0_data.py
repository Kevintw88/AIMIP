"""PH0-S04 / PH0-S05 的逐用途授權、離線切換與 PIT 驗證。"""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from unittest import TestCase
from unittest.mock import patch

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


DATASET = DatasetKey("mock:native", "synthetic-close")
OBSERVED = datetime(2026, 4, 7, 5, 30, tzinfo=UTC)
PUBLISHED = OBSERVED + timedelta(minutes=30)
FIRST_SEEN = PUBLISHED + timedelta(minutes=5)
AVAILABLE = FIRST_SEEN + timedelta(minutes=2)
INGESTED = AVAILABLE + timedelta(minutes=1)
DAY = OBSERVED.date()
INSTRUMENT = "SYNTHETIC-1"
SESSION = "synthetic-day"
FLOW_RIGHTS = frozenset({Operation.DOWNLOAD, Operation.STORAGE, Operation.RETENTION, Operation.BACKTEST})


def approved(dataset=DATASET, operations=FLOW_RIGHTS):
    return LicenseDecision(
        dataset, "fixture-approval", LicenseStatus.APPROVED, operations, OBSERVED, "synthetic fixture"
    )


def fixture(dataset=DATASET):
    return Observation(
        dataset, INSTRUMENT, DAY, SESSION, OBSERVED, PUBLISHED, FIRST_SEEN, AVAILABLE, INGESTED, "v1", 100
    )


class LicenseTests(TestCase):
    def test_missing_pending_restricted_denied_and_malformed_grants_fail_closed(self):
        grant = approved(operations=set(Operation))
        invalid = (
            None,
            replace(grant, status=LicenseStatus.PENDING),
            replace(grant, status=LicenseStatus.RESTRICTED),
            replace(grant, status=LicenseStatus.DENIED),
            replace(grant, status="APPROVED"),
            replace(grant, terms_reference=""),
            replace(grant, decision_id=""),
            replace(grant, terms_reference=None),
            replace(grant, decision_id=None),
            replace(grant, checked_at=INGESTED + timedelta(minutes=1)),
            replace(grant, retention_until=INGESTED),
        )
        for decision in invalid:
            registry = LicenseRegistry(() if decision is None else (decision,))
            for operation in Operation:
                with self.subTest(decision=decision, operation=operation), self.assertRaises(PermissionError):
                    registry.require(DATASET, operation, now=INGESTED)

    def test_permission_cannot_imply_other_operations_or_datasets(self):
        for granted in Operation:
            registry = LicenseRegistry((approved(operations={granted}),))
            for requested in Operation:
                with self.subTest(granted=granted, requested=requested):
                    if granted is requested and requested is not Operation.AI_INFERENCE:
                        self.assertEqual(registry.require(DATASET, requested, now=INGESTED), "fixture-approval")
                    else:
                        with self.assertRaises(PermissionError):
                            registry.require(DATASET, requested, now=INGESTED)
        registry = LicenseRegistry((approved(),))
        for dataset in (DatasetKey("mock:native", "another-dataset"), DatasetKey("mock:other", DATASET.dataset_id)):
            with self.subTest(dataset=dataset), self.assertRaises(PermissionError):
                registry.require(dataset, Operation.DOWNLOAD, now=INGESTED)
        with self.assertRaises(PermissionError):
            registry.require(DATASET, "download", now=INGESTED)

    def test_connector_denies_unapproved_and_real_provider_even_with_mock_grant(self):
        openbb = DatasetKey("openbb", DATASET.dataset_id)
        cases = (
            (MockConnector(DATASET, (fixture(),)), LicenseRegistry()),
            (MockConnector(openbb, (fixture(openbb),)), LicenseRegistry((approved(openbb),))),
        )
        with patch("socket.socket", side_effect=AssertionError("unexpected socket")) as socket:
            for connector, registry in cases:
                with self.subTest(dataset=connector.dataset), self.assertRaises(PermissionError):
                    connector.fetch(registry, DAY, SESSION, now=INGESTED)
            socket.assert_not_called()

    def test_storage_retention_and_backtest_each_check_their_own_right(self):
        for missing in (Operation.STORAGE, Operation.RETENTION, Operation.BACKTEST):
            with self.subTest(missing=missing):
                registry = LicenseRegistry((approved(operations=FLOW_RIGHTS - {missing}),))
                store = ObservationStore(registry)
                row = MockConnector(DATASET, (fixture(),)).fetch(registry, DAY, SESSION, now=INGESTED)[0]
                if missing is Operation.BACKTEST:
                    store.append(row, now=INGESTED)
                    with self.assertRaises(PermissionError):
                        store.as_of(DATASET, INSTRUMENT, DAY, SESSION, cutoff=INGESTED, now=INGESTED)
                else:
                    with self.assertRaises(PermissionError):
                        store.append(row, now=INGESTED)

    def test_mixed_approval_batch_cannot_leave_partial_storage(self):
        other = DatasetKey("mock:unapproved", "synthetic-close")
        store = ObservationStore(LicenseRegistry((approved(),)))
        with self.assertRaises(PermissionError):
            store.append_many((fixture(), fixture(other)), now=INGESTED)
        self.assertEqual(store.versions(DATASET, INSTRUMENT, DAY, SESSION, now=INGESTED), ())


class PITTests(TestCase):
    def setUp(self):
        self.store = ObservationStore(LicenseRegistry((approved(),)))
        self.row = fixture()

    def as_of(self, cutoff, now=INGESTED):
        return self.store.as_of(DATASET, INSTRUMENT, DAY, SESSION, cutoff=cutoff, now=now)

    def test_distinct_release_first_seen_available_and_ingested_boundaries(self):
        self.store.append(self.row, now=INGESTED)
        for cutoff in (OBSERVED, PUBLISHED, FIRST_SEEN, AVAILABLE, INGESTED - timedelta(microseconds=1)):
            with self.subTest(cutoff=cutoff):
                self.assertIsNone(self.as_of(cutoff))
        self.assertEqual(self.as_of(INGESTED), self.row)

    def test_unknown_time_is_preserved_and_excluded(self):
        for field in ("published_at", "first_seen_at", "available_at"):
            with self.subTest(field=field):
                store = ObservationStore(self.store.registry)
                unknown = replace(self.row, **{field: None})
                store.append(unknown, now=INGESTED)
                self.assertIsNone(getattr(store.versions(DATASET, INSTRUMENT, DAY, SESSION, now=INGESTED)[0], field))
                self.assertIsNone(store.as_of(DATASET, INSTRUMENT, DAY, SESSION, cutoff=INGESTED, now=INGESTED))
        with self.assertRaises(ValueError):
            self.store.append(replace(self.row, ingested_at=None), now=INGESTED)

    def test_revision_no_leakage_duplicate_replay_and_immutable_vintage(self):
        self.store.append(self.row, now=INGESTED)
        later = INGESTED + timedelta(days=2)
        duplicate = replace(
            self.row, first_seen_at=later, available_at=later, ingested_at=later, source_revision_id="v1-alias"
        )
        self.assertIs(self.store.append(duplicate, now=later), self.row)
        correction = replace(duplicate, published_at=later, available_at=later, source_revision_id="v2", value=93)
        self.store.append(correction, now=later)
        self.assertIs(self.store.append(duplicate, now=later), self.row)
        self.assertIs(self.store.append(self.row, now=INGESTED), self.row)
        self.assertEqual(self.store.versions(DATASET, INSTRUMENT, DAY, SESSION, now=INGESTED), (self.row,))
        self.assertIs(self.as_of(INGESTED, now=later), self.row)
        self.assertIs(self.as_of(later, now=later), correction)
        self.assertEqual(self.store.versions(DATASET, INSTRUMENT, DAY, SESSION, now=later), (self.row, correction))
        self.assertNotEqual(self.row.payload_hash, correction.payload_hash)
        with self.assertRaises(ValueError):
            self.store.append(replace(correction, value=94), now=later)

    def test_future_availability_does_not_replace_prior_vintage_early(self):
        self.store.append(self.row, now=INGESTED)
        later = INGESTED + timedelta(days=2)
        available = later + timedelta(minutes=1)
        correction = replace(
            self.row, published_at=later, first_seen_at=later, available_at=available, ingested_at=later,
            source_revision_id="v2", value=93,
        )
        self.store.append(correction, now=later)
        for revision_id in ("v2", None):
            with self.subTest(revision_id=revision_id), self.assertRaises(ValueError):
                self.store.append(replace(correction, source_revision_id=revision_id, available_at=later), now=later)
        self.assertEqual(self.store.versions(DATASET, INSTRUMENT, DAY, SESSION, now=later), (self.row,))
        self.assertIs(self.as_of(later, now=later), self.row)
        self.assertIs(self.as_of(available, now=available), correction)

    def test_rejects_naive_impossible_future_and_backdated_times(self):
        with self.assertRaises(ValueError):
            replace(self.row, observed_at=OBSERVED.replace(tzinfo=None))
        with self.assertRaises(ValueError):
            replace(self.row, ingested_at=OBSERVED)
        with self.assertRaises(ValueError):
            self.store.append(self.row, now=AVAILABLE)
        with self.assertRaises(ValueError):
            self.as_of(INGESTED + timedelta(seconds=1))
        self.store.append(self.row, now=INGESTED)
        backdated = replace(self.row, ingested_at=AVAILABLE, source_revision_id="v2", value=101)
        with self.assertRaises(ValueError):
            self.store.append(backdated, now=INGESTED)

    def test_mock_provider_switch_preserves_consumer_contract_without_network(self):
        fallback = DatasetKey("mock:fallback", DATASET.dataset_id)
        registry = LicenseRegistry((approved(), approved(fallback)))
        store = ObservationStore(registry)
        with patch("socket.socket", side_effect=AssertionError("unexpected socket")) as socket:
            for dataset in (DATASET, fallback):
                row = fixture(dataset)
                connector = MockConnector(dataset, (row,))
                self.assertEqual(connector.fetch(registry, DAY, SESSION, now=PUBLISHED), ())
                self.assertEqual(connector.fetch(registry, DAY, "wrong-session", now=INGESTED), ())
                store.append_many(connector.fetch(registry, DAY, SESSION, now=INGESTED), now=INGESTED)
                joined = store.as_of(dataset, INSTRUMENT, DAY, SESSION, cutoff=INGESTED, now=INGESTED)
                self.assertEqual(joined.value, row.value)
            socket.assert_not_called()

    def test_connector_hides_known_future_fields_and_preserves_unknown_fields(self):
        future = INGESTED + timedelta(minutes=1)
        fields = ("published_at", "first_seen_at", "available_at", "ingested_at")
        for field in fields:
            with self.subTest(field=field):
                future_row = replace(self.row, **dict.fromkeys(fields) | {field: future})
                connector = MockConnector(DATASET, (future_row,))
                self.assertEqual(connector.fetch(self.store.registry, DAY, SESSION, now=INGESTED), ())
                self.assertEqual(connector.fetch(self.store.registry, DAY, SESSION, now=future), (future_row,))
        unknown = replace(self.row, available_at=None)
        connector = MockConnector(DATASET, (unknown,))
        rows = connector.fetch(self.store.registry, DAY, SESSION, now=INGESTED)
        self.assertEqual(rows, (unknown,))
        self.assertIsNone(rows[0].available_at)
