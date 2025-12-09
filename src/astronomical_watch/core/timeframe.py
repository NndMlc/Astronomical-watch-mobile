"""
timeframe.py (Core)
Convert UTC datetime into (dies, miliDies) relative to vernal equinox frame.
License: Astronomical Watch Core License v1.0 (NO MODIFICATION). See LICENSE.CORE
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from .equinox import compute_vernal_equinox

DAY_SECONDS = 86400
LAMBDA_REF_DEG = -168.975

def reference_noon_utc_for_day(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("Expect timezone-aware UTC datetime.")
    date0 = dt.date()
    base_noon = datetime(date0.year, date0.month, date0.day, 12, 0, 0, tzinfo=timezone.utc)
    offset_hours = -LAMBDA_REF_DEG / 15.0
    return base_noon - timedelta(hours=offset_hours)

def first_day_start_after_equinox(equinox: datetime) -> datetime:
    candidate = reference_noon_utc_for_day(equinox)
    if candidate < equinox:
        candidate += timedelta(days=1)
    return candidate

def astronomical_time(dt: datetime) -> tuple[int, int]:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be UTC (tz-aware).")
    year_guess = dt.year
    eq = compute_vernal_equinox(year_guess)
    if dt < eq:
        eq = compute_vernal_equinox(year_guess - 1)
    next_eq = compute_vernal_equinox(eq.year + 1)
    if dt >= next_eq:
        eq = next_eq
        next_eq = compute_vernal_equinox(eq.year + 1)
    day0 = first_day_start_after_equinox(eq)
    
    # Special handling for Dies 0 (partial day from equinox to first noon)
    if dt < day0:
        # Dies 0: calculate miliDies relative to equinox, not day0
        seconds_since_equinox = (dt - eq).total_seconds()
        # Scale to day length between equinox and first noon
        day0_length = (day0 - eq).total_seconds()
        if day0_length > 0:
            fraction = seconds_since_equinox / day0_length
            miliDies = int(fraction * 1000)
            if miliDies > 999:
                miliDies = 999
            if miliDies < 0:
                miliDies = 0
            return (0, miliDies)
        return (0, 0)
    
    # Dies 1, 2, 3... (full 24h days)
    # Dies starts at 1 because day0 is the first noon after equinox
    seconds_since_day0 = (dt - day0).total_seconds()
    days_after_day0 = int(seconds_since_day0 // DAY_SECONDS)
    dies = days_after_day0 + 1  # +1 because Dies 0 already passed
    current_day_start = day0 + timedelta(days=days_after_day0)
    intra = (dt - current_day_start).total_seconds()
    if intra < 0:
        intra = 0
    miliDies = int((intra / DAY_SECONDS) * 1000)
    if miliDies > 999:
        miliDies = 999
    return dies, miliDies
