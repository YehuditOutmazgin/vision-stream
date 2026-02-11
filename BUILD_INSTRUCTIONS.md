# VisionStream Build Instructions

## Overview
This document explains how to build VisionStream into a standalone executable (.exe on Windows, app on macOS, executable on Linux).

## Prerequisites

### Required Software
- **Python 3.11+** - Download from [python.org](https://www.python.org/downloads/)
- **pip** - Usually comes with Python
- **FFmpeg** - Required for video decoding
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Linux**: `sudo apt-get install ffmpeg` (Ubuntu/Debian)

### Verify Installation
```bash
python --version          # Should be 3.11 or higher
pip --version            # Should be installed
ffmpeg -version          # Should show FFmpeg version
```

## Building on Windows

### Option 1: Automatic Build (Recommended)
```bash
# Double-click build.bat
# OR run from command prompt:
build.bat  # or .\build.bat in PowerShell
```

### Option 2: Manual Build
```bash
# Install dependencies
pip install -r src/requirements.txt
pip install pyinstaller

# Build the executable
pyinstaller pyinstaller_spec.spec --distpath dist --workpath build
```

### Output
- **Location**: `dist/VisionStream/VisionStream.exe`
- **Size**: ~200-300 MB (includes Python runtime and all dependencies)
- **Standalone**: Can be run on any Windows machine without Python installed

## Building on macOS

### Automatic Build
```bash
chmod +x build.sh
./build.sh
```

### Manual Build
```bash
# Install dependencies
pip3 install -r src/requirements.txt
pip3 install pyinstaller

# Build the application
pyinstaller pyinstaller_spec.spec --distpath dist --workpath build
```

### Output
- **Location**: `dist/VisionStream/VisionStream.app`
- **Run**: Double-click the .app or `open dist/VisionStream/VisionStream.app`

## Building on Linux

### Automatic Build
```bash
chmod +x build.sh
./build.sh
```

### Manual Build
```bash
# Install dependencies
pip3 install -r src/requirements.txt
pip3 install pyinstaller

# Build the executable
pyinstaller pyinstaller_spec.spec --distpath dist --workpath build
```

### Output
- **Location**: `dist/VisionStream/VisionStream`
- **Run**: `./dist/VisionStream/VisionStream`

## Troubleshooting

### Issue: "FFmpeg not found"
**Solution**: Install FFmpeg and ensure it's in your PATH
```bash
# Windows (using Chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

### Issue: "ModuleNotFoundError: No module named 'av'"
**Solution**: Install PyAV
```bash
pip install av
```

### Issue: "ModuleNotFoundError: No module named 'PySide6'"
**Solution**: Install PySide6
```bash
pip install PySide6
```

### Issue: Build fails with "No module named 'src'"
**Solution**: Run build from the project root directory (where build.bat/build.sh is located)

### Issue: Executable is very large (>500MB)
**This is normal** - includes Python runtime, Qt libraries, and FFmpeg. You can reduce size by:
1. Using UPX compression (already enabled in spec)
2. Removing unused modules from hiddenimports
3. Using a lighter Python distribution

## Distribution

### For End Users
1. Run the build script to create the executable
2. Share the entire `dist/VisionStream/` folder
3. Users can run the executable directly without installing Python

### Creating an Installer (Optional)
For professional distribution, consider using:
- **NSIS** (Windows) - Free, open-source installer
- **Inno Setup** (Windows) - Easy to use
- **DMG** (macOS) - Disk image format
- **AppImage** (Linux) - Portable application format

## Build Customization

### Modify PyInstaller Spec
Edit `pyinstaller_spec.spec` to customize:
- **Icon**: Add `icon='path/to/icon.ico'` to EXE()
- **Console**: Change `console=False` to `console=True` for debug output
- **One-file**: Add `onefile=True` to create single .exe instead of folder

### Example: Single-file executable
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VisionStream',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    onefile=True,  # Add this line
)
```

## Verification

After building, verify the executable works:

1. **Windows**: Double-click `VisionStream.exe`
2. **macOS**: Double-click `VisionStream.app` or run `open dist/VisionStream/VisionStream.app`
3. **Linux**: Run `./dist/VisionStream/VisionStream`

The application should:
- Launch without errors
- Display the VisionStream window
- Allow entering RTSP URLs
- Play video streams correctly

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the `logs/` directory
3. Ensure all prerequisites are installed
4. Try building from a clean state (delete `build/` and `dist/` folders)

## Next Steps

Once built, you can:
1. Test the executable on different machines
2. Create an installer for distribution
3. Add code signing for security
4. Distribute to end users
