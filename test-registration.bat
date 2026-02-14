@echo off
echo ========================================
echo Testing CareOps Registration
echo ========================================
echo.

echo Test 1: Check if backend is running...
curl -s http://localhost:8000/health
if %errorlevel% == 0 (
    echo [OK] Backend is running
) else (
    echo [ERROR] Backend is NOT running!
    echo Please start it first.
    pause
    exit /b 1
)
echo.

echo Test 2: Try to register a test user...
echo.
curl -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"test123456\",\"full_name\":\"Test User\",\"workspace_name\":\"Test Workspace\"}"
echo.
echo.

echo ========================================
echo Check the response above:
echo - If you see tokens: Registration works!
echo - If you see an error: Check the error message
e