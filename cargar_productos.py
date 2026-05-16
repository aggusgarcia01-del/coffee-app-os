import sqlite3

conn = sqlite3.connect(r'C:\Users\Usuario\Desktop\cafe\coffee_app.db')
c = conn.cursor()

# Eliminar todos los productos actuales
c.execute('DELETE FROM productos')

# Cargar solo tus productos
productos = [
    ('Ristretto',     1500, 'cafe',   14),
    ('Cappuccino',    2000, 'cafe',   18),
    ('Latte',         2000, 'cafe',   18),
    ('Latte Especial',2500, 'cafe',   18),
    ('Flat White',    2200, 'cafe',   18),
    ('Medialunas',    1000, 'comida',  0),
    ('Tarta de Coco', 1800, 'comida',  0),
]
c.executemany(
    'INSERT INTO productos (nombre, precio, categoria, cafe_molido_g) VALUES (?,?,?,?)',
    productos
)
conn.commit()
conn.close()
print('✅ Productos actualizados correctamente!')
import sqlite3

conn = sqlite3.connect(r'C:\Users\Usuario\Desktop\cafe\coffee_app.db')
c = conn.cursor()

# Eliminar todos los productos actuales
c.execute('DELETE FROM productos')

# Cargar solo tus productos
productos = [
    ('Ristretto',     1500, 'cafe',   14),
    ('Cappuccino',    2000, 'cafe',   18),
    ('Latte',         2000, 'cafe',   18),
    ('Latte Especial',2500, 'cafe',   18),
    ('Flat White',    2200, 'cafe',   18),
    ('Medialunas',    1000, 'comida',  0),
    ('Tarta de Coco', 1800, 'comida',  0),
]
c.executemany(
    'INSERT INTO productos (nombre, precio, categoria, cafe_molido_g) VALUES (?,?,?,?)',
    productos
)
conn.commit()
conn.close()
print('✅ Productos actualizados correctamente!')