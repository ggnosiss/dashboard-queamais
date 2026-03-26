@echo off
echo === Configurando ambiente local do Dashboard ===

REM Backend
echo.
echo [1/4] Criando venv do backend...
cd backend
python -m venv .venv
call .venv\Scripts\activate.bat
echo [2/4] Instalando dependencias do backend...
pip install -r requirements.txt
deactivate
cd ..

REM Frontend
echo.
echo [3/4] Criando venv do frontend...
cd frontend
python -m venv .venv
call .venv\Scripts\activate.bat
echo [4/4] Instalando dependencias do frontend...
pip install -r requirements.txt
deactivate
cd ..

echo.
echo === Pronto! Agora rode: start_local.bat ===
pause
