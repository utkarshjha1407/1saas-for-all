@echo off
echo ========================================
echo CareOps Development Environment
echo ========================================
echo.

echo Starting Redis...
docker start careops-redis 2>nul || docker run -d -p 6379:6379 --name careops-redis redis:alpine
echo Redis started on port 6379
echo.

echo Starting Backend...
start cmd /k "cd Backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
echo Backend starting on http://localhost:8000
echo.

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"
echo Frontend starting on http://localhost:8080
echo.

echo ========================================
echo All services started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8080
echo API Docs: http://localhost:8000/docs
echo ========================================
