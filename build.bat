@echo off
REM Build script for VisionStream - Creates standalone .exe

echo.
echo ========================================
echo VisionStream Build Script
echo ========================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Check if requirements are installed
echo Checking dependencies...
python -m pip install -r src/requirements.txt

REM Build the executable
echo.
echo Building VisionStream.exe...
echo.

pyinstaller pyinstaller_spec.spec --distpath dist --workpath build

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\VisionStream\VisionStream.exe
echo.
pause
