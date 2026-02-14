#!/usr/bin/env python
# main.py - Entry point for Headless Bing Search Automator

import argparse
import logging
import sys
import os

from config import Config
from utils.logger import setup_logging
from utils.network import is_connected, wait_for_connection
from gui_module import GUI
from browser_controller import BrowserController
from data_manager import DataManager
from rewards_watcher import RewardsWatcher
from daily_topics import DailyTopics
from utils.runtime_topic_generator import RuntimeTopicGenerator
from version import __version__

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Application:
    """Main application class to orchestrate the components."""
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing application components...")

        self.data_manager = DataManager(self.config)
        
        # Select and instantiate topic provider based on configuration
        topic_provider = self._create_topic_provider(config)
        
        self.browser_controller = BrowserController(
            self.config, self.data_manager, topic_provider
        )
        self.gui = GUI(self.config, self.data_manager, self.browser_controller)
        self.rewards_watcher = RewardsWatcher(self.config, self.data_manager, self.gui)

        self.browser_controller.gui = self.gui
        self.browser_controller.metrics_collector = self.gui.metrics_collector
        self.gui.rewards_watcher = self.rewards_watcher
        self.logger.info("Application components initialized successfully.")

    def _create_topic_provider(self, config):
        """Create and return appropriate topic provider based on config.
        
        Args:
            config: Config object
            
        Returns:
            TopicProvider: Either DailyTopics or RuntimeTopicGenerator
        """
        topic_generator_type = getattr(config, 'topic_generator_type', 'runtime').lower()
        
        if topic_generator_type == 'runtime':
            provider = RuntimeTopicGenerator(config={
                'cache_duplicates': True,
                'max_generation_attempts': 10
            })
            self.logger.info("Using RuntimeTopicGenerator for dynamic topic generation")
        else:
            provider = DailyTopics()
            self.logger.info("Using DailyTopics for daily-based topic selection")
        
        return provider

    def run(self):
        """Start the application."""
        self.logger.info("Starting Rewards Watcher...")
        self.rewards_watcher.start()

        try:
            self.logger.info("Starting GUI...")
            self.gui.start()
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user.")
        finally:
            self.logger.info("Stopping Rewards Watcher...")
            try:
                self.rewards_watcher.stop()
            except Exception as e:
                self.logger.error(f"Error stopping rewards watcher: {e}")
            self.logger.info("Application has been shut down gracefully.")

def main():
    """Entry point of the application."""
    parser = argparse.ArgumentParser(description="Bing Search Automator (Headless with Playwright)")
    parser.add_argument('--config', default='config.yaml', help='Path to the configuration file (default: config.yaml)')
    parser.add_argument('--profile', default=None, help='Configuration profile to use (e.g., stealth_mode, speed_mode, balanced_mode)')
    args = parser.parse_args()

    # Load configuration with optional profile
    config = Config.from_yaml(args.config, profile=args.profile)

    # Set up logging
    setup_logging(log_level=config.log_level, log_file=config.log_file_path, log_format=config.log_format)
    
    # Display version
    logger = logging.getLogger(__name__)
    logger.info(f"Bing Search Automator v{__version__} starting...")

    # Create and run the application
    app = Application(config)
    
    # Ensure we have internet before starting
    if not is_connected():
        logging.getLogger(__name__).warning("No internet detected at startup. Waiting for connectivity...")
        wait_for_connection(logger=logging.getLogger(__name__))

    app.run()

if __name__ == "__main__":
    main()
