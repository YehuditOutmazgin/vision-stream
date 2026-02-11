# VisionStream - High-Performance RTSP Desktop Client

VisionStream is a robust, cross-platform desktop application designed for real-time video streaming using the **RTSP** (Real-Time Streaming Protocol). Built with **Python**, **PySide6 (Qt)**, and **PyAV (FFmpeg)**, the application focuses on ultra-low latency, stability, and high-performance decoding for modern video codecs.

## 📚 Documentation

- **[Full Specification](specification.md)** - Complete requirements and architecture
- **[Quick Build Guide](QUICK_BUILD.md)** - Build in 3 steps (recommended for first-time users)
- **[Detailed Build Instructions](BUILD_INSTRUCTIONS.md)** - Step-by-step guide for all platforms
- **[Deployment Guide](DEPLOYMENT.md)** - Distribution and release guidelines

## 🚀 Key Features

* **Real-Time Decoding**: Utilizes PyAV for efficient, zero-copy frame decoding directly from network streams
* **Ultra-Low Latency**: Optimized buffer management with Strict Latest Frame Policy (< 500ms glass-to-glass)
* **Automatic Reconnection**: Smart exponential backoff with up to 5 reconnection attempts
* **Modern GUI**: Clean, responsive light-mode interface built with PySide6 (Tailwind-inspired design)
* **Performance Monitoring**: Real-time FPS (Frames Per Second) tracking and display
* **Comprehensive Error Handling**: User-friendly error messages with categorization (Validation, Connection, Codec, Network)
* **Professional Logging**: Thread-safe logging system with file output for diagnostics
* **Cross-Platform**: Runs on Windows, macOS, and Linux

## 🛠 Tech Stack

* **Language**: Python 3.11+
* **UI Framework**: PySide6 (Qt 6 for Python)
* **Video Engine**: PyAV (Pythonic binding for FFmpeg libraries)
* **Processing**: NumPy (for high-speed frame array manipulation)
* **Deployment**: PyInstaller (standalone executable creation)

## 🎯 Supported Formats

* **Protocols**: RTSP (over TCP), Local files, Webcams
* **Video Codecs**: H.264, H.265 (HEVC)
* **File Formats**: MP4, AVI, MKV, MOV, FLV
* **Cameras**: DirectShow (Windows), V4L2 (Linux), AVFoundation (macOS)

## 📦 Building the Executable (EXE)

### Quick Start (Recommended)

See **[QUICK_BUILD.md](QUICK_BUILD.md)** for the fastest way to build:

```bash
# Windows (PowerShell)
.\build.bat

# macOS / Linux
chmod +x build.sh
./build.sh
```

### Detailed Instructions

For step-by-step instructions for your platform, see **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)**

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **FFmpeg** - Required for video decoding
  - Windows: `choco install ffmpeg` or [download](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`

### Output

- **Windows**: `dist/VisionStream/VisionStream.exe` (~250MB)
- **macOS**: `dist/VisionStream/VisionStream.app`
- **Linux**: `dist/VisionStream/VisionStream`

The executable is **standalone** and can run on any machine without Python installed.

## 🖥 Usage

1. **Launch** the application
2. **Enter** a valid RTSP URL (e.g., `rtsp://camera.local:554/stream`)
3. **Click Play** to start streaming
4. **Click Stop** to disconnect

### Supported Input Sources

- RTSP streams: `rtsp://host:port/path`
- Local files: `/path/to/video.mp4`
- Webcams: `video=Integrated Camera` (Windows)

## 🏗 Project Structure

```
VisionStream/
├── src/
│   ├── main.py                  # Application entry point
│   ├── core/                    # Stream engine, buffer, reconnection
│   │   ├── stream_engine.py     # PyAV video decoding
│   │   ├── frame_buffer.py      # Latest Frame Policy buffer
│   │   ├── reconnection_manager.py  # Auto-reconnection logic
│   │   └── __init__.py
│   ├── gui/                     # User interface components (current)
│   │   ├── components.py        # Shared UI components (Header, ControlPanel, VideoDisplay)
│   │   ├── stream_controller.py # Stream operations controller
│   │   ├── ui_manager.py        # UI state management
│   │   ├── error_display.py     # Error message presentation
│   │   ├── styles.py            # Tailwind-inspired styling
│   │   └── __init__.py
│   ├── utils/                   # Utilities and helpers
│   │   ├── config.py            # Configuration constants
│   │   ├── logger.py            # Thread-safe logging system
│   │   ├── error_handler.py     # Error message translation
│   │   ├── error_types.py       # Error categorization
│   │   ├── url_validator.py     # RTSP URL validation
│   │   ├── metrics.py           # Performance metrics
│   │   └── __init__.py
│   ├── requirements.txt         # Python dependencies
│   └── __init__.py
├── legacy/                      # Legacy UI components (kept for reference)
│   ├── main_window.py           # Original main window implementation (unused)
│   └── video_widget.py          # Original video widget with FPS/overlay (unused)
├── build.bat                    # Windows build script
├── build.sh                     # macOS/Linux build script
├── pyinstaller_spec.spec        # PyInstaller spec used by build scripts
├── specification.md             # Full requirements document
├── QUICK_BUILD.md               # Quick build guide (3 steps)
├── BUILD_INSTRUCTIONS.md        # Detailed build instructions
├── DEPLOYMENT.md                # Distribution guidelines
└── README.md                    # This file
```

## 🔧 Architecture Highlights

### Separation of Concerns
- **StreamController**: Manages stream lifecycle and reconnection
- **UIManager**: Handles UI state and updates
- **Components**: Reusable UI elements (Header, ControlPanel, VideoDisplay)
- **Core Modules**: Stream engine, frame buffer, reconnection logic

### Thread Safety
- Daemon threads for stream processing
- Thread-safe singleton logger
- Qt signals for thread-safe UI updates
- Proper resource cleanup on shutdown

### Error Handling
- Categorized errors (Validation, Connection, Codec, Network)
- User-friendly error messages
- Comprehensive logging for diagnostics
- Graceful degradation on failures

### Performance
- Zero-copy frame handling with NumPy
- Strict Latest Frame Policy (no queuing)
- Watchdog timeout detection (2.5 seconds)
- Optimized FFmpeg settings (tcp, nobuffer, low_delay)

## 📊 Specification Compliance

This project fully implements the specification with:

- ✅ **Req 1**: RTSP URL input with validation
- ✅ **Req 2**: Playback control (Play/Stop buttons)
- ✅ **Req 3**: Video display with aspect ratio preservation
- ✅ **Req 4**: Error handling with user-friendly messages
- ✅ **Req 5**: Application stability and resource management
- ✅ **Req 6**: High-performance video decoding (H.264/H.265)
- ✅ **Req 7**: Cross-platform compatibility
- ✅ **Req 8**: Automatic reconnection with exponential backoff
- ✅ **Req 9**: Operational visibility and diagnostics
- ✅ **Req 10**: Multi-stream grid architecture (future-ready)
- ✅ **Req 11**: PyInstaller deployment

See [specification.md](specification.md) for complete details.

## 🚀 Getting Started

### For Users (Reviewers / Stakeholders)
1. Download the latest executable from releases
2. Run `VisionStream.exe` (Windows) or `VisionStream.app` (macOS)
3. Enter an RTSP URL and click Play

### For Developers
1. Clone the repository
2. Install dependencies: `pip install -r src/requirements.txt`
3. Run the application: `python src/main.py`
4. Build executable: See [QUICK_BUILD.md](QUICK_BUILD.md)

## 🐛 Troubleshooting

### Application won't start
- Check logs in `logs/` directory
- Ensure FFmpeg is installed: `ffmpeg -version`
- Verify Python 3.11+: `python --version`

### Video won't play
- Verify RTSP URL format: `rtsp://host:port/path`
- Check network connectivity
- Review error message for specific issue

### Build fails
- See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) troubleshooting section
- Ensure all prerequisites are installed
- Try building from a clean state (delete `build/` and `dist/`)

## 📈 Performance Metrics

- **Latency**: < 500ms glass-to-glass (local network)
- **FPS Display**: Real-time monitoring
- **Memory**: Efficient frame buffer management
- **CPU**: Optimized decoding with FFmpeg

## 🔐 Security

- Input validation for all URLs
- Safe error handling without exposing system details
- Thread-safe operations throughout
- Proper resource cleanup

## 📝 Logging

All events are logged to `logs/visionstream_YYYY-MM-DD.log`:
- Connection/disconnection events
- Codec information
- Reconnection attempts
- Error details
- Performance metrics

## 🛣 Roadmap

- [ ] Multi-stream grid layout (2x2, 3x3, 4x4)
- [ ] Stream recording capability
- [ ] Advanced filtering and effects
- [ ] Configuration UI
- [ ] Stream scheduling

## 📞 Support

For issues or questions:
1. Check [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)
2. Review logs in `logs/` directory
3. See [specification.md](specification.md) for detailed requirements

## 📄 License

This project is provided as-is for educational and professional use.

---

**Ready to build?** → Start with [QUICK_BUILD.md](QUICK_BUILD.md)

**Need details?** → See [specification.md](specification.md)

