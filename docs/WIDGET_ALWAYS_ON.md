# Widget Always-On Implementation Summary

## Problem
Widget trebalo da pokazuje vreme čim se instalira, bez potrebe da se otvara aplikacija.

## Solution
Implementiran **Android Background Service** koji:
1. ✅ **Startuje automatski** kada se widget doda na home screen
2. ✅ **Radi u pozadini** nezavisno od main app
3. ✅ **Update-uje svaki minut** (battery-friendly)
4. ✅ **Restartuje se nakon reboot-a** device-a

## Components

### Python Service (`service/widget_service.py`)
```python
while True:
    dies, milidies = astronomical_time(now)
    update_android_widget(dies, milidies)
    time.sleep(60)
```

### Java Receivers
1. **AstroWidgetProvider.java** - Pokreće/zaustavlja service
2. **WidgetAutoStart.java** - Auto-start nakon boot/update

### AndroidManifest
- `APPWIDGET_ENABLED` → Startuje service kad se doda widget
- `BOOT_COMPLETED` → Restartuje service nakon reboot-a
- `MY_PACKAGE_REPLACED` → Restartuje nakon app update-a

### Permissions
- `FOREGROUND_SERVICE` - Za background service
- `WAKE_LOCK` - Da održava service aktivnim
- `RECEIVE_BOOT_COMPLETED` - Za auto-start

## User Experience

### Before (old implementation)
```
1. Install app
2. Add widget to home screen → Shows "---"
3. Open app → Widget starts updating
4. Close app → Widget stops
5. Reboot → Widget shows old value
```

### After (new implementation)
```
1. Install app
2. Add widget to home screen → Immediately shows "264.840"
3. Widget updates every 60s automatically
4. Works without opening app
5. Survives reboot (auto-restarts)
6. Small notification: "Astronomical Watch running"
```

## Battery Impact
- Update frequency: **60 seconds** (vs 0.2s when app open)
- Foreground service: **Persistent but lightweight**
- No GPS/sensors: **Only CPU for calculation**
- Estimated impact: **< 1% battery per day**

## Build Changes

### buildozer.spec
```ini
services = WidgetService:service/widget_service.py:foreground
requirements = ...,pyjnius
android.permissions = INTERNET,ACCESS_NETWORK_STATE,BIND_APPWIDGET,
                     FOREGROUND_SERVICE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED
android.add_src = %(source.dir)s/android_resources/src
android.extra_manifest_xml = %(source.dir)s/android_resources/AndroidManifest_extra.xml
```

## Testing

### Manual Test
```bash
# Build and install
buildozer android debug
adb install -r bin/*.apk

# Add widget to home screen
# Check it shows current time immediately

# Reboot device
adb reboot

# After boot, check widget still updates
```

### Expected Behavior
- Widget shows time within 10 seconds of being added
- Updates visible every 60 seconds
- Persistent notification visible
- Survives app force-stop (Android 8+)
- Restarts after reboot

## Troubleshooting

### Widget shows "---"
- Check notification: "Astronomical Watch" should be visible
- Settings → Apps → Astronomical Watch → Battery → Unrestricted
- Check logcat: `adb logcat | grep "Widget service"`

### Service not starting
- Verify permissions in AndroidManifest
- Check Android version (requires API 21+)
- Disable battery optimization for app

### Widget not updating
- Foreground service should show notification
- If missing, service was killed by Android
- Add to battery whitelist in Settings

## Future Improvements
- [ ] Configurable update frequency (30s/60s/120s)
- [ ] Silent notification option (Android 13+)
- [ ] Widget tap to force refresh
- [ ] Show "last updated" timestamp
- [ ] Multiple widget sizes with different info
