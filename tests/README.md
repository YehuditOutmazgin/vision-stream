# VisionStream Tests

This directory contains unit tests for VisionStream components.

## Test Coverage

- **test_url_validator.py**: 12 tests covering RTSP URL validation, local file paths, and webcam identifiers
- **test_reconnection_manager.py**: 10 tests covering state machine logic, reconnection attempts, and error handling

## Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

Run specific test:
```bash
pytest tests/test_url_validator.py::TestURLValidator::test_valid_rtsp_basic -v
```
