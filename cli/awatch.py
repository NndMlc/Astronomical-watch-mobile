#!/usr/bin/env python
"""CLI tool (MIT licensed) printing astronomical time as DDD.mmm"""
from __future__ import annotations
from datetime import datetime, timezone
from astronomical_watch import astronomical_time

def main():
    now = datetime.now(timezone.utc)
    day_index, milli = astronomical_time(now)
    print(f"{day_index:03d}.{milli:03d}")

if __name__ == "__main__":
    main()
