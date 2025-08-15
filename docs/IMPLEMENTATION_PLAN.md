# Tomatempo — Implementation Plan (TDD Roadmap)

*Last updated: 2025-08-14*

This plan turns the Technical Overview into a concrete, test-driven delivery path. Each step lists **Objective**, **Expected Outcomes**, **Subtasks**, **Acceptance Criteria**, **Risks & Mitigations**, and **Test Strategy**. The goal is to keep iterations small, shippable, and continuously verifiable.

---

## Guiding Principles

* **CLI-first**: the terminal is the source of truth.
* **TDD**: write tests first (unit → integration → e2e), then implement.
* **No I/O at import time**: files/dirs are created **on first use** only.
* **Single binary target** later; developer experience via Poetry.
* **SQLite by default**; optional `DATABASE_URL` for future Postgres.

### Status Legend

* ☐ Not started
* ◐ In progress
* ✔ Done
* ✖ Blocked

---

## Milestones (high level)

* **M0 — Project Bootstrap**: repo, packaging, quality gates, canary tests.
* **M1 — Time Core**: slices, tomato rules, basic settings; no persistence.
* **M2 — Persistence & CRUD**: SQLite schema + CRUD for Project → Initiative → Deliverable → Task.
* **M3 — Timer & Pool**: focus/switch/start/pause/stop, pool & assign, reports basics.
* **M4 — Notes & Views**: notes (text), dashboards, settings persistence.
* **M5 — Breaks, Counting & Packaging**: break policy, overtime, progress, packaging for OSs.
* **M6 — Attachments & Polish**: image attachments v1, exports, resilience/backup.

---

## M0 — Bootstrap & Guardrails

**Objective**: A clean repo that builds, tests, and lints consistently.

**Expected Outcomes**

* `tomatempo` package imports cleanly; CLI `--help` runs.
* Pre-commit + CI stages (lint → smoke → tests).

**Subtasks**

* Repo layout `src/`; `pyproject.toml` with console script.
* Tooling: Poetry, Ruff (check+format), mypy, pytest + pytest-cov, pre-commit.
* CI (e.g., GitHub Actions): matrix py3.12; cache Poetry; jobs for lint/smoke/tests.

**Acceptance Criteria**

* `poetry run tomatempo --help` exits 0.
* `pre-commit run --all-files` clean.
* Canary tests pass: import package, import CLI, `--help`.

**Risks & Mitigations**

* Misconfigured pyproject → **Mitigation**: `poetry check` in CI.
* Editors not using venv → **Mitigation**: doc for venv + mypy path.

**Test Strategy**

* `test_smoke_imports_*` (pytest marker `smoke`).
* Ruff/mypy in pre-commit & CI.

Status: ☐

---

## M1 — Time Core (domain, in-memory)

**Objective**: Model time slices and tomato counting rules without persistence.

**Expected Outcomes**

* Entities: `Slice` (start/end), `TomatoRules` with `cumulative` and `segment-strict` modes.
* Utilities for durations and rounding.

**Subtasks**

* Define invariants: end ≥ start; ignore slices shorter than safety threshold.
* Tomato counting: floor logic, remainders.

**Acceptance Criteria**

* 49 min cumulative ⇒ 1 tomato + 24 min remainder.
* Segment-strict only counts full 25m slices.

**Risks & Mitigations**

* Off-by-one in rounding → tests with second-level resolution.

**Test Strategy**

* Unit tests on duration math and counting rules.

Status: ☐

---

## M2 — Settings (in-memory, then persisted later)

**Objective**: Load defaults and validate settings; no disk yet.

**Expected Outcomes**

* Validated durations/enums; easy override in tests.

**Subtasks**

* Defaults: tomato/breaks, counting mode, overtime-policy.
* Parser/validator for duration strings (`25m`, `90s`, etc.).

**Acceptance Criteria**

* Invalid durations reject with clear error messages.

**Risks & Mitigations**

* Ambiguous parsing → document accepted formats; property-based tests later if needed.

**Test Strategy**

* Unit tests for parsing and validation.

Status: ☐

---

## M3 — Persistence Foundation (SQLite + Alembic)

**Objective**: Initial schema and migrations that round-trip simple records.

**Expected Outcomes**

* SQLite DB with WAL and foreign keys ON.
* Alembic migration `0001` applied in CI.

**Subtasks**

* Tables: projects, initiatives, deliverables, tasks, slices, notes.
* Connection PRAGMAs; repo pattern for CRUD thin wrappers.

**Acceptance Criteria**

* Insert/read a Project in integration tests.
* `alembic upgrade head` runs clean in CI.

**Risks & Mitigations**

* SQLModel quirks on SQLite → stick to simple types; JSON via TEXT; small, frequent migrations.

**Test Strategy**

* DB integration tests with temp DB; migration smoke test.

Status: ☐

---

## M4 — CRUD Hierarchy

**Objective**: Create/list/show/edit/move/archive for all entities.

**Expected Outcomes**

* CLI commands for Project/Initiative/Deliverable/Task basics.

**Subtasks**

* Entity status enums; rename/move; filters and sorting.

**Acceptance Criteria**

* Cannot create Task without Deliverable.
* Listing by parent filters correctly.

**Risks & Mitigations**

* Name collisions → support id | "exact" | \~fuzzy; unique constraints as needed.

**Test Strategy**

* Unit (validators), integration (repos), e2e CLI via Typer runner.

Status: ☐

---

## M5 — Timer & Focus (no Pool yet)

**Objective**: Start/pause/stop; hot-switch focus; persist slices.

**Expected Outcomes**

* `TimerService` with states; proper slice closure on actions.

**Subtasks**

* Focus management; ensure no time loss between switches.

**Acceptance Criteria**

* Start on focused task creates open slice; pause/stop closes with exact duration.
* Switch closes previous slice and opens next immediately.

**Risks & Mitigations**

* Crash mid-slice → addressed in M11 (recovery), but capture timestamps cleanly now.

**Test Strategy**

* Unit with fake clock; integration verifying stored slices; e2e CLI for basic flow.

Status: ☐

---

## M6 — Time Pool & Assign/Reassign

**Objective**: Record unfocused time and allocate later.

**Expected Outcomes**

* Pool (slices with `task_id=NULL`); assign and reassign commands.

**Subtasks**

* Granularity validation; balance checks; audit trail (simple).

**Acceptance Criteria**

* Pool shows correct balance; split assignment distributes minutes accurately.

**Risks & Mitigations**

* Double counting → ensure reassignment is a move, not copy.

**Test Strategy**

* Integration on pool math; e2e CLI for assign/reassign flows.

Status: ☐

---

## M7 — Breaks & Overtime Policy

**Objective**: Non-counting break slices and end-of-timer policies.

**Expected Outcomes**

* `break start/stop`; `overtime-policy`: truncate|carry|extend.

**Subtasks**

* Mark slice type=break; ensure breaks never count.

**Acceptance Criteria**

* Break minutes excluded from tomato counting and reports.

**Risks & Mitigations**

* Edge cases at boundaries → tests for just-before/after zero.

**Test Strategy**

* Unit on policies; integration with sequences; e2e on user commands.

Status: ☐

---

## M8 — Counting & Progress

**Objective**: Progress by tomatoes or tasks, targets and cadence.

**Expected Outcomes**

* Aggregations per Task/Deliverable/Initiative; initiative cadence weekly.

**Subtasks**

* `% complete` for target tomatoes; cadence hit/miss with week-start.

**Acceptance Criteria**

* Deliverable progress reflects assigned tomatoes; initiative cadence uses selected week start.

**Risks & Mitigations**

* Timezone confusion → store UTC, render local; tests pin tz.

**Test Strategy**

* Integration queries; report unit tests for math.

Status: ☐

---

## M9 — Notes (text)

**Objective**: Notes on any entity with tags and pinning.

**Expected Outcomes**

* `note add/ls/show/edit/delete` with filters.

**Subtasks**

* Schema for notes; basic markdown support (raw text stored).

**Acceptance Criteria**

* List filters by tags and pinned; stable ordering by created\_at.

**Risks & Mitigations**

* Large notes → cut off in views; full text always retrievable.

**Test Strategy**

* Integration (CRUD); e2e CLI for flows.

Status: ☐

---

## M10 — Views (dashboards)

**Objective**: Live textual dashboards for timer/focus and lists.

**Expected Outcomes**

* `view timer|focus|tasks|deliverables|initiatives|project --deep`; `--watch`.

**Subtasks**

* Compact vs. detailed layouts; refresh loop.

**Acceptance Criteria**

* `view timer --watch` refreshes at configured rate without drift.

**Risks & Mitigations**

* Terminal quirks → keep ANSI simple; test on common shells.

**Test Strategy**

* Snapshot-like checks for key lines; manual sanity across OSes.

Status: ☐

---

## M11 — Settings Persistence & Profiles

**Objective**: Read/write config to disk; precedence and profiles.

**Expected Outcomes**

* Config file per OS; `config set/show`; precedence: CLI > profile > global.

**Subtasks**

* Use `platformdirs` to locate files; env overrides (`TOMATEMPO_*`).

**Acceptance Criteria**

* Round-trip settings; project/initiative-level overrides apply.

**Risks & Mitigations**

* Conflicts between layers → deterministic resolution documented.

**Test Strategy**

* Integration with tmp dirs; unit precedence tests.

Status: ☐

---

## M12 — Reports & Export

**Objective**: Period reports and CSV/JSON exports.

**Expected Outcomes**

* `report --by … --range …` and `export` commands.

**Subtasks**

* Grouping by day/week; default ranges; timezone-respectful rendering.

**Acceptance Criteria**

* Totals match slice sums; CSV schema documented.

**Risks & Mitigations**

* Off-by-one on date ranges → tests for inclusive/exclusive boundaries.

**Test Strategy**

* Integration on aggregations; e2e for command output.

Status: ☐

---

## M13 — Resilience & Recovery

**Objective**: Crash-safe behavior and backups.

**Expected Outcomes**

* `state.json` for open timer recovery; optional backups/rotation.

**Subtasks**

* On restart, close previous open slice at detected crash time.

**Acceptance Criteria**

* Simulated crash test recovers and preserves time with <1s skew (clock permitting).

**Risks & Mitigations**

* Clock drift → tie to monotonic clock for durations.

**Test Strategy**

* Integration simulating abrupt stop; file integrity checks.

Status: ☐

---

## M14 — Image Attachments (v1)

**Objective**: Attach images to notes; open externally.

**Expected Outcomes**

* `note add --from-clipboard|--file` stores blobs under `media/` (by hash), EXIF stripped by default.

**Subtasks**

* `note open` uses OS viewer; `note show` lists attachment metadata.

**Acceptance Criteria**

* Deduplication by hash; attachments linked to notes; thumbnails optional.

**Risks & Mitigations**

* Platform clipboard differences → graceful fallback and guidance.

**Test Strategy**

* Integration storing assets; e2e listing/opening (mock external call).

Status: ☐

---

## M15 — Packaging & Distribution

**Objective**: Binaries per OS and basic installers.

**Expected Outcomes**

* PyInstaller/Nuitka artifact builds; `.deb/.rpm` via nfpm/fpm; macOS pkg; Windows exe/msi.

**Subtasks**

* Post-install sanity (`tomatempo --help`); create data dirs lazily.

**Acceptance Criteria**

* Smoke test runs packaged binary in clean container/VM.

**Risks & Mitigations**

* Missing shared libs → prefer static where possible; docs for requirements.

**Test Strategy**

* CI job building artifacts; smoke run in minimal images.

Status: ☐

---

## Cross-cutting Concerns

* **Docs**: keep `TECHNICAL_OVERVIEW.md` updated; create ADRs for major choices.
* **Security/Privacy**: EXIF stripping default; no telemetry by default.
* **Performance**: optional import-time canary (perf marker) with generous threshold.
* **Accessibility**: minimal ANSI output; avoid color-only signals.

---

## Release Criteria (Alpha)

* M0 → M6 complete; notes (text) present; basic views and reports available.
* No open known-data-loss bugs; recovery works.
* Package builds for Windows/Linux/macOS; smoke tests pass on each.

## Release Criteria (Beta)

* Breaks & policies, progress/cadence, settings persistence, exports.
* Image attachments v1; simple backups.

## Release Criteria (1.0)

* Polished views; packaging docs; robust error messages; ADRs for all key choices.

---

### Change Log (Implementation Plan)

* *YYYY-MM-DD*: initial version created.
