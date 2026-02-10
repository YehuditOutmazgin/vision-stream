# Quick Build Guide - VisionStream

## 🚀 Build in 3 Steps

### Step 1: Install FFmpeg (One-time)
```bash
# Windows (using Chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

### Step 2: Run Build Script
```bash
# Windows
build.bat

# macOS / Linux
chmod +x build.sh
./build.sh
```

### Step 3: Find Your Executable
- **Windows**: `dist/VisionStream/VisionStream.exe`
- **macOS**: `dist/VisionStream/VisionStream.app`
- **Linux**: `dist/VisionStream/VisionStream`

## ✅ That's It!

Your standalone executable is ready to distribute. No Python installation needed on target machines.

## 📋 What Gets Included

- ✅ Python runtime
- ✅ PySide6 (Qt libraries)
- ✅ PyAV (FFmpeg bindings)
- ✅ NumPy
- ✅ All application code

## 🐛 Troubleshooting

**Build fails?** Check:
1. Python 3.11+ installed: `python --version`
2. FFmpeg installed: `ffmpeg -version`
3. Dependencies installed: `pip install -r src/requirements.txt`
4. Run from project root directory

**Still stuck?** See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

## 📦 Distribution

Share the entire `dist/VisionStream/` folder with users. They can run the executable directly!

---

**Need more details?** → [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)
