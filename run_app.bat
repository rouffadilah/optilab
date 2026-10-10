@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Membuat virtual environment Python...
    py -m venv .venv
    if errorlevel 1 goto error
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto error
goto end
:error
echo.
echo Terjadi kesalahan. Pastikan Python 3.10+ terpasang dan koneksi internet tersedia saat instalasi pertama.
pause
:end
endlocal
