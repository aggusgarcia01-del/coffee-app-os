# ☕ Coffee App OS — Guía de Instalación y Uso

Sistema de gestión de cafetería diseñado para tablet, desarrollado en Python + Streamlit.

---

## 📋 Requisitos del Sistema

| Requisito | Mínimo recomendado |
|-----------|-------------------|
| Python    | 3.9 o superior     |
| RAM       | 512 MB             |
| Disco     | 200 MB libres      |
| OS        | Windows / macOS / Linux / Raspberry Pi OS |

---

## 🚀 Instalación Paso a Paso

### Paso 1 — Instalar Python

Descargá Python desde [python.org](https://www.python.org/downloads/).
Asegurate de marcar **"Add Python to PATH"** durante la instalación en Windows.

Verificá la instalación:
```bash
python --version
# Debería mostrar: Python 3.9.x o superior
```

### Paso 2 — Copiar los archivos del proyecto

Copiá la carpeta `coffee_app/` a la ubicación que prefieras en tu dispositivo.
Por ejemplo: `C:\Users\TuUsuario\coffee_app\` o `/home/pi/coffee_app/`.

### Paso 3 — Crear un entorno virtual (recomendado)

```bash
# Navegar a la carpeta del proyecto
cd coffee_app

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS / Linux:
source venv/bin/activate
```

### Paso 4 — Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- **Streamlit** — interfaz web
- **fpdf2** — generación de tickets PDF
- **Plotly** — gráficos del dashboard
- **Pandas** — manejo de datos

### Paso 5 — Ejecutar la aplicación

```bash
streamlit run app.py
```

La terminal mostrará algo como:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

Abrí esa URL en el navegador de tu tablet. ¡La app ya está corriendo!

---

## 📱 Uso en Tablet

### Opción A — Tablet conectada a la misma red WiFi

1. Buscá la dirección IP de la computadora que corre la app (ej. `192.168.1.100`).
2. En la tablet, abrí el navegador y entrá a `http://192.168.1.100:8501`.

Para permitir conexiones externas, ejecutá así:
```bash
streamlit run app.py --server.address 0.0.0.0
```

### Opción B — Tablet con Windows/Linux (app local)

Instalá Python y ejecutá la app directamente en la tablet. Abrí `http://localhost:8501` en el navegador.

### Opción C — Modo pantalla completa (quiosco)

En Chrome/Edge, abrí la URL y presioná `F11` para pantalla completa.
Podés crear un acceso directo en el escritorio apuntando a esa URL.

---

## ⚙️ Configuración Inicial

Al abrir la app por primera vez:

1. Andá a la pestaña **⚙️ Configuración**.
2. Completá el **Nombre del local**, **Dirección** y **Teléfono**.
3. Seleccioná el **ancho del ticket** según tu impresora (58mm o 80mm).
4. En la pestaña **📦 Stock**, cargá el stock inicial de café molido y demás insumos.
5. Desde Configuración podés también **editar los productos** del menú y sus precios.

---

## 🗄️ Base de Datos

La app crea automáticamente el archivo `coffee_app.db` (SQLite) en la misma carpeta.

**Tablas principales:**
- `productos` — menú con precios y gramaje de café por producto
- `ventas` — cabecera de cada venta (fecha, hora, tipo, pago, total)
- `detalle_ventas` — ítems de cada venta
- `stock` — stock actual y umbrales de alerta por insumo
- `movimientos_stock` — historial de cargas, salidas y mermas
- `config` — configuración general del sistema

**Backup manual:** Simplemente copiá el archivo `coffee_app.db` a un pendrive o la nube.

---

## 🖨️ Impresora Térmica

Los tickets PDF generados están optimizados para rollos de **58mm o 80mm**.

Para imprimir:
1. Descargá el PDF desde el botón **"🖨️ Descargar / Imprimir Ticket"**.
2. Abrí el PDF e imprimí sin márgenes (escala 100%).
3. En la configuración de impresión, seleccioná el tamaño de papel correcto (58mm × personalizado).

Impresoras compatibles probadas: EPSON TM-T20, Sewoo LK-T212, Bixolon SRP-330.

---

## 📦 Estructura de Archivos

```
coffee_app/
├── app.py              ← Aplicación principal (Streamlit)
├── database.py         ← Capa de datos (SQLite)
├── pdf_generator.py    ← Generador de tickets PDF (fpdf2)
├── requirements.txt    ← Dependencias Python
├── README.md           ← Esta guía
└── coffee_app.db       ← Base de datos (se crea automáticamente)
```

---

## 🔄 Flujo de Venta

```
1. Elegir Tipo de Consumo   →  🏠 En Local  o  🥡 Take-Away
2. Tocar productos          →  Se agregan al carrito
3. (Opcional) + Almíbar     →  Botón por ítem de café
4. Elegir Método de Pago    →  💵 Efectivo / 💳 Débito / 📱 Billetera
5. (Opcional) Agregar nota  →  Instrucciones especiales
6. COBRAR                   →  Registra venta + descuenta stock
7. Descargar / Imprimir     →  PDF del ticket generado
```

---

## 📊 Dashboard — Métricas disponibles

| Métrica | Descripción |
|---------|-------------|
| Ventas Totales | Suma de todos los tickets del día |
| Ticket Promedio | Promedio de monto por pedido |
| Producto más vendido | Por unidades vendidas en el día |
| Almíbares extra | Total de almíbares adicionales servidos |
| Horas Pico | Gráfico de barras por hora del día |
| Método de Pago | Distribución porcentual (torta) |
| Local vs Take-Away | Comparativo de tipos de consumo |
| Tendencia 7 días | Gráfico de línea con histórico semanal |

---

## ❓ Solución de Problemas Comunes

**La app no abre:**
```bash
# Verificar que streamlit está instalado
pip show streamlit
# Si no aparece, reinstalar:
pip install streamlit
```

**Error de módulo no encontrado:**
```bash
pip install -r requirements.txt --upgrade
```

**La base de datos no se crea:**
Asegurate de ejecutar el comando desde dentro de la carpeta `coffee_app/`:
```bash
cd coffee_app
streamlit run app.py
```

**El PDF no se genera:**
```bash
pip install fpdf2 --upgrade
```

---

## 📝 Personalización Rápida

- **Cambiar gramaje de café:** En ⚙️ Configuración → editar cada producto → campo "Gramos café".
- **Agregar insumos al stock:** Editá `database.py`, sección `stock_default`.
- **Cambiar colores:** Editá el bloque `<style>` en `app.py` → variables CSS en `:root`.
- **Precios en otra moneda:** Cambiá el símbolo `$` en `app.py` y `pdf_generator.py`.

---

*Coffee App OS — Desarrollado con Python + Streamlit + SQLite + fpdf2*
