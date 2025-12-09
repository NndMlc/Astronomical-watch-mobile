"""
Android Home Screen Widget for Astronomical Watch
Shows Dies.miliDies in compact format on home screen.
Clicking opens full application.
"""
from __future__ import annotations
import traceback

def is_android():
    """Check if running on Android"""
    try:
        from jnius import autoclass
        return True
    except:
        return False

class AstronomicalWidget:
    """
    Home screen widget showing current astronomical time.
    Uses Android RemoteViews API via Pyjnius.
    """
    
    def __init__(self):
        if not is_android():
            return
            
        try:
            from jnius import autoclass
            
            # Android classes
            self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.RemoteViews = autoclass('android.widget.RemoteViews')
            self.AppWidgetManager = autoclass('android.appwidget.AppWidgetManager')
            self.ComponentName = autoclass('android.content.ComponentName')
            self.Intent = autoclass('android.content.Intent')
            self.PendingIntent = autoclass('android.app.PendingIntent')
            
            self.activity = self.PythonActivity.mActivity
            self.package_name = self.activity.getPackageName()
            
        except Exception as e:
            print(f"AstronomicalWidget init failed: {e}")
            traceback.print_exc()
    
    def update_widget(self, dies: int, milidies: int):
        """
        Update widget display with current astronomical time.
        
        Args:
            dies: Current dies (day since equinox)
            milidies: Current milidies (1/1000 of day)
        """
        if not is_android():
            return
            
        try:
            # Get widget manager
            widget_manager = self.AppWidgetManager.getInstance(self.activity)
            
            # Create ComponentName for our widget provider
            # This would match the Java class we define in buildozer
            component = self.ComponentName(
                self.package_name,
                f"{self.package_name}.AstroWidgetProvider"
            )
            
            # Get all widget IDs
            widget_ids = widget_manager.getAppWidgetIds(component)
            
            if not widget_ids or len(widget_ids) == 0:
                return  # No widgets added to home screen
            
            # Create RemoteViews for widget layout
            views = self.RemoteViews(self.package_name, 
                                     self.activity.getResources().getIdentifier(
                                         "widget_layout", "layout", self.package_name
                                     ))
            
            # Update text: "264.840"
            time_text = f"{dies}.{milidies:03d}"
            views.setTextViewText(
                self.activity.getResources().getIdentifier(
                    "widget_time", "id", self.package_name
                ),
                time_text
            )
            
            # Create intent to open main app on click
            intent = self.Intent(self.activity, self.PythonActivity)
            intent.setFlags(self.Intent.FLAG_ACTIVITY_NEW_TASK)
            
            pending_intent = self.PendingIntent.getActivity(
                self.activity, 0, intent, 
                self.PendingIntent.FLAG_UPDATE_CURRENT | self.PendingIntent.FLAG_IMMUTABLE
            )
            
            views.setOnClickPendingIntent(
                self.activity.getResources().getIdentifier(
                    "widget_layout", "id", self.package_name
                ),
                pending_intent
            )
            
            # Update all widget instances
            for widget_id in widget_ids:
                widget_manager.updateAppWidget(widget_id, views)
                
        except Exception as e:
            print(f"Widget update failed: {e}")
            traceback.print_exc()

# Singleton instance
_widget_instance = None

def get_widget():
    """Get singleton widget instance"""
    global _widget_instance
    if _widget_instance is None:
        _widget_instance = AstronomicalWidget()
    return _widget_instance

def update_android_widget(dies: int, milidies: int):
    """
    Public API to update Android widget from main app.
    Safe to call even when not on Android.
    """
    if is_android():
        widget = get_widget()
        widget.update_widget(dies, milidies)

__all__ = ['AstronomicalWidget', 'is_android', 'update_android_widget']
