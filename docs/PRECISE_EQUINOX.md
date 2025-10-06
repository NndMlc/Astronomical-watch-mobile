# Precise Equinox Documentation

## Overview

The Astronomical Watch project now includes a hybrid precise vernal equinox capability that combines multiple calculation methods with automatic fallback and caching. This document describes the implementation, usage, and configuration of the precise equinox system.

## Hybrid Model

The system supports three precision levels with automatic method selection:

1. **Internet** - Fetch from remote JSON API (highest accuracy when available)
2. **Analytic** - High-precision Meeus-based root-finding calculation  
3. **Approx** - Legacy approximation method (fallback compatibility)

### Method Preference

Methods are tried in preference order (default: `internet`, `analytic`, `approx`) with automatic fallback if a method fails or is unavailable.

## Cache Schema Version 2

### Schema Structure

Each cached equinox entry contains:

```python
{
  "utc": "2024-03-20T03:06:14Z",        # ISO 8601 UTC timestamp
  "precision": "analytic",               # Method used: "internet", "analytic", "approx"  
  "uncertainty_s": 10.0,                 # Estimated uncertainty in seconds
  "source": "meeus_root_finding",        # Description of calculation method
  "retrieved_at": "2024-08-28T21:40:00Z", # When computed/fetched
  "legacy_approx": null                  # Original approx value if migrated from v1
}
```

### Automatic Migration

The cache automatically migrates from schema v1 (simple timestamp strings) to v2 (structured objects):

- Legacy entries are preserved in `legacy_approx` field
- Migration occurs transparently on first v2 request
- Original approximation values are retained for comparison

### Cache Location

Default cache location: `~/.astronomical_watch/equinox_cache.json`

Override with environment variable: `ASTRON_CACHE_DIR`

## Environment Variables

### ASTRON_EQUINOX_URL

Optional URL for fetching equinox data from external JSON API.

**Expected JSON format:**
```json
{
  "2023": "2023-03-20T21:24:00Z",
  "2024": "2024-03-20T03:06:14Z", 
  "2025": "2025-03-20T09:01:28Z"
}
```

**Example:**
```bash
export ASTRON_EQUINOX_URL="https://api.example.com/equinoxes.json"
```

If not set, internet method is skipped and system falls back to analytic calculation.

### ASTRON_CACHE_DIR

Optional directory for cache storage.

**Default:** `~/.astronomical_watch`

**Example:**
```bash
export ASTRON_CACHE_DIR="/tmp/astro_cache"
```

## Uncertainty Semantics

The system provides uncertainty estimates in seconds for each method:

- **Internet**: ~5 seconds (assumes external API accuracy)
- **Analytic**: ~10 seconds (based on Meeus method + numerical precision)
- **Approx**: ~3 hours (10,800 seconds, legacy method uncertainty)

These values reflect expected accuracy under normal conditions and are stored with each cache entry.

## Usage

### Service API

```python
from services.equinox_service import get_vernal_equinox

# Get equinox with default preference order
result = get_vernal_equinox(2024)
print(f"Equinox: {result['utc']}")
print(f"Method: {result['precision']}")
print(f"Uncertainty: {result['uncertainty_s']} seconds")

# Custom preference order  
result = get_vernal_equinox(2024, prefer_order=("analytic", "approx"))

# Get just the datetime
from services.equinox_service import get_vernal_equinox_datetime
dt = get_vernal_equinox_datetime(2024)
```

### Direct Method Access

```python
# Precise analytic calculation
from solar.equinox_precise import compute_vernal_equinox_precise
dt = compute_vernal_equinox_precise(2024, method="brent")

# Internet fetch (if configured)
from net.equinox_fetch import fetch_equinox_datetime  
dt = fetch_equinox_datetime(2024)

# Legacy approximation
from astronomical_watch import compute_vernal_equinox
dt = compute_vernal_equinox(2024)
```

### Cache Management

```python
from services.equinox_service import clear_cache, get_service_status

# Clear all cached entries
clear_cache()

# Get cache statistics
status = get_service_status()
print(status["cache_status"])
```

## Algorithm Details

### Time Scale Conversion

Enhanced ΔT calculation using Espenak & Meeus polynomials (1900-2050 focus):

- UTC to Terrestrial Time (TT) conversion
- Piecewise polynomial fitting for different historical periods  
- Accuracy optimized for modern era (1900-2050)

### Solar Longitude Calculation

Lightweight high-precision apparent solar longitude using Meeus algorithms:

- Geometric mean longitude and mean anomaly
- Equation of center correction
- Aberration correction (~-20.5 arcseconds)
- Simplified nutation in longitude (main term)

### Root Finding

Precise vernal equinox solver using bracket and binary/Brent root-finding:

- Target: apparent solar longitude = 0° (vernal equinox definition)
- Search window: March 18-22 (auto-expanded if needed)
- Convergence tolerance: < 2 seconds
- Maximum iterations: 30
- Methods: Brent's method (default) or bisection

## Network Behavior

### Timeout and Fallback

- Internet fetch timeout: 10 seconds
- Graceful timeout handling without exceptions
- Automatic fallback to analytic method on any network failure
- No network dependency for core functionality

### Validation

Remote timestamps are validated to ensure:
- Correct year
- March month  
- Day range 18-22
- Valid ISO 8601 format
- Astronomical reasonableness

## Testing

### Test Coverage

- `tests/test_timescales_delta_t.py` - ΔT polynomial validation
- `tests/test_equinox_precision_basic.py` - Precision and fallback testing

### Test Characteristics  

- No network required (internet fetch mocked/disabled)
- Analytic convergence within 30 iterations
- Solution stability < 2s under repeated invocation  
- March window validation (18-22 days)
- Precision comparison (analytic vs approx > 20s difference)

## Backward Compatibility

The original `compute_vernal_equinox()` function in `astronomical_watch.py` remains unchanged and fully backward compatible. Existing code continues to work without modification.

The new precise system is accessed through:
- `services.equinox_service` - Hybrid facade
- `solar.equinox_precise` - Direct analytic access
- `net.equinox_fetch` - Direct internet access

## Error Handling

### Graceful Degradation

1. Internet method failure → falls back to analytic
2. Analytic method failure → falls back to approx  
3. All methods fail → raises `RuntimeError` with details

### Method-Specific Errors

- **Internet**: Network timeouts, invalid JSON, missing year data
- **Analytic**: Root-finding convergence failures, bracket search failures
- **Approx**: Should never fail (uses existing stable implementation)

### Cache Errors

Cache read/write failures are handled silently - system continues operation without caching.

## Performance

### Typical Execution Times

- **Internet**: 0.1-10 seconds (network dependent)
- **Analytic**: 0.1-0.5 seconds (computation)
- **Approx**: 0.01-0.1 seconds (simple iteration)
- **Cache hit**: < 0.01 seconds

### Memory Usage

Minimal memory footprint:
- Cache stored on disk, loaded on demand
- No persistent in-memory state
- Automatic cleanup of computation intermediates

## Future Extensions

This precise equinox implementation provides the foundation for:

1. Precise solstice calculations 
2. All four seasonal points (equinoxes + solstices)
3. High-precision sunrise/sunset calculations
4. UI precision mode selection
5. Enhanced uncertainty modeling
6. Additional time scale support (TAI, GPS time)

The modular design allows individual components to be enhanced or replaced without affecting the overall system architecture.
