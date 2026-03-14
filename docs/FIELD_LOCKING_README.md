# Partial Field-Level Locking Implementation

## Overview

This update replaces blanket profile-based locking with **field-level locking**, where only fields that a profile actually overrides are locked in the UI, while non-overridden base config fields remain editable.

## Problem Solved

**Before:** When a user selected `stealth_mode` profile, fields like `target_points` became inaccessible even though the profile didn't define them. This created conflicts and poor UX when base config and profile parameters didn't align.

**After:** Only fields the profile explicitly overrides are locked (marked with 🔒). Everything else remains editable, giving users flexibility while preserving profile intent.

## Field Locking by Profile

### stealth_mode

**Locked Fields (🔒):**

- Search Settings: searches_before_pause, pause_duration_minutes, min_sleep_seconds, max_sleep_seconds
- Stealth: simulate_mistakes, mistake_probability, typing_speed_variance, random_mouse_movements
- Browser: slow_mo_ms

**Editable Fields:**

- target_points, poll_interval, topic_generator (search)
- headless, storage_state_path, channel (browser)
- proxy fields, logging fields

### balanced_mode

Same as stealth_mode (same overrides).

### speed_mode

Same as stealth_mode (same overrides).

### Custom Mode

**All fields editable** – user has full control.

## UI Behavior

### Label Badges

- **Locked fields:** Show "Field Name 🔒" in grey (disabled state)
- **Editable fields:** Show plain field name in normal state
- **Preview values:** When a profile is selected, the field widgets display the profile's override values as a preview

### Profile Selection Flow

1. User opens Settings > Config → Profiles tab
2. Selects a profile from dropdown (e.g., "stealth_mode")
3. Form immediately updates:
   - Non-overridden fields: calculated from base config, remain editable
   - Overridden fields: show profile values, locked with 🔒 badge
4. On Save:
   - Overridden fields use profile values
   - Non-overridden fields use form values
   - Effective config = base config deep_merged with profile overrides
5. To customize: Switch to "Custom" mode → all fields unlock → edit freely

## Implementation Details

### Data Structures

- `_profile_overrides`: Maps profile name to set of `(section, key)` tuples it overrides
- `_field_lock_labels`: Tracks label widgets for dynamic badge updates
- `_config_widgets`: Maps `(section, key)` to widget for state management

### Methods

- `_build_profile_overrides_map()`: Builds override map on config window open
- `_apply_profile_ui_state()`: Called when profile changes; locks only overridden fields
- `_add_row()`: Updated to track and support label badge updates

### No Conflicts

- Deep merge at save time handles all combinations correctly
- Profile intent is preserved (overridden fields locked)
- User flexibility is maximized (non-overridden fields editable)
- UI clearly shows which is which via 🔒 badges

## Example Scenario

User wants `stealth_mode` (for stealth behavior) but with custom point target:

1. Select "stealth_mode" profile
2. Fields automatically lock:
   - Searches Before Pause: 5 🔒 (from profile)
   - Min Sleep Seconds: 20 🔒 (from profile)
   - … other stealth fields locked …
3. But Target Points remains editable because profile doesn't override it
4. User enters: Target Points = **120** ← custom value
5. Click Save → effective config now has:
   - Stealth settings from profile
   - Searches/sleep timings from profile
   - Target points = 120 ← user's custom value
   - All other search settings from base config

Perfect balance between structure and flexibility!

## Testing

To test, open Settings > Config and try:

1. Select "stealth_mode" → observe 🔒 badges on specific fields only
2. Try editing target_points → should work (not locked)
3. Try editing searches_before_pause → should be disabled
4. Switch to "Custom" → all fields unlock (🔒 badges disappear)
5. Click Save → verify config applies immediately
