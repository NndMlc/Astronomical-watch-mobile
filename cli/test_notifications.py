#!/usr/bin/env python3
"""
Test notifikacije za velike offsete
Simulira različite scenarije offseta
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astronomical_watch.net.ntp_sync import NTPSync

def test_notification_scenarios():
    print("=" * 70)
    print("TEST NOTIFIKACIJA - Različiti Scenariji Offseta")
    print("=" * 70)
    print()
    
    # Kreiraj test instancu sa nižim pragom za demo
    ntp = NTPSync(warning_threshold=5.0)  # 5 sekundi za test
    
    print("📋 Konfigurisano:")
    print(f"   Prag upozorenja: {ntp._warning_threshold} sekundi")
    print()
    
    # Scenario 1: Mali offset (OK)
    print("1️⃣  SCENARIO 1: Mali offset (0.5s)")
    print("   " + "─" * 60)
    ntp._check_and_notify_offset(0.5)
    print()
    
    # Scenario 2: Veliki offset (upozorenje)
    print("2️⃣  SCENARIO 2: Veliki pozitivan offset (+75s)")
    print("   " + "─" * 60)
    ntp._check_and_notify_offset(75.0)
    print()
    
    # Scenario 3: Ponovni veliki offset (ne šalje ponovo)
    print("3️⃣  SCENARIO 3: Još uvek veliki offset (+80s)")
    print("   " + "─" * 60)
    ntp._check_and_notify_offset(80.0)
    print("   (Ne šalje notifikaciju ponovo - već je poslata)")
    print()
    
    # Scenario 4: Offset se vratio u normalu
    print("4️⃣  SCENARIO 4: Offset se vratio u normalu (0.3s)")
    print("   " + "─" * 60)
    ntp._check_and_notify_offset(0.3)
    print()
    
    # Scenario 5: Negativan veliki offset
    print("5️⃣  SCENARIO 5: Negativan veliki offset (-120s)")
    print("   " + "─" * 60)
    ntp._check_and_notify_offset(-120.0)
    print()
    
    # Scenario 6: Offset tačno 1 sat (mogući problem sa zonom)
    print("6️⃣  SCENARIO 6: Tačno 1 sat (+3600s) - mogući timezone issue?")
    print("   " + "─" * 60)
    ntp._last_warning_state = None  # Reset za ovaj test
    ntp._check_and_notify_offset(3600.0)
    print()
    
    # Scenario 7: Offset tačno 2 sata
    print("7️⃣  SCENARIO 7: Tačno 2 sata (+7200s)")
    print("   " + "─" * 60)
    ntp._last_warning_state = None  # Reset za ovaj test
    ntp._check_and_notify_offset(7200.0)
    print()
    
    print("=" * 70)
    print("✅ Test završen!")
    print()
    print("💡 Napomena: Na pravom Android uređaju bi se prikazale notifikacije")
    print("   Trenutno radimo u development okruženju bez Pyjnius-a")
    print()

if __name__ == "__main__":
    test_notification_scenarios()
