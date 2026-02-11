# VisionStream - High-Performance RTSP Desktop Client

VisionStream is a robust, cross-platform desktop application designed for real-time video streaming using the **RTSP** (Real-Time Streaming Protocol). Built with **Python**, **PySide6 (Qt)**, and **PyAV (FFmpeg)**, the application focuses on ultra-low latency, stability, and high-performance decoding for modern video codecs.

## 🚀 Key Features

* **Multiple Input Sources**: Supports RTSP streams, local video files (MP4, AVI, etc.), and webcams (DirectShow on Windows).
* **Real-Time Decoding**: Utilizes PyAV for efficient, zero-copy frame decoding directly from network streams.
* **Low Latency**: Optimized buffer management to ensure minimal delay between the source and display.
* **Modern GUI**: A clean, responsive user interface built with PySide6.
* **Asynchronous Connection**: Non-blocking connection handling keeps the GUI responsive during stream initialization.
* **Performance Monitoring**: Real-time FPS (Frames Per Second) tracking and display.
* **Error Handling**: Comprehensive validation and user feedback for connection issues or invalid URLs.
* **Smart Reconnection**: Automated handling of network interruptions to ensure stream continuity.

## 🛠 Tech Stack

* **Language**: Python 3.10+
* **UI Framework**: PySide6 (Qt for Python)
* **Video Engine**: PyAV (Pythonic binding for FFmpeg libraries)
* **Processing**: NumPy (for high-speed frame array manipulation)

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
1. Enter `video=Integrated Camera` (or your webcam's name from Device Manager).
2. Alternatively, enter just the device index (e.g., `0` for the first webcam).
3. Click **Play** to start the webcam feed.

**Note**: The connection process runs asynchronously in a background thread, keeping the GUI responsive even during slow network connections.

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

The project includes unit tests for critical components:

- **URLValidator**: Tests for RTSP URL validation, local files, and webcam identifiers (12 tests)
- **ReconnectionManager**: Tests for state machine logic and reconnection behavior (10 tests)

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_url_validator.py -v
```

## 🛣 Roadmap (Upcoming Features)

* Multi-stream Grid layout for concurrent monitoring.
* Advanced playback controls (pause, seek, speed control).
* Recording and snapshot capabilities.

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

