@echo off
echo ========================================
echo Fixing Frontend Issues
echo ========================================
echo.

echo Step 1: Stopping any running dev servers...
taskkill /F /IM node.exe 2>nul
echo Done.
echo.

echo Step 2: Clearing node_modules cache...
cd frontend
if exist node_modules rmdir /s /q node_modules
echo Done.
echo.

echo Step 3: Reinstalling dependencies...
call npm install
echo Done.
echo.

echo Step 4: Starting frontend...
echo Frontend will start on http://localhost:8080
echo.
call npm run dev

pause
