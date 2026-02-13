# utils/topic_provider.py
"""Abstract interface for topic generation strategies"""

from abc import ABC, abstractmethod
from typing import Dict


class TopicProvider(ABC):
    """Abstract base class for all topic generation strategies"""
    
    @abstractmethod
    def get_next_topic(self) -> str:
        """Return the next search topic.
        
        Returns:
            str: A search term/topic to use
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset provider state for a new search session.
        
        Called when starting a new search cycle to clear any generated topics
        or reset internal counters.
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, int]:
        """Get provider statistics for debugging.
        
        Returns:
            dict: Statistics about topic generation (generated_count, unique_topics, etc.)
        """
        pass
