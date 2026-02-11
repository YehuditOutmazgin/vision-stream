# Building VisionStream Executable

This guide explains how to build a standalone Windows executable for VisionStream.

## Overview

The build process uses **PyInstaller** to create a portable Windows application that includes:
- Python runtime
- PySide6 (Qt framework)
- PyAV (FFmpeg video libraries)
- All project dependencies

**Result:** A folder containing VisionStream.exe and all required DLLs (~200-300 MB)

## Prerequisites

1. **Windows OS** (Windows 10/11 recommended)
2. **Python 3.10 or higher**
3. **Git** (optional, for cloning)

## Step-by-Step Build Instructions

### 1. Install Dependencies

```bash
# Navigate to project root
cd vision-stream

# Install all required packages
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import PySide6; import av; import numpy; print('All dependencies installed!')"
```

### 2. Run Tests (Recommended)

Before building, ensure all tests pass:

```bash
pytest tests/ -v
```

Expected output: `22 passed`

### 3. Build the Executable

```bash
pyinstaller main.spec
```

**What happens during build:**
1. PyInstaller analyzes `src/main.py` and all imports
2. Collects PySide6 DLLs (Qt framework, ~100 MB)
3. Collects PyAV/FFmpeg libraries (video codecs, ~50 MB)
4. Bundles Python runtime and dependencies
5. Creates executable in `dist/VisionStream/`

**Build time:** 2-5 minutes (depending on CPU)

### 4. Verify Build Output

```
dist/
└── VisionStream/
    ├── VisionStream.exe          # Main executable (GUI app)
    ├── PySide6/                  # Qt DLLs and plugins
    │   ├── Qt6Core.dll
    │   ├── Qt6Gui.dll
    │   ├── Qt6Widgets.dll
    │   └── plugins/
    ├── av.libs/                  # FFmpeg codec libraries
    │   ├── avcodec-*.dll
    │   ├── avformat-*.dll
    │   └── avutil-*.dll
    ├── _internal/                # Python runtime + packages
    │   ├── python311.dll
    │   ├── numpy/
    │   └── [other packages]
    └── [additional DLLs]
```

### 5. Test the Executable

```bash
# Navigate to output directory
cd dist\VisionStream

# Run the executable
VisionStream.exe
```

**Test checklist:**
- [ ] Application window opens
- [ ] No console window appears
- [ ] Can enter RTSP URL
- [ ] Play/Stop buttons work
- [ ] No error messages on startup

## Distribution

### Creating Distribution Package

**Automated (Recommended):**
```bash
# Run the build script (builds, tests, and creates ZIP)
build-distribution.bat
```

This creates: `dist/VisionStream-v1.0.0.zip`

**Manual:**
```bash
# Build
pyinstaller main.spec


# Create ZIP
cd dist
powershell Compress-Archive -Path VisionStream -DestinationPath VisionStream-v1.0.0.zip
```

### What to Send to Users

**Send:** `VisionStream-v1.0.0.zip` (~200-300 MB)

**DO NOT send only the .exe file!**

The executable requires all supporting files:
- PySide6/ (Qt framework)
- av.libs/ (FFmpeg codecs)
- _internal/ (Python runtime)
- All DLL files

### User Instructions

1. Extract the entire ZIP file
2. Open the VisionStream folder
3. Run VisionStream.exe
4. Keep all files together - don't move just the .exe

### Deployment to Other Machines

1. **Copy the entire `VisionStream/` folder** to target machine
2. **No installation required** - just run `VisionStream.exe`
3. **First run:** Windows SmartScreen may warn (not signed)
   - Click "More info" → "Run anyway"
   - To avoid: Sign the executable with a code signing certificate

**Requirements on target machine:**
- Windows 10/11 (64-bit)
- No Python installation needed
- No additional dependencies needed

## Troubleshooting

### Build Issues

**Error: "PyInstaller not found"**
```bash
pip install pyinstaller
```

**Error: "Module not found during build"**
```bash
# Clean previous builds
rmdir /s /q build dist
# Rebuild
pyinstaller main.spec
```

**Error: "collect_all not found"**
- Update PyInstaller: `pip install --upgrade pyinstaller`

### Runtime Issues

**Error: "DLL not found" when running .exe**
- **Cause:** Copied only VisionStream.exe without supporting files
- **Solution:** Copy the **entire** `dist/VisionStream/` folder

**Console window appears**
- Check `main.spec`: Ensure `console=False`
- Rebuild: `pyinstaller main.spec`

**Application crashes on startup**
- Run from command line to see error messages:
  ```bash
  cd dist\VisionStream
  VisionStream.exe
  ```
- Check `logs/` folder for error logs

**"VCRUNTIME140.dll missing" error**
- Install Microsoft Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

## Advanced Configuration

### Reducing Executable Size

Edit `main.spec`:

```python
# Exclude unused modules
excludes=['tkinter', 'matplotlib', 'scipy']

# Disable UPX compression (faster build, larger size)
upx=False
```

### Adding Application Icon

1. Create/obtain `icon.ico` file
2. Place in project root
3. Edit `main.spec`:
```python
exe = EXE(
    ...
    icon='icon.ico',
)
```

### Debug Build

For troubleshooting, create a debug build:

```python
# In main.spec
exe = EXE(
    ...
    console=True,  # Show console for debug output
    debug=True,    # Enable debug mode
)
```

## Build Automation

### GitHub Actions (CI/CD)

Create `.github/workflows/build.yml`:

```yaml
name: Build EXE
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
      - run: pyinstaller main.spec
      - uses: actions/upload-artifact@v3
        with:
          name: VisionStream-Windows
          path: dist/VisionStream/
```

## File Size Breakdown

Typical build size: **~250 MB**

- PySide6 (Qt): ~100 MB
- PyAV/FFmpeg: ~50 MB
- Python runtime: ~30 MB
- NumPy: ~20 MB
- Application code: ~5 MB
- Other dependencies: ~45 MB

## Performance Notes

- **Startup time:** 2-3 seconds (cold start)
- **Memory usage:** ~150 MB (idle), ~300 MB (streaming)
- **No performance difference** vs running from Python

## Support

For build issues:
1. Check this guide's Troubleshooting section
2. Review PyInstaller logs in `build/VisionStream/`
3. Open an issue on GitHub with build logs
