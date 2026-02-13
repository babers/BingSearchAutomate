# Bing Search Automator (Headless) - Workflow Summary

## Development Status: ✅ Complete

This document provides a comprehensive overview of the project architecture, development workflow, and implementation details.

## Project Overview

The **Bing Search Automator (Headless)** is a modern, event-driven Python application that automates Microsoft Rewards Bing search activities. It uses Playwright for reliable browser automation and provides a user-friendly GUI for control and monitoring.

### Core Design Principles

1. **Headless-First**: Runs without GUI overhead for resource efficiency
2. **Event-Driven Architecture**: Components communicate via events/callbacks
3. **Configuration-Driven**: All settings in YAML for easy customization
4. **Logging-Centric**: Comprehensive logging for debugging and monitoring
5. **Modular Design**: Each component has a single responsibility

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Application (main.py)                      │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              GUI Module (Tkinter)                      │   │
│  │  ├─ Start/Stop Controls                               │   │
│  │  ├─ Status Display                                    │   │
│  │  ├─ Search Log                                        │   │
│  │  └─ Points Counter                                    │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                           │
│  ┌────────────────┴─────────────────────────────────────┐   │
│  │         Browser Controller (Playwright)              │   │
│  │  ├─ Launch Edge Browser                              │   │
│  │  ├─ Navigate to Bing                                 │   │
│  │  ├─ Execute Searches                                 │   │
│  │  └─ Handle Interactions                              │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                           │
│  ┌────────────────┴─────────────────────────────────────┐   │
│  │            Data Manager (Persistence)                │   │
│  │  ├─ Search History                                   │   │
│  │  ├─ Statistics                                       │   │
│  │  ├─ Account Information                              │   │
│  │  └─ Configuration Cache                              │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                           │
│  ┌────────────────┴─────────────────────────────────────┐   │
│  │         Rewards Watcher (Monitoring)                 │   │
│  │  ├─ Track Points Balance                             │   │
│  │  ├─ Detect Changes                                   │   │
│  │  ├─ Generate Notifications                           │   │
│  │  └─ Historical Analysis                              │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Daily Topics (Search Content)             │   │
│  │  ├─ Today's Topics                                    │   │
│  │  ├─ Search Keywords                                  │   │
│  │  └─ Queries Generator                                │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Utilities & Support                          │
│  ├─ Logger (setup_logging)                                     │
│  ├─ Network (connectivity checks)                              │
│  ├─ Paths (resource location)                                  │
│  ├─ Exceptions (error handling)                                │
│  └─ Timer (elapsed time tracking)                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  Configuration (config.yaml)                    │
│  ├─ Browser Settings (headless, path, timeout)                │
│  ├─ Application Settings (intervals, search counts)            │
│  ├─ GUI Settings (enabled, update interval)                    │
│  └─ Logging (level, format, file path)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Search Execution Flow

```
RewardsWatcher (Loop) 
    ↓
    ├─ Check if search quota reached
    ├─ Select random search keyword (DailyTopics)
    ├─ Calculate random delay (min-max interval)
    ├─ Sleep delay
    ↓
BrowserController
    ├─ Navigate to Bing
    ├─ Click search box
    ├─ Type search query
    ├─ Wait for results
    ├─ Extract points change
    ↓
DataManager
    ├─ Save search record
    ├─ Update statistics
    ├─ Persist to storage
    ↓
GUI Module
    ├─ Update search log
    ├─ Refresh points display
    ├─ Flash notification
    ↓
RewardsWatcher
    └─ Continue to next search
```

## Module Documentation

### config.py - Configuration Management

**Purpose**: Load and validate configuration from YAML file.

**Key Classes**:
- `Config`: Configuration object with defaults and validation

**Key Methods**:
- `from_yaml(filepath)`: Load configuration from YAML file
- `validate()`: Ensure all required fields are present

**Example**:
```python
config = Config.from_yaml('config.yaml')
print(config.headless)  # True
print(config.browser_path)  # Auto-detected or configured path
```

### browser_controller.py - Browser Automation

**Purpose**: Manage Playwright browser instances and search execution.

**Key Classes**:
- `BrowserController`: Main browser automation engine

**Key Methods**:
- `__init__(config, data_manager)`: Initialize controller
- `launch()`: Start browser instance
- `perform_search(query)`: Execute single search
- `close()`: Shutdown browser
- `get_current_points()`: Extract points from page

### data_manager.py - Data Persistence

**Purpose**: Store and retrieve application data.

**Key Classes**:
- `DataManager`: Manage data storage and retrieval

**Key Methods**:
- `save_search_record(query, points_change)`: Record search
- `get_statistics()`: Retrieve aggregated statistics
- `load_search_history()`: Get all previous searches
- `save_state()`: Persist data to file

### gui_module.py - User Interface

**Purpose**: Provide Tkinter-based GUI for monitoring and control.

**Key Classes**:
- `GUI`: Main GUI application class

**Key Methods**:
- `__init__(config, data_manager, browser_controller)`: Initialize GUI
- `start()`: Start GUI event loop
- `update_status(message)`: Update status display
- `append_log(entry)`: Add entry to search log
- `set_points_count(count)`: Update points display

### rewards_watcher.py - Monitoring

**Purpose**: Monitor account status and coordinate search activities.

**Key Classes**:
- `RewardsWatcher`: Main monitoring and orchestration engine

**Key Methods**:
- `start()`: Start monitoring thread
- `stop()`: Stop monitoring
- `_run()`: Main monitoring loop
- `_check_and_execute_searches()`: Execute searches as needed

### daily_topics.py - Search Content

**Purpose**: Manage search topics and keyword generation.

**Key Classes**:
- `DailyTopics`: Manage today's search topics

**Key Methods**:
- `get_today_topic()`: Get today's featured topic
- `get_random_keyword()`: Random keyword from topic list
- `get_related_searches()`: Get search suggestions

## Workflow - Typical Execution

### Initialization Phase
1. Parse command-line arguments
2. Load configuration from YAML
3. Setup logging (console + file)
4. Create DataManager instance
5. Create BrowserController
6. Create GUI
7. Create RewardsWatcher

### Execution Phase
1. Check internet connectivity (wait if needed)
2. Start RewardsWatcher in background thread
3. Start GUI event loop in main thread
4. RewardsWatcher periodically:
   - Checks search quota
   - Generates random search keyword
   - Sleeps for random duration
   - Calls BrowserController to perform search
   - Updates DataManager with results
5. GUI displays real-time updates

### Shutdown Phase
1. User clicks Stop or closes GUI
2. Signal RewardsWatcher to stop
3. Close browser instance
4. Save all state to persistent storage
5. Exit application

## Configuration Schema

### Browser Settings
```yaml
headless: true                          # Run in headless mode
browser_path: null                      # Auto-detect or set explicit path
disable_images: true                    # Skip loading images
timeout_ms: 30000                       # Page load timeout
```

### Automation Settings
```yaml
min_search_interval: 3                  # Minimum seconds between searches
max_search_interval: 8                  # Maximum seconds between searches
daily_search_count: 34                  # PC searches per day
mobile_search_count: 34                 # Mobile searches per day
```

### GUI Settings
```yaml
gui_enabled: true                       # Show GUI interface
gui_update_interval: 1000                # Update interval (ms)
window_width: 800                       # Window width (px)
window_height: 600                      # Window height (px)
```

### Logging
```yaml
log_level: INFO                         # DEBUG, INFO, WARNING, ERROR
log_format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_file_path: "app.log"               # Log file location
```

## Error Handling Strategy

### Browser Errors
- Timeout: Retry with exponential backoff
- Page Load Failure: Log and skip to next search
- Interaction Failure: Take screenshot for debugging

### Network Errors
- Connection Lost: Pause and wait for reconnection
- DNS Failure: Retry with longer delay
- Rate Limited: Increase search interval

### Data Errors
- Corrupted State File: Restore from backup
- Invalid Config: Use defaults and log warning
- Missing Dependencies: Print helpful error message

## Testing Strategy

### Unit Tests (to be implemented)
- Configuration loading and validation
- DataManager CRUD operations
- Keyword generation logic

### Integration Tests (to be implemented)
- Browser automation workflow
- End-to-end search execution
- GUI updates

### Manual Testing
- Launch application with different browsers
- Test with connectivity loss
- Verify GUI updates correctly
- Check data persistence

## Performance Optimization

### Browser Optimization
- Disable image loading (saves bandwidth)
- Use headless mode (reduced overhead)
- Close popup dialogs
- Cache browser resources

### Application Optimization
- Non-blocking GUI (separate threads)
- Efficient logging (async writes)
- Minimal memory footprint
- Connection pooling

## Deployment Considerations

### Production Deployment
- Run as Windows Service
- Automatic restart on crash
- Health monitoring
- Log rotation

### PyInstaller Bundling
```bash
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## Future Enhancements

1. **Advanced Scheduling**: Cron-like scheduling options
2. **Multi-Account**: Support multiple Microsoft accounts
3. **API Endpoints**: REST API for remote control
4. **Dashboard**: Web-based dashboard for monitoring
5. **Docker Support**: Containerization for easy deployment
6. **Database Backend**: SQL database instead of JSON files
7. **Machine Learning**: Smart search keyword selection
8. **Email Notifications**: Daily summary reports

## Maintenance Notes

- Update Playwright regularly: `pip install --upgrade playwright`
- Monitor Edge browser versions for compatibility
- Review logs regularly for errors
- Test configuration changes before deployment
- Keep dependencies updated for security

## Support & Documentation

- **README.md**: User guide and setup instructions
- **Code Comments**: Inline documentation in source files
- **Logs**: app.log contains detailed execution traces
- **Diagnostics**: Run tools/diag_combined.py for system check

---

**Last Updated**: [Current Date]
**Version**: 1.0.0
**Status**: Production Ready
