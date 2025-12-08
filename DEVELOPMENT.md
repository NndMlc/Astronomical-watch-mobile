# Development Preview Options

## Overview
Kivy aplikacije zahtevaju GUI display. U cloud okruženjima (GitHub Codespaces) postoje različite opcije za pregled.

## Opcija 1: Desktop Emulator (Najbolje za Linux/Mac/Windows)

### Lokalni Development
```bash
# Aktiviraj environment i pokreni
poetry run python main.py
```

Ili koristi `dev.sh` script:
```bash
./dev.sh
```

## Opcija 2: VNC Viewer (Za Codespaces)

### Setup VNC Server
```bash
# 1. Instaliraj VNC server
sudo apt-get update
sudo apt-get install -y x11vnc xvfb

# 2. Startuj virtual display
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99

# 3. Startuj VNC server
x11vnc -display :99 -forever -nopw &

# 4. Port forward 5900 u VS Code
```

### Konektuj sa VNC Client
- Preuzmi VNC Viewer (RealVNC, TigerVNC, etc.)
- Konektuj na: `localhost:5900`
- Pokreni aplikaciju: `./dev.sh`

## Opcija 3: Browser Preview (Workaround)

### Kivy na Web (Eksperimentalno)
Koristi Pyodide ili PyScript za web verziju:
```bash
# Ovo zahteva refaktorisanje koda
pip install pyodide-build
```

## Opcija 4: Android Emulator + VS Code

**Najbolja opcija za preview mobilne verzije:**

### 1. Instaliraj Android iOS Emulator Extension
Već instalirana: `diemasmichiels.emulate`

### 2. Build i deploy na emulator
```bash
# Build debug APK
buildozer android debug

# Instaliraj na emulator (mora biti pokrenut)
adb install bin/astronomicalwatch-0.1.0-arm64-v8a-debug.apk

# Ili koristi buildozer deploy
buildozer android debug deploy run
```

### 3. Pokreni emulator iz VS Code
- Pritisni `Ctrl+Shift+P`
- Upiši "Emulate"
- Izaberi "Start Android Emulator"

## Opcija 5: Live Reload Development

### Dodaj hot reload
Instaliraj `watchdog` za auto-restart:
```bash
poetry add --group dev watchdog
```

### Kreiraj watch script
```python
# watch.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys

class RestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_app()
    
    def start_app(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen([sys.executable, "main.py"])
    
    def on_modified(self, event):
        if event.src_path.endswith('.py') or event.src_path.endswith('.kv'):
            print(f"🔄 Detected change in {event.src_path}, restarting...")
            self.start_app()

if __name__ == "__main__":
    handler = RestartHandler()
    observer = Observer()
    observer.schedule(handler, path='src/', recursive=True)
    observer.start()
    
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        if handler.process:
            handler.process.terminate()
```

Pokreni:
```bash
poetry run python watch.py
```

## Opcija 6: Screenshot/Recording Mode

Dodaj u kod za automatsko snimanje ekrana:
```python
# U main.py
from kivy.core.window import Window

def take_screenshot(dt):
    Window.screenshot('screenshots/screen_{}.png'.format(int(dt)))

# Dodaj u build()
Clock.schedule_interval(take_screenshot, 5)  # Screenshot svakih 5s
```

## Preporuka

**Za development u Codespaces:**
1. ✅ Koristi **Android Emulator** (Opcija 4) - najrealniji preview
2. ✅ Ili **VNC Server** (Opcija 2) - najbolji desktop preview
3. ⚠️ Izbjegavaj direktno pokretanje (nema display)

**Za lokalni development:**
1. ✅ Koristi **Desktop preview** (Opcija 1) - najbrže
2. ✅ Dodaj **Live Reload** (Opcija 5) - najviše produktivno
3. ✅ Testiraj na **Android Emulator** (Opcija 4) pre deploya

## VS Code Tasks

Dodaj u `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Kivy App",
      "type": "shell",
      "command": "poetry run python main.py",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Build Android Debug",
      "type": "shell",
      "command": "buildozer android debug",
      "problemMatcher": []
    },
    {
      "label": "Deploy to Android",
      "type": "shell",
      "command": "buildozer android debug deploy run",
      "problemMatcher": []
    }
  ]
}
```

Pokreni sa: `Ctrl+Shift+P` → "Tasks: Run Task"
