# Requirements Document: VisionStream Desktop Player

## Introduction

VisionStream - A high-performance, native desktop video player for Windows built with Python 3.11, PySide6, and PyAV (FFmpeg backend). The application supports **RTSP streams**, **local video files**, and **webcams** with ultra-low latency streaming, supporting H.264/H.265 codecs. The architecture emphasizes thread-safe operations, zero-copy frame handling, NumPy integration, asynchronous connection handling, and responsive UI even under network stress conditions.

**Technology Stack:**
- **GUI Framework:** PySide6 (Qt 6 for Python)
- **Video Engine:** PyAV (FFmpeg Python bindings)
- **Frame Processing:** NumPy arrays with zero-copy techniques
- **Python Version:** 3.11+
- **Target Platform:** Windows (cross-platform capable)

**Development Strategy:**
- **Phase 1 (MVP):** Single-stream RTSP player with all core features (Requirements 1-9, 11)
- **Phase 2 (Future):** Multi-stream grid support (Requirement 10) - architecture designed to support this from the start
- **Architecture Principle:** All components (VideoEngine, VideoWidget, StreamManager) are designed as reusable, independent modules to enable future grid expansion with minimal refactoring

## Glossary

- **RTSP**: Real Time Streaming Protocol - a network protocol for streaming video/audio over TCP
- **Stream**: A continuous flow of video data from an RTSP source
- **Codec**: Video compression format (H.264, H.265/HEVC)
- **GUI**: Graphical User Interface built with PySide6 (Qt for Python)
- **Player**: The application component that handles video playback and rendering
- **URL**: Uniform Resource Locator - the address of the RTSP stream
- **Frame**: A single image in a video sequence
- **PyAV**: Python bindings for FFmpeg library
- **FFmpeg**: Multimedia framework for encoding/decoding video
- **Thread-Safe**: Operations that can be safely executed from multiple threads
- **Zero-Copy**: Frame handling that avoids unnecessary memory copies
- **Producer-Consumer**: Asynchronous pattern where Stream Engine produces frames and UI consumes them
- **Daemon Thread**: Background thread that doesn't prevent application exit
- **NumPy Array**: Efficient numerical array representation for frame data

## Requirements

### Requirement 1: Multi-Source Input Support

**User Story:** As a user, I want to input different video sources (RTSP, local files, webcams), so that I can view various types of video content.

#### Acceptance Criteria

1. WHEN the application starts, THE Player SHALL display a text input field for entering video source URLs/paths
2. WHEN a user enters an RTSP URL (e.g., `rtsp://host:port/path`), THE Player SHALL accept and validate it
3. WHEN a user enters a local file path (e.g., `C:\Videos\sample.mp4`), THE Player SHALL accept and validate it
4. WHEN a user enters a webcam identifier (e.g., `video=Integrated Camera` or `0`), THE Player SHALL accept it
5. WHEN a user attempts to enter an empty URL, THE Player SHALL prevent submission and maintain the current state
6. WHEN a user enters a malformed RTSP URL, THE Player SHALL validate the format and provide feedback
7. WHEN the start() method is called, THE Player SHALL initiate connection asynchronously in a background thread to keep the GUI responsive
8. WHEN connection is in progress, THE Player SHALL allow the GUI to remain interactive and responsive
9. WHEN connection succeeds or fails, THE Player SHALL notify the GUI via Qt signals (connection_established or error_occurred)

### Requirement 2: Playback Control

**User Story:** As a user, I want to control video playback with a Play button, so that I can start and stop streaming on demand.

#### Acceptance Criteria

1. WHEN a valid RTSP URL is entered and the Play button is clicked, THE Player SHALL initiate connection to the RTSP stream
2. WHEN the Play button is clicked with an empty URL field, THE Player SHALL prevent playback and display an error message
3. WHEN a stream is playing, THE Player SHALL display a Stop button to allow the user to terminate playback
4. WHEN the Stop button is clicked, THE Player SHALL close the stream connection and clear the video display

### Requirement 3: Video Display

**User Story:** As a user, I want to see the video stream displayed in the application window, so that I can view the content being streamed.

#### Acceptance Criteria

1. WHEN a stream connection is successfully established, THE Player SHALL display the video frames in the main window
2. WHEN video frames are received, THE Player SHALL render them continuously without significant lag
3. WHEN the stream is stopped or disconnected, THE Player SHALL clear the video display area
4. WHEN the window is resized, THE Player SHALL scale the video display appropriately
5. WHEN the window is resized, THE Player SHALL maintain the video's original aspect ratio using letterboxing (black bars on sides/top-bottom) if necessary

### Requirement 4: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages when something goes wrong, so that I understand why the stream failed to play.

#### Acceptance Criteria

1. IF the RTSP URL is invalid or malformed, THEN THE Player SHALL display a Validation Error message indicating the URL format is incorrect
2. IF the RTSP server is offline or refuses the connection, THEN THE Player SHALL display a Connection Error message with the server status
3. IF the stream codec is unsupported, THEN THE Player SHALL display a Codec Error indicating the specific codec issue (e.g., "Unsupported codec: VP9")
4. IF a network timeout occurs during playback, THEN THE Player SHALL display a timeout error message and trigger automatic reconnection
5. IF a network error occurs during playback, THEN THE Player SHALL display the error and allow the user to retry
6. WHEN an error occurs, THE Player SHALL maintain application stability and allow the user to enter a new URL
7. THE UI SHALL differentiate between three error categories: Validation Errors (malformed URL), Connection Errors (server offline/refused), and Codec Errors (unsupported video format)

### Requirement 5: Application Stability and Performance

**User Story:** As a user, I want the application to run smoothly without crashes, so that I can reliably stream video.

#### Acceptance Criteria

1. WHEN the application is running, THE Player SHALL handle stream interruptions gracefully without crashing
2. WHEN multiple connection attempts are made, THE Player SHALL manage resources properly and not leak memory
3. WHEN the application window is closed, THE Player SHALL properly release all resources and connections
4. WHEN video is being decoded, THE Player SHALL maintain responsive UI without freezing
5. WHEN frames are being processed, THE Player SHALL use zero-copy frame handling to minimize memory overhead
6. WHEN the stream engine is running, THE Player SHALL use daemon threads that don't prevent application exit
7. UPON application close, THE Player SHALL execute a graceful shutdown sequence:
   - Send a stop signal to the VideoEngine
   - Close the PyAV container safely
   - Join daemon threads with a maximum timeout of 1 second before complete exit
   - Release all FFmpeg resources and network connections

### Requirement 6: High-Performance Video Decoding with Latest Frame Policy

**User Story:** As a professional user, I want ultra-low latency video streaming with efficient frame handling, so that I can monitor real-time video feeds with minimal delay.

#### Acceptance Criteria

1. WHEN video frames are received, THE Player SHALL decode H.264 and H.265 (HEVC) codecs using FFmpeg
2. WHEN frames are decoded, THE Player SHALL convert them to RGB24 format using NumPy arrays
3. WHEN frames are rendered, THE Player SHALL use zero-copy techniques to avoid unnecessary memory copies
4. WHEN the window is resized, THE Player SHALL scale video using smooth transformation without blocking the UI
5. WHEN the stream is active, THE Player SHALL maintain frame rate without significant CPU overhead
6. THE Player SHALL aim for a glass-to-glass latency of less than 500ms on a local network (Note: Over internet connections, latency may be higher depending on network conditions)
7. THE Player SHALL implement a Strict Latest Frame Policy using a single-frame buffer. When a new frame is decoded, it immediately overwrites the previous one to ensure the user sees the most recent data
8. WHEN the frame buffer receives a new frame, THE Player SHALL immediately replace the current frame without queuing to ensure real-time display
9. WHEN opening an RTSP stream, THE Player SHALL force RTSP over TCP (interleaved mode) to prevent image artifacts and packet loss
10. WHEN opening an RTSP stream, THE Player SHALL configure PyAV/FFmpeg with the following parameters:
    - rtsp_transport: tcp
    - fflags: nobuffer
    - flags: low_delay
    These settings minimize internal buffering and ensure low-latency frame delivery
11. THE initial connection timeout SHALL be set to 10 seconds before displaying a connection error

### Requirement 7: Cross-Platform Compatibility

**User Story:** As a developer, I want the application to be built with cross-platform libraries, so that it can potentially run on Linux and macOS in the future.

#### Acceptance Criteria

1. THE Player SHALL use PySide6 (Qt for Python) for cross-platform GUI
2. THE Player SHALL use PyAV/FFmpeg for cross-platform video handling
3. WHEN the application is packaged, THE Player SHALL be distributable as a standalone executable
4. THE Player SHALL use Python 3.11+ for modern language features and performance

### Requirement 8: Automatic Reconnection and Watchdog Mechanism

**User Story:** As a professional user, I want the application to automatically recover from network interruptions, so that I don't have to manually restart streams when temporary network issues occur.

#### Acceptance Criteria

1. WHEN a stream is interrupted or no frames are received for 2.5 seconds, THE Player SHALL detect the disconnection
2. WHEN a disconnection is detected, THE Player SHALL automatically attempt to reconnect using exponential backoff strategy
3. WHEN reconnecting, THE Player SHALL use the following retry schedule: immediate, 2 seconds, 5 seconds, 10 seconds, 30 seconds
4. WHEN a reconnection attempt is in progress, THE Player SHALL display a "Connecting..." indicator or spinner on the video display
5. WHEN a stream successfully reconnects, THE Player SHALL resume playback without user intervention
6. WHEN maximum reconnection attempts (5 attempts) are exhausted, THE Player SHALL display a descriptive error message and allow manual retry
7. THE Watchdog mechanism SHALL monitor frame arrival continuously with a 2.5-second timeout threshold to ensure responsive detection of network failures

### Requirement 9: Operational Visibility and Diagnostics

**User Story:** As a developer/tester, I want comprehensive logging and real-time metrics, so that I can diagnose issues and verify performance.

#### Acceptance Criteria

1. WHEN the application runs, THE Player SHALL log all connection/disconnection events with timestamps
2. WHEN codec errors occur, THE Player SHALL log the error details for debugging
3. WHEN a stream connects, THE Player SHALL log the detected resolution and FPS
4. WHEN the application is running, THE Player SHALL display current FPS (Frames Per Second) in the top-right corner with semi-transparent background
5. WHEN the application runs, THE Player SHALL write all logs to a file in the application directory for post-analysis
6. WHEN errors occur, THE Player SHALL include error codes and descriptions in both UI and logs

### Requirement 10: Multi-Stream Grid Display (Future-Ready Architecture)

**User Story:** As a professional user, I want the application to be designed for future multi-stream capability, so that I can monitor multiple cameras simultaneously in a future version.

#### Acceptance Criteria

1. WHEN the application is designed, THE Player architecture SHALL support multiple independent VideoEngine instances
2. WHEN VideoWidget is implemented, THE Player SHALL design it as a reusable, self-contained component
3. WHEN the application runs, THE Player SHALL use a thread pool or separate daemon threads for each stream instance
4. WHEN multiple streams are added (future feature), THE Player SHALL support configurable grid layouts (1x1, 2x2, 3x3, 4x4)
5. WHEN the window is resized, THE Player SHALL scale all grid cells proportionally while maintaining aspect ratios
6. WHEN a stream fails in a grid, THE Player SHALL display an error in that cell without affecting other streams
7. THE Player architecture SHALL be designed to minimize CPU and memory overhead when multiple streams are active

### Requirement 11: Deployment and Distribution

**User Story:** As an end-user, I want to install and run the application easily on Windows, so that I can use it without complex setup procedures.

#### Acceptance Criteria

1. WHEN the application is built, THE Player SHALL be packaged as a single .exe file using PyInstaller for simplicity and compatibility
2. WHEN the .exe is executed on a clean Windows system, THE Player SHALL run without requiring Python installation
3. WHEN the .exe is executed, THE Player SHALL include all required FFmpeg DLLs and dependencies bundled together
4. WHEN the application is distributed, THE Player SHALL include a README with installation and usage instructions
5. WHEN the application runs, THE Player SHALL create a logs directory in the application folder for diagnostic files

## Known Limitations

1. **RTSP External Streams**: Connection stability and latency depend heavily on:
   - Network conditions (bandwidth, packet loss, jitter)
   - Firewall and NAT configurations
   - Router port forwarding settings
   - ISP throttling policies
   - Local network streams typically achieve <500ms latency, but internet streams may vary significantly

2. **Codec Support**: Currently limited to H.264 and H.265/HEVC. Other codecs (VP9, AV1, MJPEG) are not supported.

3. **Webcam Platform Support**: Webcam support is Windows-only via DirectShow. Linux (V4L2) and macOS (AVFoundation) are not yet implemented.

4. **Single Stream Limitation**: Only one stream can be active at a time. Multi-stream grid view is planned for Phase 2.

5. **Asynchronous Connection**: The start() method returns immediately and performs connection in a background thread. Errors are reported via Qt signals, not return values.

## System Architecture Diagram

### Data Flow - Sequence Diagram

```
User                Main Window         Stream Engine           RTSP Server         Frame Buffer        Video Widget
 |                      |                    |                      |                    |                   |
 |--Enter URL---------->|                    |                      |                    |                   |
 |                      |                    |                      |                    |                   |
 |--Click Play--------->|                    |                      |                    |                   |
 |                      |--Start Stream----->|                      |                    |                   |
 |                      |                    |--Connect RTSP------->|                    |                   |
 |                      |                    |<--RTSP Response------|                    |                   |
 |                      |                    |                      |                    |                   |
 |                      |                    |--Request Frame------>|                    |                   |
 |                      |                    |<--Video Packet-------|                    |                   |
 |                      |                    |                      |                    |                   |
 |                      |                    |--Decode Frame------->|                    |                   |
 |                      |                    |--Convert to RGB24--->|                    |                   |
 |                      |                    |--Add to Buffer------>|                    |                   |
 |                      |                    |                      |                    |                   |
 |                      |<--Frame Ready Signal (Qt Signal)----------|                    |                   |
 |                      |                    |                      |                    |--Get Frame------->|
 |                      |                    |                      |                    |<--NumPy Array-----|
 |                      |                    |                      |                    |                   |
 |                      |                    |                      |                    |                   |--Render to QImage
 |                      |                    |                      |                    |                   |--Display on Screen
 |                      |                    |                      |                    |                   |
 |<--Video Displayed----|                    |                      |                    |                   |
 |                      |                    |                      |                    |                   |
 |--Click Stop--------->|                    |                      |                    |                   |
 |                      |--Stop Stream------>|                      |                    |                   |
 |                      |                    |--Close Connection--->|                    |                   |
 |                      |                    |<--Connection Closed--|                    |                   |
 |                      |                    |--Clear Buffer------->|                    |                   |
 |                      |<--Stream Stopped Signal (Qt Signal)-------|                    |                   |
 |                      |                    |                      |                    |                   |--Clear Display
 |<--Display Cleared----|                    |                      |                    |                   |
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     VisionStream RTSP Viewer                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              GUI Layer (PySide6 / Qt)                    │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Main Window                                             │   │
│  │  ├─ URL Input Field                                      │   │
│  │  ├─ Play/Stop Buttons                                    │   │
│  │  ├─ Video Widget (QLabel with QImage rendering)          │   │
│  │  └─ Status/Error Display                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ▲                                     │
│                           │ Qt Signals                          │
│                           │ (Thread-Safe)                       │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │              Stream Engine (Daemon Thread)               │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  RTSP Connection Manager                                 │   │
│  │  ├─ URL Validation                                       │   │
│  │  ├─ Connection Handling                                  │   │
│  │  └─ Error Management                                     │   │
│  │                                                          │   │
│  │  PyAV Decoder (FFmpeg Backend)                           │   │
│  │  ├─ H.264/H.265 Decoding                                 │   │
│  │  ├─ RGB24 Conversion                                     │   │
│  │  └─ NumPy Array Generation                               │   │
│  │                                                          │   │
│  │  Frame Buffer Manager                                    │   │
│  │  ├─ Single-Frame Buffer (Strict Latest Frame Policy)     │   │
│  │  ├─ Zero-Copy Frame Handling                             │   │
│  │  └─ Watchdog Monitor (2.5s Timeout)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ▲                                     │
│                           │ RTSP Protocol                       │
│                           │ (TCP)                               │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │              External Resources                          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  RTSP Server (Network)                                   │   │
│  │  FFmpeg Libraries (C-Level)                              │   │
│  │  NumPy (Numerical Processing)                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Thread Model

```
Main Thread (UI Thread)
├─ Event Loop (PySide6/Qt)
├─ User Input Handling
├─ Video Widget Rendering
└─ Signal Reception from Stream Engine

Stream Engine Thread (Daemon)
├─ RTSP Connection
├─ PyAV Decoding
├─ Frame Buffer Management
└─ Signal Emission to Main Thread
```

### Data Flow - Frame Processing Pipeline

```
RTSP Server
    │
    ├─ TCP Stream (H.264/H.265 packets)
    │
    ▼
PyAV Container (av.open with rtsp_transport=tcp, fflags=nobuffer, flags=low_delay)
    │
    ├─ Demux RTSP packets over TCP
    │
    ▼
PyAV Decoder (FFmpeg with low_delay configuration)
    │
    ├─ Decode to raw frames
    │
    ▼
Frame Conversion
    │
    ├─ to_ndarray() → NumPy RGB24 array
    │ (Zero-Copy: Direct pointer to FFmpeg buffer)
    │
    ▼
Frame Buffer (Strict Latest Frame Policy)
    │
    ├─ Single-frame buffer
    │ (New frame immediately overwrites previous frame)
    │
    ▼
Qt Signal (Thread-Safe)
    │
    ├─ Emit frameReady signal to Main Thread
    │
    ▼
Video Widget (Main Thread)
    │
    ├─ Convert NumPy array to QImage
    ├─ Scale with aspect ratio preservation
    ├─ Render to screen
    ├─ Display FPS counter
    │
    ▼
Display on Screen
```

### Reconnection Logic - State Machine

```
┌─────────────────────────────────────────────────────────────┐
│                    Stream State Machine                     │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   IDLE       │
                    │ (No Stream)  │
                    └──────┬───────┘
                           │ User clicks Play
                           ▼
                    ┌──────────────┐
                    │  CONNECTING  │
                    │ (Attempt 1)  │
                    └──────┬───────┘
                           │
                    ┌──────┴──────┐
                    │             │
                 Success        Failure
                    │             │
                    ▼             ▼
            ┌──────────────┐  ┌──────────────┐
            │   PLAYING    │  │  RETRY_1     │
            │ (Streaming)  │  │ (Wait 2s)    │
            └──────┬───────┘  └──────┬───────┘
                   │                 │
            ┌──────┴──────┐          ▼
            │             │    ┌──────────────┐
        Timeout      Disconnect│  CONNECTING  │
        (2.5s no     (Network) │ (Attempt 2)  │
         frames)               └──────┬───────┘
            │             │           │
            │             │    ┌──────┴──────┐
            │             │    │             │
            │             │Success      Failure
            │             │    │             │
            │             │    ▼             ▼
            │             │ PLAYING    ┌──────────────┐
            │             │            │  RETRY_2     │
            │             │            │ (Wait 5s)    │
            │             │            └──────┬───────┘
            │             │                   │
            └─────────────┴───────────────────┘
                          │
                    ┌─────┴──────┐
                    │            │
              Max Retries    Success
              Exceeded       (Reconnect)
                    │            │
                    ▼            ▼
            ┌──────────────┐  PLAYING
            │   ERROR      │
            │ (Show Error) │
            └──────┬───────┘
                   │ User clicks Play again
                   ▼
                  IDLE
```

### Watchdog Mechanism - Frame Monitoring

```
Stream Engine Thread
│
├─ Last Frame Timestamp: T0
├─ Watchdog Interval: 2.5 seconds (timeout threshold)
│
├─ Every 100ms:
│  ├─ Check: (Current Time - Last Frame Timestamp) > 2.5s?
│  │
│  ├─ If YES:
│  │  ├─ Emit: frameTimeout signal
│  │  ├─ Trigger: Reconnection Logic (immediately)
│  │  └─ Update UI: "Connecting..."
│  │
│  └─ If NO:
│     └─ Continue monitoring
│
└─ When new frame arrives:
   ├─ Update: Last Frame Timestamp = Current Time
   └─ Continue monitoring
```

### Logging Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Logging System                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Stream Engine Thread                                       │
│  ├─ [2024-01-15 10:30:45] CONNECT: rtsp://camera1:554/...   │
│  ├─ [2024-01-15 10:30:46] CODEC: H.264, 1920x1080, 30 FPS   │
│  ├─ [2024-01-15 10:30:50] TIMEOUT: No frames for 2.5s       │
│  ├─ [2024-01-15 10:30:50] RECONNECT: Attempt 1 (immediate)  │
│  ├─ [2024-01-15 10:30:52] RECONNECT: Attempt 2 (wait 2s)    │
│  ├─ [2024-01-15 10:30:52] CONNECT: Successfully reconnected │
│  └─ [2024-01-15 10:30:53] RESUME: Playback resumed          │
│                                                             │
│  Main Thread (UI)                                           │
│  ├─ [2024-01-15 10:30:45] UI: Play button clicked           │
│  ├─ [2024-01-15 10:30:46] UI: FPS counter: 30 FPS           │
│  ├─ [2024-01-15 10:30:50] UI: Showing "Connecting..."       │
│  └─ [2024-01-15 10:30:52] UI: Playback resumed              │
│                                                             │
│  Output Files:                                              │
│  ├─ logs/visionstream_2024-01-15.log                        │
│  └─ logs/visionstream_errors.log                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
