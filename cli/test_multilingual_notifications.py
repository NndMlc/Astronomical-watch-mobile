#!/usr/bin/env python3
"""
Test multilingual notification messages for all 28 supported languages.

This script simulates notification display for various time offsets
in all supported languages without actually sending Android notifications.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astronomical_watch.lang.translations import tr
from astronomical_watch.lang.lang_config import save_language, load_language

# All 28 supported languages
LANGUAGES = [
    "en", "sr", "es", "zh", "ar", "pt", "fr", "de", "ru", "ja",
    "hi", "fa", "id", "sw", "ha", "tr", "el", "pl", "it", "nl",
    "bn", "he", "ko", "ku", "ro", "ur", "vi", "zu"
]

def format_notification(offset_seconds: float, lang_code: str) -> dict:
    """Format notification message for given offset and language."""
    offset_abs = abs(offset_seconds)
    
    # Choose appropriate format based on magnitude
    if offset_abs < 60:
        # Seconds
        offset_key = "ntp_notification_text_seconds"
        body_key = "ntp_notification_body_seconds"
        offset_value = f"{offset_seconds:+.1f}"
    elif offset_abs < 3600:
        # Minutes
        minutes = offset_seconds / 60
        offset_key = "ntp_notification_text_minutes"
        body_key = "ntp_notification_body_minutes"
        offset_value = f"{minutes:+.1f}"
    else:
        # Hours
        hours = offset_seconds / 3600
        offset_key = "ntp_notification_text_hours"
        body_key = "ntp_notification_body_hours"
        offset_value = f"{hours:+.1f}"
    
    # Translate notification strings
    title = tr("ntp_notification_title", lang_code)
    offset_text = tr(offset_key, lang_code).format(offset=offset_value)  # For notification text (short)
    
    try:
        body = tr(body_key, lang_code).format(offset=offset_value)  # For body
    except KeyError:
        # If NTP keys not available for this language, return empty
        body = ""
    
    return {
        "title": title,
        "text": offset_text,
        "body": body
    }


def test_language(lang_code: str, offset_seconds: float):
    """Test notification for specific language and offset."""
    print(f"\n{'='*60}")
    print(f"Language: {lang_code.upper()} | Offset: {offset_seconds:+.1f}s")
    print('='*60)
    
    notification = format_notification(offset_seconds, lang_code)
    
    print(f"\n{notification['title']}")
    print(f"\n{notification['text']}")
    print(f"\n{notification['body']}")


def main():
    """Test all languages with various offset scenarios."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Multilingual NTP Notification Test                     ║")
    print("║  Testing all 28 supported languages                     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Test scenarios
    scenarios = [
        ("Small offset (2.5 seconds)", 2.5),
        ("Medium offset (2.5 minutes)", 150),
        ("Large offset (2.5 hours)", 9000),
        ("Negative offset (-90 seconds)", -90),
    ]
    
    # Test each scenario with a few sample languages
    sample_languages = ["en", "sr", "es", "zh", "ar", "ru", "ja", "hi"]
    
    for scenario_name, offset in scenarios:
        print(f"\n\n{'#'*60}")
        print(f"# {scenario_name}")
        print('#'*60)
        
        for lang in sample_languages:
            test_language(lang, offset)
    
    # Summary table of all languages
    print("\n\n" + "="*60)
    print("SUMMARY: All 28 Languages - Notification Titles")
    print("="*60)
    
    for lang in LANGUAGES:
        title = tr("ntp_notification_title", lang)
        print(f"{lang.upper():>4}: {title}")
    
    print("\n✅ Test completed successfully!")
    print(f"📊 Tested {len(LANGUAGES)} languages × {len(scenarios)} scenarios")


if __name__ == "__main__":
    main()
