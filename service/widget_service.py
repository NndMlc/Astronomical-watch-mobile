"""
Background service for Android widget updates.
Runs independently of main app, updates widget every minute.
"""
from __future__ import annotations
import time
from datetime import datetime, timezone

def update_widget_loop():
    """
    Background service main loop.
    Updates widget every 60 seconds even when app is closed.
    """
    try:
        from astronomical_watch.core.timeframe import astronomical_time
        from astronomical_watch.android.widget_provider import update_android_widget, is_android
        
        if not is_android():
            print("Widget service: Not on Android, exiting")
            return
            
        print("Widget service: Started")
        
        while True:
            try:
                # Calculate current astronomical time
                now = datetime.now(timezone.utc)
                dies, milidies = astronomical_time(now)
                
                # Update widget
                update_android_widget(dies, milidies)
                
                print(f"Widget service: Updated to {dies}.{milidies:03d}")
                
                # Sleep for 1 minute (reduces battery usage)
                time.sleep(60)
                
            except Exception as e:
                print(f"Widget service: Update error: {e}")
                time.sleep(60)  # Continue even on error
                
    except Exception as e:
        print(f"Widget service: Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_widget_loop()
