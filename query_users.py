import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='mapaConocimiento', user='postgres', password='adminsanny')
cur = conn.cursor()

cur.execute("""
    SELECT u.id, u.username, u.email, u.nombre_completo, u.activo,
           u.debe_cambiar_contrasena,
           LEFT(u.password, 10) AS pass_prefix,
           string_agg(r.nombre, ', ') AS roles
    FROM usuario u
    LEFT JOIN rol_usuario ru ON u.id = ru.usuario_id
    LEFT JOIN rol r ON ru.rol_id = r.id
    GROUP BY u.id, u.username, u.email, u.nombre_completo, u.activo, u.debe_cambiar_contrasena, u.password
    ORDER BY u.id
""")
rows = cur.fetchall()
cols = [d[0] for d in cur.description]
print(cols)
for r in rows:
    print(r)

cur.close()
conn.close()
