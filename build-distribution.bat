@echo off
REM VisionStream - Create Distribution Package
REM This script builds the executable and creates a ZIP for distribution

echo ========================================
echo VisionStream - Build Distribution
echo ========================================
echo.

REM Step 1: Clean previous builds
echo [1/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Done.
echo.

REM Step 2: Run tests
echo [2/4] Running tests...
python -m pytest tests/ -v
if errorlevel 1 (
    echo.
    echo ERROR: Tests failed! Fix tests before building.
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 3: Build executable
echo [3/4] Building executable with PyInstaller...
pyinstaller main.spec
if errorlevel 1 (
    echo.
    echo ERROR: Build failed! Check the error messages above.
    pause
    exit /b 1
)
echo Done.
echo.


REM Step 4: Create ZIP
echo [4/4] Creating distribution ZIP...
cd dist
powershell -Command "Compress-Archive -Path VisionStream -DestinationPath VisionStream-v1.0.0.zip -Force"
cd ..
echo Done.
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Distribution package created:
echo   dist\VisionStream-v1.0.0.zip
echo.
echo You can now send this ZIP file to users.
echo.
pause
