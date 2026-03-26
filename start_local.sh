#!/bin/bash
# Executa backend e frontend localmente (sem Docker)
# Uso: bash start_local.sh

echo "=== Dashboard local ==="

# Copia .env para o backend
cp .env backend/.env

# Backend
echo "[1/2] Iniciando FastAPI em http://localhost:8000 ..."
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

sleep 2

# Frontend
echo "[2/2] Iniciando Dash em http://localhost:8050 ..."
cd frontend
BACKEND_URL=http://localhost:8000 API_KEY=dev-local-key-123 .venv/Scripts/python app.py &
FRONTEND_PID=$!
cd ..

echo ""
echo "Dashboard: http://localhost:8050"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar tudo."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servidores parados.'" EXIT
wait
