# Bing Search Automator

Automated Microsoft Rewards Bing search workflow using Playwright with a desktop dashboard, profile-driven configuration, and robust completion controls.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-2.0.2-brightgreen.svg)](version.py)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

## Latest Release: 2.0.2

- Help menu with About + in-app Documentation manual
- Completion UX improvements (centered dialog, 60s auto-close, audible cue)
- Session Statistics now show actual Start and Completion timestamps
- Local logging folder (`logging/app.log`, `logging/topics.log`)
- Runtime topic logging support
- Field-level profile locking improvements
- `testing_mode` profile removed
- Installer excludes markdown files

## Documentation

Full user and technical documentation is available here:

- [docs/README.md](docs/README.md)
- [docs/ENHANCEMENTS.md](docs/ENHANCEMENTS.md)
- [docs/FIELD_LOCKING_README.md](docs/FIELD_LOCKING_README.md)
- [docs/INSTALLER_README.md](docs/INSTALLER_README.md)

## Quick Start

```bash
pip install -r requirements.txt
python -m playwright install
python main.py
```

## Repository

- GitHub: https://github.com/babers/BingSearchAutomate
- Author: Baber Saeed
