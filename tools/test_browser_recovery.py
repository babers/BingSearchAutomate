#!/usr/bin/env python3
"""
Test browser recovery when manually closed.
This simulates what happens when the browser window is closed by the user.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from data_manager import DataManager
from browser_controller import BrowserController


async def test_recovery():
    """Test that browser can recover from being closed."""
    print("\n" + "="*70)
    print("BROWSER RECOVERY TEST")
    print("="*70)
    
    # Setup
    config = Config.from_yaml()
    data_manager = DataManager(config)
    controller = BrowserController(config, data_manager, gui=None)
    
    print("\n[TEST 1] Initial browser setup and points fetch...")
    try:
        points1 = await controller.get_current_points()
        print(f"✓ First fetch successful: {points1} points")
    except Exception as e:
        print(f"✗ First fetch failed: {e}")
        return False
    
    print("\n[TEST 2] Simulating browser closure...")
    # Simulate manual browser close
    await controller._close_browser()
    controller.page = None
    controller.browser_context = None
    controller.browser = None
    print("✓ Browser closed")
    
    print("\n[TEST 3] Attempting to fetch points after closure...")
    print("  (This should auto-recover by creating new browser)")
    try:
        points2 = await controller.get_current_points()
        print(f"✓ Auto-recovery successful: {points2} points")
    except Exception as e:
        print(f"✗ Auto-recovery failed: {e}")
        return False
    
    print("\n[TEST 4] Verifying browser is working normally...")
    try:
        points3 = await controller.get_current_points()
        print(f"✓ Third fetch successful: {points3} points")
    except Exception as e:
        print(f"✗ Third fetch failed: {e}")
        return False
    
    # Cleanup
    print("\n[CLEANUP] Closing browser...")
    await controller._close_browser()
    print("✓ Browser closed cleanly")
    
    print("\n" + "="*70)
    print("✓ ALL RECOVERY TESTS PASSED")
    print("="*70)
    print("\nThe browser can now automatically recover if manually closed!")
    return True


async def main():
    """Run the test."""
    try:
        success = await test_recovery()
        return 0 if success else 1
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
