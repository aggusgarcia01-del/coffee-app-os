@echo off
title Lanzando Coffee App OS...
cd /d "%~dp0"

:: Abrir el navegador antes de lanzar el servidor
start "" "http://localhost:8501"

:: Lanzar Streamlit
python -m streamlit run app.py --server.headless true
pause