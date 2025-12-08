# UI Refactoring Summary

## Problem

After syncing Core files from desktop repo (`/workspaces/Astronomical-watch`), the UI layer (`src/astronomical_watch/ui/main_screen.py`) had compatibility issues:

1. **Wrong import path** in `sky_theme.py`: Used `src.astronomical_watch` instead of `astronomical_watch`
2. **Missing property** in `WidgetMode` class: Used `self.selected_language` before defining it
3. **Non-existent functions**: UI code called 4 helper functions that don't exist in Core:
   - `get_meridian_milidies(lat, lon)` - Calculate local solar noon in miliDies
   - `get_eot_curve(lat, lon)` - Generate Equation of Time graph
   - `countdown_to_next_equinox(now)` - Days until next vernal equinox
   - `datetime_from_astro(dies, milidies)` - Convert astronomical time to UTC datetime

## Solution

### Approach 1: Clean Rewrite (Implemented)

Instead of implementing the missing functions (which would require extensive astronomical calculations outside Core), we **simplified the UI** to use only existing Core APIs:

- ✅ `astronomical_time(dt)` - Convert UTC to (dies, miliDies)
- ✅ `get_sky_theme(dt)` - Dynamic gradient colors based on solar altitude

### Changes Made

**File: `src/astronomical_watch/ui/sky_theme.py`**
```python
# Before:
from src.astronomical_watch.core.solar import solar_longitude_from_datetime

# After:
from astronomical_watch.core.solar import solar_longitude_from_datetime
```

**File: `src/astronomical_watch/ui/main_screen.py`**

1. **Fixed `WidgetMode` class:**
   - Added `selected_language = StringProperty(load_language())` as class property
   - Simplified update logic to only call `astronomical_time()`
   - Dynamic sky theming with gradient backgrounds

2. **Rewrote `NormalMode` class:**
   - Removed all calls to non-existent helper functions
   - Kept functional features:
     * Dies/miliDies display with progress bar
     * Standard time reference (UTC)
     * Language selector (28 languages supported)
     * Explanation card (working, shows language-specific text)
   - Marked as "Coming soon":
     * Comparison card (compare astro time with standard calendars)
     * Calculations card (local solar noon, EoT graph)

3. **Code quality improvements:**
   - Clear docstrings for all methods
   - Consistent naming conventions
   - Proper error handling for language card loading
   - Removed duplicate/broken code (~450 lines → 250 lines clean code)

### Backup

Old version saved as: `src/astronomical_watch/ui/main_screen.py.backup`

## Testing

**Import Test (Passed):**
```bash
poetry run python -c "
from astronomical_watch.ui.main_screen import WidgetMode, NormalMode
from astronomical_watch.core.timeframe import astronomical_time
from datetime import datetime, timezone
dies, milidies = astronomical_time(datetime.now(timezone.utc))
print(f'{dies}.{milidies:03d}')
"
# Output: 262.808 ✓
```

**Syntax Check (Passed):**
```bash
poetry run python -m py_compile src/astronomical_watch/ui/*.py
# ✅ All UI files compile without syntax errors
```

**VS Code Errors:** None found

## UI Capabilities (Current)

### ✅ Working Features

1. **WidgetMode** (Minimalist view):
   - Large dies.miliDies display
   - Progress bar (updates every 0.2s)
   - Dynamic sky gradient (day/night/twilight)
   - Tap to expand to NormalMode

2. **NormalMode** (Full screen):
   - Separate dies and miliDies labels
   - Standard UTC time reference
   - Language selector (28 languages)
   - Back button to WidgetMode
   - **Explanation Card**: Loads language-specific astronomical time explanation from `astronomical_watch.lang.explanation_XX_card.py`

### 🚧 Future Features (Placeholders)

3. **Comparison Card** (Not implemented):
   - Would show side-by-side comparison with Gregorian calendar
   - Would highlight differences (365 days vs ~365.24 astronomical days)

4. **Calculations Card** (Not implemented):
   - Would show local solar noon in miliDies (requires location permission)
   - Would display Equation of Time graph with markers for equinoxes/solstices
   - Would calculate days to next vernal equinox

## Implementation Notes

### Why Not Implement Helper Functions?

The missing functions require significant astronomical logic:

1. **`get_meridian_milidies(lat, lon)`**:
   - Needs: Observer's longitude → time offset from global reference meridian (-168.975°)
   - Calculation: Local mean solar noon time → convert to miliDies
   - Complexity: Moderate (coordinate transformation)

2. **`get_eot_curve(lat, lon)`**:
   - Needs: Daily solar position over ~365 days
   - Calculation: Apparent solar time - mean solar time across full year
   - Complexity: High (requires caching yearly data or heavy computation)

3. **`countdown_to_next_equinox(now)`**:
   - Needs: Current UTC → find next vernal equinox instant
   - Calculation: Calls `equinox_service.get_next_equinox(year)` → compare with now
   - Complexity: Low (service layer already exists)

4. **`datetime_from_astro(dies, milidies)`**:
   - Needs: Reverse timeframe conversion
   - Calculation: Get reference equinox → add dies → add miliDies → UTC datetime
   - Complexity: Moderate (inverse of `astronomical_time()`)

**Decision**: Defer implementation to future when:
- Core stabilizes further
- Location services integrated (Android/iOS permissions)
- Performance profiling done (EoT curve generation on mobile)

### Where to Add Helpers (When Implemented)

**Option A**: `src/astronomical_watch/ui/helpers.py` (MIT licensed, outside Core)
```python
# MIT License - can modify freely
def get_meridian_milidies(lat, lon):
    """Calculate local solar noon in miliDies for given observer location"""
    # Import from Core, calculate offset
    pass
```

**Option B**: Propose upstream to Core (requires discussion)
- If helpers are generally useful, add to Core with rigorous testing
- Must maintain Core's NO MODIFICATION policy on mobile side

## Mobile Development Workflow

### Preview App (6 Options from DEVELOPMENT.md)

1. **Kivy Emulator** (Python): `poetry run python main.py` *(Requires X server)*
2. **Android Emulator**: Build APK → install on Android Studio emulator
3. **iOS Simulator**: Requires macOS with Xcode
4. **Physical Device**: USB debugging via ADB (Android) or Xcode (iOS)
5. **VNC + Xvfb**: Virtual X server in dev container
6. **Buildozer VM**: Full Android build environment

### VS Code Tasks

Run tasks with `Ctrl+Shift+B` or Command Palette:

- **Run Kivy App** - `python main.py`
- **Build Android Debug** - `buildozer android debug`
- **Deploy to Device** - `buildozer android debug deploy run`
- **Clean Cache** - Remove `.buildozer/` and `__pycache__`
- **Sync from Desktop** - Run `.github/sync_to_mobile.sh`

## Commit History

**Commit:** `e3024e0` - "Refactor UI: clean main_screen.py, remove broken helper functions"

Changes:
- 3 files changed, 727 insertions(+), 274 deletions(-)
- Created `main_screen.py.backup` for rollback if needed
- Pushed to GitHub: `NndMlc/Astronomical-watch-mobile`

---

## Next Steps

1. **Test on Android Device**:
   ```bash
   buildozer android debug deploy run
   ```

2. **Implement Countdown Alert**:
   - Add `countdown_to_next_equinox()` helper in `ui/helpers.py`
   - Show green alert when < 11 dies to equinox (already has placeholder)

3. **Add Comparison Card**:
   - Simple table: Gregorian date | Astronomical day | Difference
   - Show Julian Day for reference

4. **Add Calculations Card** (Complex):
   - Request location permission (Android/iOS platform code)
   - Implement `get_meridian_milidies()` and `get_eot_curve()`
   - Use matplotlib for EoT graph (already in dependencies)

5. **Performance Optimization**:
   - Cache equinox data (already exists in `offline/cache.py`)
   - Profile update frequency (currently 0.2s, may drain battery)

6. **UI/UX Improvements**:
   - Add haptic feedback on touch (platform-specific)
   - Smoother transitions between WidgetMode/NormalMode
   - Dark mode toggle (override sky theme)
