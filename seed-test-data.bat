@echo off
echo.
echo ========================================
echo   CareOps - Seed Test Data
echo ========================================
echo.

cd Backend
call venv\Scripts\activate
python seed_test_data.py

echo.
echo Press any key to exit...
pause > nul
