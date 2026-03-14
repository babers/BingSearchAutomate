# utils/logger.py - Logging configuration

import logging
import os
from datetime import datetime

def setup_logging(log_level='INFO', log_file=None, log_format=None):
    """Configure logging for the application."""
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_topics_logger(topics_log_file):
    """Get a dedicated logger for search topics (runtime generation mode).
    
    Args:
        topics_log_file: Path to topics.log file
        
    Returns:
        logger: Logger instance for topics, or None if file cannot be created
    """
    if not topics_log_file:
        return None
    
    try:
        log_dir = os.path.dirname(topics_log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Create dedicated topics logger
        topics_logger = logging.getLogger('topics_logger')
        topics_logger.setLevel(logging.INFO)
        
        # Clear any existing handlers to avoid duplicates
        topics_logger.handlers = []
        
        # Create file handler with simple format: datetime, topic
        file_handler = logging.FileHandler(topics_log_file)
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        topics_logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        topics_logger.propagate = False
        
        return topics_logger
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to setup topics logger: {e}")
        return None


def log_search_topic(topics_logger, topic_text):
    """Log a search topic to the topics log.
    
    Args:
        topics_logger: Logger instance from get_topics_logger()
        topic_text: The search topic to log
    """
    if topics_logger:
        try:
            topics_logger.info(topic_text)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to log topic: {e}")
