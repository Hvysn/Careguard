@echo off
echo ========================================================
echo   CareGuard Healthcare Insurance RAG System Setup
echo ========================================================

REM 1. Copy template .env for backend if not present
if not exist backend\.env (
    copy backend\.env.example backend\.env
    echo [Setup] Created backend\.env from template
)

echo.
echo [1/3] Setting up Python AI Microservice...
cd ai-service
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
python ingest.py
cd ..

echo.
echo [2/3] Setting up Node.js Express Backend...
cd backend
call npm install
cd ..

echo.
echo [3/3] Setting up React Frontend...
cd frontend
call npm install
cd ..

echo.
echo ========================================================
echo   Installation Complete!
echo   To run the system, open 3 terminal windows:
echo     1. cd ai-service ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload --port 8000
echo     2. cd backend ^&^& npm run dev
echo     3. cd frontend ^&^& npm run dev
echo ========================================================
