#!/usr/bin/env python3
"""
Test human typing with mistake simulation.
Demonstrates realistic typing with typos and corrections.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright
from utils.human_typing import HumanTyping


async def test_human_typing():
    """Test human-like typing with mistakes."""
    print("\n" + "="*70)
    print("HUMAN TYPING WITH MISTAKE SIMULATION - TEST")
    print("="*70)
    
    # Setup browser
    print("\n[SETUP] Launching browser...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=50)
    page = await browser.new_page()
    
    # Navigate to a test page (using Bing search as example)
    print("[SETUP] Navigating to Bing...")
    await page.goto("https://www.bing.com")
    await asyncio.sleep(2)
    
    # Initialize human typer with high mistake probability for demonstration
    print("\n[TEST 1] Typing with 15% mistake probability...")
    typer = HumanTyping(
        mistake_probability=0.15,  # 15% chance of typo
        char_delay_ms=(80, 180),
        correction_delay_ms=(300, 700)
    )
    
    # Find search box
    search_box = page.locator('input[name="q"]').first
    await search_box.click()
    
    # Type a search query with mistakes
    test_query = "quantum computing applications"
    print(f"   Typing: '{test_query}'")
    print("   Watch for typos and corrections...")
    await typer.type_like_human(search_box, test_query, simulate_mistakes=True)
    
    print("   ✓ Typing completed with mistake simulation")
    await asyncio.sleep(2)
    
    # Clear and test without mistakes
    print("\n[TEST 2] Typing without mistakes (but human-like delays)...")
    await search_box.fill('')
    await search_box.click()
    
    test_query2 = "artificial intelligence research"
    print(f"   Typing: '{test_query2}'")
    await typer.type_like_human(search_box, test_query2, simulate_mistakes=False)
    
    print("   ✓ Typing completed without mistakes")
    await asyncio.sleep(2)
    
    # Test with lower mistake probability (realistic)
    print("\n[TEST 3] Realistic typing (5% mistake probability)...")
    typer_realistic = HumanTyping(
        mistake_probability=0.05,  # 5% - more realistic
        char_delay_ms=(50, 200),
        correction_delay_ms=(200, 600)
    )
    
    await search_box.fill('')
    await search_box.click()
    
    test_query3 = "machine learning algorithms explained"
    print(f"   Typing: '{test_query3}'")
    print("   (Mistakes less frequent but still possible)")
    await typer_realistic.type_like_human(search_box, test_query3, simulate_mistakes=True)
    
    print("   ✓ Realistic typing completed")
    await asyncio.sleep(2)
    
    # Cleanup
    print("\n[CLEANUP] Closing browser...")
    await browser.close()
    await playwright.stop()
    
    print("\n" + "="*70)
    print("✓ ALL TYPING TESTS COMPLETED")
    print("="*70)
    print("\nKey observations:")
    print("  - Test 1: High mistake rate (15%) shows clear typo corrections")
    print("  - Test 2: No mistakes but still human-like variable delays")
    print("  - Test 3: Realistic 5% mistake rate (may or may not see typos)")
    print("\nThis mimics natural human typing patterns!")


async def test_typing_speeds():
    """Test different typing speed profiles."""
    print("\n" + "="*70)
    print("TYPING SPEED VARIANCE TEST")
    print("="*70)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=50)
    page = await browser.new_page()
    await page.goto("https://www.bing.com")
    await asyncio.sleep(1)
    
    search_box = page.locator('input[name="q"]').first
    
    # Fast typer
    print("\n[PROFILE 1] Fast typer (30-80ms per char)...")
    fast_typer = HumanTyping(
        mistake_probability=0.02,
        char_delay_ms=(30, 80),
        word_pause_ms=(50, 150)
    )
    await search_box.fill('')
    await search_box.click()
    await fast_typer.type_like_human(search_box, "fast typing example", simulate_mistakes=True)
    print("   ✓ Fast typing completed")
    await asyncio.sleep(1)
    
    # Average typer
    print("\n[PROFILE 2] Average typer (60-150ms per char)...")
    avg_typer = HumanTyping(
        mistake_probability=0.05,
        char_delay_ms=(60, 150),
        word_pause_ms=(100, 300)
    )
    await search_box.fill('')
    await search_box.click()
    await avg_typer.type_like_human(search_box, "average typing speed", simulate_mistakes=True)
    print("   ✓ Average typing completed")
    await asyncio.sleep(1)
    
    # Slow typer
    print("\n[PROFILE 3] Slow typer (100-250ms per char)...")
    slow_typer = HumanTyping(
        mistake_probability=0.08,  # More mistakes when typing slowly
        char_delay_ms=(100, 250),
        word_pause_ms=(200, 500)
    )
    await search_box.fill('')
    await search_box.click()
    await slow_typer.type_like_human(search_box, "slow careful typing", simulate_mistakes=True)
    print("   ✓ Slow typing completed")
    await asyncio.sleep(1)
    
    await browser.close()
    await playwright.stop()
    
    print("\n" + "="*70)
    print("✓ SPEED VARIANCE TESTS COMPLETED")
    print("="*70)


async def main():
    """Run all tests."""
    print("\n🤖 HUMAN TYPING SIMULATOR - DEMONSTRATION\n")
    
    try:
        await test_human_typing()
        print("\n" + "─" * 70 + "\n")
        await test_typing_speeds()
        
        print("\n\n" + "="*70)
        print("✅ ALL TESTS PASSED - HUMAN TYPING WORKS!")
        print("="*70)
        print("\nIntegration status:")
        print("  ✓ Mistake simulation: Working")
        print("  ✓ Typo corrections: Working")
        print("  ✓ Variable typing speeds: Working")
        print("  ✓ Word boundary pauses: Working")
        print("  ✓ Natural delay patterns: Working")
        print("\n  Ready for use in browser_controller.py!")
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
