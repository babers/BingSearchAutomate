# Bing Search Automator (Headless)

Automated Microsoft Rewards Bing search workflow with Playwright, real-time desktop UI, profile-based settings, and robust runtime safety controls.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-2.0.2-brightgreen.svg)](../version.py)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](../LICENSE)

## Version 2.0.2 Highlights

This release consolidates recent UX, configuration, and logging improvements:

- Added Help menu with About and in-app Documentation manual.
- Added completion workflow UX:
  - Centered completion dialog on dashboard area.
  - Auto-close after 60 seconds.
  - Audible completion chime.
  - Status set to `Completed`.
  - `Start` re-enabled and `Stop` disabled on completion.
- Added Session Statistics timestamps:
  - Actual Start time.
  - Actual Completion time.
- Added runtime topics logging to `logging/topics.log`.
- Moved logs to local project folder `logging/` instead of AppData.
- Improved profile behavior with field-level locking:
  - Only profile-overridden fields lock.
  - Non-overridden fields remain editable.
- Removed `testing_mode` profile from configuration and docs.
- Moved README-style markdown files under `docs/`.
- Ensured markdown files are excluded from installer packaging.

## Overview

Bing Search Automator performs controlled Bing searches for Microsoft Rewards with:

- Playwright-based browser automation (Edge channel support).
- Configurable stealth behavior (typing/mouse randomization).
- Adaptive pacing and pause logic.
- Real-time Tkinter dashboard and progress graph.
- SQLite-backed search persistence.
- Runtime topic generation and topic logging.

## Core Features

### Automation

- Automated Bing search execution.
- Rewards points monitoring.
- Target-based session completion.
- Start/stop controls with responsive interruption.

### Stealth & Behavior

- Optional simulated typing mistakes.
- Typing speed variance.
- Optional random mouse movement and scrolling.
- Configurable slow motion (`slow_mo_ms`) for interaction pacing.

### Topics

- Runtime topic generator (dynamic generation).
- Daily topic mode.
- Runtime topic logging to `logging/topics.log` with timestamped entries.

### Observability

- Main logs in `logging/app.log`.
- Session statistics panel:
  - Success rate.
  - Searches/minute.
  - Points per search.
  - ETA.
  - Start timestamp.
  - Completion timestamp.

## Requirements

- Windows
- Python 3.8+
- Microsoft Edge installed
- Internet connectivity

## Installation

From repository root:

```bash
pip install -r requirements.txt
python -m playwright install
```

Run:

```bash
python main.py
```

## Configuration

Main config file: `../config.yaml`

### Important Sections

- `search_settings`
  - `target_points`
  - `searches_before_pause`
  - `pause_duration_minutes`
  - `min_sleep_seconds` / `max_sleep_seconds`
  - `poll_interval`
  - `topic_generator` (`runtime` or `daily`)
- `browser`
  - `headless`
  - `slow_mo_ms`
  - `storage_state_path`
  - `channel`
- `proxy`
  - `enabled`
  - `rotation_strategy`
  - `proxies`
- `stealth`
  - `simulate_mistakes`
  - `mistake_probability`
  - `typing_speed_variance`
  - `random_mouse_movements`
  - `random_scrolling`
- `logging`
  - `level`
  - `format`

### Profiles

Available predefined profiles:

- `stealth_mode`
- `balanced_mode`
- `speed_mode`

Custom mode is available from Settings UI and unlocks all editable fields.

## UI Guide

### Current Status Panel

Shows live status values:

- Total Searches
- Rewards Points
- Elapsed
- Selected Mode
- Status (`Idle`, `Running`, `Stopped`, `Completed`)
- Network (`Online` / `Offline`)

### Session Statistics Panel

Shows computed and timestamp metrics:

- Success Rate
- Searches/min
- Points/Search
- ETA
- Start (actual system timestamp)
- Completed At (actual system timestamp)

### Controls

- `Start Searching`: begins session and resets session counters.
- `Stop`: requests graceful stop.

Completion behavior automatically enforces:

- Start enabled
- Stop disabled

### Help Menu

- `Help > About`
  - Software name
  - Author
  - Version
  - Git repository link
- `Help > Documentation`
  - Detailed in-app user manual for all UI options

### Settings Menu

`Settings > Config` opens editable configuration tabs:

- Profiles
- Search
- Browser
- Proxy
- Stealth
- Logging

Profile locking behavior:

- In predefined profiles, only overridden fields lock.
- Non-overridden fields remain editable.

## Logging Paths

Logs are now kept in local project folder:

- `logging/app.log`
- `logging/topics.log`

`topics.log` is written when `search_settings.topic_generator` is set to `runtime`.

## Completion UX

When target points are achieved:

- Status changes to `Completed`.
- Completion dialog opens centered on dashboard.
- Audible cue is played.
- Dialog auto-closes after 60 seconds.
- Completion timestamp is recorded in Session Statistics.

## Installer Notes

- Markdown files are excluded from installer package.
- Installer build files:
  - `../installer/BingSearchAutomate.spec`
  - `../installer/BingSearchAutomate.iss`

## Project Structure

```text
BingSearchAutomate-Headless/
├── main.py
├── config.py
├── config.yaml
├── browser_controller.py
├── data_manager.py
├── rewards_watcher.py
├── gui_module.py
├── version.py
├── requirements.txt
├── installer/
├── utils/
├── docs/
│   ├── README.md
│   ├── ENHANCEMENTS.md
│   ├── FIELD_LOCKING_README.md
│   └── ...
└── logging/
```

## Repository

GitHub: https://github.com/babers/BingSearchAutomate

## Additional Docs

See related documentation in this folder:

- `ENHANCEMENTS.md`
- `FIELD_LOCKING_README.md`
- `INSTALLER_README.md`
- `TESTING_QUICKSTART.md`
- `WORKFLOW_SUMMARY.md`
