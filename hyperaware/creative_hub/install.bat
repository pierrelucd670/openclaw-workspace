@echo off
:: LTX-2 Quick Install for Windows 11
:: Target: G:\ai\ltx2 | GPU: RTX 3060 12GB
echo === LTX-2 Creative Hub Install ===
echo Target: G:\ai\ltx2

:: Create dirs
mkdir G:\ai\ltx2 2>nul

:: Download main install script
echo Downloading install script...
powershell -Command "Invoke-WebRequest http://192.168.2.21:9999/install_ltx2_win11.ps1 -OutFile G:\ai\install_ltx2.ps1" 2>nul

if not exist "G:\ai\install_ltx2.ps1" (
    echo ERROR: Download failed. Check network to 192.168.2.21:9999
    pause
    exit /b 1
)

:: Run install
echo Running installation...
powershell -ExecutionPolicy Bypass -File G:\ai\install_ltx2.ps1

echo.
echo === DONE ===
pause
