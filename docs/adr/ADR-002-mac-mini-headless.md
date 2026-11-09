# ADR-002 v1.2 — Mac mini M4 Unattended Runtime
**Decision:** Accepted requirements · **Feasibility:** BLOCKED pending physical PoC
## Hardware
Apple Mac mini M4; 32GB unified RAM; 1TB SSD; wired network. 24×7 unattended required.
## Preferred runtime (candidate, NOT verified)
macOS host → system LaunchDaemon → headless Linux ARM64 VM (initially 6 vCPU / 16GB RAM) → systemd + Docker Engine / Compose → PostgreSQL, Prefect, workers, API and private dashboard.
Docker Desktop auto-start upon *user login* does not prove pre-login service recovery. Never declare unattended functionality validated without testing.
## Boot and disk unlock risk
- Power restoration must boot host automatically (verify the particular macOS version and hardware setting).
- System daemon must launch VM without user session and survive service failure.
- FileVault may require pre-boot unlock. **Do not disable FileVault or enable automatic login** without explicit user security approval.
- If FileVault blocks unattended cold boot, flag BLOCKED; investigate safe unlock orchestration or alternative hardware/runtime. No unapproved workaround.
## Persistent storage and backups
PostgreSQL within guest persistent volume (consistent logical backup), authorized Parquet under managed persistent storage, audit/forecasts backed up with encryption to independent destination. No copying running database/VM image as sole backup. Proposed RPO ≤24h, RTO ≤8h subject to drills.
## Acceptance PoC
1. Three unattended cold boots and power restorations, no GUI login.
2. VM and Docker start; DB/API/worker healthy within *target* ten minutes after host/network readiness.
3. Recovery after VM kill / worker kill / network outage.
4. Scheduling catches up without duplicate ingestion.
5. Database consistent; encrypted external backup restores on clean machine.
6. Tailscale/SSH/private access only; no DB public binding.
7. ARM64 Python/OpenBB/quant package compatibility measured.
## Fallbacks
A: macOS native LaunchDaemons for services; B: separate Linux host. Both require independent unattended and encryption tests.
## Pending
FileVault/security trade-off, VM runtime implementation, backup destination, UPS, macOS build and actual field test.
