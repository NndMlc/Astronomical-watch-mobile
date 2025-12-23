# NTP Sinhronizacija Vremena

## Pregled

Astronomical Watch sada uključuje automatsku NTP (Network Time Protocol) sinhronizaciju za obezbeđivanje tačnog vremena, nezavisno od preciznosti sistemskog sata uređaja.

## Problem

Mobilni uređaji mogu imati netačan sistemski sat zbog:
- Ručnog podešavanja vremena
- Problema sa automatskom sinhronizacijom
- Drifta baterije CMOS/RTC (Real-Time Clock)
- Offline režima bez pristupa mobilnoj mreži

Pošto Astronomical Watch izračunava dies/miliDies na osnovu tačnog UTC vremena, greška od samo nekoliko sekundi može prouzrokovati netačan prikaz.

## Rešenje

### NTP Modul (`net/ntp_sync.py`)

Novi modul automatski:
1. **Fetch-uje tačno vreme** sa pouzdanih NTP servera (pool.ntp.org, time.google.com, itd.)
2. **Izračunava offset** između sistemskog i NTP vremena
3. **Kešira offset** sa TTL (Time To Live) od 1 sat
4. **Periodično ažurira** offset u pozadinskom thread-u
5. **Primenjuje korekciju** na sve vremenske proračune

### Arhitektura

```
┌─────────────────────────────────────┐
│  UI Layer (main_screen.py)          │
│  - WidgetMode                        │
│  - NormalMode                        │
└────────────┬────────────────────────┘
             │ get_corrected_time()
             ▼
┌─────────────────────────────────────┐
│  NTPSync (net/ntp_sync.py)          │
│  - Offset cache (1h TTL)            │
│  - Background sync thread           │
└────────────┬────────────────────────┘
             │ fetch_ntp_time()
             ▼
┌─────────────────────────────────────┐
│  NTP Servers                         │
│  - pool.ntp.org                     │
│  - time.google.com                  │
│  - time.cloudflare.com              │
└─────────────────────────────────────┘
```

### Integracija u Aplikaciju

**WidgetMode i NormalMode** (`ui/main_screen.py`):
```python
from astronomical_watch.net.ntp_sync import get_ntp_sync

def __init__(self):
    # Inicijalizuj NTP sync sa automatskim ažuriranjem svakih 1 sat
    self.ntp_sync = get_ntp_sync()
    self.ntp_sync.start_background_sync(interval_seconds=3600)

def update(self, dt=0):
    # Koristi NTP-korigovano vreme umesto sistemskog
    now = self.ntp_sync.get_corrected_time()
    dies, milidies = astronomical_time(now)
```

## Karakteristike

### Automatska Sinhronizacija
- **Inicijalni fetch**: Pri prvom pokretanju aplikacije
- **Periodično ažuriranje**: Svakih 1 sat (3600 sekundi)
- **Background thread**: Ne blokira UI
- **Graceful degradation**: Ako NTP nije dostupan, koristi sistemsko vreme

### Notifikacije o Netačnosti
- **Automatska detekcija**: Proverava offset nakon svake sinhronizacije
- **Prag upozorenja**: 60 sekundi (1 minut)
- **Smart alerts**: Samo jedna notifikacija dok problem traje (ne uznemirava stalno)
- **UTC provera**: Eliminiše lažne alarme zbog vremenskih zona
- **Cooldown period**: Minimum 1 sat između ponovljenih notifikacija
- **Podrška za 28 jezika**: Notifikacije se prikazuju na izabranom jeziku korisnika

**Primer na srpskom:**
```
⚠️ Sistemski sat je netačan

Razlika: +2.5 minuta

Vaš sistemski sat odstupa +2.5 minuta.

Astronomski sat koristi NTP sinhronizaciju za tačno 
vreme, ali preporučujemo da omogućite automatsku 
sinhronizaciju vremena u podešavanjima uređaja.
```

**Primer na engleskom:**
```
⚠️ System Clock Inaccurate

Time difference: +2.5 minutes

Your system clock is off by +2.5 minutes.

Astronomical Watch uses NTP synchronization for 
accurate time, but we recommend enabling automatic 
time synchronization in your device settings.
```

### Multi-Server Fallback
Pokušava sa različitim serverima po redosledu:
1. `pool.ntp.org` (globalni pool servera)
2. `time.google.com` (Google Public NTP)
3. `time.cloudflare.com` (Cloudflare NTP)
4. `time.windows.com` (Microsoft NTP)
5. `time.apple.com` (Apple NTP)

### Keširanje
- **TTL**: 1 sat (3600 sekundi)
- **Thread-safe**: Koristi `threading.Lock()` za thread-safe pristup
- **Automatski refresh**: Kada cache istekne, automatski fetch-uje novi offset

### Preciznost
- **NTP protokol**: RFC 5905 standard
- **Tipična preciznost**: ±50ms preko interneta
- **Offset primena**: Primenjuje se na svaki `get_corrected_time()` poziv

## Upotreba

### Test NTP Sinhronizacije

```bash
poetry run python cli/test_ntp.py
```

**Primer output-a:**
```
============================================================
NTP Sinhronizacija - Test
============================================================

📡 Pribavljam tačno vreme sa NTP servera...

⏰ Sistemsko vreme:  2025-12-23 14:30:45.123 UTC
🌐 NTP vreme:        2025-12-23 14:30:47.456 UTC
📊 Offset:           +2.333 sekundi
⚠️  Mala netačnost sistemskog sata

============================================================
Astronomsko vreme
============================================================

⏰ Sistemsko:  268.612
🌐 NTP:        268.615
📊 Razlika:    +3 milidies (+259.2 sekundi)

============================================================
Cache info
============================================================
Poslednja sinhronizacija: 2025-12-23 14:30:45.234567+00:00
Cache validan:            True
```

### Programatska Upotreba

```python
from astronomical_watch.net.ntp_sync import get_accurate_time, get_ntp_sync

# Dobij tačno vreme (automatski primenjuje NTP korekciju)
now = get_accurate_time()

# Ili koristi NTPSync instancu direktno
ntp = get_ntp_sync()
ntp.start_background_sync(interval_seconds=3600)  # Sync svakih 1 sat
accurate_time = ntp.get_corrected_time()

# Informacije o offsetu
info = ntp.get_offset_info()
print(f"Offset: {info['offset_seconds']}s")
print(f"Poslednja sinhronizacija: {info['last_sync']}")
print(f"Cache validan: {info['cache_valid']}")
```

## Konfiguracija

### Promena Intervala Sinhronizacije

U `main_screen.py`:
```python
# Promena sa 1 sat (3600s) na 30 minuta (1800s)
self.ntp_sync.start_background_sync(interval_seconds=1800)
```

### Promena TTL Cache-a

```python
from astronomical_watch.net.ntp_sync import NTPSync

# Cache validan 30 minuta
ntp = NTPSync(cache_ttl_seconds=1800)
```

### Dodavanje Dodatnih NTP Servera

U `net/ntp_sync.py`:
```python
NTP_SERVERS = [
    "pool.ntp.org",
    "time.google.com",
    "time.cloudflare.com",
    "rs.pool.ntp.org",  # Srpski NTP pool
    "ba.pool.ntp.org",  # Bosanski NTP pool
]
```

## Performanse

### Network Impact
- **Inicijalni fetch**: ~100-500ms (zavisi od latencije)
- **Packet size**: 48 bytes (request) + 48 bytes (response) = 96 bytes
- **Frekvencija**: Svakih 1 sat = 96 bytes/h = ~2.3 KB/dan
- **Minimalan impact**: Zanemarljiv uticaj na potrošnju podataka

### Battery Impact
- **Background thread**: Spava većinu vremena (`time.sleep(3600)`)
- **Wake-up**: Samo za 1 NTP request svakih 1 sat
- **CPU usage**: Minimalan (< 0.1% CPU during fetch)

### UI Performance
- **Non-blocking**: NTP fetch se izvršava u pozadinskom thread-u
- **Cache**: Vraća keširani offset bez network delay-a
- **Fallback**: Ako NTP nije dostupan, instant fallback na sistemsko vreme

## Limitacije

1. **Zahteva Internet**: NTP mora imati pristup UDP portu 123
2. **Firewall/NAT**: Neki firewall-ovi mogu blokirati NTP pakete
3. **Offline mode**: Kada je uređaj offline, koristi poslednji keširani offset
4. **Mobile data**: Koristi male količine mobilnih podataka (2-3 KB/dan)

## Troubleshooting

### NTP Sinhronizacija Ne Radi

**Provera:**
```bash
# Test NTP konekcije sa command line
poetry run python -c "from astronomical_watch.net.ntp_sync import NTPSync; ntp = NTPSync(); print(ntp.fetch_ntp_time())"
```

**Mogući uzroci:**
- Firewall blokira UDP port 123
- Nema internet konekcije
- DNS resolution problem za NTP servere

**Rešenje:**
- Proverite internet konekciju
- Testirati sa različitim NTP serverima
- Proveriti firewall postavke

### Veliki Offset (>10 sekundi)

**Uzrok**: Sistemski sat značajno odstupa od tačnog vremena.

**Rešenje**: 
- Ažurirajte sistemsko vreme ručno
- Omogućite automatsku sinhronizaciju vremena na uređaju
- NTP modul će automatski primeniti korekciju

### Notifikacija o Netačnosti

Aplikacija prikazuje notifikaciju kada:
- **Offset > 60 sekundi** (1 minut)
- **Samo jednom po sesiji** (cooldown 1 sat)
- **Ne uznemirava stalno** ako problem traje

**Sadržaj notifikacije:**
- Naslov: "⚠️ Sistemski sat je netačan"
- Tekst: Razlika u sekundama/minutima/satima
- Preporuka: Omogućiti automatsku sinhronizaciju

**Lažni alarmi (vremenske zone):**
- **NEĆE se desiti** jer koristimo UTC na obe strane
- Dodatna provera: Offset koji je tačno 1h, 2h, 3h može ukazivati na problem sa zonom
- Ali pošto je `datetime.now(timezone.utc)` eksplicitan, nema problema

## Budući Razvoj

Planirane funkcionalnosti:
- [x] Notifikacija kada je sistemski sat jako netačan ✅
- [ ] Persistent cache (čuvanje offseta između sesija)
- [ ] Fallback na HTTP time API (ako je NTP blokiran)
- [ ] UI indicator za NTP sync status
- [ ] Statistika preciznosti (tracking drift-a vremena)
- [ ] Konfiguracija preko UI (enable/disable NTP sync)
- [ ] Notifikacija kada je sistemski sat jako netačan
- [ ] Statistika preciznosti (tracking drift-a vremena)
- [ ] Konfiguracija preko UI (enable/disable NTP sync)

## Reference

- [RFC 5905 - Network Time Protocol Version 4](https://tools.ietf.org/html/rfc5905)
- [NTP Pool Project](https://www.pool.ntp.org/)
- [Google Public NTP](https://developers.google.com/time)
- [Cloudflare Time Services](https://www.cloudflare.com/time/)
