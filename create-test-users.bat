@echo off
echo.
echo ========================================
echo   Creating Test Users via API
echo ========================================
echo.

echo Creating Wellness Clinic Owner (Alice)...
curl -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"alice@wellnessclinic.com\",\"password\":\"password123\",\"full_name\":\"Alice Johnson\",\"workspace_name\":\"Wellness Clinic\"}"
echo.
echo.

timeout /t 2 /nobreak > nul

echo Creating Therapy Center Owner (David)...
curl -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"david@therapycenter.com\",\"password\":\"password123\",\"full_name\":\"David Brown\",\"workspace_name\":\"Therapy Center\"}"
echo.
echo.

echo ========================================
echo   Test Users Created!
echo ========================================
echo.
echo Login Credentials:
echo   alice@wellnessclinic.com / password123
echo   david@therapycenter.com / password123
echo.
echo Note: Staff users need to be invited by owners
echo.
pause
