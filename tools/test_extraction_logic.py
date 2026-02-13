#!/usr/bin/env python3
"""
Test the points extraction regex and logic.
Usage: python tools/test_extraction_logic.py
"""

import re


def test_extraction(text, description):
    """Test extraction logic on a given text."""
    print(f"\nTest: {description}")
    print(f"Input: '{text}'")
    
    # Clean the text: remove commas, extra whitespace
    cleaned_text = text.replace(',', '').strip()
    print(f"Cleaned: '{cleaned_text}'")
    
    # Extract all numbers from the text
    numbers = re.findall(r'\d+', cleaned_text)
    print(f"Numbers found: {numbers}")
    
    if numbers:
        # Get the largest number as it's likely the total points
        points = int(max(numbers))
        print(f"Result: {points} (using max)")
    else:
        print(f"Result: ERROR - no numbers found")
    
    print("-" * 40)


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Points Extraction Logic")
    print("=" * 60)
    
    # Test various formats that might appear
    test_cases = [
        ("1,234", "Comma-separated number"),
        ("1234", "Plain number"),
        ("1,234 points", "Number with text"),
        ("You have 1,234 points", "Text before number"),
        ("1,234\nPoints", "Number with newline"),
        ("123 45", "Multiple numbers (should pick 45)"),
        ("100 of 1,234", "Multiple numbers with text"),
        ("1,234 / 5,000", "Fraction-like numbers"),
        ("<p>1,234</p>", "HTML tags"),
        ("   1,234   ", "Extra spaces"),
        ("Today: 50 Searches: 100 Points: 1,234", "Multiple values"),
    ]
    
    for text, description in test_cases:
        test_extraction(text, description)
    
    print("\n" + "=" * 60)
    print("Notes:")
    print("- The extraction picks the LARGEST number")
    print("- This assumes the total points is the biggest number in the text")
    print("- Adjust the logic if needed based on actual page structure")
    print("=" * 60)
