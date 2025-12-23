"""
NTP Time Synchronization Module
Periodično sinhronizuje vreme sa NTP serverima i primenjuje offset korekciju.
MIT License
"""
from __future__ import annotations
import socket
import struct
import time
from datetime import datetime, timezone, timedelta
from typing import Optional
import threading

# Import notification manager za upozorenja
try:
    from .notification_manager import get_notification_manager
except ImportError:
    # Fallback ako notification manager nije dostupan
    def get_notification_manager():
        class DummyNotificationManager:
            def show_time_sync_warning(self, offset_seconds): pass
            def show_time_sync_restored(self): pass
        return DummyNotificationManager()

# NTP konstante
NTP_PACKET_FORMAT = "!12I"
NTP_DELTA = 2208988800  # Sekunde između 1900 (NTP epoch) i 1970 (Unix epoch)
NTP_PORT = 123
NTP_TIMEOUT = 5  # sekundi

# Pool NTP servera (prioritizovani po brzini odgovora)
NTP_SERVERS = [
    "pool.ntp.org",
    "time.google.com",
    "time.cloudflare.com",
    "time.windows.com",
    "time.apple.com",
]

# Prag za upozorenje (sekunde)
# Offset veći od ovog praga će aktivirati notifikaciju
WARNING_THRESHOLD_SECONDS = 60.0  # 1 minut

class NTPSync:
    """
    NTP sinhronizator sa automatskim periodičnim ažuriranjima.
    
    Features:
    - Automatski fetch sa različitih NTP servera
    - Keširanje offseta sa TTL (Time To Live)
    - Thread-safe pristup offsetu
    - Fallback na sistemsko vreme ako NTP nije dostupan
    - Notifikacije za velike netačnosti sistemskog sata
    
    Usage:
        sync = NTPSync()
        sync.start_background_sync(interval_seconds=3600)  # Sync svakih sat vremena
        
        # Dobij tačno vreme
        accurate_now = sync.get_corrected_time()
    """
    
    def __init__(self, cache_ttl_seconds: int = 3600, warning_threshold: float = WARNING_THRESHOLD_SECONDS):
        """
        Args:
            cache_ttl_seconds: Koliko dugo je offset validan (default: 1h)
            warning_threshold: Prag za upozorenje u sekundama (default: 60s)
        """
        self._offset_seconds: Optional[float] = None
        self._last_sync: Optional[datetime] = None
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._lock = threading.Lock()
        self._background_thread: Optional[threading.Thread] = None
        self._running = False
        self._warning_threshold = warning_threshold
        self._last_warning_state = None  # True = upozorenje poslato, False = OK, None = nepoznato
        self._notification_manager = get_notification_manager()
        
    def fetch_ntp_time(self, server: str = "pool.ntp.org", timeout: int = NTP_TIMEOUT) -> Optional[datetime]:
        """
        Fetch tačno vreme sa NTP servera.
        
        Args:
            server: NTP server hostname
            timeout: Socket timeout u sekundama
            
        Returns:
            datetime objekat sa tačnim UTC vremenom, ili None ako fetch ne uspe
        """
        try:
            # Kreiraj NTP upit paket (mode 3 - client)
            ntp_packet = b'\x1b' + 47 * b'\0'
            
            # Pošalji upit
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            try:
                sock.sendto(ntp_packet, (server, NTP_PORT))
                response, _ = sock.recvfrom(1024)
            finally:
                sock.close()
            
            # Parse odgovor (transmit timestamp je na bajtu 40-47)
            if len(response) < 48:
                return None
                
            # Extract transmit timestamp (seconds since 1900)
            transmit_timestamp = struct.unpack('!12I', response[0:48])[10]
            
            # Konvertuj u Unix timestamp i zatim u datetime
            unix_timestamp = transmit_timestamp - NTP_DELTA
            ntp_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
            
            return ntp_time
            
        except (socket.timeout, socket.gaierror, OSError, struct.error) as e:
            print(f"NTP fetch error from {server}: {e}")
            return None
    
    def sync_with_ntp(self, max_attempts: int = 3) -> bool:
        """
        Sinhronizuj sa NTP serverom i izračunaj offset.
        Pokušava sa različitim serverima dok ne uspe.
        
        Args:
            max_attempts: Maksimalan broj pokušaja po serveru
            
        Returns:
            True ako je sinhronizacija uspela, False inače
        """
        for server in NTP_SERVERS:
            for attempt in range(max_attempts):
                ntp_time = self.fetch_ntp_time(server)
                
                if ntp_time is not None:
                    # VAŽNO: Oba vremena MORAJU biti UTC za tačnu proveru!
                    # datetime.now(timezone.utc) vraća UTC vreme nezavisno od lokalne zone
                    system_time = datetime.now(timezone.utc)
                    
                    # Izračunaj offset (razlika između NTP i sistemskog vremena)
                    # Pozitivan offset = sistemski sat kasni
                    # Negativan offset = sistemski sat ide napred
                    offset = (ntp_time - system_time).total_seconds()
                    
                    with self._lock:
                        self._offset_seconds = offset
                        self._last_sync = system_time
                    
                    print(f"NTP sync successful with {server}: offset = {offset:.3f}s")
                    
                    # Proveri da li treba upozorenje
                    # Koristimo abs() jer nas interesuje apsolutna razlika
                    self._check_and_notify_offset(offset)
                    
                    return True
                    
                if attempt < max_attempts - 1:
                    time.sleep(1)  # Wait pre sledećeg pokušaja
        
        print("NTP sync failed: all servers unavailable")
        return False
    
    def _check_and_notify_offset(self, offset_seconds: float):
        """
        Proveri offset i prikaži notifikaciju ako je prevelik.
        
        Koristi state tracking da ne šalje notifikaciju stalno:
        - Ako je offset veliki i ranije nije bilo upozorenja → Pošalji upozorenje
        - Ako je offset mali i ranije je bilo upozorenje → Ukloni upozorenje (opciono)
        - Inače → Ne radi ništa
        
        Args:
            offset_seconds: Trenutni offset između NTP i sistemskog vremena
        """
        # Koristi apsolutnu vrednost jer nas interesuje veličina razlike
        abs_offset = abs(offset_seconds)
        
        # Da li je offset prevelik?
        is_large_offset = abs_offset > self._warning_threshold
        
        # Proveri da li treba poslati/ukloniti notifikaciju
        if is_large_offset and self._last_warning_state != True:
            # Prevelik offset i ranije nije bilo upozorenja
            print(f"⚠️  Large time offset detected: {offset_seconds:+.1f}s (threshold: {self._warning_threshold}s)")
            print(f"    System time is {'behind' if offset_seconds > 0 else 'ahead'} by {abs_offset:.1f}s")
            
            # Dodatna provera: Da li je razlika stvarno u vremenu a ne u zoni?
            # Offset koji je tačno 1h, 2h, 3h... može ukazivati na problem sa zonom
            # Ali pošto koristimo UTC na obe strane, ovo ne bi trebalo da se desi
            hours_offset = abs_offset / 3600.0
            is_full_hour = abs(hours_offset - round(hours_offset)) < 0.01  # ±36 sekundi
            
            if is_full_hour and abs_offset >= 3600:
                print(f"    NOTE: Offset is close to {round(hours_offset)}h - possible timezone issue?")
                print(f"    Double-checking: Both times should be UTC...")
                # Ipak pošalji notifikaciju, ali sa opaskom
            
            # Pošalji notifikaciju
            self._notification_manager.show_time_sync_warning(offset_seconds)
            self._last_warning_state = True
            
        elif not is_large_offset and self._last_warning_state == True:
            # Offset je sada OK i ranije je bilo upozorenje
            print(f"✅ Time offset back to normal: {offset_seconds:+.3f}s")
            
            # Opciono: Ukloni notifikaciju (možda ne treba uznemiravati korisnika)
            # self._notification_manager.show_time_sync_restored()
            
            self._last_warning_state = False
        
        elif not is_large_offset and self._last_warning_state is None:
            # Prvo pokretanje, offset je OK
            print(f"✅ Time offset within acceptable range: {offset_seconds:+.3f}s")
            self._last_warning_state = False
    
    def get_corrected_time(self, force_sync: bool = False) -> datetime:
        """
        Dobij tačno UTC vreme sa primenjenom NTP korekcijom.
        
        Args:
            force_sync: Ako True, forsiraj novi NTP fetch
            
        Returns:
            datetime objekat sa korektovanim UTC vremenom
        """
        with self._lock:
            # Proveri da li treba refresh offseta
            if force_sync or self._offset_seconds is None or self._is_cache_expired():
                # Release lock tokom NTP fetcha (može trajati nekoliko sekundi)
                pass
            else:
                # Primeni keširani offset
                system_time = datetime.now(timezone.utc)
                corrected_time = system_time + timedelta(seconds=self._offset_seconds)
                return corrected_time
        
        # Sync van locka
        self.sync_with_ntp()
        
        # Apply offset
        with self._lock:
            system_time = datetime.now(timezone.utc)
            if self._offset_seconds is not None:
                corrected_time = system_time + timedelta(seconds=self._offset_seconds)
            else:
                # Fallback na sistemsko vreme ako sync ne uspe
                corrected_time = system_time
                
        return corrected_time
    
    def _is_cache_expired(self) -> bool:
        """Proveri da li je keširani offset istekao."""
        if self._last_sync is None:
            return True
        age = datetime.now(timezone.utc) - self._last_sync
        return age > self._cache_ttl
    
    def start_background_sync(self, interval_seconds: int = 3600):
        """
        Pokreni pozadinski thread koji periodično sinhronizuje vreme.
        
        Args:
            interval_seconds: Interval između sinhronizacija (default: 1h)
        """
        if self._running:
            print("Background NTP sync already running")
            return
        
        self._running = True
        
        def sync_loop():
            # Inicijalna sinhronizacija
            self.sync_with_ntp()
            
            while self._running:
                time.sleep(interval_seconds)
                if self._running:
                    self.sync_with_ntp()
        
        self._background_thread = threading.Thread(target=sync_loop, daemon=True)
        self._background_thread.start()
        print(f"Background NTP sync started (interval: {interval_seconds}s)")
    
    def stop_background_sync(self):
        """Zaustavi pozadinski sync thread."""
        if self._running:
            self._running = False
            if self._background_thread is not None:
                self._background_thread.join(timeout=5)
            print("Background NTP sync stopped")
    
    def get_offset_info(self) -> dict:
        """
        Dobij informacije o trenutnom offsetu.
        
        Returns:
            Dict sa 'offset_seconds', 'last_sync', 'cache_valid'
        """
        with self._lock:
            return {
                'offset_seconds': self._offset_seconds,
                'last_sync': self._last_sync,
                'cache_valid': not self._is_cache_expired() if self._last_sync else False
            }


# Globalna instanca (singleton pattern)
_global_ntp_sync: Optional[NTPSync] = None

def get_ntp_sync() -> NTPSync:
    """Dobij globalnu NTP sync instancu (singleton)."""
    global _global_ntp_sync
    if _global_ntp_sync is None:
        _global_ntp_sync = NTPSync()
    return _global_ntp_sync

def get_accurate_time() -> datetime:
    """
    Convenience funkcija: Dobij tačno UTC vreme sa NTP korekcijom.
    
    Returns:
        datetime objekat sa korektovanim UTC vremenom
    """
    return get_ntp_sync().get_corrected_time()
