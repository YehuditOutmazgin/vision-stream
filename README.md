# VisionStream - High-Performance RTSP Desktop Client

VisionStream is a robust, cross-platform desktop application designed for real-time video streaming using the **RTSP** (Real-Time Streaming Protocol). Built with **Python**, **PySide6 (Qt)**, and **PyAV (FFmpeg)**, the application focuses on ultra-low latency, stability, and high-performance decoding for modern video codecs.

## 🚀 Key Features

* **Real-Time Decoding**: Utilizes PyAV for efficient, zero-copy frame decoding directly from network streams.
* **Low Latency**: Optimized buffer management to ensure minimal delay between the source and display.
* **Modern GUI**: A clean, responsive user interface built with PySide6.
* **Performance Monitoring**: Real-time FPS (Frames Per Second) tracking and display.
* **Error Handling**: Comprehensive validation and user feedback for connection issues or invalid URLs.
* **Smart Reconnection**: Automated handling of network interruptions to ensure stream continuity.

## 🛠 Tech Stack

* **Language**: Python 3.10+
* **UI Framework**: PySide6 (Qt for Python)
* **Video Engine**: PyAV (Pythonic binding for FFmpeg libraries)
* **Processing**: NumPy (for high-speed frame array manipulation)

## 📦 Building the Executable (EXE)

To create a standalone Windows executable that includes all video dependencies (FFmpeg/PyAV libraries), follow these steps:

### 1. Prerequisites

Ensure you have the required packages installed:

```bash
pip install PySide6 av numpy pyinstaller

```

### 2. Build Process

The project includes a `main.spec` file configured with the necessary `collect_all` hooks for **PySide6** and **av**. This ensures that all required DLLs and metadata are bundled correctly into the final distribution.

Run the following command in the project root:

```bash
pyinstaller main.spec

```

### 3. Output

Once the process is complete:

* The build artifacts will be in the `build/` folder.
* The final executable will be generated in the `dist/VisionStream/` directory.

## 🖥 Usage

1. Launch the application.
2. Enter a valid RTSP URL (e.g., `rtsp://host:port/path`).
3. Click **Play** to start the stream.
4. Click **Stop** to release network resources and terminate the connection.

## 🏗 Project Structure

```text
VisionStream/
├── src/
│   ├── core/           # Stream engine, buffer, and reconnection logic
│   ├── gui/            # UI components and video widgets
│   ├── utils/          # Logging, configuration, and validation
│   └── main.py         # Application entry point
├── main.spec           # PyInstaller build configuration
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

## 🛣 Roadmap (Upcoming Features)

* Integration with local hardware (Webcams/DirectShow).
* Support for local video file playback (MP4, AVI, etc.).
* Multi-stream Grid layout for concurrent monitoring.

