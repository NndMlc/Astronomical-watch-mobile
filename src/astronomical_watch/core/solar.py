"""
solar.py (Core)
Simplified Meeus-based solar position & Equation of Time routines.

License: Astronomical Watch Core License v1.0 (NO MODIFICATION). See LICENSE.CORE
Do not redistribute modified versions of this file except under Security Exception (Section 11).
"""
from __future__ import annotations
import math
from datetime import datetime, timezone

def to_julian_date(dt: datetime) -> float:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware (UTC).")
    dt = dt.astimezone(timezone.utc)
    y = dt.year
    m = dt.month
    D = dt.day + (dt.hour + (dt.minute + dt.second/60.0)/60.0)/24.0
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + A // 4
    jd = int(365.25*(y + 4716)) + int(30.6001*(m + 1)) + D + B - 1524.5
    return jd

def julian_centuries_tt(jd_tt: float) -> float:
    return (jd_tt - 2451545.0) / 36525.0

def apparent_solar_longitude(jd_tt: float) -> float:
    T = julian_centuries_tt(jd_tt)
    M = (357.52911 + 35999.05029*T - 0.0001537*T*T) % 360.0
    L0 = (280.46646 + 36000.76983*T + 0.0003032*T*T) % 360.0
    Mrad = math.radians(M)
    C = (1.914602 - 0.004817*T - 0.000014*T*T)*math.sin(Mrad) \
        + (0.019993 - 0.000101*T)*math.sin(2*Mrad) \
        + 0.000289*math.sin(3*Mrad)
    true_long = L0 + C
    omega = (125.04 - 1934.136*T) % 360.0
    lambda_app = true_long - 0.00569 - 0.00478*math.sin(math.radians(omega))
    return lambda_app % 360.0

def mean_obliquity(T: float) -> float:
    seconds = 21.448 - T*(46.815 + T*(0.00059 - T*0.001813))
    eps0 = 23 + (26 + (seconds/60.0))/60.0
    return eps0

def equation_of_time(dt: datetime) -> float:
    if dt.tzinfo is None:
        raise ValueError("UTC datetime required.")
    jd = to_julian_date(dt)
    T = julian_centuries_tt(jd)
    L0 = (280.46646 + 36000.76983*T + 0.0003032*T*T) % 360
    M = (357.52911 + 35999.05029*T - 0.0001537*T*T) % 360
    e = 0.016708634 - 0.000042037*T - 0.0000001267*T*T
    eps = mean_obliquity(T)
    L0r = math.radians(L0)
    Mr = math.radians(M)
    epsr = math.radians(eps)
    y = math.tan(epsr/2)**2
    E = 4*math.degrees(y*math.sin(2*L0r) - 2*e*math.sin(Mr) + 4*e*y*math.sin(Mr)*math.cos(2*L0r)
                       - 0.5*y*y*math.sin(4*L0r) - 1.25*e*e*math.sin(2*Mr))
    return E  # minutes approx
"""
