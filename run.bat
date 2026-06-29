@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\streamlit.exe" (
    echo Virtual environment not found. Run: python -m venv venv ^& venv\Scripts\pip install -r requirements.txt
    exit /b 1
)
for /d /r src %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
if exist "__pycache__" rd /s /q "__pycache__"
venv\Scripts\streamlit.exe run app.py
