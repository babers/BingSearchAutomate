"""
Human-like typing simulation with realistic mistakes and corrections.
Mimics natural typing behavior including typos, backspaces, and variable speeds.
"""

import asyncio
import random
import logging
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


# Common typing mistakes mapping (nearby keys on QWERTY keyboard)
TYPO_MAP = {
    'a': ['s', 'q', 'w', 'z'],
    'b': ['v', 'g', 'h', 'n'],
    'c': ['x', 'd', 'f', 'v'],
    'd': ['s', 'e', 'r', 'f', 'c', 'x'],
    'e': ['w', 'r', 'd', 's'],
    'f': ['d', 'r', 't', 'g', 'v', 'c'],
    'g': ['f', 't', 'y', 'h', 'b', 'v'],
    'h': ['g', 'y', 'u', 'j', 'n', 'b'],
    'i': ['u', 'o', 'k', 'j'],
    'j': ['h', 'u', 'i', 'k', 'm', 'n'],
    'k': ['j', 'i', 'o', 'l', 'm'],
    'l': ['k', 'o', 'p'],
    'm': ['n', 'j', 'k'],
    'n': ['b', 'h', 'j', 'm'],
    'o': ['i', 'p', 'l', 'k'],
    'p': ['o', 'l'],
    'q': ['w', 'a'],
    'r': ['e', 't', 'f', 'd'],
    's': ['a', 'w', 'e', 'd', 'x', 'z'],
    't': ['r', 'y', 'g', 'f'],
    'u': ['y', 'i', 'j', 'h'],
    'v': ['c', 'f', 'g', 'b'],
    'w': ['q', 'e', 's', 'a'],
    'x': ['z', 's', 'd', 'c'],
    'y': ['t', 'u', 'h', 'g'],
    'z': ['a', 's', 'x'],
}


class HumanTyping:
    """Simulates realistic human typing with mistakes and corrections."""
    
    def __init__(self, mistake_probability: float = 0.05, 
                 correction_delay_ms: tuple = (200, 600),
                 char_delay_ms: tuple = (50, 200),
                 word_pause_ms: tuple = (100, 400)):
        """
        Args:
            mistake_probability: Chance of making a typo (0.0 to 1.0)
            correction_delay_ms: (min, max) delay before correcting typo
            char_delay_ms: (min, max) delay between characters
            word_pause_ms: (min, max) pause after spaces (word boundaries)
        """
        self.mistake_probability = mistake_probability
        self.correction_delay_range = correction_delay_ms
        self.char_delay_range = char_delay_ms
        self.word_pause_range = word_pause_ms
        self.logger = logging.getLogger(__name__)
    
    def _should_make_mistake(self) -> bool:
        """Determine if a typo should be made."""
        return random.random() < self.mistake_probability
    
    def _get_typo_char(self, char: str) -> str:
        """Get a realistic typo for a character."""
        char_lower = char.lower()
        if char_lower in TYPO_MAP and TYPO_MAP[char_lower]:
            typo = random.choice(TYPO_MAP[char_lower])
            # Preserve case
            return typo.upper() if char.isupper() else typo
        return char
    
    def _get_char_delay(self) -> float:
        """Get random delay between characters in milliseconds."""
        return random.uniform(*self.char_delay_range)
    
    def _get_word_pause(self) -> float:
        """Get random pause after word boundary in milliseconds."""
        return random.uniform(*self.word_pause_range)
    
    def _get_correction_delay(self) -> float:
        """Get delay before correcting a mistake in milliseconds."""
        return random.uniform(*self.correction_delay_range)
    
    async def type_like_human(self, element: Locator, text: str, 
                             simulate_mistakes: bool = True) -> None:
        """
        Type text into an element with human-like behavior.
        
        Args:
            element: Playwright locator for the input element
            text: Text to type
            simulate_mistakes: Whether to simulate typos and corrections
        """
        self.logger.debug(f"Typing '{text}' with human-like behavior (mistakes={simulate_mistakes})")
        
        # Clear existing text
        await element.fill('')
        
        for i, char in enumerate(text):
            # Determine if we should make a mistake
            if simulate_mistakes and self._should_make_mistake() and char.isalpha():
                # Type wrong character
                typo = self._get_typo_char(char)
                await element.type(typo, delay=self._get_char_delay())
                self.logger.debug(f"Typo: typed '{typo}' instead of '{char}'")
                
                # Brief pause before noticing mistake
                correction_delay = self._get_correction_delay()
                await asyncio.sleep(correction_delay / 1000)
                
                # Delete the mistake (backspace)
                await element.press('Backspace')
                await asyncio.sleep(random.uniform(50, 150) / 1000)
                
                # Type correct character
                await element.type(char, delay=self._get_char_delay())
                self.logger.debug(f"Corrected to '{char}'")
            else:
                # Type normally
                delay = self._get_char_delay()
                await element.type(char, delay=delay)
            
            # Extra pause after spaces (word boundaries)
            if char == ' ':
                word_pause = self._get_word_pause()
                await asyncio.sleep(word_pause / 1000)
            
            # Very small random pause between characters
            await asyncio.sleep(random.uniform(10, 50) / 1000)
        
        self.logger.info(f"Completed typing '{text}' with {text.count(' ') + 1} words")
    
    async def type_with_mistakes(self, page: Page, selector: str, text: str) -> None:
        """
        Convenience method to type with mistakes using a CSS selector.
        
        Args:
            page: Playwright page object
            selector: CSS selector for the input element
            text: Text to type
        """
        element = page.locator(selector).first
        await self.type_like_human(element, text, simulate_mistakes=True)
    
    async def type_without_mistakes(self, page: Page, selector: str, text: str) -> None:
        """
        Type with human-like delays but no mistakes.
        
        Args:
            page: Playwright page object
            selector: CSS selector for the input element
            text: Text to type
        """
        element = page.locator(selector).first
        await self.type_like_human(element, text, simulate_mistakes=False)


# Global singleton for easy import
_default_typer = None


def get_human_typer(mistake_probability: float = 0.05) -> HumanTyping:
    """Get or create the default human typing simulator."""
    global _default_typer
    if _default_typer is None:
        _default_typer = HumanTyping(mistake_probability=mistake_probability)
    return _default_typer


async def human_type(element: Locator, text: str, mistakes: bool = True) -> None:
    """
    Quick helper function for human-like typing.
    
    Args:
        element: Playwright locator for input element
        text: Text to type
        mistakes: Whether to simulate typos
    """
    typer = get_human_typer()
    await typer.type_like_human(element, text, simulate_mistakes=mistakes)
