@echo off
echo ========================================
echo Building Headscale Installer
echo ========================================
echo.

REM Clean previous builds
echo [1/5] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del /q *.spec

REM Check if Python is installed
echo [2/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
echo [3/5] Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found, installing...
    pip install pyinstaller
)

REM Build the executable
echo [4/5] Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name="HeadscaleInstaller" ^
    --icon=icon.ico ^
    headscale_installer.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Check if exe was created
echo [5/5] Verifying build...
if exist "dist\HeadscaleInstaller.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESS!
    echo ========================================
    echo.
    echo Executable: dist\HeadscaleInstaller.exe
    echo Size: 
    for %%A in ("dist\HeadscaleInstaller.exe") do echo %%~zA bytes
    echo.
    echo Next steps:
    echo 1. Test the installer: dist\HeadscaleInstaller.exe
    echo 2. Sign it (optional): run sign.ps1
    echo 3. Distribute to users
    echo.
) else (
    echo ERROR: Executable not found in dist folder
    pause
    exit /b 1
)

pause
