# VisionStream - High-Performance RTSP Desktop Client

VisionStream is a robust, cross-platform desktop application designed for real-time video streaming using the **RTSP** (Real-Time Streaming Protocol). Built with **Python**, **PySide6 (Qt)**, and **PyAV (FFmpeg)**, the application focuses on ultra-low latency, stability, and high-performance decoding for modern video codecs.

![VisionStream Application](assets/screenshot.png)
*VisionStream running with H.264 codec at 3840x2160 (4K UHD) resolution*

---

## ⚡ Quick Start

Get up and running in 3 steps:

```bash
pip install -r requirements.txt
python src/main.py
```

Then enter an RTSP URL or local video path (e.g., `C:\Videos\sample.mp4`) and click **Play**.

**Run tests:** `pytest tests/ -v`

---

## 🚀 Key Features

✅ **Ultra-low latency** (<500ms glass-to-glass on local networks)  
✅ **Automatic reconnection** with exponential backoff (5 attempts)  
✅ **Real-time FPS monitoring** and performance tracking  
✅ **Multiple input sources**: RTSP streams, local files, webcams  
✅ **Zero-copy frame decoding** for maximum performance  
✅ **Asynchronous connection** - GUI stays responsive always  
✅ **Comprehensive error handling** with clear user feedback  
✅ **Smart buffer management** - Latest Frame Policy for minimal delay

## 🛠 Tech Stack

* **Language**: Python 3.10+
* **UI Framework**: PySide6 (Qt for Python)
* **Video Engine**: PyAV (Pythonic binding for FFmpeg libraries)
* **Processing**: NumPy (for high-speed frame array manipulation)

**Supported Codecs**: H.264, H.265/HEVC  
**Supported Platforms**: Windows 10/11 (Linux/macOS support planned)

### Native Performance Architecture

VisionStream leverages **native C-bindings** for maximum performance:

- **FFmpeg C-bindings via PyAV**: Direct access to FFmpeg's native decoding libraries without Python overhead
- **Zero-copy frame handling**: NumPy arrays reference FFmpeg's memory buffers directly, eliminating unnecessary copies
- **Efficient memory management**: Single-frame buffer with immediate replacement (Latest Frame Policy)
- **Hardware acceleration ready**: Architecture supports future GPU decoding integration

## 📊 Performance Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| **Startup Time** | <1.5s | Cold start to ready state |
| **Memory Usage** | ~150-200 MB | Single 1080p H.264 stream |
| **Latency (LAN)** | <500ms | Glass-to-glass on local network |
| **CPU Usage** | 5-15% | Intel i5/i7, 1080p@30fps |
| **Frame Drop Rate** | <0.1% | Stable network conditions |
| **Reconnection Time** | 2-5s | Automatic recovery from interruption |

*Tested on: Windows 11, Intel i7-10th gen, 16GB RAM, 1Gbps LAN*

## 🚦 Getting Started

### Prerequisites

- Python 3.10 or higher
- Windows 10/11 (for webcam support)
- Git (optional)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yehuditOutmazgin/vision-stream.git
cd vision-stream
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python src/main.py
```

### Running Tests

```bash
pytest tests/ -v
```

## 📦 Building the Executable (EXE)

VisionStream can be packaged as a standalone Windows executable that includes all dependencies (Python, PySide6, PyAV/FFmpeg) - no installation required on target machines.

### Quick Build

```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
pyinstaller main.spec

# Output: dist/VisionStream/VisionStream.exe
```

### Distribution

**The entire `dist/VisionStream/` folder is portable:**
- Copy the complete folder to any Windows machine
- No Python installation required
- Run `VisionStream.exe` directly
- Size: ~200-300 MB (includes Qt, FFmpeg, Python runtime)

**⚠️ IMPORTANT: Send the entire folder, not just the .exe file!**

The executable requires all supporting files (DLLs, libraries) in the same directory.

**To distribute:**
```bash
# Create ZIP package
build-distribution.bat

# Send: dist/VisionStream-v1.0.0.zip
```

**📚 For detailed build instructions, troubleshooting, and advanced options, see [BUILD.md](BUILD.md)**

## 🖥 Usage

### RTSP Streams
1. Launch the application.
2. Enter a valid RTSP URL (e.g., `rtsp://192.168.1.100:554/stream`).
3. Click **Play** to start the stream.
4. Click **Stop** to release network resources and terminate the connection.

### Local Video Files
1. Enter the full path to a video file (e.g., `C:\Videos\sample.mp4`).
2. Click **Play** to start playback.

### Webcam (Windows)
1. Click **List Cameras** to see all available webcams on your system
2. Select a camera from the list - the app will automatically start streaming
3. Alternatively, manually enter `video=Integrated Camera` (replace with your camera name)

**Webcam Tips:**
- Use **List Cameras** to discover the exact names of your webcams
- If a camera fails to open, try using its full name from the list
- Camera names can be found in Windows Device Manager under "Cameras"

### Example RTSP URLs for Testing

Public test streams you can use:

```
rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4
rtsp://rtsp.stream/pattern
```

**Note**: Public test streams may not always be available. For local testing, use a video file path.

**Connection behavior**: The connection process runs asynchronously in a background thread, keeping the GUI responsive even during slow network connections. If connection fails, automatic reconnection will attempt up to 5 times with increasing delays (0s, 2s, 5s, 10s, 30s).

## 🏗 Project Structure

```text
VisionStream/
├── src/
│   ├── core/           # Stream engine, buffer, and reconnection logic
│   ├── gui/            # UI components and video widgets
│   ├── utils/          # Logging, configuration, and validation
│   └── main.py         # Application entry point
├── tests/              # Unit tests
│   ├── test_url_validator.py
│   └── test_reconnection_manager.py
├── assets/             # Images and resources
├── .editorconfig       # Code style configuration
├── .gitignore          # Git ignore rules
├── build-distribution.bat  # Automated build script
├── BUILD.md            # Detailed build instructions
├── CHANGELOG.md        # Version history
├── CONTRIBUTING.md     # Contribution guidelines
├── LICENSE             # MIT License
├── main.spec           # PyInstaller build configuration
├── README.md           # Project documentation
├── requirements.txt    # Project dependencies
├── setup.py            # Package installation script
└── specification.md    # Detailed requirements specification
```

## 🧪 Testing

The project includes 25 unit tests for critical components:

- **URLValidator**: RTSP URL validation, local files, webcam identifiers, and file existence checks (15 tests)
- **ReconnectionManager**: State machine logic and reconnection behavior (10 tests)

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_url_validator.py -v
```

## 🛣 Roadmap

### Phase 1: Core Features (Current - v1.0)
- ✅ Single-stream RTSP player with H.264/H.265 support
- ✅ Ultra-low latency streaming (<500ms)
- ✅ Automatic reconnection with exponential backoff
- ✅ Real-time FPS monitoring
- ✅ Multiple input sources (RTSP, files, webcams)

### Phase 2: Advanced UI (v1.5 - Planned)
- 🔄 **Migration to QML**: Modern declarative UI with hardware-accelerated rendering
- 🔄 **Multi-stream Grid Layout**: Display 4, 9, or 16 streams simultaneously
- 🔄 **Drag-and-drop stream management**: Rearrange streams in grid
- 🔄 **Per-stream controls**: Individual play/pause/stop for each stream
- 🔄 **Grid presets**: Save and load multi-stream configurations

### Phase 3: Professional Features (v2.0 - Future)
- 📋 Advanced playback controls (pause, seek, speed control)
- 📋 Recording and snapshot capabilities
- 📋 Stream analytics and statistics dashboard
- 📋 PTZ (Pan-Tilt-Zoom) camera control
- 📋 Motion detection and alerts
- 📋 Cloud storage integration

**Architecture Note**: The current codebase is designed with modularity in mind. Core components (StreamEngine, VideoWidget, ReconnectionManager) are independent and reusable, enabling seamless expansion to multi-stream grid layouts with minimal refactoring.

## 🔧 Troubleshooting

### Application won't start
- **Check Python version**: Run `python --version` (requires 3.10+)
- **Reinstall dependencies**: `pip install -r requirements.txt --force-reinstall`
- **Check logs**: Look in `logs/` directory for error details

### Video won't play
- **Invalid URL**: Ensure RTSP URL format is correct (`rtsp://host:port/path`)
- **Network issues**: Check firewall settings and network connectivity
- **Codec not supported**: VisionStream supports H.264 and H.265 only
- **Authentication**: Include credentials in URL: `rtsp://username:password@host:port/path`

### Stream keeps disconnecting
- **Network instability**: Check your network connection quality
- **Firewall blocking**: Allow Python/VisionStream through Windows Firewall
- **Server timeout**: Some RTSP servers have connection time limits
- **Automatic reconnection**: The app will retry up to 5 times automatically

### Poor performance / High latency
- **Network bandwidth**: Ensure sufficient bandwidth for the stream
- **CPU usage**: Close other applications to free up resources
- **Local network**: Best performance on LAN (<500ms latency)
- **Internet streams**: Latency varies based on distance and network conditions

### FFmpeg/PyAV errors
- **Reinstall PyAV**: `pip uninstall av && pip install av`
- **Check FFmpeg**: PyAV includes FFmpeg libraries automatically
- **See logs**: Check `logs/` for detailed FFmpeg error messages

**For detailed technical information, see [specification.md](specification.md)**

---

## ⚠️ Known Limitations

* **RTSP External Streams**: Latency and connection stability depend on network conditions and firewall configurations. Local network streams typically achieve <500ms latency, but internet streams may vary.
* **Codec Support**: Limited to H.264 and H.265/HEVC codecs. Other codecs (VP9, AV1) are not currently supported.
* **Webcam Compatibility**: Windows-only webcam support via DirectShow. Linux/macOS webcam support is not yet implemented.
* **Single Stream**: Currently supports one stream at a time. Multi-stream grid view is planned for future releases.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📧 Support

For issues and questions, please open an issue on GitHub.
