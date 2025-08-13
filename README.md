# Tomatempo 🍅

A fast, no-nonsense **CLI Pomodoro** for people who actually switch tasks mid-tomato — with clean semantics for **Projects → Initiatives → Deliverables → Tasks**, universal **Notes**, a **Time Pool** for unassigned work, and a live **view** module.

> Goal: ship a **robust CLI first** (Windows, Linux, macOS). GUIs may come later; the terminal is home.

---

## Table of Contents

* [Why Tomatempo?](#why-tomatempo)
* [Core Concepts](#core-concepts)
* [Install](#install)
* [Quick Start](#quick-start)
* [CLI Reference](#cli-reference)
* [Views (Dashboards)](#views-dashboards)
* [Settings](#settings)
* [Time Pool & Assign](#time-pool--assign)
* [Notes Everywhere](#notes-everywhere)
* [Reports & Export](#reports--export)
* [Configuration & Data](#configuration--data)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)

---

## Why Tomatempo?

* **Hot task switching** without losing minutes. Close one slice, open another — the timer keeps flowing.
* **Unassigned time (Time Pool)** for those “freeform focus” blocks you’ll tag later.
* **Universal Notes** on any entity (Project/Initiative/Deliverable/Task).
* **Flexible progress**: by tomatoes or by tasks, per deliverable/initiative.
* **View module** for live terminal dashboards.

---

## Core Concepts

* **Tomato**: 25 minutes by default (customizable).
* **Slice**: a continuous chunk of time recorded while the timer runs (to the second).
* **Breaks**: short/long; never count toward tomatoes.
* **Project → Initiative → Deliverable → Task**:

  * **Project**: the big container (e.g., “Math Degree”).
  * **Initiative (ini)**: a line of work under a project; can be **finite** (target) or **continuous** (cadence).
  * **Deliverable (dlv)**: a package with a **Definition of Done**.
  * **Task**: atomic action, gets minutes/tomatoes.
* **Time Pool**: minutes captured without a focused task (a safe “inbox of minutes”).
* **Assign**: link minutes from the Pool (or reassign) to a Task/Deliverable.

Naming & aliases used by the CLI:
`project (proj)`, `initiative (ini)`, `deliverable (dlv)`, `task (task)`, `note (note)`.

---

## Install

Tomatempo ships as a single binary: `tomatempo`.

> Until official packages are published, use **Build from source**.

### Windows

* Download `tomatempo-<version>-windows-x64.exe` from Releases.
* Optional: add folder to PATH for global `tomatempo`.

### macOS

* Download `tomatempo-<version>-macos-universal` (or `.pkg`) and place in `/usr/local/bin/`.
* (Later) Homebrew:

  ```bash
  brew install tomatempo/tap/tomatempo
  ```

### Linux

* **Debian/Ubuntu (.deb)**:

  ```bash
  sudo dpkg -i tomatempo_<version>_amd64.deb
  ```
* **Fedora/RHEL (.rpm)**:

  ```bash
  sudo rpm -i tomatempo-<version>.x86_64.rpm
  ```
* **Build from source** (generic):

  ```bash
  # Clone
  git clone https://github.com/you/tomatempo && cd tomatempo
  # Build (single static binary; details may vary based on language)
  make build
  # Install
  sudo make install
  ```

---

## Quick Start

```bash
# Create a project and an initiative
tomatempo project add "Math Degree"
tomatempo initiative add "Semester Readings" --project "Math Degree" --cadence "10 tomatoes/week"

# Create a deliverable and tasks
tomatempo deliverable add "Chomsky Summary" --initiative "Semester Readings" --dod "3 pages + 10 quotes"
tomatempo task add "Extract quotes" --deliverable "Chomsky Summary"

# Focus and start the timer
tomatempo focus task "Extract quotes"
tomatempo timer start            # default 25m; recorded to the focused task
tomatempo timer pause            # or stop to close slice completely

# View live dashboard
tomatempo view timer --watch

# Work “freeform” then assign later
tomatempo focus clear
tomatempo timer start            # goes to Time Pool
tomatempo assign 15m @task:"Extract quotes" 10m @task:12345
```

---

## CLI Reference

> **Conventions**: IDs or quoted names accepted. Common flags: `--format table|json|csv`, `--columns`, `--filter`, `--sort`, `--limit`.

### Projects

```bash
tomatempo project add "Math Degree"
tomatempo project ls --filter status=active --columns id,name,status,tomatoes
tomatempo project show "Math Degree" --deep
tomatempo project set "Math Degree" --status on-hold
tomatempo project rename "Math Degree" "Mathematics BSc"
tomatempo project delete <id>            # --force to hard-delete
```

### Initiatives

```bash
tomatempo initiative add "Semester Readings" --project "Mathematics BSc" --cadence "10 tomatoes/week"
tomatempo initiative ls --project "Mathematics BSc" --columns id,name,cadence,tomatoes,progress
tomatempo initiative set <id> --target-tomatoes 60
tomatempo initiative set <id> --progress-mode tomatoes|tasks
tomatempo initiative close <id>     # reopen | archive
tomatempo initiative show <id> --deep
```

### Deliverables

```bash
tomatempo deliverable add "Chomsky Summary" --initiative "Semester Readings"
tomatempo deliverable set <id> --dod "3 pages + 10 quotes" --target-tomatoes 6
tomatempo deliverable ls --initiative "Semester Readings" --filter status=in-progress
tomatempo deliverable done <id>     # reopen | archive
tomatempo deliverable move <id> --initiative "<new ini>"
```

### Tasks

```bash
tomatempo task add "Extract quotes" --deliverable "Chomsky Summary" --estimate "2 tomatoes" --priority 3
tomatempo task ls --deliverable "Chomsky Summary" --filter status=open --sort -priority
tomatempo task set <id> --status open|blocked|done
tomatempo task move <id> --deliverable "<dlv>"
```

### Focus & Timer

```bash
tomatempo focus task <id|name>     # closes slice for previous focus, opens new slice
tomatempo focus clear              # next time goes to Pool
tomatempo timer start [25m]        # countdown; records to focus or Pool
tomatempo timer pause
tomatempo timer stop
tomatempo break start [5m]         # never counts to tomatoes
tomatempo break stop
```

---

## Views (Dashboards)

```bash
tomatempo view timer [--watch] [--compact]         # remaining time, focus/Pool, last slices
tomatempo view focus                               # focused entity + history
tomatempo view tasks --deliverable "<dlv>" --columns id,name,tomatoes,progress
tomatempo view deliverables --initiative "<ini>" --progress-mode tomatoes
tomatempo view initiatives --project "<proj>"
tomatempo view project "<proj>" --deep             # tree view
tomatempo view board --deliverable "<dlv>"         # kanban by status
tomatempo view progress --initiative "<ini>" --watch
tomatempo view pool [--range this-week]
```

---

## Settings

All settings are configurable via `config set`. Popular ones:

```bash
tomatempo config set tomato-length 25m
tomatempo config set short-break-length 5m
tomatempo config set long-break-length 15m
tomatempo config set tomatoes-per-long-break 4
tomatempo config set auto-start-next-tomato false
tomatempo config set overtime-policy truncate      # truncate|carry|extend
tomatempo config set tomato-counting-mode cumulative  # or segment-strict
tomatempo config set default-progress-mode tomatoes   # tomatoes|tasks
tomatempo config set default-cadence "10 tomatoes/week"
tomatempo config set view-refresh-rate 1s
tomatempo config set notes-editor "nvim"
```

See full catalog in `docs/SETTINGS.md` (or run `tomatempo config show --help`).

---

## Time Pool & Assign

* If you start the timer with **no focus**, minutes go to the **Time Pool**.
* Assign later, in granular chunks:

```bash
tomatempo pool show --range today
tomatempo assign 20m @task:84938 5m @task:84949
tomatempo assign 25m --to deliverable "Chomsky Summary"   # optional: auto create “General Work” task
tomatempo reassign 10m --from @task:84938 --to @task:84949
```

**Tomato counting** (default **cumulative**): every 25 minutes **assigned to the same task** ⇒ +1 tomato (remainders carry over). Switch to `segment-strict` if you only want full 25-min slices to count.

---

## Notes Everywhere

Attach notes to **any** entity:

```bash
tomatempo note add --on project "Mathematics BSc" "Kickoff scope and risks"
tomatempo note add --on initiative "<ini-id>" "Cadence targets and reading list" --tags plan,reading
tomatempo note add --on deliverable "<dlv-id>" "Outline + sources"
tomatempo note add --on task "<task-id>" "Edge cases to verify" --pin
tomatempo note ls  --on task "<task-id>" --filter tags=blocked
tomatempo note edit <note-id> "Updated approach"
tomatempo note delete <note-id>
```

`notes-editor` and `notes-template` can open your editor and seed markdown.

---

## Reports & Export

```bash
tomatempo report --by task|deliverable|initiative|project --range this-week --group-by day
tomatempo report --initiative "<ini>" --progress-mode tomatoes --format table
tomatempo export --range 2025-08-01..2025-08-13 --format csv --out ./logs.csv
```

---

## Configuration & Data

* **Config file**: `~/.config/tomatempo/config.yaml` (macOS: `~/Library/Application Support/Tomatempo/`; Windows: `%APPDATA%\Tomatempo\`).
* **Data dir**: `~/.local/share/tomatempo/` (platform-appropriate).
* **Autosave** every few seconds; optional backups (daily/weekly).
* **Privacy**: no breaks or telemetry counted toward tomatoes; encryption-at-rest optional when enabled.

Examples:

```bash
tomatempo config show
tomatempo config set backup-frequency weekly
tomatempo config set retention 180d
tomatempo config set do-not-disturb 22:00-07:00
```

---

## Roadmap

* Packaging: signed installers for **Windows**, `.deb`/`.rpm` for **Linux**, `.pkg`/Homebrew for **macOS**.
* Richer **view** widgets (burn-down, cadence heatmap).
* **Import/Export** for common trackers (CSV/JSON).
* Optional **profiles** (work/study) with per-project overrides.
* (Later) GUI wrapper; the CLI remains the source of truth.

---

## Contributing

1. Fork & clone.
2. Create a branch: `feat/your-feature`.
3. Write tests where it makes sense.
4. Open a PR with a clear description and CLI examples.

Bug reports & feature requests: open an Issue with **expected behavior**, **actual behavior**, **steps to reproduce**, and `tomatempo config show` output (scrub sensitive paths).

---

## License

MIT (suggested). See `LICENSE`.

---

**Tip**: Add shell completions (`bash`, `zsh`, `fish`) once the argument model stabilizes:

```bash
tomatempo completions zsh > ~/.zsh/completions/_tomatempo
```

Happy slicing! 🍅
