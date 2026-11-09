# Phase 0 — Codex Validation Plan and Acceptance Contract

**Status:** SPECIFICATION_READY — NOT EXECUTED, NOT AUTHORIZED TO RUN ON THE MAC
**Date:** 2026-11-09
**Scope:** R01–R07 feasibility, risk spike, mocks and documented gate evidence, not complete feature development.

## Safe first step
1. Read README, AGENTS.md, ADRs, ARR-001, all specs and the current branch.
2. Create a dedicated `phase0/validation` branch/PR after user authorizes execution; never overwrite unexpected changes.
3. Run `python3 scripts/validate_specs.py` and GitHub Actions `Specification Validation`; report actual outputs, no invented PASS.
4. Produce a coverage/gap matrix and an execution matrix. **Use mocked/synthetic data only** until dataset rights are approved.
5. Never touch billing/payment methods, subscribe to data, send billable AI traffic, trade, disable FileVault, configure auto-login or perform unapproved outage tests.
6. Distinguish Phase 0 `SPEC_READY` from `EXECUTION_AUTHORIZED`, `TEST_PASS`, `PRODUCTION_READY`.

## Milestone A — Specification / offline contract tests (can run in safe repo sandbox upon approval)
- `PH0-S01`: R04 seeds exactly 10 instruments / 14 signals with stable IDs, plus R06 7/3 listing eligibility and dataset rights PENDING.
- `PH0-S02`: R05: holiday / night-session calendar mapping, dataset availability unknown, delayed publication, T+1/T+2/T+5/T+20 revisions, dedupe and failure retries. Use synthetic input; no false SLA assertions.
- `PH0-S03`: A price corporate action fixture including 0050 4:1 split, hypothetical cash dividend, no future adjustment leakage; next-session execution and fees.
- `PH0-S04`: PIT/as-of joins reject missing historical release/available timestamps and distinguish `published_at`, `first_seen_at`, `ingested_at`.
- `PH0-S05`: Data license registry denies every unapproved storage/backtest/AI operation; no hidden OpenBB bypass.
- `PH0-S06`: Zero OpenAI API budget blocks all billable calls (including 0-cost-estimate, null estimate, retry, alternate LLM, embeddings) with **zero actual external network requests**; `MOCK_ONLY` output labeled and deterministic pipeline continues.
- `PH0-S07`: Static unit/contract tests run on clean CI and return documented PASS; commit and run URL recorded.
- `PH0-S08`: Future R07-04 equipment/offsite purchase objects cannot be approved while default budget 0, no quote, or without user approval.
**Acceptance:** full mock contract suite passes; real-data privileges not granted; tests reproduce deterministically with no paid service.

## Milestone B — Read-only host inventory (requires physical Mac access and explicit scoped authorization)
- `PH0-H01`: Record Mac model, OS and build, architecture, memory, disk, existing FileVault, energy auto-start setting, ethernet, user login context and system security config.
- `PH0-H02`: List candidate VM runtime and pinned ARM64 OS image, network/storage behavior; do not install system services at inspection step.
- `PH0-H03`: List all existing backup drives/NAS/UPS, usable bytes/health, encryption, restore keys, offsite options and exact costs (unknown remains null).
- `PH0-H04`: Draft risk assessment/rollback plan for any later privileged daemon install, outage test, or disk security change.
**Acceptance:** signed/informed approval before risky changes; no security downgrade. Unknown/unavailable hardware evidence remains NOT_RUN/BLOCKED.

## Milestone C — Controlled host/VM and recovery proof (requires separate approval and safe backup)
- `PH0-B01`: On approved Mac/OS, verify supported power-restoration behavior, and report exact OS minimum setting.
- `PH0-B02`: Demonstrate `LaunchDaemon` starts before GUI login with least privilege; no user login item dependency.
- `PH0-B03`: Prove headless ARM64 VM boots pre-login, starts Docker Engine/Compose, persists storage and networks; health checked.
- `PH0-B04`: Test FileVault-on cold power cycle. If unlocking blocks unattended operation, **FAIL the zero-touch criterion**, do not treat remote human SSH unlock as passing. Present secure alternative/risk decision; never change FileVault automatically.
- `PH0-B05`: Repeat at least 3 independently observed cold boots/power restores with **no human login/unlock action**. Target healthy required services <=10 minutes after host and network readiness. Record actual durations.
- `PH0-B06`: Kill guest/worker, disconnect/reconnect network under approved test plan, recover idempotently and show no duplicate data.
- `PH0-B07`: Test clean-target restore of consistent PostgreSQL backup + required authorized files from independent encrypted storage. Prove checksums and *measured* RPO <=24h, RTO <=8h before marking verified.
- `PH0-B08`: If existing UPS present, verify shutdown signaling; if none, document outage risk and recovery. UPS availability alone is not security acceptance.
**Acceptance:** all essential unattended, restore and private-security checks PASS. Otherwise system production release is BLOCKED, fallback evaluation required.

## Milestone D — OpenBB / source candidate spike (no unlicensed data)
- `PH0-O01`: Pin OpenBB V5 and Python dependency hashes, test Linux ARM64 import/API/MCP smoke, memory under guest 16GB.
- `PH0-O02`: Build one mock Taiwan provider via native connector and OpenBB extension; compare interfaces, failure propagation, latency and maintenance cost.
- `PH0-O03`: Prove switch between providers without altering PIT data schema or Quant consumer code.
- `PH0-O04`: Show default-deny dataset license filtering before any real ingestion/warehouse/backtest/external AI usage.
- `PH0-O05`: If use of a real free source is desired, first record dataset-specific legal terms and a permission decision; otherwise keep MOCK_ONLY.
**Acceptance:** conditional adoption recommendation backed by logs and fallback to native connector; external provider rights unresolved remain blocked.

## Evidence template (mandatory)
For every gate record:
- gate_id, execution_status = NOT_RUN/PASS/FAIL/BLOCKED;
- test date UTC, platform/version, git SHA, config and test dataset identifier;
- exact steps/commands, expected outcome, actual outcome, duration;
- sanitized logs, CI run URL (if any), artifacts/hash, remediation;
- decision owner review and security/user approval where required.

## Exit matrix
- **Phase 0 spec** ready: ADR-001–007 accepted and this document committed.
- **Phase 0 execution** authorized: explicit user permission + scope + safe boundaries.
- **Phase 0 technical pass**: all mandatory gates with evidence; conditional OpenBB may fall back to native.
- **Production ready**: separate go-live security, data license, live data quality, backups/DR and zero-touch verification; **not conferred** by this review.
- Failure of FileVault/zero-touch criterion: no change to `PASS` by assumption or by manual SSH unlock.
