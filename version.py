# version.py
"""Version information for Bing Search Automator."""

__version__ = "2.0.2"
__version_info__ = (2, 0, 2)

# Version history:
# 2.0.2 (2026-03-13):
#   - Added Help menu with About and in-app Documentation manual
#   - Added completion dialog polish (centered, auto-close, audible cue)
#   - Added session start/completion timestamps in statistics panel
#   - Added runtime topic logging to logging/topics.log
#   - Moved logs to local ./logging folder
#   - Implemented field-level profile locking improvements
#   - Removed testing_mode profile
#   - Moved README-style markdown files under docs and excluded .md from installer
#
# 2.0.0 (2026-02-14):
#   - Added real-time statistics dashboard with metrics tracking
#   - Implemented configuration profiles (stealth/balanced/speed/testing)
#   - Added persistent database connections (50-70% performance improvement)
#   - Implemented exponential backoff retry for better error recovery
#   - Added LRU cache with configurable limit for topic generator
#   - Implemented smart pause algorithm with adaptive duration
#   - Added 4-tier selector fallbacks for robust points extraction
#   - Comprehensive type hints across all modules
#   - Fixed graph plotting and metrics integration bugs
#
# 1.0.0 (Initial):
#   - Basic headless browser automation
#   - GUI with real-time monitoring
#   - SQLite database for search history
#   - Playwright-based Bing search automation
