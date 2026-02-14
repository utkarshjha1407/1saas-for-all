@echo off
echo ========================================
echo Restarting Backend Server
echo ========================================
echo.

echo Step 1: Stopping any running backend processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

echo Step 2: Starting backend with new configuration...
cd Backend
call venv\Scripts\activate
echo Backend starting on http://localhost:8000
echo Press Ctrl+C to stop
echo.
uvicorn app.main:app --reload --port 8000
