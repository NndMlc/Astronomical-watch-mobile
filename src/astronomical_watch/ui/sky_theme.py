"""
Shared gradient helper for sky-based themes.
Computes dynamic sky gradients based on astronomical data (solar position, time, etc.)
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Tuple
from src.astronomical_watch.core.solar import solar_longitude_from_datetime

class SkyTheme:
    """Represents a sky theme with gradient colors and text colors."""
    def __init__(self, top_color: str, bottom_color: str, text_color: str):
        self.top_color = top_color
        self.bottom_color = bottom_color
        self.text_color = text_color
        self.text_hex = text_color  # Alias for consistency

def get_solar_altitude_approximation(dt: datetime) -> float:
    """
    Approximate solar altitude for theme computation.
    This is a simplified calculation for UI purposes.
    Returns altitude in degrees (negative = below horizon).
    """
    solar_lon = solar_longitude_from_datetime(dt)
    declination = 23.5 * math.sin(solar_lon + math.pi/2)
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    hour_angle = (hour - 12) * 15 * math.pi / 180
    latitude = 45.0 * math.pi / 180
    declination_rad = declination * math.pi / 180
    sin_altitude = (math.sin(latitude) * math.sin(declination_rad) + 
                   math.cos(latitude) * math.cos(declination_rad) * math.cos(hour_angle))
    sin_altitude = max(-1.0, min(1.0, sin_altitude))
    altitude_rad = math.asin(sin_altitude)
    altitude_degrees = altitude_rad * 180 / math.pi
    return altitude_degrees

def get_sky_theme(dt: datetime = None) -> SkyTheme:
    if dt is None:
        dt = datetime.now(timezone.utc)
    altitude = get_solar_altitude_approximation(dt)
    if altitude > 50:
        return SkyTheme("#1e3a8a", "#3b82f6", "#ffffff")
    elif altitude > 20:
        return SkyTheme("#2563eb", "#60a5fa", "#000000")
    elif altitude > 0:
        return SkyTheme("#7c3aed", "#f59e0b", "#ffffff")
    elif altitude > -10:
        return SkyTheme("#1e1b4b", "#7c2d12", "#ffffff")
    else:
        return SkyTheme("#0f172a", "#1e293b", "#e2e8f0")

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_gradient_colors(theme: SkyTheme, steps: int = 256) -> list[str]:
    top_rgb = hex_to_rgb(theme.top_color)
    bottom_rgb = hex_to_rgb(theme.bottom_color)
    colors = []
    for i in range(steps):
        factor = i / (steps - 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * factor)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * factor)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * factor)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append(hex_color)
    return colors

__all__ = [
    'SkyTheme',
    'get_sky_theme', 
    'get_solar_altitude_approximation',
    'create_gradient_colors',
    'hex_to_rgb'
]
