@echo off
title Despachando Actualizacion a GitHub...
echo.
echo 1. Empaquetando archivos nuevos...
git add .
echo.
set /p msg="2. Escribi que cambiaste (ej: fondo claro): "
git commit -m "%msg%"
echo.
echo 3. Subiendo cambios al GitHub de aggusgarcia01...
git push -u origin main
echo.
echo ===================================
echo   ¡Todo subido a la nube con existo!
echo ===================================
pause