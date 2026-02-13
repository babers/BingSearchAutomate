#!/usr/bin/env python3
"""
Detailed debug tool to inspect XPath extraction on the Bing rewards page.
This tool opens the page and shows exactly what the XPath is returning.
"""

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from utils.network import is_connected, wait_for_connection


async def inspect_xpath_extraction():
    """Inspect the exact XPath extraction."""
    print("=" * 70)
    print("Bing Rewards Points - XPath Extraction Inspector")
    print("=" * 70)
    
    config = Config.from_yaml()
    print(f"\n[CONFIG]")
    print(f"  Rewards URL: {config.rewards_url}")
    print(f"  Points XPath: {config.points_xpath}")
    
    # Check network
    print(f"\n[NETWORK] Checking connectivity...", end=" ")
    if not is_connected():
        print("NOT CONNECTED. Waiting...")
        wait_for_connection()
    print("OK")
    
    # Import Playwright
    try:
        from playwright.async_api import async_playwright
    except Exception as e:
        print(f"\n[ERROR] Failed to import Playwright: {e}")
        return
    
    async with async_playwright() as p:
        try:
            print(f"\n[BROWSER] Launching Chromium...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"[BROWSER] Navigating to rewards page...")
            await page.goto(config.rewards_url, wait_until='networkidle', timeout=30000)
            
            print(f"[BROWSER] Page loaded. Waiting 3 seconds for content to stabilize...")
            await page.wait_for_timeout(3000)
            
            # Test the XPath extraction
            print(f"\n[EXTRACTION] Testing XPath: {config.points_xpath}")
            print("-" * 70)
            
            try:
                # Get the element using the XPath
                locator = page.locator(f"xpath={config.points_xpath}").first
                
                # Get raw text content
                points_text = await locator.text_content()
                print(f"Raw text from XPath:")
                print(f"  Value: '{points_text}'")
                print(f"  Length: {len(points_text)} chars")
                print(f"  Repr: {repr(points_text)}")
                
                # Apply the extraction logic (FIRST number)
                print(f"\n[LOGIC] Applying extraction logic:")
                match = re.search(r'\d+', points_text)
                
                if match:
                    points = int(match.group())
                    print(f"  Regex search result: FOUND")
                    print(f"  First number: {match.group()}")
                    print(f"  Extracted points: {points}")
                    print(f"  ✓ SUCCESS: Got {points}")
                else:
                    print(f"  Regex search result: NOT FOUND")
                    print(f"  ✗ FAILED: No numbers matched")
                    
                    # Try to understand what's in the text
                    print(f"\n[DEBUG] Analyzing text content:")
                    print(f"  Is empty?: {len(points_text.strip()) == 0}")
                    print(f"  Contains digits?: {any(c.isdigit() for c in points_text)}")
                    
                    # Show character breakdown
                    print(f"\n[DEBUG] Character breakdown:")
                    for i, char in enumerate(points_text[:100]):  # First 100 chars
                        if char == '\n':
                            print(f"    [{i}] '\\n' (newline)")
                        elif char == ' ':
                            print(f"    [{i}] ' ' (space)")
                        elif char.isdigit():
                            print(f"    [{i}] '{char}' (DIGIT)")
                        else:
                            print(f"    [{i}] '{char}'")
                
                # Also get HTML to understand structure
                print(f"\n[HTML] Element HTML structure:")
                html = await locator.evaluate("el => el.outerHTML")
                print(html[:500])  # First 500 chars of HTML
                
                # Take screenshot for visual inspection
                print(f"\n[SCREENSHOT] Taking screenshot...")
                await page.screenshot(path="xpath_inspection.png")
                print(f"  Saved to: xpath_inspection.png")
                
                # Try to get the parent element to understand context
                print(f"\n[PARENT] Inspecting parent elements...")
                parent_html = await locator.evaluate("el => el.parentElement?.outerHTML")
                if parent_html:
                    print(f"  Parent HTML: {parent_html[:300]}")
                
            except Exception as e:
                print(f"\n[ERROR] Failed to extract using XPath: {e}")
                print(f"  This suggests the XPath might be incorrect or outdated")
                
                # Try to find alternative selectors
                print(f"\n[FALLBACK] Attempting to find alternatives...")
                
                # Look for any element with "point" in id or class
                try:
                    elements = await page.query_selector_all('[id*="point"], [class*="point"]')
                    print(f"  Found {len(elements)} elements with 'point' in id/class")
                    
                    for i, el in enumerate(elements[:5]):
                        text = await el.text_content()
                        if text and len(text.strip()) > 0:
                            print(f"    [{i}] '{text.strip()[:60]}'")
                except Exception as alt_e:
                    print(f"  Fallback search failed: {alt_e}")
            
            await browser.close()
            
            print("\n" + "=" * 70)
            print("Note: Check xpath_inspection.png for visual confirmation")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n[FATAL ERROR] {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(inspect_xpath_extraction())
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Inspection cancelled by user")
    except Exception as e:
        print(f"\n[FATAL] {e}", exc_info=True)
