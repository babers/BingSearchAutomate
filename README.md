# BingSearchAutomate-Headless

> Automated Microsoft Rewards Bing search activities using headless browser automation with Playwright

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen.svg)](version.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🆕 Latest Enhancements (v2.0)

**Major performance and feature improvements!** See [ENHANCEMENTS.md](ENHANCEMENTS.md) for full details.

- ✅ **Persistent DB Connection** - 50-70% faster database operations
- ✅ **Exponential Backoff Retry** - Better error resilience  
- ✅ **Type Hints** - Full type coverage for better code quality
- ✅ **LRU Cache** - Bounded memory usage in topic generator
- ✅ **Statistics Dashboard** - Real-time success rate, ETA, searches/min
- ✅ **Configuration Profiles** - Switch between stealth/balanced/speed modes
- ✅ **Smart Pause Algorithm** - Adaptive pausing based on points velocity
- ✅ **Selector Fallbacks** - Robust points extraction with multiple selectors

---

## Overview

**BingSearchAutomate-Headless** is a production-ready Python application that automates Microsoft Rewards Bing search activities. It uses Playwright for headless browser automation with Microsoft Edge to perform searches, monitor reward points, and manage search quotas efficiently.

The application includes:

- ✅ Headless browser automation with Playwright
- ✅ Real-time rewards point monitoring with statistics dashboard
- ✅ Configurable search intervals and quotas
- ✅ Tkinter-based GUI for monitoring and control
- ✅ Human-like behavior simulation (typing delays, mouse movements)
- ✅ Proxy rotation support
- ✅ Database-backed search history with persistent connections
- ✅ Comprehensive logging and error handling with exponential backoff
- ✅ Multiple configuration profiles (stealth, balanced, speed, testing)

## Features

### Core Automation Features

- **Headless Browser Control**: Automates Microsoft Edge browser via Playwright API
- **Search Automation**: Executes Bing searches with configurable intervals and quotas
- **Rewards Monitoring**: Real-time tracking of Microsoft Rewards points
- **Smart Scheduling**: Configurable pause intervals to avoid detection
- **Search History**: Persists all searches in SQLite database for tracking

### Advanced Capabilities

- **Human Behavior Simulation**
  - Variable typing speeds
  - Random typo generation with configurable probability
  - Random mouse movements before searches
  - Configurable slowdown for human-like interaction
  
- **Proxy Support**
  - Rotation strategies: random, round-robin, sequential
  - Easy proxy configuration via YAML
  - Seamless IP rotation

- **Topic Generation**
  - **Runtime Mode**: Dynamically generates search topics at runtime
  - **Daily Mode**: Pre-compiled daily search topic lists
  - Configurable via YAML

- **Monitoring & Control**
  - Tkinter GUI with real-time status updates
  - Search logging and display
  - Points counter and tracking
  - Start/stop controls

## Requirements

### System Requirements

- **OS**: Windows (Microsoft Edge required)
- **Python**: 3.8 or higher
- **Memory**: 512 MB minimum
- **Internet**: Active internet connection

### Dependencies

playwright          # Browser automation
matplotlib          # Data visualization
lxml               # XML parsing
PyYAML             # Configuration management
tkinter            # GUI (built-in with Python on Windows)

## Installation

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/babers/BingSearchAutomate-Headless.git
   cd BingSearchAutomate-Headless
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   python -m playwright install
   ```

3. **Configure the application**

   ```bash
   # Copy config template and customize
   cp config.yaml.example config.yaml
   # Edit config.yaml with your preferences
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

### Automatic Setup

For automatic dependency installation and execution:

```bash
python tools/run_ensure.py
```

## Configuration

The application uses a `config.yaml` file for all settings. Key configuration options:

### Search Settings

```yaml
search_settings:
  target_points: 90              # Target points per session
  searches_before_pause: 10      # Searches before taking a pause
  pause_duration_minutes: 1      # Pause duration in minutes
  min_sleep_seconds: 15          # Minimum sleep between searches
  max_sleep_seconds: 20          # Maximum sleep between searches
  poll_interval: 5               # Points polling interval
  topic_generator: 'runtime'     # 'runtime' or 'daily'
```

### Browser Settings

```yaml
browser:
  headless: true                 # Run in headless mode
  slow_mo_ms: 0                  # Slowdown in milliseconds
  storage_state_path: 'storage_state.json'  # Session persistence
```

### Stealth Settings

```yaml
stealth:
  simulate_mistakes: true        # Enable typo simulation
  mistake_probability: 0.05      # 5% typo probability
  typing_speed_variance: true    # Variable typing speeds
  random_mouse_movements: true   # Human-like mouse movements
```

### Proxy Configuration

```yaml
proxy:
  enabled: false                 # Enable/disable proxies
  rotation_strategy: 'random'    # random, round_robin, sequential
  proxies:
    - 'http://proxy1.example.com:8080'
    - 'socks5://proxy2.example.com:1080'
```

For detailed configuration, see [config.yaml](config.yaml).

## Usage

### Command Line

```bash
# Run with default configuration (balanced mode)
python main.py

# Use a specific profile
python main.py --profile stealth_mode
python main.py --profile speed_mode
python main.py --profile testing_mode

# Use custom config file
python main.py --config custom_config.yaml

# Combine options
python main.py --config custom_config.yaml --profile stealth_mode

# Display available arguments
python main.py --help
```

### Configuration Profiles

Choose from pre-configured profiles:

- **`balanced_mode`** (default) - Good mix of speed and stealth
- **`stealth_mode`** - Maximum stealth, slower but most human-like
- **`speed_mode`** - Faster searches, minimal stealth features
- **`testing_mode`** - Quick testing with visible browser

### GUI Interface

The application launches a Tkinter GUI with:

- **Current Status** - Total searches, rewards points, elapsed time, network status
- **Session Statistics** - Success rate, searches/min, points/search, ETA
- Real-time search display
- Start/Stop controls
- Current topic display
- Pause timer
- Search history graph

### Programmatic Usage

```python
from config import Config
from browser_controller import BrowserController
from data_manager import DataManager

# Load configuration
with open('config.yaml') as f:
    config_data = yaml.safe_load(f)
config = Config(config_data)

# Initialize components
data_manager = DataManager(config)
browser_controller = BrowserController(config, data_manager)

# Run automation
browser_controller.run()

## Project Structure

BingSearchAutomate-Headless/
├── main.py                          # Application entry point
├── config.py                        # Configuration management
├── browser_controller.py            # Playwright browser automation
├── data_manager.py                  # SQLite database management
├── gui_module.py                    # Tkinter user interface
├── daily_topics.py                  # Search topic management
├── rewards_watcher.py               # Rewards monitoring
├── settings_manager.py              # Settings persistence
│
├── utils/                           # Utility modules
│   ├── logger.py                    # Logging configuration
│   ├── network.py                   # Network connectivity checks
│   ├── paths.py                     # Path and resource management
│   ├── exceptions.py                # Custom exception classes
│   ├── elapsed_timer.py             # Timing utilities
│   ├── human_typing.py              # Human-like typing simulation
│   ├── proxy_rotation.py            # Proxy rotation logic
│   ├── runtime_topic_generator.py   # Dynamic topic generation
│   └── topic_provider.py            # Topic provider interface
│
├── tools/                           # Development and diagnostic tools
│   ├── run_ensure.py                # Auto dependency installer
│   ├── diag_combined.py             # System diagnostics
│   ├── diag_edge_driver.py          # Edge browser detection
│   ├── test_browser_recovery.py     # Browser recovery tests
│   ├── test_stealth_features.py     # Stealth feature tests
│   └── validate_rewards_extraction.py  # XPath validation
│
├── docs/                            # Documentation
│   ├── PROJECT_COMPLETION.md        # Project completion report
│   ├── WORKFLOW_SUMMARY.md          # Architecture documentation
│   ├── STEALTH_IMPLEMENTATION.md    # Stealth features guide
│   ├── RUNTIME_TOPICS_GUIDE.md      # Runtime topic generation
│   ├── BROWSER_RECOVERY_FIX.md      # Browser recovery details
│   └── [more documentation files]
│
├── config.yaml                      # Configuration file (user-customizable)
├── requirements.txt                 # Python dependencies
├── storage_state.json               # Browser session state
├── searches.db                      # SQLite database with search history
└── LICENSE                          # MIT License
```

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[WORKFLOW_SUMMARY.md](docs/WORKFLOW_SUMMARY.md)** - Architecture and workflow overview
- **[STEALTH_IMPLEMENTATION.md](docs/STEALTH_IMPLEMENTATION.md)** - Human behavior simulation details
- **[RUNTIME_TOPICS_GUIDE.md](docs/RUNTIME_TOPICS_GUIDE.md)** - Dynamic topic generation guide
- **[BROWSER_RECOVERY_FIX.md](docs/BROWSER_RECOVERY_FIX.md)** - Browser recovery mechanisms
- **[PROJECT_COMPLETION.md](docs/PROJECT_COMPLETION.md)** - Complete project report
- **[IMPROVEMENTS_SUMMARY.md](docs/IMPROVEMENTS_SUMMARY.md)** - Recent improvements and fixes
- **[TESTING_QUICKSTART.md](docs/TESTING_QUICKSTART.md)** - Testing guide

## Troubleshooting

### Common Issues

#### Browser Not Found

- Ensure Microsoft Edge is installed
- Run diagnostic tool: `python tools/diag_edge_driver.py`

#### Network Connectivity Issues

- Check internet connection
- Enable network retry in settings
- Check proxy configuration if enabled

#### XPath Extraction Failures

- Run validation tool: `python tools/validate_rewards_extraction.py`
- Update XPath in config.yaml if website structure changed

#### Database Errors

- The app auto-creates `searches.db` on first run
- Clear database if corrupted: Remove `searches.db` and restart

### Diagnostic Tools

```bash
# System and configuration diagnostics
python tools/diag_combined.py

# Edge browser detection
python tools/diag_edge_driver.py

# Browser recovery testing
python tools/test_browser_recovery.py

# Stealth features validation
python tools/test_stealth_features.py
```

## Development

### Running Tests

```bash
# Test browser recovery
python tools/test_browser_recovery.py

# Test stealth features
python tools/test_stealth_features.py

# Test extraction logic
python tools/test_extraction_logic.py

# Test human typing
python tools/test_human_typing.py
```

### Code Quality

The project follows Python best practices:

- PEP 8 style guidelines
- Comprehensive error handling
- Detailed logging throughout
- Type hints where applicable
- Modular architecture for maintainability

## Performance Considerations

- **Search Interval**: Randomized between `min_sleep_seconds` and `max_sleep_seconds`
- **Pause Duration**: Configurable breaks every N searches via `searches_before_pause`
- **Resource Usage**: Minimal CPU and memory footprint in headless mode
- **Database**: Efficient SQLite-based search history storage

## Security & Privacy

- ⚠️ **Educational Use**: This tool is for educational purposes only
- **Storage State**: Browser session stored in `storage_state.json`
- **Proxy Support**: Configure proxies for privacy if needed
- **Logging**: All activities logged to `app.log` and console

> **Disclaimer**: Use only with your own Microsoft Rewards account complying with Bing's terms of service. The author is not responsible for account termination or policy violations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests for:

- Bug fixes
- Feature enhancements
- Documentation improvements
- Performance optimizations

## Support

For issues, questions, or suggestions:

- Check the [documentation](docs/)
- Review [test files](tools/) for usage examples
- Check troubleshooting section above

## Changelog

### v1.0.0 (Current)

- ✅ Full Playwright integration with Microsoft Edge
- ✅ GUI for monitoring and control
- ✅ Human behavior simulation (stealth features)
- ✅ Proxy rotation support
- ✅ Runtime and daily topic generation modes
- ✅ Comprehensive logging and error handling
- ✅ Database-backed search history
- ✅ Production-ready codebase

---

**Last Updated**: February 13, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
