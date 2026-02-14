"""Configuration loader with sane defaults for packaged builds.

If explicit paths are not provided in config.yaml, defaults are placed in a
per-user app data directory so the app remains writable when installed.
"""

import yaml
import logging
import os
from typing import Optional, Dict, Any
from utils.paths import get_app_data_dir, resource_path


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

class Config:
    """
    A class to load and manage configuration from a YAML file.
    """
    def __init__(self, config_data):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Loading configuration...")
        
        # URLs
        self.rewards_url = config_data.get('urls', {}).get('rewards')
        self.search_url = config_data.get('urls', {}).get('search')
        
        # XPaths and Selectors
        self.points_xpath = config_data.get('xpaths', {}).get('points')
        self.search_box_name = config_data.get('selectors', {}).get('search_box_name')
        
        # Paths (kept for compatibility; not used in Playwright version)
        self.webdriver_path = config_data.get('paths', {}).get('webdriver')
        self.database_path = config_data.get('paths', {}).get('database')
        self.log_file_path = config_data.get('paths', {}).get('log_file')

        # Search Settings
        search_settings = config_data.get('search_settings', {})
        self.target_points = search_settings.get('target_points', 90)
        self.searches_before_pause = search_settings.get('searches_before_pause', 5)
        self.pause_duration_minutes = search_settings.get('pause_duration_minutes', 2)
        self.min_sleep_seconds = search_settings.get('min_sleep_seconds', 5)
        self.max_sleep_seconds = search_settings.get('max_sleep_seconds', 7)
        self.poll_interval = search_settings.get('poll_interval', 5)
        self.topic_generator_type = search_settings.get('topic_generator', 'runtime')  # 'runtime' or 'daily'

        # Browser Settings
        browser_settings = config_data.get('browser', {})
        self.headless = browser_settings.get('headless', True)
        self.slow_mo_ms = browser_settings.get('slow_mo_ms', 0)
        self.storage_state_path = browser_settings.get('storage_state_path')

        # Proxy Settings
        proxy_settings = config_data.get('proxy', {})
        self.proxy_enabled = proxy_settings.get('enabled', False)
        self.proxy_rotation_strategy = proxy_settings.get('rotation_strategy', 'random')
        self.proxy_list = proxy_settings.get('proxies') or []  # Handle None from YAML comments

        # Stealth Settings
        stealth_settings = config_data.get('stealth', {})
        self.simulate_mistakes = stealth_settings.get('simulate_mistakes', True)
        self.mistake_probability = stealth_settings.get('mistake_probability', 0.05)
        self.typing_speed_variance = stealth_settings.get('typing_speed_variance', True)
        self.random_mouse_movements = stealth_settings.get('random_mouse_movements', False)
        self.random_scrolling = stealth_settings.get('random_scrolling', False)

        # Logging Settings
        logging_settings = config_data.get('logging', {})
        self.log_level = logging_settings.get('level', 'INFO')
        self.log_format = logging_settings.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        self.logger.info("Configuration loaded successfully.")

    @classmethod
    def from_yaml(cls, file_path: str | None = 'config.yaml', profile: Optional[str] = None):
        """
        Loads configuration from a YAML file and creates a Config object.
        
        Args:
            file_path: Path to the configuration file
            profile: Optional profile name to use (e.g., 'stealth_mode', 'speed_mode')
        """
        try:
            path = resource_path(file_path) if file_path else resource_path('config.yaml')
            if not os.path.isfile(path):
                path = file_path or 'config.yaml'
            with open(path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Apply profile if specified
            if profile:
                profiles = config_data.get('profiles', {})
                if profile in profiles:
                    logging.info(f"Applying configuration profile: {profile}")
                    profile_data = profiles[profile]
                    # Deep merge profile settings over base config
                    config_data = deep_merge(config_data, profile_data)
                else:
                    available_profiles = ', '.join(profiles.keys())
                    logging.warning(
                        f"Profile '{profile}' not found. Available profiles: {available_profiles}"
                    )
            
            cfg = cls(config_data)

            app_dir = get_app_data_dir()
            if not cfg.database_path:
                cfg.database_path = os.path.join(app_dir, 'searches.db')
            if not cfg.log_file_path:
                cfg.log_file_path = os.path.join(app_dir, 'app.log')
            if not cfg.storage_state_path:
                cfg.storage_state_path = os.path.join(app_dir, 'playwright_storage_state.json')

            return cfg
        except FileNotFoundError:
            logging.error(f"Configuration file not found at {file_path}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML file: {e}")
            raise
