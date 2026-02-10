# VisionStream Deployment Guide

## 📋 Overview

This guide explains how to build and deploy VisionStream as a standalone executable for Windows, macOS, and Linux.

## 🎯 Quick Start

### For Windows Users
```bash
# 1. Install FFmpeg (one-time)
choco install ffmpeg

# 2. Run build script
build.bat

# 3. Find executable
# dist/VisionStream/VisionStream.exe
```

### For macOS/Linux Users
```bash
# 1. Install FFmpeg (one-time)
brew install ffmpeg          # macOS
sudo apt-get install ffmpeg  # Linux

# 2. Run build script
chmod +x build.sh
./build.sh

# 3. Find executable
# dist/VisionStream/VisionStream.app (macOS)
# dist/VisionStream/VisionStream (Linux)
```

## 📦 What's Included in the Build

The standalone executable includes:
- ✅ Python 3.11+ runtime
- ✅ PySide6 (Qt 6 for Python)
- ✅ PyAV (FFmpeg Python bindings)
- ✅ NumPy
- ✅ All VisionStream application code
- ✅ Configuration and logging system

**Size**: ~250-300 MB (includes all dependencies)

## 🚀 Distribution

### For End Users

1. **Build the executable** using the build script
2. **Create a folder** with the executable and any supporting files
3. **Share the folder** with users
4. **Users can run** the executable directly without installing Python

### Example Distribution Structure
```
VisionStream/
├── VisionStream.exe          (Windows)
├── VisionStream.app/         (macOS)
├── VisionStream              (Linux)
├── README.txt
└── USAGE.txt
```

## 🔧 Build Customization

### Single-File Executable

Edit `pyinstaller_spec.spec` and add `onefile=True`:

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
    onefile=True,  # Add this
    console=False,
)
```

Then rebuild:
```bash
pyinstaller pyinstaller_spec.spec
```

### Add Application Icon

1. Prepare an icon file (`.ico` for Windows, `.icns` for macOS)
2. Edit `pyinstaller_spec.spec`:

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
    icon='path/to/icon.ico',  # Add this
    console=False,
)
```

### Enable Console Output (Debug)

Change `console=False` to `console=True` in the spec file to see debug output.

## 🐛 Troubleshooting

### Build Fails: "FFmpeg not found"
```bash
# Install FFmpeg
choco install ffmpeg          # Windows
brew install ffmpeg           # macOS
sudo apt-get install ffmpeg   # Linux
```

### Build Fails: "Module not found"
```bash
# Reinstall dependencies
pip install -r src/requirements.txt
```

### Executable Won't Start
1. Check logs in `logs/` directory
2. Run from command line to see error messages
3. Ensure FFmpeg is installed on target machine

### Executable is Very Large
This is normal - includes Python runtime and all libraries. To reduce:
1. Use UPX compression (already enabled)
2. Remove unused modules from `hiddenimports` in spec
3. Use `onefile=False` (creates folder instead of single file)

## 📊 Build Statistics

| Platform | Executable | Size | Runtime |
|----------|-----------|------|---------|
| Windows | .exe | ~250MB | 2-3 min |
| macOS | .app | ~280MB | 2-3 min |
| Linux | binary | ~240MB | 2-3 min |

## ✅ Verification Checklist

After building, verify:
- [ ] Executable launches without errors
- [ ] Application window displays correctly
- [ ] Can enter RTSP URLs
- [ ] Can play video streams
- [ ] Error messages display properly
- [ ] Logs are created in `logs/` directory
- [ ] Application closes cleanly

## 🔐 Security Considerations

### Code Signing (Optional)

For professional distribution, consider code signing:

**Windows**:
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.server VisionStream.exe
```

**macOS**:
```bash
codesign -s "Developer ID Application" VisionStream.app
```

### Antivirus Warnings

PyInstaller executables may trigger antivirus warnings. This is normal for packaged Python applications. Users can:
1. Add the executable to antivirus whitelist
2. Build from source if they prefer

## 📝 Release Checklist

Before releasing:
- [ ] Test on clean Windows/macOS/Linux machines
- [ ] Verify all features work
- [ ] Check error handling
- [ ] Review logs for any issues
- [ ] Update version number in `src/utils/config.py`
- [ ] Create release notes
- [ ] Test with different RTSP sources

## 🚀 Continuous Deployment

For automated builds, consider:
- **GitHub Actions** - Automated builds on push
- **Azure Pipelines** - Cross-platform CI/CD
- **Jenkins** - Self-hosted CI/CD

Example GitHub Actions workflow:
```yaml
name: Build VisionStream
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r src/requirements.txt pyinstaller
      - run: pyinstaller pyinstaller_spec.spec
      - uses: actions/upload-artifact@v2
        with:
          name: VisionStream-Windows
          path: dist/VisionStream/
```

## 📞 Support

For build issues:
1. Check [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)
2. Review [QUICK_BUILD.md](QUICK_BUILD.md)
3. Check application logs in `logs/` directory
4. Verify all prerequisites are installed

---

**Ready to deploy?** Start with [QUICK_BUILD.md](QUICK_BUILD.md)
