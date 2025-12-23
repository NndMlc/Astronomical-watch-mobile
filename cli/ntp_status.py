#!/usr/bin/env python3
"""
Brzi prikaz NTP statusa - upotrebljiv u Android shell-u
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astronomical_watch.net.ntp_sync import get_ntp_sync
from datetime import datetime, timezone

ntp = get_ntp_sync()

# Sistemsko vreme
sys_time = datetime.now(timezone.utc)

# NTP vreme (automatski fetch ako je potrebno)
ntp_time = ntp.get_corrected_time()

# Info
info = ntp.get_offset_info()

print(f"Sistemsko: {sys_time.strftime('%H:%M:%S')}")
print(f"NTP:       {ntp_time.strftime('%H:%M:%S')}")

if info['offset_seconds'] is not None:
    print(f"Offset:    {info['offset_seconds']:+.3f}s")
    if abs(info['offset_seconds']) < 1.0:
        print("Status:    ✅ Tačno")
    elif abs(info['offset_seconds']) < 10.0:
        print("Status:    ⚠️ Mala razlika")
    else:
        print("Status:    ❌ Velika razlika")
else:
    print("Status:    ❌ NTP nedostupan")
