@echo off
title CareGuard Healthcare RAG Launcher
echo =================================================================
echo   Starting CareGuard Healthcare Insurance RAG System
echo =================================================================
echo.

cd /d "%~dp0"

echo [1/3] Launching Python AI Service (Port 8000)...
start "AI Microservice (Port 8000)" cmd /k "cd ai-service && if exist venv\Scripts\activate (call venv\Scripts\activate) && uvicorn main:app --reload --port 8000"

echo [2/3] Launching Node.js Express Backend (Port 5000)...
start "Backend Express (Port 5000)" cmd /k "cd backend && npm run dev"

echo [3/3] Launching React Frontend (Port 5173)...
start "Frontend React (Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo =================================================================
echo   All 3 services have been launched!
echo   Open your browser at: http://localhost:5173
echo =================================================================
pause
