# utils/runtime_topic_generator.py
"""Dynamic topic generation at runtime"""

import random
import logging
from typing import Dict, Set
from .topic_provider import TopicProvider


class RuntimeTopicGenerator(TopicProvider):
    """Generate diverse search topics dynamically at runtime.
    
    Uses template-based generation with random combinations to create
    natural-sounding search queries without needing pre-compiled lists.
    
    Example topics generated:
    - "Endangered tiger migration patterns explained"
    - "Ancient Egyptian architecture tutorial"
    - "Rare bird communication behaviors guide"
    - "Modern AI ethics vs traditional approaches"
    """
    
    # Expandable noun categories
    NOUNS = {
        'animals': [
            'dog', 'cat', 'elephant', 'dolphin', 'whale', 'chimpanzee',
            'parrot', 'eagle', 'penguin', 'lion', 'tiger', 'bear',
            'wolf', 'fox', 'deer', 'monkey', 'panda', 'koala',
            'octopus', 'butterfly', 'bee', 'ant', 'spider', 'shark',
            'crocodile', 'snake', 'alligator', 'zebra', 'horse'
        ],
        'tech': [
            'AI', 'machine learning', 'blockchain', 'quantum computing',
            'cloud storage', 'API', 'microservices', 'containerization',
            'cybersecurity', 'encryption', 'virtual reality', 'IoT',
            '5G', 'web3', 'neural networks', 'database', 'algorithm',
            'programming', 'software architecture', 'DevOps'
        ],
        'science': [
            'DNA', 'photosynthesis', 'cell division', 'mutation', 'evolution',
            'gravity', 'quantum mechanics', 'relativity', 'atom', 'molecule',
            'chemical reaction', 'thermodynamics', 'physics', 'biology',
            'chemistry', 'ecology', 'ecosystem', 'extinction'
        ],
        'history': [
            'ancient Rome', 'medieval period', 'Renaissance', 'Industrial Revolution',
            'World War II', 'Cold War', 'Roman Empire', 'Egyptian civilization',
            'Greek philosophy', 'Victorian era', 'American Revolution'
        ],
        'geography': [
            'Amazon rainforest', 'Mount Everest', 'Sahara desert', 'Arctic',
            'Antarctic', 'Great Barrier Reef', 'Grand Canyon', 'Nile River',
            'Himalayas', 'oceans', 'volcanoes', 'tectonic plates'
        ],
        'business': [
            'startup', 'marketing strategy', 'financial planning', 'investment',
            'entrepreneurship', 'management', 'negotiation', 'branding',
            'sales technique', 'supply chain', 'customer service'
        ]
    }
    
    ADJECTIVES = [
        'endangered', 'ancient', 'rare', 'modern', 'advanced', 'basic',
        'mysterious', 'fascinating', 'dangerous', 'harmless', 'intelligent',
        'unique', 'remarkable', 'unusual', 'common', 'extinct', 'evolving',
        'revolutionary', 'controversial', 'natural', 'artificial'
    ]
    
    ACTIVITIES = [
        'communication', 'migration', 'hunting', 'mating', 'behavior',
        'development', 'adaptation', 'reproduction', 'social structure',
        'feeding habits', 'camouflage', 'survival', 'intelligence',
        'tool use', 'learning', 'memory', 'cooperation'
    ]
    
    VERBS = [
        'explained', 'tutorial', 'guide', 'analysis', 'overview',
        'best practices', 'tips and tricks', 'for beginners',
        'advanced strategies', 'comparison', 'advantages', 'disadvantages'
    ]
    
    CONTEXTS = [
        '2024', 'in 2025', 'future predictions', 'history of',
        'impact on society', 'recent developments', 'latest research'
    ]
    
    def __init__(self, config=None):
        """Initialize the runtime topic generator.
        
        Args:
            config (dict, optional): Configuration dictionary with options like:
                - 'cache_duplicates': Whether to track and avoid duplicate topics
                - 'max_generation_attempts': Max attempts to avoid duplicates
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        self.generated_topics: Set[str] = set()
        self.generation_count = 0
        
        self.cache_duplicates = self.config.get('cache_duplicates', True)
        self.max_generation_attempts = self.config.get('max_generation_attempts', 10)
        
        self.logger.info(
            f"RuntimeTopicGenerator initialized (cache_duplicates={self.cache_duplicates})"
        )
    
    def get_next_topic(self) -> str:
        """Generate and return the next search topic.
        
        Returns random combination of words to create natural-sounding search queries.
        If cache_duplicates is enabled, attempts to avoid returning same topic twice.
        
        Returns:
            str: A dynamically generated search topic
        """
        
        def _generate() -> str:
            """Internal function to generate a single topic"""
            # Randomly select from templates
            noun_category = random.choice(list(self.NOUNS.keys()))
            noun = random.choice(self.NOUNS[noun_category])
            adjective = random.choice(self.ADJECTIVES)
            
            # Randomly choose generation template
            template = random.choice([
                f"{adjective} {noun}",
                f"{noun} {random.choice(self.ACTIVITIES)}",
                f"{noun} {random.choice(self.ACTIVITIES)} {random.choice(self.VERBS)}",
                f"{adjective} {noun} {random.choice(self.VERBS)}",
                f"{noun} {random.choice(self.VERBS)} {random.choice(self.CONTEXTS)}"
            ])
            
            return template.strip()
        
        # Generate topic, avoiding duplicates if caching enabled
        topic = _generate()
        attempts = 0
        
        while self.cache_duplicates and topic in self.generated_topics and attempts < self.max_generation_attempts:
            topic = _generate()
            attempts += 1
        
        if attempts >= self.max_generation_attempts:
            self.logger.debug(f"Max generation attempts reached, using duplicate topic: {topic}")
        
        self.generated_topics.add(topic)
        self.generation_count += 1
        
        self.logger.debug(f"Generated topic #{self.generation_count}: {topic}")
        return topic
    
    def reset(self):
        """Reset provider state for a new search session.
        
        Clears the topic cache and resets counters.
        """
        self.logger.info(
            f"RuntimeTopicGenerator reset (generated {self.generation_count} unique topics)"
        )
        self.generated_topics.clear()
        self.generation_count = 0
    
    def get_statistics(self) -> Dict[str, int]:
        """Get generation statistics.
        
        Returns:
            dict: Statistics including generated_count, unique_topics
        """
        return {
            'generated_count': self.generation_count,
            'unique_topics': len(self.generated_topics),
            'generator_type': 'RuntimeTopicGenerator',
            'cache_enabled': self.cache_duplicates
        }
