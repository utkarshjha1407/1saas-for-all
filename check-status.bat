@echo off
echo ========================================
echo CareOps Status Check
echo ========================================
echo.

echo Checking Backend (Port 8000)...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Backend is running on http://localhost:8000
    curl http://localhost:8000/health
) else (
    echo [ERROR] Backend is NOT running on port 8000
    echo Please start it with: restart-backend.bat
)
echo.

echo Checking Frontend (Port 8080)...
curl -s http://localhost:8080 >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Frontend is running on http://localhost:8080
) else (
    echo [ERROR] Frontend is NOT running on port 8080
    echo Please start it with: cd frontend ^&^& npm run dev
)
echo.

echo Configuration Check:
echo - Frontend URL: http://localhost:8080
echo - Backend URL: http://localhost:8000
echo - API Endpoint: http://localhost:8000/api/v1
echo.

echo ========================================
echo Next Steps:
echo 1. If backend is not running: Run restart-backend.bat
echo 2. If frontend is not running: cd frontend ^&^& npm run dev
echo 3. Open browser: http://localhost:8080
echo ========================================
pause
