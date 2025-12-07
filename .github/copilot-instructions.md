# Copilot Instructions for Astronomical Watch Mobile

## Project Overview

This is a mobile astronomical timekeeping application (Python/Kivy) that tracks time based on real astronomical phenomena—specifically, the vernal equinox. The system represents time as `(day_index, milli_day)` where day 0 starts at the first reference noon after the vernal equinox.

**Key Concept**: Unlike standard calendars, this astronomical frame resets annually at each vernal equinox, expressing time in "dies" (days since equinox) and "milidies" (1/1000th of a day = 86.4 seconds).

## Critical: Dual License Architecture

**IMMUTABLE CORE (NO MODIFICATION LICENSE)**: Files under `src/astronomical_watch/core/` are frozen and cannot be modified:
- `solar.py`, `equinox.py`, `timeframe.py`, `timebase.py`, `vsop87_earth.py`, `nutation.py`, `frames.py`, `delta_t.py`
- See `LICENSE.CORE` and `CORE_FILES.md` for complete list
- Bug fixes must maintain observable behavior; propose upstream via PR
- DO NOT modify Core files without explicit permission

**MIT LICENSE**: All other files (`ui/`, `services/`, `net/`, `lang/`, `cli/`, etc.) can be freely modified.

When implementing features, work outside the Core. Import and call Core APIs but never modify Core source.

## Architecture

### Core Layer (`src/astronomical_watch/core/`)
Canonical astronomical algorithms implementing the spec in `SPEC.md`:
- **Equinox calculation**: `equinox.py` - Iterative solver for apparent solar longitude = 0°
- **Time conversion**: `timeframe.py` - Converts UTC → (day_index, milli_day) relative to equinox
- **Solar position**: `solar.py` - Geocentric apparent solar ecliptic longitude using VSOP87D + nutation
- **Timescales**: `timebase.py` - Julian Day, TT approximation, ΔT modeling

### VSOP87D Precision System
Dynamic coefficient loading for configurable accuracy (see `VSOP87D_SYSTEM.md`):
- Generator: `scripts/generate_vsop87.py` - Downloads VSOP87D.EAR, generates coefficient files
- Runtime: `vsop87_earth.py` accepts `max_error_arcsec` parameter for on-demand precision
- Example: `apparent_solar_longitude(jd, max_error_arcsec=1.0)` uses 1 arcsec accuracy
- Generated files stored in `scripts/vsop87_coefficients/`

### Hybrid Equinox Service (`services/equinox_service.py`)
Three-tier precision hierarchy with automatic fallback:
1. **Internet** (5s uncertainty) - Fetches from JSON API via `ASTRON_EQUINOX_URL` env var
2. **Analytic** (10s uncertainty) - Meeus-based root finding in `solar/equinox_precise.py`
3. **Approx** (3h uncertainty) - Legacy method for compatibility

Cache: `~/.astronomical_watch/equinox_cache.json` (schema v2 with auto-migration)

### UI Layer (`src/astronomical_watch/ui/`)
Kivy-based mobile interface:
- **main_screen.py**: Widget/Normal modes, dynamic sky theming based on solar position
- **sky_theme.py**: Gradient backgrounds tied to time of day
- Updates every 0.2s: `astronomical_time(now)` returns current (dies, milidies)

### Internationalization (`src/astronomical_watch/lang/`)
20 languages supported via `translations.py`:
- Language cards: `explanation_*_card.py` (20 files, one per language)
- Usage: `tr("key", lang_code)` for runtime translation lookup
- Config: `lang_config.py` loads/saves user preference

### CLI (`cli/awatch.py`)
Simple MIT-licensed tool: prints current astronomical time as `DDD.mmm` format.

## Development Workflows

### Running the App
```bash
# Mobile app (Kivy)
python main.py

# CLI tool
python cli/awatch.py
# Output: 042.573 (day 42, milidan 573)
```

### Generating VSOP87 Coefficients
```bash
# Auto-select threshold for 10 arcsecond accuracy
python src/astronomical_watch/scripts/generate_vsop87.py --auto-upgrade --target-arcsec 10

# Custom amplitude threshold
python src/astronomical_watch/scripts/generate_vsop87.py --threshold 1e-6
```

### Environment Variables
- `ASTRON_EQUINOX_URL`: JSON API endpoint for internet equinox fetch (optional)
- `ASTRON_CACHE_DIR`: Cache directory override (default: `~/.astronomical_watch`)

### Python Environment
- Requires Python ≥3.10
- Main dependency: `kivy>=2.3.0`
- Use dev container (Ubuntu 24.04.3 LTS) for consistent environment

## Project-Specific Patterns

### Time Representation
- **Internal**: Julian Day (TT) for astronomical calculations
- **User-facing**: `(day_index, milli_day)` tuple
- **Display format**: `DDD.mmm` (e.g., "042.573")
- **Global reference**: Fixed meridian at -168.975° longitude

### Coordinate Systems
- **Ecliptic coordinates**: Primary for solar position (λ, β, R)
- **Equatorial conversion**: Via `frames.py` using mean obliquity
- **Nutation**: Applied via `nutation_simple()` - simplified model, not IAU 2000A yet

### Error Handling Philosophy
The Core uses simple algorithms (Meeus low-precision) with room for improvement:
- Current accuracy: ~10-60 arcseconds depending on VSOP87 threshold
- Future: Add IAU 2006 precession, higher-order nutation, refined ΔT
- Fallback: Hybrid service ensures graceful degradation (internet → analytic → approx)

### Cache Schema Evolution
When working with `offline/cache.py`:
- Schema v2 uses structured JSON objects with `precision`, `uncertainty_s`, `source` fields
- Auto-migrates v1 (plain timestamps) preserving original in `legacy_approx`
- Always include `retrieved_at` ISO timestamp

## Common Pitfalls

1. **Don't modify Core files** - Even for "small fixes", propose upstream instead
2. **Timezone awareness** - Always use `timezone.utc` for datetime objects; Core expects UTC
3. **VSOP87 time units** - `earth_heliocentric_*` takes Julian millennia, not centuries
4. **Equinox edge case** - day_index resets to 0 at equinox instant, but milli_day continues until next global noon (23:15:54 UTC)
5. **Language card naming** - Must follow `explanation_XX_card.py` pattern where XX is ISO 639-1 code

## Key Files for Context

- **Spec**: `SPEC.md` - Immutable reference for astronomical time definition
- **Time system**: `docs/ASTRO_TIME_SYSTEM.md` - Global noon, milidans, rollover semantics
- **Precision docs**: `docs/PRECISE_EQUINOX.md` - Hybrid equinox system details
- **VSOP87 guide**: `VSOP87D_SYSTEM.md` - Dynamic coefficient loading
- **Contributing**: `CONTRIBUTING.md` - Core modification policy

## Testing Notes

No test suite currently exists (grep found no test files). When adding tests:
- Focus on non-Core components (services, UI, network, cache)
- For Core: Only regression tests verifying unchanged behavior
- Test astronomical calculations against known ephemeris data
- Mock network calls in `net/equinox_fetch.py` tests
