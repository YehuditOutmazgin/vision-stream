# Changelog

## [Unreleased] - 2026-02-10

### Added
- **Testing Infrastructure**: Added comprehensive unit tests
  - 12 tests for URLValidator (RTSP validation, local files, webcam identifiers)
  - 10 tests for ReconnectionManager (state machine, reconnection logic)
  - Total: 22 passing tests
  
- **Enhanced UX**:
  - Stream info overlay (resolution, codec, FPS) displayed in video widget
  - Consistent error messages using Config.ERROR_MESSAGES
  - Improved status feedback during connection

### Changed
- **Documentation Updates**:
  - README.md: Added support for RTSP, local files, and webcams
  - README.md: Documented asynchronous connection behavior
  - README.md: Added "Known Limitations" section
  - README.md: Added "Testing" section with pytest instructions
  - specification.md: Updated Requirement 1 to reflect multi-source support
  - specification.md: Added "Known Limitations" section
  - specification.md: Documented asynchronous start() behavior

- **Project Structure**:
  - Moved requirements.txt to project root
  - Added pytest to dependencies
  - Created tests/ directory with proper structure
  - Added BUILD.md with comprehensive build instructions
  - Added CHANGELOG.md for version tracking
  - Added LICENSE (MIT)
  - Added CONTRIBUTING.md for contributors
  - Added .editorconfig for code consistency
  - Added setup.py for package installation

- **Code Quality**:
  - Translated all Hebrew comments to English for international collaboration
  - Improved code consistency and readability

### Technical Details
- All error dialogs use centralized Config.ERROR_MESSAGES
- Video widget now displays stream metadata (resolution/codec) alongside FPS
- Asynchronous connection handling documented in both README and specification
- Known limitations clearly documented for users and developers
- All code comments and documentation now in English
- PyInstaller build configuration optimized with collect_all hooks
- Portable executable includes all dependencies (~200-300 MB)
