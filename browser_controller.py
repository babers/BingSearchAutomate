# browser_controller.py
# Headless Playwright-based browser controller for automated Bing searches

import logging
import os
import random
import re
import threading
import time
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

from config import Config
from data_manager import DataManager
from utils.network import is_connected
from utils import elapsed_timer
from utils.human_typing import HumanTyping
from utils.proxy_rotation import create_proxy_rotator_from_config
from utils.topic_provider import TopicProvider

# Constants
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)
VIEWPORT_WIDTH_RANGE = (1366, 1920)
VIEWPORT_HEIGHT_RANGE = (768, 1080)
MAX_RETRY_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 2

class BrowserController:
    def __init__(self, config: Config, data_manager: DataManager, 
                 topic_provider: TopicProvider, gui=None, metrics_collector=None):
        self.config = config
        self.data_manager = data_manager
        self.gui = gui
        self.topics_provider = topic_provider  # Injected dependency
        self.metrics_collector = metrics_collector  # For tracking search statistics
        self.logger = logging.getLogger(__name__)
        self.last_points = 0
        self.stop_event = threading.Event()
        
        # Initialize human typing simulator
        self.human_typer = HumanTyping(
            mistake_probability=config.mistake_probability if config.simulate_mistakes else 0.0,
            char_delay_ms=(50, 200) if config.typing_speed_variance else (100, 120),
            word_pause_ms=(100, 400),
            correction_delay_ms=(200, 600)
        )
        
        # Store stealth settings
        self.random_mouse_movements = config.random_mouse_movements
        
        # Initialize proxy rotator if enabled
        self.proxy_rotator = None
        if config.proxy_enabled:
            proxy_config = {
                'enabled': config.proxy_enabled,
                'rotation_strategy': config.proxy_rotation_strategy,
                'proxies': config.proxy_list
            }
            self.proxy_rotator = create_proxy_rotator_from_config(proxy_config)
            if self.proxy_rotator:
                self.logger.info(f"Proxy rotation enabled with {len(self.proxy_rotator.proxies)} proxies")
            else:
                self.logger.warning("Proxy enabled but no valid proxies configured")

    async def _setup_browser(self):
        """Initialize Playwright and launch a headless browser."""
        try:
            self.playwright = await async_playwright().start()
            # Launch headless Chromium for stealth
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                slow_mo=self.config.slow_mo_ms,
                args=[
                    '--disable-blink-features=AutomationControlled',  # Hide automation signature
                    '--disable-dev-shm-usage',  # Use /tmp instead of shared memory
                ]
            )
            # Create a context with user agent to mimic real browser
            context_kwargs = {
                "user_agent": USER_AGENT,
                "viewport": {
                    "width": random.randint(*VIEWPORT_WIDTH_RANGE),
                    "height": random.randint(*VIEWPORT_HEIGHT_RANGE)
                },
                "locale": "en-US",
                "timezone_id": "America/New_York"
            }
            
            # Add proxy if rotator is available
            if self.proxy_rotator:
                proxy_config = self.proxy_rotator.get_next_proxy()
                if proxy_config:
                    context_kwargs["proxy"] = proxy_config.to_playwright_format()
                    self.logger.info(f"Using proxy: {proxy_config}")
            
            # Load storage state if available
            if self.config.storage_state_path and os.path.isfile(self.config.storage_state_path):
                context_kwargs["storage_state"] = self.config.storage_state_path
                self.logger.info("Loaded storage state for session reuse.")
            
            self.browser_context = await self.browser.new_context(**context_kwargs)
            self.page = await self.browser_context.new_page()
            
            # Add stealth scripts to hide automation
            await self._apply_stealth_scripts()
            
            self.logger.info("Playwright browser setup successfully.")
        except Exception as e:
            self.logger.error(f"Failed to setup Playwright browser: {e}")
            raise

    def _is_browser_alive(self) -> bool:
        """Check if browser, context, and page are still open."""
        try:
            if not self.browser or not self.browser_context or not self.page:
                return False
            # Check if browser is still connected
            if not self.browser.is_connected():
                return False
            return True
        except Exception:
            return False

    async def _apply_stealth_scripts(self):
        """Apply JavaScript to hide automation markers."""
        try:
            # Remove webdriver flag
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # Mock plugins
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            # Mock languages
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            # Hide Chrome automation extension
            await self.page.add_init_script("""
                window.chrome = {
                    runtime: {}
                };
            """)
            
            self.logger.debug("Applied stealth scripts to hide automation markers")
        except Exception as e:
            self.logger.warning(f"Failed to apply stealth scripts: {e}")

    async def _perform_random_mouse_movements(self):
        """Perform random mouse movements to simulate human behavior."""
        try:
            # Get viewport size
            viewport_size = self.page.viewport_size
            if not viewport_size:
                viewport_size = {'width': 1280, 'height': 720}  # Default size
            
            # Perform 2-4 random mouse movements
            num_movements = random.randint(2, 4)
            self.logger.debug(f"Performing {num_movements} random mouse movements")
            
            for i in range(num_movements):
                # Generate random position within viewport
                x = random.randint(100, viewport_size['width'] - 100)
                y = random.randint(100, viewport_size['height'] - 100)
                
                # Move mouse with smooth animation
                await self.page.mouse.move(x, y, steps=random.randint(10, 20))
                
                # Random pause between movements (50-300ms)
                await asyncio.sleep(random.uniform(0.05, 0.3))
                
        except Exception as e:
            self.logger.debug(f"Random mouse movement error (non-critical): {e}")

    async def _ensure_browser_ready(self):
        """Ensure browser is ready, recreate if needed."""
        if not self._is_browser_alive():
            self.logger.warning("Browser is not alive, setting up new browser instance...")
            try:
                # Clean up old references
                await self._close_browser()
            except Exception as cleanup_error:
                self.logger.debug(f"Error during cleanup: {cleanup_error}")
            # Set up fresh browser
            await self._setup_browser()

    async def _close_browser(self):
        """Gracefully close the browser and context."""
        try:
            if self.page:
                await self.page.close()
            if self.browser_context:
                if self.config.storage_state_path:
                    try:
                        await self.browser_context.storage_state(path=self.config.storage_state_path)
                        self.logger.info("Saved storage state for session reuse.")
                    except Exception as storage_error:
                        self.logger.warning(f"Failed to save storage state: {storage_error}")
                await self.browser_context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("Playwright browser closed successfully.")
        except Exception as e:
            self.logger.error(f"Error closing Playwright browser: {e}")

    def _wait_for_connection(self, retry_seconds: int = 5) -> bool:
        """Block until internet is available or stop_event is set. Returns True when connected, False if stopped."""
        while not self.stop_event.is_set():
            if is_connected():
                self.logger.info("Network connectivity available.")
                return True
            self.logger.warning(f"No internet connectivity detected. Retrying in {retry_seconds} seconds...")
            # Use stop_event.wait() instead of time.sleep() for better responsiveness
            if self.stop_event.wait(timeout=retry_seconds):
                break
        self.logger.info("Stop requested while waiting for network; aborting wait.")
        return False

    async def get_current_points(self):
        """Fetches the current rewards points from the rewards page."""
        try:
            if not is_connected():
                self.logger.warning("No internet connection detected. Waiting...")
                if not self._wait_for_connection():
                    return self.last_points
            
            # Ensure browser is ready (creates new if closed)
            await self._ensure_browser_ready()
            
            self.logger.info(f"Navigating to rewards URL: {self.config.rewards_url}")
            await self.page.goto(self.config.rewards_url, wait_until='networkidle', timeout=30000)
            
            # Add realistic human delay before parsing
            await self.page.wait_for_timeout(random.uniform(2000, 4000))
            
            # Try multiple selectors with fallback chain
            selectors = [
                ("xpath", self.config.points_xpath),
                ("css", "mee-rewards-user-points-details p"),
                ("css", "[class*='points'] p"),
                ("text", "Available points")  # Text-based fallback
            ]
            
            points_text = None
            successful_selector = None
            
            for selector_type, selector in selectors:
                try:
                    if selector_type == "xpath":
                        points_element = self.page.locator(f"xpath={selector}").first
                    elif selector_type == "css":
                        points_element = self.page.locator(selector).first
                    elif selector_type == "text":
                        # Search for element containing text
                        points_element = self.page.get_by_text(selector, exact=False).first
                    
                    points_text = await points_element.text_content(timeout=5000)
                    
                    if points_text:
                        successful_selector = f"{selector_type}: {selector}"
                        self.logger.debug(f"Successfully extracted points using {successful_selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Selector {selector_type}='{selector}' failed: {e}")
                    continue
            
            if not points_text:
                self.logger.warning("All selectors failed to extract points")
                return self.last_points
            
            self.logger.debug(f"Raw points text from {successful_selector}: '{points_text}'")
            
            # Extract FIRST number (matching reference implementation)
            match = re.search(r'\d+', points_text)
            
            if match:
                points = int(match.group())
                self.logger.info(f"Current rewards points: {points} (extracted via {successful_selector})")
                return points
            else:
                self.logger.warning(f"Could not parse points from text: '{points_text}'")
                return self.last_points
                
        except PlaywrightError as e:
            # Browser was closed or connection lost
            if "closed" in str(e).lower():
                self.logger.warning("Browser was closed, will recreate on next attempt.")
                self.page = None
                self.browser_context = None
                self.browser = None
            else:
                self.logger.error(f"Playwright error while getting points: {e}", exc_info=True)
            return self.last_points
        except Exception as e:
            self.logger.error(f"Error while getting points: {e}", exc_info=True)
            return self.last_points

    async def _perform_search(self, term: str) -> None:
        """Performs a single search on Bing with exponential backoff retry."""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            backoff_delay = INITIAL_BACKOFF_SECONDS * (2 ** attempt)  # Exponential: 2s, 4s, 8s
            
            try:
                if not is_connected():
                    self.logger.warning("No internet connection before search. Waiting...")
                    if not self._wait_for_connection():
                        return
                
                # Ensure browser is ready before searching
                await self._ensure_browser_ready()
                
                self.logger.info(f"Navigating to search URL (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS})")
                await self.page.goto(self.config.search_url, wait_until='networkidle')
                
                # Add human-like random delay before typing
                await self.page.wait_for_timeout(random.uniform(500, 2000))
                
                # Perform random mouse movements if enabled (adds human-like behavior)
                if self.random_mouse_movements:
                    await self._perform_random_mouse_movements()
                
                # Find search box and type the term with human-like typing speed
                search_box = self.page.locator(f"input[name='{self.config.search_box_name}']").first
                await search_box.click()
                
                # Add small delay after click (human reaction time)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Use human typing with mistake simulation
                await self.human_typer.type_like_human(
                    search_box, 
                    term, 
                    simulate_mistakes=self.config.simulate_mistakes
                )
                
                # Brief pause before pressing Enter (human thinking time)
                await asyncio.sleep(random.uniform(0.3, 0.8))
                
                # Press Enter
                await search_box.press('Enter')
                self.logger.info(f"Performed search for term: '{term}'")
                
                # Wait for page to fully load with human-like thinking time
                await self.page.wait_for_timeout(random.uniform(self.config.min_sleep_seconds * 1000, self.config.max_sleep_seconds * 1000))
                return
                
            except PlaywrightError as e:
                # Browser might have been closed (retryable)
                if "closed" in str(e).lower():
                    self.logger.warning(f"Browser was closed during search attempt {attempt + 1}. Marking for recreation.")
                    self.page = None
                    self.browser_context = None
                    self.browser = None
                    if attempt < MAX_RETRY_ATTEMPTS - 1:
                        self.logger.info(f"Retrying in {backoff_delay}s (exponential backoff)...")
                        await asyncio.sleep(backoff_delay)
                        continue
                self.logger.warning(f"Playwright error on attempt {attempt + 1} for term '{term}': {e}")
                if attempt == MAX_RETRY_ATTEMPTS - 1:
                    self.logger.error(f"All retries exhausted for term '{term}'.")
                    raise
                self.logger.info(f"Retrying in {backoff_delay}s (exponential backoff)...")
                await asyncio.sleep(backoff_delay)
            except Exception as e:
                self.logger.warning(f"Search attempt {attempt + 1} failed for term '{term}': {e}")
                if attempt == MAX_RETRY_ATTEMPTS - 1:
                    self.logger.error(f"All retries exhausted for term '{term}'.")
                    raise
                self.logger.info(f"Retrying in {backoff_delay}s (exponential backoff)...")
                await asyncio.sleep(backoff_delay)

    def start_searching(self):
        """Starts the search loop in a new thread."""
        self.logger.info("Starting search process...")
        # Reset data manager to clear completion flags from previous run
        self.data_manager.reset()
        self.stop_event.clear()
        self.running = True
        threading.Thread(target=self._search_loop_thread, daemon=True).start()

    def _search_loop_thread(self):
        """Wrapper to run async search loop in a thread."""
        try:
            asyncio.run(self._search_loop())
        except Exception as e:
            self.logger.critical(f"Error in search loop thread: {e}", exc_info=True)
        finally:
            self.running = False

    async def _search_loop(self):
        """The main loop for performing searches until the target is met."""
        try:
            await self._setup_browser()
            initial_points = await self.get_current_points()
            self.data_manager.rewards_points = initial_points
            self.last_points = initial_points  # Set initial value for comparison
            
            # Display initial points in GUI
            if self.gui:
                self.gui.update_rewards_label(initial_points)

            unchanged_points_counter = 0

            while self.running and await self.get_current_points() < self.config.target_points:
                if self.stop_event.is_set():
                    self.logger.info("Stop event received, exiting search loop.")
                    break

                # Get next topic from injected provider
                term = self.topics_provider.get_next_topic()

                if self.gui:
                    self.gui.set_current_topic(term)

                # Record search start time for metrics
                search_start_time = time.time()
                points_before_search = await self.get_current_points()
                
                try:
                    await self._perform_search(term)
                    current_points = await self.get_current_points()
                    self.data_manager.update_rewards(current_points)
                    self.data_manager.add_search(term, current_points)
                    
                    # Calculate search duration and points gained
                    search_duration_ms = (time.time() - search_start_time) * 1000
                    points_gained = max(0, current_points - points_before_search)
                    
                    # Record successful search in metrics
                    if self.metrics_collector:
                        self.metrics_collector.record_search_duration(search_duration_ms, points_gained)
                    
                    # Update GUI immediately with new points and search count
                    if self.gui:
                        self.gui.update_rewards_label(current_points)
                        counts = self.data_manager.get_current_counts()
                        self.gui.update_total_label(counts['total'])
                        
                except Exception as e:
                    self.logger.error(f"Search failed for term '{term}': {e}")
                    current_points = await self.get_current_points()
                    # Record failed search in metrics
                    if self.metrics_collector:
                        self.metrics_collector.record_error(type(e).__name__)
                    # Continue to next search
                    continue

                if current_points > self.last_points:
                    self.last_points = current_points
                    unchanged_points_counter = 0
                elif current_points == self.last_points:
                    unchanged_points_counter += 1
                    if unchanged_points_counter >= self.config.searches_before_pause:
                        # Smart pause: calculate adaptive pause duration based on velocity
                        base_pause_seconds = self.config.pause_duration_minutes * 60
                        # For each unsuccessful search beyond the threshold, add 10% more pause time
                        extra_pause_factor = 1 + (unchanged_points_counter - self.config.searches_before_pause) * 0.1
                        adaptive_pause = int(base_pause_seconds * extra_pause_factor)
                        # Cap at 5x the base pause duration
                        adaptive_pause = min(adaptive_pause, base_pause_seconds * 5)
                        
                        self.logger.info(
                            f"Rewards points unchanged for {unchanged_points_counter} searches. "
                            f"Pausing for {adaptive_pause}s (adaptive: {extra_pause_factor:.1f}x base)..."
                        )
                        if self.gui:
                            self.gui.set_pause_timer(adaptive_pause)
                        await self.page.wait_for_timeout(adaptive_pause * 1000)
                        unchanged_points_counter = 0
                else:
                    self.last_points = current_points
                    unchanged_points_counter = 0

                # Human-like delay between searches with random mini-pauses
                base_sleep = random.uniform(self.config.min_sleep_seconds, self.config.max_sleep_seconds)
                # Occasionally add extra pause for more human-like behavior (20% chance)
                if random.random() < 0.2:
                    extra_pause = random.uniform(5, 15)
                    self.logger.debug(f"Adding mini-pause of {extra_pause:.1f}s for natural behavior")
                    base_sleep += extra_pause
                
                await self.page.wait_for_timeout(base_sleep * 1000)

        except Exception as e:
            self.logger.critical(f"A critical error occurred in the search loop: {e}", exc_info=True)
        finally:
            current_points = None
            try:
                current_points = await self.get_current_points()
                if current_points >= self.config.target_points:
                    elapsed = elapsed_timer.stop()
                    self.logger.info(
                        f"Target reached (points={current_points}). Elapsed time: {elapsed:.1f} seconds"
                    )
            except Exception:
                pass
            
            self.logger.info("Search loop finished.")
            self.running = False
            
            try:
                await self._close_browser()
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            
            self.data_manager.mark_loop_complete()
            if current_points is None:
                try:
                    current_points = await self.get_current_points()
                except Exception:
                    current_points = None

            if current_points is not None and current_points >= self.config.target_points:
                self.data_manager.mark_rewards_complete()

    def stop_searching(self):
        """Stops the search loop gracefully."""
        self.logger.info("Stop searching requested.")
        self.running = False
        self.stop_event.set()
