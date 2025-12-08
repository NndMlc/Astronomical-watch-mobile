# Build Instructions for Astronomical Watch Mobile

## Prerequisites

### For Android Build

1. **Install Buildozer**:
```bash
pip install buildozer
```

2. **Install Dependencies** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y python3-pip build-essential git python3 python3-dev \
    ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
    openjdk-17-jdk zip unzip autoconf libtool pkg-config
```

3. **Android SDK & NDK**:
   - Buildozer će automatski preuzeti Android SDK i NDK pri prvom build-u
   - Ili instaliraj Android Studio i podesi `ANDROID_HOME` environment variable

### For iOS Build (samo macOS)

1. **Install Xcode** iz App Store

2. **Install Kivy-iOS toolchain**:
```bash
pip install kivy-ios
```

3. **Install dependencies**:
```bash
brew install autoconf automake libtool pkg-config
```

## Build Process

### Android APK

1. **Debug build**:
```bash
buildozer android debug
```

2. **Release build** (za produkciju):
```bash
buildozer android release
```

APK fajl će biti u `bin/` folderu.

3. **Deploy na povezan uređaj**:
```bash
buildozer android debug deploy run
```

### iOS (samo na macOS)

1. **Kreiranje Xcode projekta**:
```bash
toolchain build kivy
toolchain create AstronomicalWatch ~/AstronomicalWatch
```

2. **Dodavanje Python dependencies**:
```bash
cd ~/AstronomicalWatch
toolchain pip install requests
```

3. **Otvaranje u Xcode**:
```bash
open AstronomicalWatch.xcodeproj
```

4. **Build u Xcode** i deploy na simulator ili device

## VS Code Extensions

Preporučene ekstenzije već instalirane:
- **Kivy** (`battlebas.kivy-vscode`) - Kivy language support
- **Material Kivy** (`haddiebakrie.material-kv`) - Kivy & KivyMD support sa .spec tipom
- **Android iOS Emulator** (`diemasmichiels.emulate`) - Pokretanje emulatora

Dodatne korisne:
- **Android** (`adelphes.android-dev-ext`) - Android debugging support

## Troubleshooting

### Buildozer greške

1. **"Command failed: ./distribute.sh"**:
   - Pokreni: `buildozer android clean`
   - Proveri da li su sve dependencies instalirane

2. **NDK greška**:
   - U `buildozer.spec` proveri verziju: `android.ndk = 25b`
   - Obriši `.buildozer` folder i pokušaj ponovo

3. **Java greška**:
   - Proveri Java verziju: `java -version`
   - Treba Java 17 ili novija

### iOS greške

1. **"xcrun: error"**:
   - Proveri da li je Xcode instaliran i license prihvaćen
   - Pokreni: `sudo xcode-select --reset`

2. **Provisioning profile**:
   - Potreban Apple Developer nalog za deploy na pravi uređaj
   - Za simulator nije potreban

## Build Configuration

Sve build opcije su u `buildozer.spec`:

- **Package name**: `org.astronomicalwatch.astronomical_watch`
- **Version**: `0.1.0`
- **Requirements**: Python 3.10, Kivy 2.3.1, requests, etc.
- **Permissions**: INTERNET, ACCESS_NETWORK_STATE
- **Target API**: 33 (Android 13)
- **Min API**: 21 (Android 5.0)

## Testing

1. **Desktop testing** (pre build-a):
```bash
python main.py
```

2. **Android emulator**:
   - Koristi VS Code ekstenziju "Android iOS Emulator"
   - Ili Android Studio AVD Manager

3. **iOS simulator**:
   - Pokreni iz Xcode-a
   - Ili: `xcrun simctl list` za listu simulatora

## Publishing

### Google Play Store

1. Kreiraj signed release APK:
```bash
buildozer android release
```

2. Potpiši APK sa keystore-om
3. Upload na Google Play Console

### Apple App Store

1. Build release verziju u Xcode-u
2. Archive app
3. Upload kroz Xcode ili Transporter app

## Resources

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Kivy-iOS Documentation](https://kivy-ios.readthedocs.io/)
- [Python-for-Android](https://python-for-android.readthedocs.io/)
