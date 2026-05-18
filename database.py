# =============================================================
# database.py — Capa de acceso a datos de Coffee App OS
# Motor: SQLite (local, sin servidor, ideal para tablet)
# =============================================================

import sqlite3
from datetime import datetime, date
import os

# Ruta de la base de datos (en el mismo directorio que el script)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coffee_app.db")


def get_connection():
    """Retorna una conexión a la base de datos SQLite con Row Factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder por nombre de columna
    return conn


def init_db():
    """
    Inicializa la base de datos, limpia duplicados y carga los default de forma segura.
    """
    conn = get_connection()
    c = conn.cursor()

    # ── Tabla: Productos ──────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT    NOT NULL,
            precio          REAL    NOT NULL DEFAULT 0,
            categoria       TEXT    NOT NULL DEFAULT 'cafe',
            cafe_molido_g   REAL    NOT NULL DEFAULT 18,
            activo          INTEGER NOT NULL DEFAULT 1
        )
    ''')

    # 🧹 LA ASPIRADORA: Borra todos los duplicados que se te acumularon antes
    c.execute('''
        DELETE FROM productos 
        WHERE id NOT IN (SELECT MIN(id) FROM productos GROUP BY nombre)
    ''')

    # ── Tabla: Ventas (cabecera) ──────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha           DATE    NOT NULL,
            hora            TEXT    NOT NULL,
            tipo_consumo    TEXT    NOT NULL,   -- 'local' | 'takeaway'
            metodo_pago     TEXT    NOT NULL,   -- 'efectivo' | 'debito' | 'billetera'
            subtotal        REAL    NOT NULL,
            total           REAL    NOT NULL,
            ticket_num      INTEGER NOT NULL,
            notas           TEXT    DEFAULT ''
        )
    ''')

    # ── Tabla: Detalle de Ventas (ítems) ──────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id        INTEGER NOT NULL,
            producto_id     INTEGER NOT NULL,
            nombre_producto TEXT    NOT NULL,
            cantidad        INTEGER NOT NULL DEFAULT 1,
            precio_unitario REAL    NOT NULL,
            subtotal_item   REAL    NOT NULL,
            almibar_extra   INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (venta_id) REFERENCES ventas(id)
        )
    ''')

    # ── Tabla: Stock de insumos ───────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            insumo           TEXT    NOT NULL UNIQUE,
            cantidad_actual  REAL    NOT NULL DEFAULT 0,
            unidad           TEXT    NOT NULL DEFAULT 'g',
            cantidad_alerta  REAL    NOT NULL DEFAULT 0
        )
    ''')

    # ── Tabla: Movimientos de stock (entrada/salida/merma) ────
    c.execute('''
        CREATE TABLE IF NOT EXISTS movimientos_stock (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha             TEXT    NOT NULL,
            tipo              TEXT    NOT NULL,   -- 'entrada' | 'salida' | 'merma'
            insumo            TEXT    NOT NULL,
            cantidad          REAL    NOT NULL,
            motivo            TEXT    DEFAULT '',
            referencia_venta  INTEGER DEFAULT NULL
        )
    ''')

    # ── Tabla: Configuración general ──────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    ''')

    # 🛡️ CARGA SEGURA: Solo inserta los productos por defecto si NO existen
    productos_default = [
        ('Espresso',         1500.0, 'cafe',   18.0),
        ('Cortado',          1700.0, 'cafe',   18.0),
        ('Café con Leche',   2000.0, 'cafe',   18.0),
        ('Cappuccino',       2200.0, 'cafe',   18.0),
        ('Americano',        1800.0, 'cafe',   18.0),
        ('Latte',            2500.0, 'cafe',   18.0),
        ('Medialunas x2',    1200.0, 'comida',  0.0),
        ('Tostado Jamón',    2200.0, 'comida',  0.0),
        ('Agua Mineral',      800.0, 'bebida',  0.0),
        ('Jugo de Naranja',  1500.0, 'bebida',  0.0),
    ]
    for p in productos_default:
        c.execute('SELECT id FROM productos WHERE nombre = ?', (p[0],))
        if not c.fetchone():
            c.execute('''
                INSERT INTO productos (nombre, precio, categoria, cafe_molido_g)
                VALUES (?, ?, ?, ?)
            ''', p)

    # ── Datos iniciales: Stock por defecto ────────────────────
    stock_default = [
        ('Café Molido', 1000.0, 'g',   200.0),
        ('Leche',       5000.0, 'ml', 1000.0),
        ('Azúcar',      2000.0, 'g',   500.0),
        ('Almíbar',      500.0, 'ml',  100.0),
    ]
    for s in stock_default:
        c.execute('''
            INSERT OR IGNORE INTO stock (insumo, cantidad_actual, unidad, cantidad_alerta)
            VALUES (?, ?, ?, ?)
        ''', s)

    # ── Datos iniciales: Configuración ───────────────────────
    config_default = [
        ('ticket_counter',  '1'),
        ('nombre_local',    'Coffee App OS'),
        ('direccion_local', 'Tu dirección aquí'),
        ('telefono_local',  ''),
        ('ancho_ticket_mm', '80'),
    ]
    for k, v in config_default:
        c.execute('INSERT OR IGNORE INTO config (clave, valor) VALUES (?, ?)', (k, v))

    conn.commit()
    conn.close()


# =============================================================
# PRODUCTOS
# =============================================================

def get_productos_activos():
    """Retorna todos los productos activos, ordenados por categoría."""
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM productos WHERE activo = 1 ORDER BY categoria, nombre'
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_todos_productos():
    """Retorna todos los productos (activos e inactivos)."""
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM productos ORDER BY categoria, nombre'
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def agregar_producto(nombre, precio, categoria, cafe_molido_g):
    """Inserta un nuevo producto en la base de datos."""
    conn = get_connection()
    conn.execute(
        'INSERT INTO productos (nombre, precio, categoria, cafe_molido_g) VALUES (?, ?, ?, ?)',
        (nombre, precio, categoria, cafe_molido_g)
    )
    conn.commit()
    conn.close()


def actualizar_producto(producto_id, nombre, precio, categoria, cafe_molido_g, activo):
    """Actualiza los datos de un producto existente."""
    conn = get_connection()
    conn.execute(
        'UPDATE productos SET nombre=?, precio=?, categoria=?, cafe_molido_g=?, activo=? WHERE id=?',
        (nombre, precio, categoria, cafe_molido_g, activo, producto_id)
    )
    conn.commit()
    conn.close()


def eliminar_producto(producto_id):
    """Elimina un producto de la base de datos."""
    conn = get_connection()
    conn.execute('DELETE FROM productos WHERE id = ?', (producto_id,))
    conn.commit()
    conn.close()


# =============================================================
# VENTAS
# =============================================================

def _get_siguiente_ticket():
    """Obtiene y auto-incrementa el contador de tickets. Uso interno."""
    conn = get_connection()
    row = conn.execute("SELECT valor FROM config WHERE clave = 'ticket_counter'").fetchone()
    num = int(row['valor'])
    conn.execute("UPDATE config SET valor = ? WHERE clave = 'ticket_counter'", (str(num + 1),))
    conn.commit()
    conn.close()
    return num


def registrar_venta(tipo_consumo, metodo_pago, items, notas=""):
    """Registra una venta completa: cabecera + ítems + descuento de stock."""
    now     = datetime.now()
    fecha   = now.strftime('%Y-%m-%d')
    hora    = now.strftime('%H:%M:%S')

    subtotal   = sum(i['cantidad'] * i['precio_unitario'] for i in items)
    total      = subtotal
    ticket_num = _get_siguiente_ticket()

    conn = get_connection()
    c    = conn.cursor()

    c.execute('''
        INSERT INTO ventas (fecha, hora, tipo_consumo, metodo_pago, subtotal, total, ticket_num, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fecha, hora, tipo_consumo, metodo_pago, subtotal, total, ticket_num, notas))
    venta_id = c.lastrowid

    for item in items:
        subtotal_item = item['cantidad'] * item['precio_unitario']
        c.execute('''
            INSERT INTO detalle_ventas
                (venta_id, producto_id, nombre_producto, cantidad,
                 precio_unitario, subtotal_item, almibar_extra)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            venta_id, item['producto_id'], item['nombre_producto'],
            item['cantidad'], item['precio_unitario'],
            subtotal_item, int(item.get('almibar_extra', False))
        ))

    conn.commit()
    conn.close()

    _descontar_cafe(items, venta_id, fecha, hora)

    return venta_id, ticket_num, subtotal, total


def _descontar_cafe(items, venta_id, fecha, hora):
    """Descuenta café molido según gramaje configurado en cada producto."""
    conn = get_connection()
    total_gramos = 0.0

    for item in items:
        g_por_unidad = item.get('cafe_molido_g', 0)
        if g_por_unidad and g_por_unidad > 0:
            total_gramos += g_por_unidad * item['cantidad']

    if total_gramos > 0:
        conn.execute(
            "UPDATE stock SET cantidad_actual = MAX(0, cantidad_actual - ?) WHERE insumo = 'Café Molido'",
            (total_gramos,)
        )
        conn.execute('''
            INSERT INTO movimientos_stock (fecha, tipo, insumo, cantidad, motivo, referencia_venta)
            VALUES (?, 'salida', 'Café Molido', ?, 'Venta', ?)
        ''', (f'{fecha} {hora}', total_gramos, venta_id))
        conn.commit()
    conn.close()


def get_ventas_hoy():
    """Retorna todas las ventas del día con sus ítems concatenados."""
    hoy = date.today().strftime('%Y-%m-%d')
    conn = get_connection()
    rows = conn.execute('''
        SELECT v.*,
               GROUP_CONCAT(dv.nombre_producto || ' x' || dv.cantidad, ', ') AS items_str
        FROM ventas v
        LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
        WHERE v.fecha = ?
        GROUP BY v.id
        ORDER BY v.hora DESC
    ''', (hoy,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_detalle_venta(venta_id):
    """Retorna cabecera y ítems de una venta por ID."""
    conn = get_connection()
    venta  = conn.execute('SELECT * FROM ventas WHERE id = ?', (venta_id,)).fetchone()
    items  = conn.execute('SELECT * FROM detalle_ventas WHERE venta_id = ?', (venta_id,)).fetchall()
    conn.close()
    return (dict(venta) if venta else None), [dict(i) for i in items]


# =============================================================
# STOCK
# =============================================================

def get_stock():
    """Retorna el stock actual de todos los insumos."""
    conn = get_connection()
    rows = conn.execute('SELECT * FROM stock ORDER BY insumo').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stock_bajo():
    """Retorna los insumos con stock ≤ umbral de alerta."""
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM stock WHERE cantidad_actual <= cantidad_alerta ORDER BY insumo'
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def actualizar_stock(insumo, cantidad_agregar, motivo="Carga de stock"):
    """Suma cantidad al stock de un insumo y registra el movimiento."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_connection()
    conn.execute(
        'UPDATE stock SET cantidad_actual = cantidad_actual + ? WHERE insumo = ?',
        (cantidad_agregar, insumo)
    )
    conn.execute('''
        INSERT INTO movimientos_stock (fecha, tipo, insumo, cantidad, motivo)
        VALUES (?, 'entrada', ?, ?, ?)
    ''', (now, insumo, cantidad_agregar, motivo))
    conn.commit()
    conn.close()


def actualizar_umbral_stock(insumo, nuevo_umbral):
    """Actualiza el umbral de alerta de un insumo."""
    conn = get_connection()
    conn.execute('UPDATE stock SET cantidad_alerta = ? WHERE insumo = ?', (nuevo_umbral, insumo))
    conn.commit()
    conn.close()


def registrar_merma(insumo, cantidad, motivo):
    """Descuenta una merma del stock y la registra como movimiento tipo 'merma'."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_connection()
    conn.execute(
        'UPDATE stock SET cantidad_actual = MAX(0, cantidad_actual - ?) WHERE insumo = ?',
        (cantidad, insumo)
    )
    conn.execute('''
        INSERT INTO movimientos_stock (fecha, tipo, insumo, cantidad, motivo)
        VALUES (?, 'merma', ?, ?, ?)
    ''', (now, insumo, cantidad, motivo))
    conn.commit()
    conn.close()


def get_mermas(dias=7):
    """Retorna el historial de mermas de los últimos N días."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT * FROM movimientos_stock
        WHERE tipo = 'merma'
          AND date(fecha) >= date('now', ? || ' days')
        ORDER BY fecha DESC
    ''', (f'-{dias}',)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_historial_stock(insumo=None, limite=50):
    """Retorna el historial de movimientos de stock."""
    conn = get_connection()
    if insumo:
        rows = conn.execute('''
            SELECT * FROM movimientos_stock WHERE insumo = ?
            ORDER BY fecha DESC LIMIT ?
        ''', (insumo, limite)).fetchall()
    else:
        rows = conn.execute('''
            SELECT * FROM movimientos_stock ORDER BY fecha DESC LIMIT ?
        ''', (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =============================================================
# MÉTRICAS / DASHBOARD
# =============================================================

def get_resumen_hoy():
    """Retorna métricas clave del día actual."""
    hoy = date.today().strftime('%Y-%m-%d')
    conn = get_connection()

    row = conn.execute('''
        SELECT COUNT(*) AS cantidad, COALESCE(SUM(total), 0) AS total
        FROM ventas WHERE fecha = ?
    ''', (hoy,)).fetchone()

    cantidad        = row['cantidad']
    total           = row['total']
    ticket_promedio = total / cantidad if cantidad > 0 else 0

    mas_vendido = conn.execute('''
        SELECT dv.nombre_producto, SUM(dv.cantidad) AS total_vendido
        FROM detalle_ventas dv
        JOIN ventas v ON dv.venta_id = v.id
        WHERE v.fecha = ?
        GROUP BY dv.nombre_producto
        ORDER BY total_vendido DESC
        LIMIT 1
    ''', (hoy,)).fetchone()

    almibar_row = conn.execute('''
        SELECT COALESCE(SUM(dv.almibar_extra * dv.cantidad), 0) AS total_almibar
        FROM detalle_ventas dv
        JOIN ventas v ON dv.venta_id = v.id
        WHERE v.fecha = ?
    ''', (hoy,)).fetchone()

    conn.close()

    return {
        'cantidad_ventas':       cantidad,
        'total_ventas':          total,
        'ticket_promedio':       ticket_promedio,
        'producto_mas_vendido':  dict(mas_vendido) if mas_vendido else None,
        'almibares_extra':       int(almibar_row['total_almibar']) if almibar_row else 0,
    }


def get_ventas_por_hora(fecha=None):
    """Agrupa ventas por hora para el gráfico de Horas Pico."""
    if fecha is None:
        fecha = date.today().strftime('%Y-%m-%d')
    conn = get_connection()
    rows = conn.execute('''
        SELECT CAST(SUBSTR(hora, 1, 2) AS INTEGER) AS hora_num,
               COUNT(*)      AS cantidad,
               SUM(total)    AS monto_total
        FROM ventas
        WHERE fecha = ?
        GROUP BY hora_num
        ORDER BY hora_num
    ''', (fecha,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_resumen_por_fecha(fecha_str: str) -> dict:
    """Retorna métricas clave para una fecha específica (YYYY-MM-DD)."""
    conn = get_connection()

    row = conn.execute('''
        SELECT COUNT(*) AS cantidad, COALESCE(SUM(total), 0) AS total
        FROM ventas WHERE fecha = ?
    ''', (fecha_str,)).fetchone()

    cantidad        = row['cantidad']
    total           = row['total']
    ticket_promedio = total / cantidad if cantidad > 0 else 0

    mas_vendido = conn.execute('''
        SELECT dv.nombre_producto, SUM(dv.cantidad) AS total_vendido
        FROM detalle_ventas dv
        JOIN ventas v ON dv.venta_id = v.id
        WHERE v.fecha = ?
        GROUP BY dv.nombre_producto
        ORDER BY total_vendido DESC
        LIMIT 1
    ''', (fecha_str,)).fetchone()

    almibar_row = conn.execute('''
        SELECT COALESCE(SUM(dv.almibar_extra * dv.cantidad), 0) AS total_almibar
        FROM detalle_ventas dv
        JOIN ventas v ON dv.venta_id = v.id
        WHERE v.fecha = ?
    ''', (fecha_str,)).fetchone()

    conn.close()
    return {
        'cantidad_ventas':      cantidad,
        'total_ventas':         total,
        'ticket_promedio':      ticket_promedio,
        'producto_mas_vendido': dict(mas_vendido) if mas_vendido else None,
        'almibares_extra':      int(almibar_row['total_almibar']) if almibar_row else 0,
    }


def get_ventas_por_fecha(fecha_str: str) -> list:
    """Retorna todas las ventas de una fecha específica con ítems."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT v.*,
               GROUP_CONCAT(dv.nombre_producto || ' x' || dv.cantidad, ', ') AS items_str
        FROM ventas v
        LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
        WHERE v.fecha = ?
        GROUP BY v.id
        ORDER BY v.hora DESC
    ''', (fecha_str,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_productos_por_fecha(fecha_str: str) -> list:
    """Retorna ranking de productos vendidos en una fecha con cantidad y monto."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT dv.nombre_producto,
               SUM(dv.cantidad)      AS unidades,
               SUM(dv.subtotal_item) AS monto_total,
               SUM(dv.almibar_extra) AS almibares
        FROM detalle_ventas dv
        JOIN ventas v ON dv.venta_id = v.id
        WHERE v.fecha = ?
        GROUP BY dv.nombre_producto
        ORDER BY unidades DESC
    ''', (fecha_str,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ventas_por_hora_fecha(fecha_str: str) -> list:
    """Agrupa ventas por hora para una fecha específica."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT CAST(SUBSTR(hora, 1, 2) AS INTEGER) AS hora_num,
               COUNT(*)      AS cantidad,
               SUM(total)    AS monto_total
        FROM ventas
        WHERE fecha = ?
        GROUP BY hora_num
        ORDER BY hora_num
    ''', (fecha_str,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_fechas_con_ventas(limite=30) -> list:
    """Retorna las últimas N fechas que tuvieron al menos una venta."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT DISTINCT fecha FROM ventas
        ORDER BY fecha DESC
        LIMIT ?
    ''', (limite,)).fetchall()
    conn.close()
    return [r['fecha'] for r in rows]


def get_ventas_ultimos_dias(dias=7):
    """Retorna totales agrupados por día para los últimos N días."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT fecha,
               COUNT(*)   AS cantidad,
               SUM(total) AS monto_total
        FROM ventas
        WHERE date(fecha) >= date('now', ? || ' days')
        GROUP BY fecha
        ORDER BY fecha
    ''', (f'-{dias}',)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =============================================================
# CONFIGURACIÓN
# =============================================================

def get_config(clave):
    """Lee un valor de configuración. Retorna '' si no existe."""
    conn = get_connection()
    row  = conn.execute('SELECT valor FROM config WHERE clave = ?', (clave,)).fetchone()
    conn.close()
    return row['valor'] if row else ''


def set_config(clave, valor):
    """Guarda o actualiza un valor de configuración."""
    conn = get_connection()
    conn.execute('INSERT OR REPLACE INTO config (clave, valor) VALUES (?, ?)', (clave, str(valor)))
    conn.commit()
    conn.close()
