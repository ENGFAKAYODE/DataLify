@echo off
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -m streamlit run app.py --server.port 8504
) else (
    python -m streamlit run app.py --server.port 8504
)

endlocal
