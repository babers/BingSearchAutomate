"""
Proxy rotation utilities for avoiding detection.
Supports multiple proxy types and automatic rotation.
"""

import random
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """Configuration for a single proxy."""
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"  # http, https, socks5
    
    def to_playwright_format(self) -> Dict[str, str]:
        """Convert to Playwright proxy format."""
        proxy_dict = {"server": self.server}
        if self.username and self.password:
            proxy_dict["username"] = self.username
            proxy_dict["password"] = self.password
        return proxy_dict
    
    def __str__(self) -> str:
        """String representation without exposing credentials."""
        if self.username:
            return f"{self.proxy_type}://{self.username}:***@{self.server}"
        return f"{self.proxy_type}://{self.server}"


class ProxyRotator:
    """Manages proxy rotation for browser sessions."""
    
    def __init__(self, proxies: List[ProxyConfig] = None, 
                 rotation_strategy: str = "random"):
        """
        Args:
            proxies: List of proxy configurations
            rotation_strategy: 'random', 'round_robin', or 'sequential'
        """
        self.proxies = proxies or []
        self.rotation_strategy = rotation_strategy
        self.current_index = 0
        self.usage_count = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize usage tracking
        for i, proxy in enumerate(self.proxies):
            self.usage_count[i] = 0
    
    def add_proxy(self, server: str, username: str = None, 
                  password: str = None, proxy_type: str = "http") -> None:
        """Add a proxy to the rotation pool."""
        proxy = ProxyConfig(
            server=server,
            username=username,
            password=password,
            proxy_type=proxy_type
        )
        idx = len(self.proxies)
        self.proxies.append(proxy)
        self.usage_count[idx] = 0
        self.logger.info(f"Added proxy to pool: {proxy}")
    
    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get the next proxy based on rotation strategy."""
        if not self.proxies:
            self.logger.warning("No proxies available in pool")
            return None
        
        if self.rotation_strategy == "random":
            idx = random.randint(0, len(self.proxies) - 1)
        elif self.rotation_strategy == "round_robin":
            idx = self.current_index
            self.current_index = (self.current_index + 1) % len(self.proxies)
        else:  # sequential
            idx = self.current_index
            if self.current_index >= len(self.proxies) - 1:
                self.logger.info("Completed one rotation cycle, restarting")
            self.current_index = (self.current_index + 1) % len(self.proxies)
        
        proxy = self.proxies[idx]
        self.usage_count[idx] += 1
        self.logger.info(f"Selected proxy (strategy={self.rotation_strategy}): {proxy} "
                        f"(used {self.usage_count[idx]} times)")
        return proxy
    
    def get_random_proxy(self) -> Optional[ProxyConfig]:
        """Get a random proxy regardless of strategy."""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def get_least_used_proxy(self) -> Optional[ProxyConfig]:
        """Get the proxy with the least usage."""
        if not self.proxies:
            return None
        
        min_usage = min(self.usage_count.values())
        least_used_indices = [idx for idx, count in self.usage_count.items() 
                             if count == min_usage]
        idx = random.choice(least_used_indices)
        
        proxy = self.proxies[idx]
        self.usage_count[idx] += 1
        self.logger.info(f"Selected least-used proxy: {proxy} "
                        f"(used {self.usage_count[idx]} times)")
        return proxy
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for all proxies."""
        stats = {}
        for idx, proxy in enumerate(self.proxies):
            stats[str(proxy)] = self.usage_count[idx]
        return stats
    
    @classmethod
    def from_list(cls, proxy_list: List[str], rotation_strategy: str = "random") -> 'ProxyRotator':
        """
        Create a ProxyRotator from a list of proxy strings.
        
        Format examples:
        - "http://proxy.example.com:8080"
        - "http://user:pass@proxy.example.com:8080"
        - "socks5://proxy.example.com:1080"
        """
        rotator = cls(rotation_strategy=rotation_strategy)
        
        for proxy_str in proxy_list:
            try:
                # Parse proxy string
                if "://" in proxy_str:
                    proxy_type, rest = proxy_str.split("://", 1)
                else:
                    proxy_type = "http"
                    rest = proxy_str
                
                # Check for authentication
                if "@" in rest:
                    auth, server = rest.rsplit("@", 1)
                    if ":" in auth:
                        username, password = auth.split(":", 1)
                    else:
                        username, password = auth, None
                else:
                    server = rest
                    username, password = None, None
                
                rotator.add_proxy(server, username, password, proxy_type)
            except Exception as e:
                logger.error(f"Failed to parse proxy '{proxy_str}': {e}")
        
        return rotator


def create_proxy_rotator_from_config(proxy_config: Dict) -> Optional[ProxyRotator]:
    """
    Create a ProxyRotator from configuration dictionary.
    
    Expected format:
    {
        'enabled': True,
        'rotation_strategy': 'random',
        'proxies': [
            'http://proxy1.example.com:8080',
            'http://user:pass@proxy2.example.com:8080',
        ]
    }
    """
    if not proxy_config.get('enabled', False):
        logger.info("Proxy rotation is disabled in configuration")
        return None
    
    proxy_list = proxy_config.get('proxies', [])
    if not proxy_list:
        logger.warning("Proxy enabled but no proxies configured")
        return None
    
    strategy = proxy_config.get('rotation_strategy', 'random')
    rotator = ProxyRotator.from_list(proxy_list, rotation_strategy=strategy)
    
    logger.info(f"Created proxy rotator with {len(rotator.proxies)} proxies, "
                f"strategy: {strategy}")
    return rotator
