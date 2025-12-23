# NTP Sinhronizacija - Kako Radi

## Problem

Mobilni telefoni često imaju netačan sistemski sat zbog:
- Lošeg internet povezivanja
- Ručnog podešavanja vremena
- Problema sa baterijom
- Greške tokom dužeg offline perioda

**Rezultat**: Astronomical Watch prikazuje netačno vreme jer koristi sistemski sat.

## Rešenje

Dodao sam **automatsku NTP sinhronizaciju** koja:

1. **Pribavlja tačno vreme** sa internet servera
2. **Izračunava razliku** (offset) između sistemskog i tačnog vremena
3. **Primenjuje korekciju** na sve proračune
4. **Automatski se ažurira** svakih 1 sat
5. **Upozorava te** ako je sistemski sat jako netačan (>60 sekundi)

## Kako Koristiti

### Testiranje

```bash
poetry run python cli/test_ntp.py
```

Ova komanda će prikazati:
- Trenutno sistemsko vreme
- Tačno NTP vreme
- Razliku (offset) u sekundama
- Astronomsko vreme za oba

### U Aplikaciji

Aplikacija **automatski koristi NTP vreme**! Nije potrebna nikakva konfiguracija.

Kada pokrenete aplikaciju:
1. Odmah se konektuje na NTP server (pool.ntp.org)
2. Preuzme tačno vreme (traje ~0.5 sekundi)
3. Svakih 1 sat se automatski ažurira

### Bez Interneta

Ako nema internet konekcije:
- Aplikacija koristi sistemsko vreme (kao i ranije)
- Kada se internet vrati, automatski se sinhronizuje
- Keširani offset ostaje validan 1 sat

## Preciznost

- **NTP preciznost**: ±50 milisekundi preko interneta
- **Uticaj na Dies/miliDies**: Praktično zanemarljiv
- **1 milidan = 86.4 sekunde**, tako da greška od 50ms se ne vidi

## Notifikacije

### Podrška za 28 Jezika

**Notifikacije se automatski prikazuju na izabranom jeziku korisnika!**

Kada korisnik izabere jezik u aplikaciji (npr. Srpski, Engleski, Español, 中文, itd.), notifikacije će biti prikazane na tom jeziku.

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

### Kada se Prikazuje Upozorenje

Aplikacija će prikazati notifikaciju kada:
- Razlika između sistemskog i NTP vremena je **veća od 60 sekundi** (1 minut)
- Notifikacija se šalje **samo jednom** dok problem traje
- **Cooldown period**: Minimum 1 sat između notifikacija

### Šta Piše u Notifikaciji

```
⚠️ Sistemski sat je netačan

Razlika: +2.5 minuta (ili -1.3 sata, itd.)

Vaš sistemski sat odstupa od tačnog vremena.
Astronomical Watch koristi NTP sinhronizaciju 
za tačno vreme, ali preporučujemo da omogućite 
automatsku sinhronizaciju vremena u podešavanjima.
```

### Zaštita od Lažnih Alarma

**Problem**: Šta ako je offset prouzrokovan vremenskom zonom a ne netačnim satom?

**Rešenje**:
1. **Oba vremena su UTC**: `datetime.now(timezone.utc)` i NTP vreme su oba u UTC
2. **Nema konverzije zona**: Ne koristimo lokalnu vremensku zonu nigde
3. **Dodatna provera**: Ako je offset tačno 1h, 2h, 3h... to MOŽE značiti problem sa zonom
4. **Ali u praksi**: Pošto je UTC eksplicitan, ovo se neće desiti

**Primer**:
```python
# POGREŠNO (može biti problem sa zonom):
system_time = datetime.now()  # Lokalna zona!

# ISPRAVNO (što radimo):
system_time = datetime.now(timezone.utc)  # Uvek UTC!
```

## Potrošnja

### Internet
- **Veličina paketa**: 96 bytes (minimalno!)
- **Frekvencija**: Svakih 1 sat
- **Dnevno**: ~2.3 KB (praktično ništa)

### Baterija
- **Minimalna potrošnja**: Thread spava 99.99% vremena
- **Buđenje**: Samo za 1 NTP upit na sat
- **CPU**: < 0.1% tokom fetch-a

## NTP Serveri

Aplikacija koristi sledeće servere (po redosledu):
1. **pool.ntp.org** - Globalni pool NTP servera
2. **time.google.com** - Google Public NTP
3. **time.cloudflare.com** - Cloudflare NTP
4. **time.windows.com** - Microsoft NTP
5. **time.apple.com** - Apple NTP

Ako prvi ne radi, automatski prelazi na sledeći.

## Dodavanje Srpskih Servera

U fajlu `src/astronomical_watch/net/ntp_sync.py` možete dodati lokalne servere:

```python
NTP_SERVERS = [
    "rs.pool.ntp.org",  # Srpski NTP pool
    "ba.pool.ntp.org",  # Bosanski NTP pool
    "pool.ntp.org",
    "time.google.com",
    # ...
]
```

## Promena Intervala Ažuriranja

U `main_screen.py` možete promeniti interval:

```python
# Umesto 1 sat (3600 sekundi), svake 30 minute:
self.ntp_sync.start_background_sync(interval_seconds=1800)

# Ili svakih 2 sata:
self.ntp_sync.start_background_sync(interval_seconds=7200)
```

## Pitanja i Odgovori

**P: Da li će raditi bez interneta?**  
O: Da! Koristi sistemsko vreme kao fallback.

**P: Koliko troši internet?**  
O: ~2-3 KB dnevno (praktično ništa).

**P: Da li usporava aplikaciju?**  
O: Ne! Sve radi u pozadinskom thread-u.

**P: Šta ako je firewall blokira NTP?**  
O: Fallback na sistemsko vreme, aplikacija radi normalno.

**P: Može li se isključiti NTP sync?**  
O: Trenutno ne, ali možete lako dodati opciju u settings.

## Tehnički Detalji

Za više informacija pogledajte:
- [docs/NTP_SYNC.md](NTP_SYNC.md) - Puna tehnička dokumentacija
- [net/ntp_sync.py](../src/astronomical_watch/net/ntp_sync.py) - Izvorni kod
- [RFC 5905](https://tools.ietf.org/html/rfc5905) - NTP protokol specifikacija
