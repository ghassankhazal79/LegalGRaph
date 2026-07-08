@echo off
echo Installing PyInstaller...
pip install pyinstaller
echo Building GUI EXE...
pyinstaller --onefile --windowed --name LegalAI_Launcher launcher_gui.py
echo Done. Check dist\LegalAI_Launcher.exe
pause
