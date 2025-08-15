# Tomatempo — Technical Overview 🍅

*Last updated: 2025-08-14*

## 1) What is Tomatempo?

Tomatempo is a **CLI-first Pomodoro tool** designed for real-world contexts where you **switch tasks mid-tomato** and sometimes work **unassigned** time you’ll allocate later. The CLI is the source of truth; other UIs may come later.

### Core goals

* **Frictionless time capture**: start, pause, stop, hot-switch focus without losing seconds.
* **Assign later**: capture into a **Time Pool** and allocate minutes afterward.
* **Auditability**: every second is a **Slice**; tomatoes are computed, not manually edited.
* **Clarity**: a simple hierarchy and consistent terminology across commands, storage and reports.

### Core concepts (glossary)

* **Project → Initiative → Deliverable → Task**

  * *Project*: big container.
  * *Initiative* (finite or continuous; can have **cadence targets**).
  * *Deliverable*: package with a **Definition of Done**.
  * *Task*: atomic action that accumulates minutes/tomatoes.
* **Tomato**: 25 minutes (configurable).
* **Slice**: continuous time chunk while the timer runs (stored to the second).
* **Break**: short/long; never counts toward tomatoes.
* **Time Pool**: captured minutes with **no owner** yet (unassigned).
* **Assign/Reassign**: link minutes from the Pool (or move between tasks).
* **Notes**: text + optional image attachments on any entity.

---

## 2) Tech stack & standards

* **Language/runtime**: Python **3.12+**
* **CLI**: Typer (Click)
* **Persistence**: SQLModel (SQLAlchemy 2.x) + **SQLite** (WAL) by default; optional `DATABASE_URL` for Postgres later
* **Migrations**: Alembic
* **Paths**: `platformdirs` (config/data/cache/logs by OS; env overrides)
* **Lint/format**: Ruff (check + format)
* **Type checking**: mypy
* **Tests**: pytest (+ pytest-cov), TDD style; smoke tests for imports/CLI
* **Packaging**:

  * Dev: `pipx` / `poetry`
  * Binaries: PyInstaller/Nuitka
  * Installers: nfpm/fpm (`.deb/.rpm`), pkg/Homebrew for macOS, Pynsist/MSIX for Windows

**Design tenets**

* No I/O at import time; create files/dirs **on first use**.
* Store times in **UTC seconds**; display per locale/format settings.
* No pickle; config as YAML/INI; data in SQLite; media as files.
* Transactions are short and event-based (start/pause/stop/switch/assign).

---

## 3) Installing (targets)

* **Windows**: signed `.exe`/`.msi` (later), or `pipx install tomatempo`
* **macOS**: Homebrew tap (later) or universal binary/`.pkg`
* **Linux**: `.deb` (Debian/Ubuntu), `.rpm` (Fedora/RHEL), or build from source

**Build from source (dev)**

```bash
git clone <repo> && cd tomatempo
poetry install
poetry run tomatempo --help
```

---

## 4) CLI map (v1 scope)

> Entities & aliases: `project (proj)`, `initiative (ini)`, `deliverable (dlv)`, `task (task)`, `note (note)`.

### 4.1 CRUD & navigation

* **Project**

  * `project add|ls|show|set|rename|delete`
* **Initiative**

  * `initiative add|ls|show|set|close|reopen|archive`
  * Targets/cadence: `--target-tomatoes`, `--cadence "10 tomatoes/week"`, `--progress-mode tomatoes|tasks`
* **Deliverable**

  * `deliverable add|ls|show|set|done|reopen|archive|move`
  * DoD: `--dod "3 pages + 10 quotes"`
* **Task**

  * `task add|ls|show|set|move`
  * Estimation/prio: `--estimate "2 tomatoes"`, `--priority 1..5`

### 4.2 Focus & timer

* `focus task <id|name>`, `focus clear`
* `timer start [25m]`, `timer pause`, `timer stop`
* Breaks: `break start [5m]`, `break stop` (break slices don’t count)

### 4.3 Time Pool & assignment

* `pool show [--range today|this-week|…]`
* `assign 20m @task:84938 5m @task:84949`
* `assign 25m --to deliverable "<dlv>"` (creates/uses a “General Work” quick task if enabled)
* `reassign 10m --from @task:A --to @task:B`

### 4.4 Notes

* `note add --on project|initiative|deliverable|task <id> "text…" [--tags …] [--pin] [--from-clipboard] [--file <path> …]`
* `note ls|show|edit|delete`
* (Future) `note open` (external viewer), inline preview per terminal support

### 4.5 Views (dashboards)

* `view timer [--watch] [--compact]`
* `view focus`
* `view tasks|deliverables|initiatives [--filters]`
* `view project "<proj>" --deep`
* `view board --deliverable "<dlv>"` (status lanes)
* `view pool [--range …]`

### 4.6 Reporting & export

* `report --by task|deliverable|initiative|project --range this-week --group-by day|week`
* `export --range … --format csv|json --out ./logs.csv`

---

## 5) Settings (high-impact defaults)

* **tomato-length**: `25m`
* **short-break-length**: `5m`; **long-break-length**: `15m`; **tomatoes-per-long-break**: `4`
* **tomato-counting-mode**: `cumulative` | `segment-strict`
* **overtime-policy**: `truncate|carry|extend`
* **pool-enabled**: `true`
* **default-progress-mode**: `tomatoes`
* **view-refresh-rate**: `1s`, **show-emojis**: `true`
* **notes-editor**: `$EDITOR`, **strip-exif**: `true`
* **workday**: `09:00-18:00`, **week-start**: `monday`

See `tomatempo config set/show` and (later) `docs/SETTINGS.md`.

---

## 6) Data & storage (paths and files)

### 6.1 Directories by OS (via `platformdirs`)

(Overridable by env/flags; precedence: **CLI flag** > `TOMATEMPO_*` > OS defaults.)

* **Config**

  * Linux: `~/.config/tomatempo/config.yaml`
  * macOS: `~/Library/Application Support/Tomatempo/config.yaml`
  * Windows: `%APPDATA%\Tomatempo\config.yaml`
* **Data/state** (DB, media, backups, exports)

  * Linux: `~/.local/state/tomatempo/` (or `~/.local/share/tomatempo/`)
  * macOS: `~/Library/Application Support/Tomatempo/`
  * Windows: `%LOCALAPPDATA%\Tomatempo\`
* **Cache**

  * Linux: `~/.cache/tomatempo/`
  * macOS: `~/Library/Caches/Tomatempo/`
  * Windows: `%LOCALAPPDATA%\Tomatempo\Cache\`
* **Logs**

  * Linux: `~/.local/state/tomatempo/logs/`
  * macOS: `~/Library/Logs/Tomatempo/`
  * Windows: `%LOCALAPPDATA%\Tomatempo\Logs\`

### 6.2 Files & structure (inside Data/State)

```
Tomatempo/
├─ tomatempo.db           # SQLite (WAL enabled)
├─ state.json             # crash recovery: open timer/focus, timestamps
├─ media/                 # image blobs, named by content hash
├─ thumbnails/            # (optional) small previews for TUI
├─ backups/               # rotating DB/zip backups
└─ exports/               # CSV/JSON user exports
```

**Env overrides**: `TOMATEMPO_CONFIG`, `TOMATEMPO_DATA_DIR`, `TOMATEMPO_CACHE_DIR`, `TOMATEMPO_LOG_DIR`.

**I/O policy**: create directories/files **on first use**; never on import.

---

## 7) Schema overview (v1)

* **projects** (id, name, status, created\_at, …)
* **initiatives** (id, project\_id, name, status, cadence, target\_tomatoes, progress\_mode, …)
* **deliverables** (id, initiative\_id, name, status, dod, target\_tomatoes, …)
* **tasks** (id, deliverable\_id, name, status, priority, estimate\_tomatoes, …)
* **slices** (id, task\_id **nullable**, start\_ts, end\_ts, type: work|break, origin: auto|manual)
* **notes** (id, entity\_type, entity\_id, text, tags, pinned, created\_at, …)
* **media\_assets** (hash, mime, bytes, width, height, stored\_ext, created\_at)
* **note\_attachments** (note\_id, asset\_hash, caption, order)

Indexes on FKs and time columns (e.g., `slices.start_ts`). Foreign keys ON. WAL + `synchronous=NORMAL`.

---

## 8) Security & privacy

* **EXIF stripping** enabled by default on image attachments (configurable).
* No background telemetry. Optional **local** metrics file (opt-in later).
* Encryption-at-rest may be added later (setting: `encrypt-store`).
* Crash recovery stores only minimal state in `state.json`.

---

## 9) Testing & quality

* **Smoke tests** (“canaries”): package import, CLI `--help`, no side effects at import.
* **Unit**: time rules (slices, tomato counting modes, overtime policies).
* **Integration**: repositories + migrations; pool assign/reassign invariants.
* **E2E (CLI)**: flows for focus/switch/stop; view/report happy paths.
* **Pre-commit**: ruff (fix), ruff-format, mypy; smoke subset on pre-commit or pre-push.
* **CI stages**: lint → smoke → tests → package.

---

## 10) Packaging & distribution

* **Single binary** per OS via PyInstaller/Nuitka.
* Linux: `.deb/.rpm` via nfpm/fpm; macOS: `.pkg` + Homebrew tap; Windows: `.exe`/`.msi`.
* Post-install: create data dirs lazily; add shell completions command (`tomatempo completions …`).

---

## 11) Known trade-offs & future work

* SQLite single-user fits the CLI; optional Postgres via `DATABASE_URL` later.
* Inline image preview depends on terminal protocol (Kitty/iTerm/WezTerm/Sixel); default is **external viewer** fallback.
* Views are textual first; charts/heatmaps may come later.

---

## 12) Changelog pointers

* Versioning: SemVer; expose `tomatempo.__version__`.
* Keep ADRs for significant choices in `docs/adr/` (e.g., directory policy, DB choice, counting mode).

---

### Appendix A — Command snippets (reference)

* Focus & timer:

  * `focus task "<name>"` → `timer start` → `timer pause|stop`
  * `focus clear` → `timer start` (to Pool)
* Assign later:

  * `pool show` → `assign 20m @task:A 5m @task:B`
* Progress by tomatoes:

  * `deliverable set <id> --target-tomatoes 6` → `view deliverables --columns id,name,tomatoes,target,progress`

---

## Document maintenance

* Treat this file as a **living overview**.
* When a design decision is finalized, add a brief line here and open a focused **ADR** under `docs/adr/`.
* Keep sections short; link out to deep docs (`SETTINGS.md`, `MIGRATIONS.md`, `PACKAGING.md`) as they appear.
