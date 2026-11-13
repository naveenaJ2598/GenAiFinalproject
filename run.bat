@echo off
title LinguaMate AI Launcher
cd /d "%~dp0"

echo ==========================================
echo          LINGUAMATE AI
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install Python 3.11 or newer and try again.
    pause
    exit /b 1
)

echo [1/3] Installing/checking required packages...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Package installation failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul
if errorlevel 1 (
    echo WARNING: Ollama may not be running.
    echo Start Ollama, then ensure qwen2.5:1.5b is available.
    echo Run: ollama pull qwen2.5:1.5b
) else (
    echo Ollama is responding.
)

echo.
echo [3/3] Starting LinguaMate AI...
python -m streamlit run frontend/app.py
pause
