"""
Notification Manager za Astronomical Watch
Prikazuje notifikacije o NTP statusu na Android uređajima.
MIT License
"""
from __future__ import annotations
from datetime import datetime, timezone
import traceback

def is_android():
    """Proveri da li aplikacija radi na Android-u"""
    try:
        from jnius import autoclass
        return True
    except:
        return False

def get_current_language():
    """Dobij trenutni izabrani jezik korisnika"""
    try:
        from astronomical_watch.lang.lang_config import load_language
        return load_language()
    except:
        return "en"  # Fallback na engleski

def tr(key: str, lang_code: str = None) -> str:
    """
    Prevedi ključ na izabrani jezik.
    
    Args:
        key: Translation key
        lang_code: Language code (default: trenutni jezik korisnika)
    
    Returns:
        Prevedeni string ili key ako prevod ne postoji
    """
    try:
        from astronomical_watch.lang.translations import TRANSLATIONS
        if lang_code is None:
            lang_code = get_current_language()
        return TRANSLATIONS.get(lang_code, {}).get(key, key)
    except:
        return key

class NotificationManager:
    """
    Manager za prikaz notifikacija na Android-u.
    Koristi Pyjnius za pristup Android Notification API-ju.
    """
    
    CHANNEL_ID = "astronomical_watch_alerts"
    CHANNEL_NAME = "Astronomical Watch Alerts"
    NOTIFICATION_ID_TIME_SYNC = 1001
    
    def __init__(self):
        self._initialized = False
        self._last_notification_time = None
        self._notification_cooldown_seconds = 3600  # Ne šalji istu notifikaciju češće od 1h
        
        if not is_android():
            return
        
        try:
            from jnius import autoclass
            
            # Android klase
            self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.NotificationManager = autoclass('android.app.NotificationManager')
            self.NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
            self.Context = autoclass('android.content.Context')
            self.NotificationChannel = autoclass('android.app.NotificationChannel')
            self.PendingIntent = autoclass('android.app.PendingIntent')
            self.Intent = autoclass('android.content.Intent')
            
            try:
                # Android O (API 26+) zahteva NotificationChannel
                self.Build_VERSION = autoclass('android.os.Build$VERSION')
                if self.Build_VERSION.SDK_INT >= 26:
                    self._create_notification_channel()
            except:
                pass  # Starije verzije Androida ne podržavaju channels
            
            self._initialized = True
            
        except Exception as e:
            print(f"NotificationManager init error: {e}")
            traceback.print_exc()
    
    def _create_notification_channel(self):
        """Kreiraj notification channel za Android O+ (API 26+)"""
        try:
            activity = self.PythonActivity.mActivity
            notification_manager = activity.getSystemService(self.Context.NOTIFICATION_SERVICE)
            
            # Kreiraj channel sa normalnim prioritetom
            importance = 3  # IMPORTANCE_DEFAULT
            channel = self.NotificationChannel(
                self.CHANNEL_ID,
                self.CHANNEL_NAME,
                importance
            )
            channel.setDescription("Upozorenja o sinhronizaciji vremena")
            
            notification_manager.createNotificationChannel(channel)
            print("Notification channel created")
            
        except Exception as e:
            print(f"Error creating notification channel: {e}")
    
    def _can_send_notification(self) -> bool:
        """Proveri da li možemo poslati notifikaciju (cooldown period)"""
        if self._last_notification_time is None:
            return True
        
        now = datetime.now(timezone.utc)
        elapsed = (now - self._last_notification_time).total_seconds()
        
        return elapsed >= self._notification_cooldown_seconds
    
    def show_time_sync_warning(self, offset_seconds: float):
        """
        Prikaži upozorenje o velikoj netačnosti sistemskog sata.
        
        Args:
            offset_seconds: Razlika između NTP i sistemskog vremena
        """
        if not self._initialized or not is_android():
            print(f"⚠️  UPOZORENJE: Sistemski sat je netačan za {offset_seconds:+.1f}s")
            return
        
        if not self._can_send_notification():
            print("Notification cooldown active, skipping...")
            return
        
        try:
            # Dobij trenutni jezik korisnika
            lang_code = get_current_language()
            
            activity = self.PythonActivity.mActivity
            
            # Intent za otvaranje aplikacije kada se tapne notifikacija
            intent = activity.getIntent()
            pending_intent = self.PendingIntent.getActivity(
                activity, 0, intent, 
                self.PendingIntent.FLAG_UPDATE_CURRENT | self.PendingIntent.FLAG_IMMUTABLE
            )
            
            # Formatiraj offset za prikaz (u izabranom jeziku)
            if abs(offset_seconds) < 60:
                offset_key = "ntp_notification_text_seconds"
                body_key = "ntp_notification_body_seconds"
                offset_value = f"{offset_seconds:+.1f}"
            elif abs(offset_seconds) < 3600:
                offset_key = "ntp_notification_text_minutes"
                body_key = "ntp_notification_body_minutes"
                minutes = offset_seconds / 60
                offset_value = f"{minutes:+.1f}"
            else:
                offset_key = "ntp_notification_text_hours"
                body_key = "ntp_notification_body_hours"
                hours = offset_seconds / 3600
                offset_value = f"{hours:+.1f}"
            
            # Prevedi notification strings
            title = tr("ntp_notification_title", lang_code)
            offset_text = tr(offset_key, lang_code).format(offset=offset_value)  # For notification text (short)
            body = tr(body_key, lang_code).format(offset=offset_value)  # For body (with units included)
            
            # Kreiraj notifikaciju
            builder = self.NotificationCompat.Builder(activity, self.CHANNEL_ID)
            builder.setSmallIcon(activity.getApplicationInfo().icon)
            builder.setContentTitle(title)
            builder.setContentText(offset_text)
            builder.setStyle(
                self.NotificationCompat.BigTextStyle().bigText(body)
            )
            builder.setPriority(self.NotificationCompat.PRIORITY_DEFAULT)
            builder.setContentIntent(pending_intent)
            builder.setAutoCancel(True)
            
            # Prikaži notifikaciju
            notification_manager = activity.getSystemService(self.Context.NOTIFICATION_SERVICE)
            notification_manager.notify(self.NOTIFICATION_ID_TIME_SYNC, builder.build())
            
            print(f"✅ Notification sent ({lang_code}): Time offset = {offset_seconds:+.1f}s")
            print(f"   Title: {title}")
            print(f"   Text: {offset_text}")
            self._last_notification_time = datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"Error showing notification: {e}")
            traceback.print_exc()
    
    def show_time_sync_restored(self):
        """
        Prikaži notifikaciju da je sistemski sat sada tačan.
        (Opcionalno - možda ne želimo da uznemiravamo korisnika)
        """
        if not self._initialized or not is_android():
            return
        
        try:
            activity = self.PythonActivity.mActivity
            notification_manager = activity.getSystemService(self.Context.NOTIFICATION_SERVICE)
            
            # Ukloni prethodnu notifikaciju
            notification_manager.cancel(self.NOTIFICATION_ID_TIME_SYNC)
            print("✅ Time sync warning cleared")
            
        except Exception as e:
            print(f"Error clearing notification: {e}")


# Globalna instanca (singleton pattern)
_global_notification_manager = None

def get_notification_manager() -> NotificationManager:
    """Dobij globalnu NotificationManager instancu (singleton)."""
    global _global_notification_manager
    if _global_notification_manager is None:
        _global_notification_manager = NotificationManager()
    return _global_notification_manager
