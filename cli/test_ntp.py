#!/usr/bin/env python3
"""
Test NTP sinhronizacije - Demo skripta
Prikazuje razliku između sistemskog i NTP vremena.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astronomical_watch.net.ntp_sync import NTPSync, get_accurate_time
from astronomical_watch.core.timeframe import astronomical_time
from datetime import datetime, timezone

def main():
    print("=" * 60)
    print("NTP Sinhronizacija - Test")
    print("=" * 60)
    print()
    
    # Kreiraj NTP sync instancu
    ntp = NTPSync(cache_ttl_seconds=300)  # Cache 5 minuta
    
    print("📡 Pribavljam tačno vreme sa NTP servera...")
    print()
    
    # Sistemsko vreme
    system_time = datetime.now(timezone.utc)
    print(f"⏰ Sistemsko vreme:  {system_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} UTC")
    
    # NTP vreme
    ntp_time = ntp.get_corrected_time()
    print(f"🌐 NTP vreme:        {ntp_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} UTC")
    
    # Offset
    offset_info = ntp.get_offset_info()
    if offset_info['offset_seconds'] is not None:
        offset = offset_info['offset_seconds']
        print(f"📊 Offset:           {offset:+.3f} sekundi")
        
        if abs(offset) < 1.0:
            print(f"✅ Sistemski sat je tačan (razlika < 1s)")
        elif abs(offset) < 10.0:
            print(f"⚠️  Mala netačnost sistemskog sata")
        else:
            print(f"❌ VELIKA netačnost sistemskog sata!")
    else:
        print("❌ NTP sinhronizacija nije uspela")
    
    print()
    print("=" * 60)
    print("Astronomsko vreme")
    print("=" * 60)
    print()
    
    # Astronomsko vreme sa sistemskim satom
    dies_sys, milidies_sys = astronomical_time(system_time)
    print(f"⏰ Sistemsko:  {dies_sys:03d}.{milidies_sys:03d}")
    
    # Astronomsko vreme sa NTP satom
    dies_ntp, milidies_ntp = astronomical_time(ntp_time)
    print(f"🌐 NTP:        {dies_ntp:03d}.{milidies_ntp:03d}")
    
    # Razlika
    if dies_sys == dies_ntp:
        diff_milidies = milidies_ntp - milidies_sys
        print(f"📊 Razlika:    {diff_milidies:+d} milidies ({diff_milidies * 86.4:+.1f} sekundi)")
    else:
        print(f"📊 Razlika:    {dies_ntp - dies_sys} dies razlike!")
    
    print()
    print("=" * 60)
    print("Cache info")
    print("=" * 60)
    print()
    print(f"Poslednja sinhronizacija: {offset_info['last_sync']}")
    print(f"Cache validan:            {offset_info['cache_valid']}")
    print()
    
    print("💡 Preporuka: Integriši NTP sync u main_screen.py")
    print("   za automatsko ažuriranje svakih 1 sat.")

if __name__ == "__main__":
    main()
