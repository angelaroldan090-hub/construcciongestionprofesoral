import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='mapaConocimiento', user='postgres', password='adminsanny')
cur = conn.cursor()

# Eliminar rutarol de COORDINADOR_PROFESORAL y DECANO
cur.execute("""
    DELETE FROM rutarol
    WHERE fkidrol IN (
        SELECT id FROM rol WHERE nombre IN ('COORDINADOR_PROFESORAL', 'DECANO')
    )
""")
deleted = cur.rowcount
conn.commit()
print(f"Eliminadas {deleted} asignaciones de COORDINADOR_PROFESORAL y DECANO")

# Verificación
cur.execute("""
    SELECT ro.nombre AS rol, COUNT(*) AS rutas
    FROM rutarol rr
    JOIN rol ro ON rr.fkidrol = ro.id
    GROUP BY ro.nombre ORDER BY ro.nombre
""")
print("\nEstado actual de rutarol:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} rutas")

cur.close()
conn.close()
