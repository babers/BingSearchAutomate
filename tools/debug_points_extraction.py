#!/usr/bin/env python3
"""
Debug tool for testing points extraction from rewards page.
Usage: python tools/debug_points_extraction.py
"""

import asyncio
import re
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from utils.network import is_connected, wait_for_connection


async def test_points_extraction():
    """Test the points extraction logic."""
    print("=" * 60)
    print("Bing Rewards Points Extraction Diagnostic Tool")
    print("=" * 60)
    
    # Load configuration
    config = Config.from_yaml()
    print(f"\n[CONFIG] Rewards URL: {config.rewards_url}")
    print(f"[CONFIG] Points XPath: {config.points_xpath}")
    
    # Check network connectivity
    print("\n[NETWORK] Checking internet connectivity...")
    if not is_connected():
        print("[NETWORK] No internet detected. Waiting for connection...")
        wait_for_connection()
    print("[NETWORK] Connected!")
    
    # Import Playwright
    try:
        from playwright.async_api import async_playwright
        print("[PLAYWRIGHT] Importing Playwright... OK")
    except Exception as e:
        print(f"[ERROR] Failed to import Playwright: {e}")
        return
    
    # Launch browser and test extraction
    async with async_playwright() as p:
        try:
            print("\n[BROWSER] Launching Chromium...")
            browser = await p.chromium.launch(headless=False)  # headless=False for visual confirmation
            context = await browser.new_context()
            page = await context.new_page()
            
            print(f"[BROWSER] Navigating to {config.rewards_url}...")
            await page.goto(config.rewards_url, wait_until='networkidle', timeout=30000)
            
            print("[BROWSER] Waiting for page to stabilize...")
            await page.wait_for_timeout(3000)
            
            # Take a screenshot
            screenshot_path = "debug_rewards_page.png"
            print(f"[SCREENSHOT] Taking screenshot and saving to {screenshot_path}...")
            await page.screenshot(path=screenshot_path)
            print(f"[SCREENSHOT] Screenshot saved!")
            
            # Test primary extraction method
            print("\n[EXTRACTION] Testing primary XPath method...")
            try:
                locator = page.locator(f"xpath={config.points_xpath}").first
                points_text = await locator.text_content()
                print(f"[EXTRACTION] Raw text: '{points_text}'")
                
                # Clean and extract
                cleaned_text = points_text.replace(',', '').strip()
                print(f"[EXTRACTION] Cleaned text: '{cleaned_text}'")
                
                numbers = re.findall(r'\d+', cleaned_text)
                print(f"[EXTRACTION] All numbers found: {numbers}")
                
                if numbers:
                    points = int(max(numbers))
                    print(f"[EXTRACTION] ✓ Extracted points (max): {points}")
                else:
                    print(f"[EXTRACTION] ✗ No numbers extracted!")
                    
            except Exception as e:
                print(f"[EXTRACTION] ✗ Error with primary method: {e}")
            
            # Test alternate method (full page search)
            print("\n[EXTRACTION] Testing alternate method (page content search)...")
            try:
                all_text = await page.content()
                # Look for pattern like "1234 points" or similar
                patterns = [
                    r'(\d+)\s*(?:points?|pts?)',  # X points/pts
                    r'(\d+)\s*(?:<!--)',  # X followed by comment
                    r'>"(\d+)<',  # >NUMBER<
                ]
                
                found_any = False
                for pattern in patterns:
                    matches = re.findall(pattern, all_text, re.IGNORECASE)
                    if matches:
                        print(f"[EXTRACTION] Pattern '{pattern[:30]}...' found: {matches[:3]}")
                        found_any = True
                
                if not found_any:
                    print(f"[EXTRACTION] ✗ No patterns matched in page content")
                    
            except Exception as e:
                print(f"[EXTRACTION] ✗ Error with alternate method: {e}")
            
            # Try to find all text elements
            print("\n[DEBUG] Attempting to find potential points elements...")
            try:
                elements = await page.query_selector_all('p, span, div, [class*="point"], [id*="point"]')
                print(f"[DEBUG] Found {len(elements)} elements with point-like names/tags")
                
                # Sample first 10 elements
                for i, elem in enumerate(elements[:10]):
                    text = await elem.text_content()
                    if text and len(text.strip()) > 0:
                        print(f"  [{i}] {text.strip()[:100]}")
                        
            except Exception as e:
                print(f"[DEBUG] Error scanning elements: {e}")
            
            print("\n" + "=" * 60)
            print("Manual Inspection:")
            print("1. Check the screenshot 'debug_rewards_page.png' in the project root")
            print("2. Right-click on the points display and select 'Inspect Element'")
            print("3. Look for the element's XPath or ID")
            print("4. Update config.yaml with the correct XPath if needed")
            print("=" * 60)
            
            # Keep browser open for manual inspection
            print("\n[INFO] Browser is still open. You can manually inspect the page.")
            print("Press Ctrl+C to close the browser and exit.")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n[BROWSER] Closing browser...")
            
            await browser.close()
            
        except Exception as e:
            print(f"[ERROR] {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(test_points_extraction())
    except KeyboardInterrupt:
        print("\n[CANCELLED] Diagnostic cancelled by user.")
    except Exception as e:
        print(f"[FATAL] {e}", exc_info=True)
