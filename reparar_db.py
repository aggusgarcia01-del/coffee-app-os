import sqlite3
import os

# Ruta de tu base de datos
DB_PATH = "coffee_app.db"

def reparar():
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró {DB_PATH}. Asegurate de correr el script en la misma carpeta.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("🛠️ Iniciando reparación de la base de datos...")

    try:
        # 1. Crear una tabla temporal con el esquema CORRECTO (agregando UNIQUE)
        c.execute('''
            CREATE TABLE productos_temp (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre          TEXT    NOT NULL UNIQUE,
                precio          REAL    NOT NULL DEFAULT 0,
                categoria       TEXT    NOT NULL DEFAULT 'cafe',
                cafe_molido_g   REAL    NOT NULL DEFAULT 18,
                activo          INTEGER NOT NULL DEFAULT 1
            )
        ''')

        # 2. Migrar los datos únicos de la tabla vieja a la nueva
        # Usamos GROUP BY nombre para quedarnos con una sola versión de cada producto
        c.execute('''
            INSERT OR IGNORE INTO productos_temp (nombre, precio, categoria, cafe_molido_g, activo)
            SELECT nombre, precio, categoria, cafe_molido_g, activo
            FROM productos
            GROUP BY nombre
        ''')

        # 3. Borrar la tabla vieja y renombrar la nueva
        c.execute("DROP TABLE productos")
        c.execute("ALTER TABLE productos_temp RENAME TO productos")

        conn.commit()
        print("✅ ¡Reparación exitosa! Duplicados eliminados y restricción UNIQUE aplicada.")

    except sqlite3.Error as e:
        print(f"❌ Error durante la reparación: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reparar()