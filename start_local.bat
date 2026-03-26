@echo off
echo === Iniciando Dashboard (local) ===

REM Copia o .env para dentro do backend (uvicorn lê do diretório de trabalho)
copy /Y .env backend\.env >nul

REM Backend em nova janela
echo Iniciando Backend (FastAPI) em http://localhost:8000 ...
start "Backend - FastAPI" cmd /k "cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

REM Aguarda 3 segundos para o backend subir
timeout /t 3 /nobreak >nul

REM Frontend em nova janela
echo Iniciando Frontend (Dash) em http://localhost:8050 ...
start "Frontend - Dash" cmd /k "cd frontend && .venv\Scripts\activate && set BACKEND_URL=http://localhost:8000 && set API_KEY=dev-local-key-123 && python app.py"

echo.
echo Dashboard: http://localhost:8050
echo API Docs:  http://localhost:8000/docs
echo.
echo Feche as janelas para parar os servidores.
