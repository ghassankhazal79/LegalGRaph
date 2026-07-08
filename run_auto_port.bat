@echo off
cd /d "%~dp0"
set USE_FAISS=0
set DEVICE=-1
python app\app.py
pause
