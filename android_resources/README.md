# Android Home Screen Widget Setup

This directory contains Android-specific resources for the home screen widget.

## Structure

```
android_resources/
├── AndroidManifest_extra.xml  # Widget receiver declaration
├── res/
│   ├── layout/
│   │   └── widget_layout.xml  # Widget UI layout
│   └── xml/
│       └── widget_info.xml    # Widget metadata
└── src/
    └── AstroWidgetProvider.java  # Widget provider class
```

## Widget Functionality

- **Display**: Shows Dies.miliDies (e.g., "264.840") on home screen
- **Update**: Refreshes automatically when app is running
- **Interaction**: Tapping widget opens full application
- **Size**: Minimal (110dp × 40dp), resizable

## Build Integration

The widget is integrated via `buildozer.spec`:
- `requirements` includes `pyjnius` for Java bridge
- `android.permissions` includes `BIND_APPWIDGET`
- `android.add_src` points to Java source files
- `android.extra_manifest_xml` registers receiver

## Usage on Android

1. Build APK: `buildozer android debug`
2. Install on device
3. Long-press home screen → Widgets → Astronomical Watch
4. Drag to home screen
5. Widget updates every 0.2s when app runs in background

## Technical Details

- **Python → Java**: Pyjnius calls `AppWidgetManager.updateAppWidget()`
- **Java → Python**: Widget tap launches `PythonActivity`
- **Updates**: Handled by `update_android_widget()` in main_screen.py
- **Layout**: RemoteViews with TextView (monospace font)
