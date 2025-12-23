#!/usr/bin/env python3
"""
Automatski dodaj NTP translation keys u translations.py za SVE jezike
"""
import re

# NTP translations for ALL 28 languages
NTP_TRANS = {
    "en": {
        "ntp_notification_title": "⚠️ System Clock Inaccurate",
        "ntp_notification_text_seconds": "Time difference: {offset} seconds",
        "ntp_notification_text_minutes": "Time difference: {offset} minutes",
        "ntp_notification_text_hours": "Time difference: {offset} hours",
        "ntp_notification_body": "Your system clock is off by {offset_text}.\\n\\nAstronomical Watch uses NTP synchronization for accurate time, but we recommend enabling automatic time synchronization in your device settings.",
    },
    "sr": {
        "ntp_notification_title": "⚠️ Sistemski sat je netačan",
        "ntp_notification_text_seconds": "Razlika: {offset} sekundi",
        "ntp_notification_text_minutes": "Razlika: {offset} minuta",
        "ntp_notification_text_hours": "Razlika: {offset} sati",
        "ntp_notification_body": "Vaš sistemski sat odstupa {offset_text}.\\n\\nAstronomski sat koristi NTP sinhronizaciju za tačno vreme, ali preporučujemo da omogućite automatsku sinhronizaciju vremena u podešavanjima uređaja.",
    },
    "es": {
        "ntp_notification_title": "⚠️ Reloj del sistema inexacto",
        "ntp_notification_text_seconds": "Diferencia: {offset} segundos",
        "ntp_notification_text_minutes": "Diferencia: {offset} minutos",
        "ntp_notification_text_hours": "Diferencia: {offset} horas",
        "ntp_notification_body": "Su reloj del sistema está desfasado {offset_text}.\\n\\nReloj Astronómico utiliza sincronización NTP para tiempo preciso, pero recomendamos habilitar la sincronización automática de tiempo en la configuración de su dispositivo.",
    },
    "zh": {
        "ntp_notification_title": "⚠️ 系统时钟不准确",
        "ntp_notification_text_seconds": "时间差：{offset} 秒",
        "ntp_notification_text_minutes": "时间差：{offset} 分钟",
        "ntp_notification_text_hours": "时间差：{offset} 小时",
        "ntp_notification_body": "您的系统时钟偏差{offset_text}。\\n\\n天文表使用NTP同步来保持准确时间，但我们建议在设备设置中启用自动时间同步。",
    },
    "ar": {
        "ntp_notification_title": "⚠️ ساعة النظام غير دقيقة",
        "ntp_notification_text_seconds": "الفرق: {offset} ثانية",
        "ntp_notification_text_minutes": "الفرق: {offset} دقيقة",
        "ntp_notification_text_hours": "الفرق: {offset} ساعة",
        "ntp_notification_body": "ساعة النظام الخاصة بك متأخرة {offset_text}.\\n\\nالساعة الفلكية تستخدم مزامنة NTP للوقت الدقيق، ولكن نوصي بتمكين المزامنة التلقائية للوقت في إعدادات جهازك.",
    },
    "pt": {
        "ntp_notification_title": "⚠️ Relógio do sistema impreciso",
        "ntp_notification_text_seconds": "Diferença: {offset} segundos",
        "ntp_notification_text_minutes": "Diferença: {offset} minutos",
        "ntp_notification_text_hours": "Diferença: {offset} horas",
        "ntp_notification_body": "Seu relógio do sistema está atrasado {offset_text}.\\n\\nRelógio Astronômico usa sincronização NTP para tempo preciso, mas recomendamos habilitar a sincronização automática de tempo nas configurações do dispositivo.",
    },
    "fr": {
        "ntp_notification_title": "⚠️ Horloge système inexacte",
        "ntp_notification_text_seconds": "Différence: {offset} secondes",
        "ntp_notification_text_minutes": "Différence: {offset} minutes",
        "ntp_notification_text_hours": "Différence: {offset} heures",
        "ntp_notification_body": "Votre horloge système est décalée de {offset_text}.\\n\\nMontre Astronomique utilise la synchronisation NTP pour un temps précis, mais nous recommandons d'activer la synchronisation automatique du temps dans les paramètres de votre appareil.",
    },
    "de": {
        "ntp_notification_title": "⚠️ Systemuhr ungenau",
        "ntp_notification_text_seconds": "Unterschied: {offset} Sekunden",
        "ntp_notification_text_minutes": "Unterschied: {offset} Minuten",
        "ntp_notification_text_hours": "Unterschied: {offset} Stunden",
        "ntp_notification_body": "Ihre Systemuhr weicht {offset_text} ab.\\n\\nAstronomische Uhr verwendet NTP-Synchronisation für genaue Zeit, aber wir empfehlen, die automatische Zeitsynchronisation in den Geräteeinstellungen zu aktivieren.",
    },
    "ru": {
        "ntp_notification_title": "⚠️ Системные часы неточны",
        "ntp_notification_text_seconds": "Разница: {offset} секунд",
        "ntp_notification_text_minutes": "Разница: {offset} минут",
        "ntp_notification_text_hours": "Разница: {offset} часов",
        "ntp_notification_body": "Ваши системные часы отстают на {offset_text}.\\n\\nАстрономические часы используют синхронизацию NTP для точного времени, но мы рекомендуем включить автоматическую синхронизацию времени в настройках устройства.",
    },
    "ja": {
        "ntp_notification_title": "⚠️ システム時計が不正確です",
        "ntp_notification_text_seconds": "時間差：{offset} 秒",
        "ntp_notification_text_minutes": "時間差：{offset} 分",
        "ntp_notification_text_hours": "時間差：{offset} 時間",
        "ntp_notification_body": "システム時計が{offset_text}ずれています。\\n\\n天文時計はNTP同期を使用して正確な時刻を保っていますが、デバイス設定で自動時刻同期を有効にすることをお勧めします。",
    },
    "hi": {
        "ntp_notification_title": "⚠️ सिस्टम घड़ी गलत है",
        "ntp_notification_text_seconds": "अंतर: {offset} सेकंड",
        "ntp_notification_text_minutes": "अंतर: {offset} मिनट",
        "ntp_notification_text_hours": "अंतर: {offset} घंटे",
        "ntp_notification_body": "आपकी सिस्टम घड़ी {offset_text} से गलत है।\\n\\nखगोलीय घड़ी सटीक समय के लिए NTP सिंक्रनाइज़ेशन का उपयोग करती है, लेकिन हम अनुशंसा करते हैं कि आप अपने डिवाइस सेटिंग्स में स्वचालित समय सिंक्रनाइज़ेशन सक्षम करें।",
    },
    "fa": {
        "ntp_notification_title": "⚠️ ساعت سیستم نادرست است",
        "ntp_notification_text_seconds": "تفاوت: {offset} ثانیه",
        "ntp_notification_text_minutes": "تفاوت: {offset} دقیقه",
        "ntp_notification_text_hours": "تفاوت: {offset} ساعت",
        "ntp_notification_body": "ساعت سیستم شما {offset_text} عقب است.\\n\\nساعت نجومی از همگام‌سازی NTP برای زمان دقیق استفاده می‌کند، اما توصیه می‌کنیم همگام‌سازی خودکار زمان را در تنظیمات دستگاه خود فعال کنید.",
    },
    "id": {
        "ntp_notification_title": "⚠️ Jam sistem tidak akurat",
        "ntp_notification_text_seconds": "Perbedaan: {offset} detik",
        "ntp_notification_text_minutes": "Perbedaan: {offset} menit",
        "ntp_notification_text_hours": "Perbedaan: {offset} jam",
        "ntp_notification_body": "Jam sistem Anda terlambat {offset_text}.\\n\\nJam Astronomi menggunakan sinkronisasi NTP untuk waktu yang akurat, tetapi kami merekomendasikan mengaktifkan sinkronisasi waktu otomatis di pengaturan perangkat Anda.",
    },
    "sw": {
        "ntp_notification_title": "⚠️ Saa ya mfumo si sahihi",
        "ntp_notification_text_seconds": "Tofauti: {offset} sekunde",
        "ntp_notification_text_minutes": "Tofauti: {offset} dakika",
        "ntp_notification_text_hours": "Tofauti: {offset} masaa",
        "ntp_notification_body": "Saa yako ya mfumo imechelewa {offset_text}.\\n\\nSaa ya Falaki inatumia usawazishaji wa NTP kwa wakati sahihi, lakini tunapendekeza kuwezesha usawazishaji wa wakati wa kiotomatiki katika mipangilio ya kifaa chako.",
    },
    "ha": {
        "ntp_notification_title": "⚠️ Agogon tsarin ba daidai ba ne",
        "ntp_notification_text_seconds": "Bambanci: {offset} daƙiƙa",
        "ntp_notification_text_minutes": "Bambanci: {offset} mintuna",
        "ntp_notification_text_hours": "Bambanci: {offset} hours",
        "ntp_notification_body": "Agogon tsarin ku ya jinkirta {offset_text}.\\n\\nAgogon Astronomical yana amfani da daidaitawar NTP don lokaci madaidaici, amma muna ba da shawarar kunna daidaitawar lokaci ta atomatik a cikin saitunan na'urar ku.",
    },
    "tr": {
        "ntp_notification_title": "⚠️ Sistem saati yanlış",
        "ntp_notification_text_seconds": "Fark: {offset} saniye",
        "ntp_notification_text_minutes": "Fark: {offset} dakika",
        "ntp_notification_text_hours": "Fark: {offset} saat",
        "ntp_notification_body": "Sistem saatiniz {offset_text} gerideKalıyor.\\n\\nAstronomi Saati doğru zaman için NTP senkronizasyonu kullanır, ancak cihaz ayarlarınızda otomatik zaman senkronizasyonunu etkinleştirmenizi öneririz.",
    },
    "el": {
        "ntp_notification_title": "⚠️ Το ρολόι συστήματος είναι ανακριβές",
        "ntp_notification_text_seconds": "Διαφορά: {offset} δευτερόλεπτα",
        "ntp_notification_text_minutes": "Διαφορά: {offset} λεπτά",
        "ntp_notification_text_hours": "Διαφορά: {offset} ώρες",
        "ntp_notification_body": "Το ρολόι του συστήματός σας καθυστερεί {offset_text}.\\n\\nΤο Αστρονομικό Ρολόι χρησιμοποιεί συγχρονισμό NTP για ακριβή ώρα, αλλά συνιστούμε να ενεργοποιήσετε τον αυτόματο συγχρονισμό ώρας στις ρυθμίσεις της συσκευής σας.",
    },
    "pl": {
        "ntp_notification_title": "⚠️ Zegar systemowy jest niedokładny",
        "ntp_notification_text_seconds": "Różnica: {offset} sekund",
        "ntp_notification_text_minutes": "Różnica: {offset} minut",
        "ntp_notification_text_hours": "Różnica: {offset} godzin",
        "ntp_notification_body": "Twój zegar systemowy jest opóźniony o {offset_text}.\\n\\nZegar Astronomiczny wykorzystuje synchronizację NTP dla dokładnego czasu, ale zalecamy włączenie automatycznej synchronizacji czasu w ustawieniach urządzenia.",
    },
    "it": {
        "ntp_notification_title": "⚠️ Orologio di sistema impreciso",
        "ntp_notification_text_seconds": "Differenza: {offset} secondi",
        "ntp_notification_text_minutes": "Differenza: {offset} minuti",
        "ntp_notification_text_hours": "Differenza: {offset} ore",
        "ntp_notification_body": "L'orologio del tuo sistema è in ritardo di {offset_text}.\\n\\nOrologio Astronomico utilizza la sincronizzazione NTP per un tempo preciso, ma consigliamo di abilitare la sincronizzazione automatica del tempo nelle impostazioni del dispositivo.",
    },
    "nl": {
        "ntp_notification_title": "⚠️ Systeemklok onnauwkeurig",
        "ntp_notification_text_seconds": "Verschil: {offset} seconden",
        "ntp_notification_text_minutes": "Verschil: {offset} minuten",
        "ntp_notification_text_hours": "Verschil: {offset} uur",
        "ntp_notification_body": "Uw systeemklok loopt {offset_text} achter.\\n\\nAstronomische Klok gebruikt NTP-synchronisatie voor nauwkeurige tijd, maar we raden aan om automatische tijdsynchronisatie in te schakelen in uw apparaatinstellingen.",
    },
    "bn": {
        "ntp_notification_title": "⚠️ সিস্টেম ঘড়ি অসঠিক",
        "ntp_notification_text_seconds": "পার্থক্য: {offset} সেকেন্ড",
        "ntp_notification_text_minutes": "পার্থক্য: {offset} মিনিট",
        "ntp_notification_text_hours": "পার্থক্য: {offset} ঘন্টা",
        "ntp_notification_body": "আপনার সিস্টেম ঘড়ি {offset_text} পিছিয়ে আছে।\\n\\nজ্যোতির্বিজ্ঞান ঘড়ি সঠিক সময়ের জন্য NTP সিঙ্ক্রোনাইজেশন ব্যবহার করে, তবে আমরা আপনার ডিভাইস সেটিংসে স্বয়ংক্রিয় সময় সিঙ্ক্রোনাইজেশন সক্ষম করার পরামর্শ দিই।",
    },
    "he": {
        "ntp_notification_title": "⚠️ שעון המערכת לא מדויק",
        "ntp_notification_text_seconds": "הפרש: {offset} שניות",
        "ntp_notification_text_minutes": "הפרש: {offset} דקות",
        "ntp_notification_text_hours": "הפרש: {offset} שעות",
        "ntp_notification_body": "שעון המערכת שלך מפגר ב-{offset_text}.\\n\\nהשעון האסטרונומי משתמש בסנכרון NTP לזמן מדויק, אך אנו ממליצים להפעיל סנכרון זמן אוטומטי בהגדרות המכשיר שלך.",
    },
    "ko": {
        "ntp_notification_title": "⚠️ 시스템 시계가 부정확합니다",
        "ntp_notification_text_seconds": "시간 차이: {offset} 초",
        "ntp_notification_text_minutes": "시간 차이: {offset} 분",
        "ntp_notification_text_hours": "시간 차이: {offset} 시간",
        "ntp_notification_body": "시스템 시계가 {offset_text} 늦습니다.\\n\\n천문 시계는 정확한 시간을 위해 NTP 동기화를 사용하지만 장치 설정에서 자동 시간 동기화를 활성화하는 것이 좋습니다.",
    },
    "ku": {
        "ntp_notification_title": "⚠️ Saeta sîstemê ne rast e",
        "ntp_notification_text_seconds": "Cûda: {offset} çirke",
        "ntp_notification_text_minutes": "Cûda: {offset} deqîqe",
        "ntp_notification_text_hours": "Cûda: {offset} saet",
        "ntp_notification_body": "Saeta sîstemê te {offset_text} paşve ye.\\n\\nSaeta Astronomî ji bo wextê rast NTP-senkronîzasyonê bi kar tîne, lê em pêşniyar dikin ku hûn di mîhengên cîhaza xwe de senkronîzasyona wextê ya otomatîk çalak bikin.",
    },
    "ro": {
        "ntp_notification_title": "⚠️ Ceasul sistemului este inexact",
        "ntp_notification_text_seconds": "Diferență: {offset} secunde",
        "ntp_notification_text_minutes": "Diferență: {offset} minute",
        "ntp_notification_text_hours": "Diferență: {offset} ore",
        "ntp_notification_body": "Ceasul sistemului dvs. întârzie cu {offset_text}.\\n\\nCeasul Astronomic folosește sincronizarea NTP pentru timp precis, dar vă recomandăm să activați sincronizarea automată a timpului în setările dispozitivului.",
    },
    "ur": {
        "ntp_notification_title": "⚠️ سسٹم کلاک غلط ہے",
        "ntp_notification_text_seconds": "فرق: {offset} سیکنڈ",
        "ntp_notification_text_minutes": "فرق: {offset} منٹ",
        "ntp_notification_text_hours": "فرق: {offset} گھنٹے",
        "ntp_notification_body": "آپ کی سسٹم کلاک {offset_text} پیچھے ہے۔\\n\\nفلکیاتی گھڑی درست وقت کے لیے NTP ہم آہنگی استعمال کرتی ہے، لیکن ہم تجویز کرتے ہیں کہ آپ اپنے آلے کی ترتیبات میں خودکار وقت ہم آہنگی کو فعال کریں۔",
    },
    "vi": {
        "ntp_notification_title": "⚠️ Đồng hồ hệ thống không chính xác",
        "ntp_notification_text_seconds": "Chênh lệch: {offset} giây",
        "ntp_notification_text_minutes": "Chênh lệch: {offset} phút",
        "ntp_notification_text_hours": "Chênh lệch: {offset} giờ",
        "ntp_notification_body": "Đồng hồ hệ thống của bạn chậm {offset_text}.\\n\\nĐồng hồ Thiên văn sử dụng đồng bộ NTP để có thời gian chính xác, nhưng chúng tôi khuyên bạn nên bật đồng bộ thời gian tự động trong cài đặt thiết bị của bạn.",
    },
    "zu": {
        "ntp_notification_title": "⚠️ Iwashi lesistimu alinembile",
        "ntp_notification_text_seconds": "Umehluko: {offset} imizuzwana",
        "ntp_notification_text_minutes": "Umehluko: {offset} imizuzu",
        "ntp_notification_text_hours": "Umehluko: {offset} amahora",
        "ntp_notification_body": "Iwashi lakho lesistimu lisalela ngo-{offset_text}.\\n\\nIwashi Lezinkanyezi lisebenzisa ukuvumelanisa kwe-NTP ngesikhathi esinembile, kodwa siphakamisa ukuthi unike amandla ukuvumelanisa kwesikhathi ngokuzenzakalelayo ezilungiselelweni zedivayisi yakho.",
    },
}

print("=" * 70)
print("NTP Translation Keys for All 28 Languages")
print("=" * 70)
print()

for lang_code, translations in NTP_TRANS.items():
    print(f"✅ {lang_code}: {len(translations)} keys")
    for key in translations:
        print(f"   - {key}")
    print()

print("=" * 70)
print(f"Total languages: {len(NTP_TRANS)}")
print(f"Total keys per language: {len(list(NTP_TRANS.values())[0])}")
print("=" * 70)
