# Android Widget Implementation Guide

## Overview

Astronomical Watch supports Android Home Screen Widgets with **automatic background updates**! The widget displays the current astronomical time (Dies.miliDies) and works immediately after installation - no need to open the app first.

## Architecture

### Widget Display
- **Compact view**: Shows "264.840" format (Dies . miliDies)
- **Transparent background**: Blends with any home screen theme
- **Monospace font**: Clear, readable digits
- **Auto-updates**: Every 60 seconds via background service

### Background Service
- **Starts automatically** when widget is added
- **Runs in foreground** (persistent notification)
- **Updates every 60 seconds** (battery-optimized)
- **Survives device reboot** (BOOT_COMPLETED receiver)

### Interaction
- **Tap widget** → Opens full Astronomical Watch app
- **No configuration** needed
- **Multiple instances** supported

## Files Structure

```
src/astronomical_watch/android/
├── __init__.py
└── widget_provider.py          # Python widget controller (Pyjnius)

android_resources/
├── AndroidManifest_extra.xml   # Receiver registration
├── res/
│   ├── layout/
│   │   └── widget_layout.xml   # Widget UI
│   └── xml/
│       └── widget_info.xml     # Widget metadata
└── src/
    └── AstroWidgetProvider.java  # Java AppWidgetProvider
```

## How It Works

### 1. Widget Added to Home Screen
```
User adds widget → onEnabled() called
                 → startForegroundService(widget_service.py)
                 → Service calculates time every 60s
                 → Updates widget via RemoteViews
```

### 2. Background Service (service/widget_service.py)
```python
while True:
    dies, milidies = astronomical_time(now)
    update_android_widget(dies, milidies)
    time.sleep(60)  # Update every minute
```

### 3. Auto-Start on Boot
```
Device boots → BOOT_COMPLETED broadcast
            → WidgetAutoStart receiver
            → Restarts service if widget exists
```

### 4. Service Lifecycle
- **Widget added**: Service starts
- **Widget removed**: Service stops (onDisabled)
- **App updated**: Service restarts (MY_PACKAGE_REPLACED)
- **Device reboot**: Service auto-restarts
```python
# Get Android AppWidgetManager
widget_manager = AppWidgetManager.getInstance(activity)

# Update RemoteViews
views = RemoteViews(package_name, layout_id)
views.setTextViewText(text_view_id, f"{dies}.{milidies:03d}")
widget_manager.updateAppWidget(widget_ids, views)
```

### 4. Java Provider (AstroWidgetProvider.java)
```java
public class AstroWidgetProvider extends AppWidgetProvider {
    @Override
    public void onUpdate(Context context, ...) {
        // Sets default text and click handler
        // Actual updates come from Python via Pyjnius
    }
}
```

## Building

### Requirements
```bash
# In buildozer.spec
requirements = python3==3.10,kivy==2.3.1,pyjnius,...
android.permissions = INTERNET,ACCESS_NETWORK_STATE,BIND_APPWIDGET
android.add_src = %(source.dir)s/android_resources/src
android.extra_manifest_xml = %(source.dir)s/android_resources/AndroidManifest_extra.xml
```

### Build APK
```bash
# Clean build
buildozer android clean

# Build debug APK
buildozer android debug

# Install to device
buildozer android deploy run
```

## Adding Widget to Home Screen

1. **Long-press** empty area on home screen
2. Tap **"Widgets"**
3. Find **"Astronomical Watch"**
4. **Drag** to home screen
5. **Widget starts updating immediately** (no need to open app!)
6. Notification appears: "Astronomical Watch - Updates astronomical time widget"

## Update Mechanism

- **Background Service**: Runs continuously, updates every 60 seconds
- **Battery Optimized**: Uses foreground service with low frequency updates
- **Persistent**: Survives device reboot and app updates
- **Automatic**: Starts when widget added, stops when all widgets removed

## Limitations

- **Android only**: Widget not available on iOS (different API)
- **Update frequency**: Depends on app running state
- **Battery**: Frequent updates consume more power
- **API level**: Requires Android API 21+ (Lollipop)

## Customization

### Widget Size
Edit `android_resources/res/xml/widget_info.xml`:
```xml
<appwidget-provider
    android:minWidth="110dp"     <!-- Adjust width -->
    android:minHeight="40dp"     <!-- Adjust height -->
    android:resizeMode="horizontal|vertical">
</appwidget-provider>
```

### Widget Appearance
Edit `android_resources/res/layout/widget_layout.xml`:
```xml
<TextView
    android:id="@+id/widget_time"
    android:textSize="24sp"        <!-- Font size -->
    android:textColor="#FFFFFF"    <!-- Color -->
    android:background="#88000000" <!-- Background -->
/>
```

### Update Frequency
Edit `src/astronomical_watch/ui/main_screen.py`:
```python
# Change from 0.2s to 1.0s
Clock.schedule_interval(self.update, 1.0)
```

## Troubleshooting

### Widget not appearing
- Check `buildozer.spec` has `BIND_APPWIDGET` permission
- Verify `android.add_src` path is correct
- Rebuild: `buildozer android clean && buildozer android debug`

### Widget shows "---"
- Open app at least once after installation
- Check app is not force-closed by Android
- Enable background activity for app in Settings

### Widget not updating
- Ensure app is running (even minimized)
- Check battery optimization settings
- Verify Pyjnius imported successfully (check logcat)

### Build errors
```bash
# Missing pyjnius
pip install pyjnius

# NDK/SDK issues
buildozer android clean
rm -rf .buildozer
buildozer android debug
```

## Future Enhancements

- [ ] Background service for persistent updates
- [ ] Widget configuration (theme, size presets)
- [ ] Multiple widget styles (minimal, detailed)
- [ ] Notification shade widget
- [ ] Lock screen widget support
- [ ] iOS Today Widget (separate implementation)

## Technical Notes

- **RemoteViews**: Limited layout options (no Canvas/custom drawing)
- **PendingIntent**: Required for click handling
- **Broadcast Receiver**: Handles system widget update requests
- **Pyjnius**: Enables Python → Java interop without JNI
