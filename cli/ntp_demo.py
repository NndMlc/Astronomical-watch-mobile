#!/usr/bin/env python3
"""
Demo integracije NTP sinhronizacije sa Astronomical Watch
Prikazuje kako se tačno vreme koristi za izračunavanje Dies/miliDies
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astronomical_watch.net.ntp_sync import get_ntp_sync
from astronomical_watch.core.timeframe import astronomical_time
from datetime import datetime, timezone
import time

def format_time_diff(seconds):
    """Formatiraj razliku u vremenu u čitljiv format"""
    if abs(seconds) < 1:
        return f"{seconds*1000:.0f} ms"
    elif abs(seconds) < 60:
        return f"{seconds:.1f} s"
    elif abs(seconds) < 3600:
        mins = seconds / 60
        return f"{mins:.1f} min"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} h"

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "ASTRONOMICAL WATCH - NTP DEMO" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Inicijalizuj NTP
    print("⏳ Inicijalizacija NTP sinhronizacije...")
    ntp = get_ntp_sync()
    
    # Automatski fetch (prvi put može trajati 0.5-1s)
    start_time = time.time()
    accurate_now = ntp.get_corrected_time()
    fetch_duration = time.time() - start_time
    
    print(f"✅ NTP sync završen za {fetch_duration:.2f}s")
    print()
    
    # Prikaz vremena
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ VREME                                                           │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    system_time = datetime.now(timezone.utc)
    ntp_time = accurate_now
    
    print(f"│ Sistemsko UTC:  {system_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}      │")
    print(f"│ NTP UTC:        {ntp_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}      │")
    
    info = ntp.get_offset_info()
    if info['offset_seconds'] is not None:
        offset_str = format_time_diff(info['offset_seconds'])
        print(f"│ Offset:         {offset_str:>20}                         │")
    
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    
    # Astronomsko vreme
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ ASTRONOMSKO VREME                                               │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    dies_sys, milidies_sys = astronomical_time(system_time)
    dies_ntp, milidies_ntp = astronomical_time(ntp_time)
    
    print(f"│ Sistemsko:      {dies_sys:03d}.{milidies_sys:03d}                                   │")
    print(f"│ NTP:            {dies_ntp:03d}.{milidies_ntp:03d}                                   │")
    
    if dies_sys == dies_ntp:
        diff_milidies = milidies_ntp - milidies_sys
        diff_seconds = diff_milidies * 86.4
        if diff_milidies != 0:
            print(f"│ Razlika:        {diff_milidies:+4d} milidies ({diff_seconds:+6.1f}s)              │")
        else:
            print("│ Razlika:        Identično ✨                                │")
    else:
        print(f"│ Razlika:        {dies_ntp - dies_sys:+4d} dies! (velika greška)                │")
    
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    
    # Status i info
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STATUS                                                          │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    if info['offset_seconds'] is not None:
        if abs(info['offset_seconds']) < 1.0:
            status = "✅ ODLIČNO - Sistemski sat je tačan"
        elif abs(info['offset_seconds']) < 10.0:
            status = "⚠️  UPOZORENJE - Mala netačnost"
        else:
            status = "❌ GREŠKA - Sistemski sat je značajno netačan"
        print(f"│ {status:<60} │")
    else:
        print("│ ❌ NTP nije dostupan - koristi se sistemsko vreme              │")
    
    if info['last_sync']:
        age = (datetime.now(timezone.utc) - info['last_sync']).total_seconds()
        age_str = format_time_diff(age)
        print(f"│ Poslednja sinhronizacija: pre {age_str:<29} │")
    
    print(f"│ Cache validan: {'DA ✓' if info['cache_valid'] else 'NE ✗':<51} │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    
    # Primer integracije
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ KAKO SE KORISTI U KODU                                          │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    print("  from astronomical_watch.net.ntp_sync import get_ntp_sync")
    print("  from astronomical_watch.core.timeframe import astronomical_time")
    print()
    print("  # Inicijalizacija (jednom pri startu)")
    print("  ntp = get_ntp_sync()")
    print("  ntp.start_background_sync(interval_seconds=3600)  # Svakih 1 sat")
    print()
    print("  # Dobijanje tačnog vremena (u update loop-u)")
    print("  now = ntp.get_corrected_time()  # Umesto datetime.now()")
    print("  dies, milidies = astronomical_time(now)")
    print()
    print("═" * 70)
    print()
    print("💡 TIP: Pokrenite 'poetry run python cli/ntp_status.py' za brzi status")
    print()

if __name__ == "__main__":
    main()
