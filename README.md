# Astronomical Watch Mobile 🌍⏰

A mobile phone application that tracks time based on real astronomical phenomena—specifically, the vernal equinox. Instead of arbitrary calendar months, time is expressed as **dies** (days since equinox) and **miliDies** (1/1000th of a day = 86.4 seconds).

## ✨ Features

- 📅 **Astronomical Time Display**: Shows current dies.miliDies based on actual solar position
- 🌌 **Dynamic Sky Theme**: Background gradients change based on solar altitude (day/night/twilight)
- 🌐 **28 Languages**: Full internationalization (English, Español, 中文, العربية, and 24 more)
- 📱 **Widget & Normal Modes**: Minimalist widget or detailed full-screen view
- 🏠 **Android Home Screen Widget**: Shows Dies.miliDies on your home screen (tap to open app)
- 🔄 **Auto-updating**: Refreshes every 0.2 seconds with smooth progress bars
- ⏱️ **NTP Time Sync**: Automatic synchronization with internet time servers for precise timekeeping

## 🚀 Quick Start

### Option 1: View in VS Code (Recommended for Development)

**No phone needed! Run in your browser:**

```bash
./launch_vnc.sh
```

Then open in VS Code:
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Simple Browser: Show`
3. URL: `http://localhost:6080/vnc.html`
4. Click **Connect** button

### Option 2: Run with Virtual Display (Headless)

```bash
./launch_xvfb.sh
```

Runs Kivy app with Xvfb (no GUI visible, but logs show it's working).

### Option 3: Build for Android/iOS

See **[BUILD.md](BUILD.md)** for complete instructions.

**Android:**
```bash
buildozer android debug
```

**iOS** (macOS only):
```bash
kivy-ios build astronomical_watch kivy
```

## 📖 Documentation

- **[BUILD.md](BUILD.md)** - Build instructions for Android/iOS
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development workflows and preview options
- **[SPEC.md](SPEC.md)** - Astronomical time system specification
- **[UI_REFACTOR.md](UI_REFACTOR.md)** - Recent UI compatibility fixes
- **[docs/NTP_SYNC.md](docs/NTP_SYNC.md)** - NTP time synchronization system
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI agent development guide

## 🎨 Screenshots

*Coming soon: Screenshots of Widget Mode, Normal Mode, and Language Selection*

## 🏗️ Architecture

### Dual License System

- **Core** (`src/astronomical_watch/core/`) - Immutable astronomical algorithms (NO MODIFICATION LICENSE)
- **Everything else** - MIT License (freely modifiable)

### Key Components

- **Core Layer**: VSOP87D-based solar position, precise equinox calculation, timeframe conversion
- **UI Layer**: Kivy-based mobile interface with dynamic theming
- **Services**: Hybrid equinox service (Internet → Analytic → Approx fallback)
- **Internationalization**: 28 languages via `lang/` translation files

## ⏰ Current Astronomical Time

Run this to see the current time:

```bash
poetry run python cli/awatch.py
```

Example output: `262.815` (day 262, milidan 815 since last vernal equinox)

## 🛠️ Development Setup

**Requirements:**
- Python ≥ 3.10
- Poetry (dependency management)
- For GUI preview: Xvfb, x11vnc, noVNC

**Install dependencies:**
```bash
poetry install
```

**Run tests:**
```bash
# Coming soon: test suite in development
```

**Sync Core from desktop repo:**
```bash
.github/sync_to_mobile.sh
```

## 📱 Usage

### Widget Mode (Minimalist)
- Shows large **dies.miliDies** display
- Progress bar for current milidan
- Tap anywhere → switches to Normal Mode

### Normal Mode (Full Screen)
- Dies and miliDies shown separately
- Standard UTC time reference
- Three card buttons:
  - **Explanation**: Learn about astronomical time (28 languages)
  - **Comparison**: Compare with standard calendars (coming soon)
  - **Calculations**: Local solar noon, equation of time graph (coming soon)
- Language selector (🌐 button)
- Back button (<) returns to Widget Mode

## 🌍 How It Works

Instead of arbitrary calendar dates, this system tracks time relative to the **vernal equinox** (when the Sun crosses the celestial equator):

- **Day 0** starts at the first **reference noon** after the equinox
- **Reference noon** = 23:15:54 UTC (when global reference meridian at -168.975° longitude experiences mean solar noon)
- **1 dies** = 1 solar day (from noon to noon)
- **1 miliDies** = 86.4 seconds (1/1000th of a day)

See **[SPEC.md](SPEC.md)** for complete technical specification.

## 🤝 Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines.

**Important**: Core files (`src/astronomical_watch/core/`) cannot be modified. Propose changes upstream via PR.

## 📜 License

- **Core algorithms**: NO MODIFICATION LICENSE (see [LICENSE.CORE](LICENSE.CORE))
- **UI and services**: MIT License (see [LICENSE.MIT](LICENSE.MIT))

## 🔗 Related Projects

- **Desktop version**: [Astronomical-watch](https://github.com/NndMlc/Astronomical-watch) (where Core is developed)

## 📞 Support

Found a bug? Open an issue on GitHub.

---

**Current Status**: ✅ Working | 🚧 Comparison & Calculations cards in development
