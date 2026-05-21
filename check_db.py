import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='mapaConocimiento', user='postgres', password='adminsanny')
cur = conn.cursor()

tables = ['usuario', 'rol', 'rol_usuario', 'ruta', 'rutarol']
for table in tables:
    try:
        cur.execute(f'SELECT COUNT(*) FROM {table}')
        count = cur.fetchone()[0]
        print(f'{table}: {count} registros')
        if count > 0:
            cur.execute(f'SELECT * FROM {table} LIMIT 5')
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            print(f'  Columnas: {cols}')
            for row in rows:
                print(f'  {row}')
    except Exception as e:
        print(f'{table}: ERROR - {e}')
        conn.rollback()

cur.close()
conn.close()
