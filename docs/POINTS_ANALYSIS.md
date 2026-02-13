# Rewards Points Display - Analysis and Fixes

## Issue Analysis

The rewards points displayed in the GUI might not match the actual points shown directly in the browser for several reasons:

### Root Causes Identified

1. **Points Extraction Logic**
   - **Original Issue**: The regex `\d+` extracts only the FIRST number from text
   - **Problem**: If the page contains multiple numbers (e.g., "50 today, total 1,234"), the code was getting 50 instead of 1,234
   - **Fix**: Now extracts ALL numbers and uses the LARGEST one, which is typically the total points

2. **Text Format Handling**
   - **Original Issue**: Numbers with commas (e.g., "1,234") weren't being handled
   - **Problem**: Regex would extract "1" and "234" separately, not "1234"
   - **Fix**: Now removes commas before regex to handle formatted numbers

3. **Page Load Timing**
   - **Original Issue**: Only 1-3 second random delay before extraction
   - **Problem**: The points element might not be fully rendered yet
   - **Fix**: Increased to 2-4 seconds and using `wait_until='networkidle'`

4. **GUI Update Timing**
   - **Original Issue**: GUI only updated via rewards_watcher polling (every 5 seconds)
   - **Problem**: Users didn't see immediate feedback after searches
   - **Fix**: Added direct GUI updates from browser_controller immediately after fetching points

5. **Error Handling & Fallback**
   - **Original Issue**: Limited error handling; only one extraction method
   - **Problem**: If XPath fails, no alternative method exists
   - **Fix**: Added fallback method to search page content for points patterns

## Changes Made

### 1. Enhanced `get_current_points()` in browser_controller.py

**Improvements:**

```python
# OLD: match = re.search(r'\d+', points_text)
# NEW:
numbers = re.findall(r'\d+', cleaned_text)  # Get ALL numbers
points = int(max(numbers))  # Use the LARGEST one
```

**Details:**

- Removes commas from text: `cleaned_text = points_text.replace(',', '').strip()`
- Extracts all numbers: `numbers = re.findall(r'\d+', cleaned_text)`
- Picks the largest: `points = int(max(numbers))`
- Enhanced logging with all numbers found
- Increased wait time from 1-3s to 2-4s
- Added screenshot saving with timestamps for debugging
- Implemented fallback extraction method

### 2. Direct GUI Updates in Search Loop

**Added immediate updates after each search:**

```python
# Update GUI immediately with new points and search count
if self.gui:
    self.gui.update_rewards_label(current_points)
    counts = self.data_manager.get_current_counts()
    self.gui.update_total_label(counts['total'])
```

**Added initial points display:**

```python
# Display initial points in GUI
if self.gui:
    self.gui.update_rewards_label(initial_points)
```

## Diagnostic Tools

### 1. `tools/debug_points_extraction.py`

- Opens the rewards page in a visible browser
- Takes a screenshot
- Tests both primary (XPath) and alternate (page content) extraction methods
- Shows all numbers found in the text
- Allows manual inspection of the page structure

**Usage:**

```bash
python tools/debug_points_extraction.py
```

### 2. `tools/test_extraction_logic.py`

- Tests the extraction regex on various text formats
- Shows how different formats are handled
- Useful for verifying the logic without opening a browser

**Usage:**

```bash
python tools/test_extraction_logic.py
```

## Data Flow - Updated

```
Browser Page Load
   ↓
get_current_points()
   ├→ Navigate to rewards URL
   ├→ Wait 2-4 seconds for load
   ├→ Extract via XPath (primary method)
   │  ├→ Get text from element
   │  ├→ Remove commas and clean
   │  ├→ Find all numbers
   │  └→ Use LARGEST number
   ├→ If fails, try alternate method (fallback)
   ├→ Log all found numbers
   └→ Return points
   ↓
Search Loop in browser_controller.py
   ├→ Update data_manager: update_rewards(current_points)
   ├→ Add search: add_search(term, current_points)
   ├→ Direct GUI update: gui.update_rewards_label(current_points)  [IMMEDIATE]
   └→ Update search count: gui.update_total_label(counts['total'])  [IMMEDIATE]
   ↓
GUI Display Updates
   ├→ Immediate updates via browser_controller (real-time)
   └→ Periodic updates via rewards_watcher (every 5 seconds, as fallback)
```

## Verification Steps

To verify the fixes are working correctly:

1. **Check the logs:**
   - Look for "Current rewards points: X" messages
   - Check "all found numbers: [...]" to see what was extracted
   - Look for "points found using alternate method" if XPath fails

2. **Take a screenshot:**
   - Run the debug tool: `python tools/debug_points_extraction.py`
   - Compare the extracted points with what's shown on the browser

3. **Monitor the GUI:**
   - Points should update immediately after each search
   - Should match the value on <https://rewards.bing.com/pointsbreakdown>

4. **Check database:**
   - Each search is logged in `searches.db`
   - Points for each search are stored there

## If Points Still Don't Match

1. **XPath Might Have Changed**
   - Run the debug tool to see what's being extracted
   - Right-click the points display on the rewards page
   - Select "Inspect Element"
   - Find the correct element and update `config.yaml`

2. **Page Structure Changed**
   - Bing updates their UI frequently
   - The debug tool can help identify the new structure
   - Take a screenshot and examine the page manually

3. **Alternative XPath Options to Try:**
   - Use browser DevTools to find the element
   - common patterns:
     - `//mee-rewards-user-points-details//p` (current)
     - `//span[contains(text(), 'Points')]`
     - `//*[contains(@id, 'point')]`
     - `//*[contains(@class, 'point')]`

## Testing Script

To thoroughly test, run this:

```bash
# 1. Test extraction logic
python tools/test_extraction_logic.py

# 2. Test actual page extraction
python tools/debug_points_extraction.py

# 3. Run the full application
python main.py

# 4. Check logs for extraction details
# Look for debug messages about points extraction
```

## Configuration Updates (if needed)

If the XPath changes, update `config.yaml`:

```yaml
xpaths:
  points: 'NEW_XPATH_HERE'
```

Then the application will automatically use the new XPath.
