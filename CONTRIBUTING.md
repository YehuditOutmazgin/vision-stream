# Contributing to VisionStream

Thank you for your interest in contributing to VisionStream! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Log files from `logs/` directory

### Suggesting Features

1. Check if the feature has been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed
   - Ensure all tests pass

4. **Commit your changes:**
   ```bash
   git commit -m "Add feature: description"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yehuditOutmazgin/vision-stream.git
cd vision-stream

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run the application
python src/main.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Keep functions focused and concise
- Use meaningful variable names

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Test edge cases and error conditions

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_url_validator.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Documentation

- Update README.md for user-facing changes
- Update BUILD.md for build-related changes
- Update CHANGELOG.md with your changes
- Add docstrings to new code
- Update specification.md for requirement changes

## Commit Messages

Use clear, descriptive commit messages:

```
Add feature: webcam support for Linux
Fix bug: reconnection timeout not working
Update docs: add installation instructions
Refactor: simplify URL validation logic
```

## Questions?

Feel free to open an issue for any questions about contributing!
