import psycopg2

try:
    conn = psycopg2.connect(host='localhost', port=5432, database='mapaConocimiento', user='postgres', password='adminsanny')
    cur = conn.cursor()

    for table in ['ruta', 'rutarol', 'rol_usuario', 'usuario', 'rol']:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        cols = cur.fetchall()
        print(f"\n{table}:")
        for c in cols:
            print(f"  {c}")

    # Also check foreign keys
    cur.execute("""
        SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name IN ('ruta', 'rutarol', 'rol_usuario')
    """)
    fks = cur.fetchall()
    print("\nForeign Keys:")
    for fk in fks:
        print(f"  {fk}")

    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
