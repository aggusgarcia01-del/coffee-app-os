# crear_entorno.py
import os

# 1. Crear requirements.txt
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("streamlit\npandas\nplotly\npyserial\n")
print("✅ requirements.txt creado.")

# 2. Crear .gitignore
with open(".gitignore", "w", encoding="utf-8") as f:
    f.write("*.db\n*.db-journal\n__pycache__/\ntickets/\n")
print("✅ .gitignore creado.")

# 3. Crear Arrancar_Sistema.bat
script_bat = """@echo off
title Arrancando Punto Cafe...
echo Iniciando el sistema de caja local...
python -m streamlit run app.py --browser.gatherUsageStats=false
pause"""

with open("Arrancar_Sistema.bat", "w", encoding="utf-8") as f:
    f.write(script_bat)
print("✅ Arrancar_Sistema.bat creado.")
print("\n¡Listo! ")