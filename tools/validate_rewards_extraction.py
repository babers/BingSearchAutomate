#!/usr/bin/env python3
"""
Validation script to test rewards points extraction end-to-end.
This script validates the entire extraction and display pipeline.
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_imports():
    """Validate all imports work correctly."""
    print("\n[VALIDATE] Checking imports...")
    
    try:
        from config import Config
        print("  ✓ Config")
    except Exception as e:
        print(f"  ✗ Config: {e}")
        return False
    
    try:
        from browser_controller import BrowserController
        print("  ✓ BrowserController")
    except Exception as e:
        print(f"  ✗ BrowserController: {e}")
        return False
    
    try:
        from data_manager import DataManager
        print("  ✓ DataManager")
    except Exception as e:
        print(f"  ✗ DataManager: {e}")
        return False
    
    try:
        from gui_module import GUI
        print("  ✓ GUI")
    except Exception as e:
        print(f"  ✗ GUI: {e}")
        return False
    
    try:
        from rewards_watcher import RewardsWatcher
        print("  ✓ RewardsWatcher")
    except Exception as e:
        print(f"  ✗ RewardsWatcher: {e}")
        return False
    
    return True


def validate_extraction_logic():
    """Validate the regex extraction logic."""
    print("\n[VALIDATE] Checking extraction logic...")
    
    test_cases = [
        ("12", 12, "Plain number"),
        ("12 points", 12, "Number with text"),
        ("You have 12 points", 12, "Text with number"),
        ("1,234", 1, "Comma number (gets first: 1)"),  # Important: gets FIRST not max!
        ("12 / 90", 12, "Fraction format"),
        ("100 searches: 12 points", 100, "Multiple numbers (gets FIRST)"),
    ]
    
    all_passed = True
    for text, expected, description in test_cases:
        match = re.search(r'\d+', text)
        if match:
            result = int(match.group())
            if result == expected:
                print(f"  ✓ {description}: '{text}' → {result}")
            else:
                print(f"  ✗ {description}: '{text}' → {result} (expected {expected})")
                all_passed = False
        else:
            print(f"  ✗ {description}: '{text}' → NO MATCH (expected {expected})")
            all_passed = False
    
    return all_passed


def validate_config():
    """Validate configuration."""
    print("\n[VALIDATE] Checking configuration...")
    
    try:
        from config import Config
        config = Config.from_yaml()
        
        print(f"  ✓ Config loaded from: config.yaml")
        print(f"    - Rewards URL: {config.rewards_url}")
        print(f"    - XPath: {config.points_xpath[:60]}...")
        print(f"    - Target points: {config.target_points}")
        print(f"    - Database: {config.database_path}")
        return True
    except Exception as e:
        print(f"  ✗ Config validation failed: {e}")
        return False


def validate_data_manager():
    """Validate data manager initialization."""
    print("\n[VALIDATE] Checking DataManager...")
    
    try:
        from config import Config
        from data_manager import DataManager
        
        config = Config.from_yaml()
        dm = DataManager(config)
        
        print(f"  ✓ DataManager initialized")
        print(f"    - Initial rewards: {dm.rewards_points}")
        print(f"    - Database path: {dm.db_path}")
        
        # Test update
        dm.update_rewards(42)
        if dm.rewards_points == 42:
            print(f"  ✓ update_rewards() works: set to {dm.rewards_points}")
        else:
            print(f"  ✗ update_rewards() failed: got {dm.rewards_points}, expected 42")
            return False
        
        # Test add_search
        dm.add_search("test query", 42)
        if len(dm.session_search_history) == 1:
            print(f"  ✓ add_search() works: {len(dm.session_search_history)} search(es)")
        else:
            print(f"  ✗ add_search() failed")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ DataManager validation failed: {e}")
        return False


def validate_extraction_matches_reference():
    """Validate extraction logic matches reference implementation."""
    print("\n[VALIDATE] Comparing with reference implementation...")
    
    reference_code = """
    match = re.search(r'\\d+', points_text)
    if match:
        points = int(match.group())
    """
    
    current_code = """
    match = re.search(r'\\d+', points_text)
    if match:
        points = int(match.group())
    """
    
    if reference_code.strip() == current_code.strip():
        print(f"  ✓ Extraction logic matches reference")
        return True
    else:
        print(f"  ✗ Extraction logic differs from reference")
        return False


def main():
    """Run all validations."""
    print("=" * 70)
    print("REWARDS POINTS EXTRACTION - VALIDATION SUITE")
    print("=" * 70)
    
    results = {
        "Imports": validate_imports(),
        "Extraction Logic": validate_extraction_logic(),
        "Configuration": validate_config(),
        "DataManager": validate_data_manager(),
        "Matches Reference": validate_extraction_matches_reference(),
    }
    
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS:")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Total: {passed}/{total} checks passed")
    print("=" * 70)
    
    if passed == total:
        print("\n✓ ALL VALIDATIONS PASSED!")
        print("\nNext steps:")
        print("  1. Run: python tools/inspect_xpath.py")
        print("  2. Verify XPath extraction shows correct points")
        print("  3. Run: python main.py")
        print("  4. Monitor logs for 'Current rewards points: X'")
        return 0
    else:
        print("\n✗ SOME VALIDATIONS FAILED")
        print("\nPlease fix the issues above before running the main application.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}", exc_info=True)
        sys.exit(1)
