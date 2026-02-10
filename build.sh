#!/bin/bash
# Build script for VisionStream - Creates standalone executable

echo ""
echo "========================================"
echo "VisionStream Build Script"
echo "========================================"
echo ""

# Check if PyInstaller is installed
python3 -m pip show pyinstaller > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing PyInstaller..."
    python3 -m pip install pyinstaller
fi

# Check if requirements are installed
echo "Checking dependencies..."
python3 -m pip install -r src/requirements.txt

# Build the executable
echo ""
echo "Building VisionStream..."
echo ""

pyinstaller pyinstaller_spec.spec --distpath dist --buildpath build --specpath .

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo ""

# Determine OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Executable location: dist/VisionStream/VisionStream"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Application location: dist/VisionStream/VisionStream.app"
fi

echo ""
