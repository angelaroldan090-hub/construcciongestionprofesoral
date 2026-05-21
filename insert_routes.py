import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='mapaConocimiento', user='postgres', password='adminsanny')
cur = conn.cursor()

# ── 1. Insertar rutas ─────────────────────────────────────────────────────────
rutas = [
    ('/docentes_estudios', 'Docentes y Estudios'),
    ('/area',              'Áreas de Conocimiento'),
    ('/termino',           'Términos Clave'),
    ('/linea',             'Líneas de Investigación'),
    ('/programa',          'Programas'),
    ('/red',               'Redes'),
    ('/evaluacion',        'Evaluaciones Docente'),
    ('/reconocimiento',    'Reconocimientos'),
    ('/experiencia',       'Experiencia'),
    ('/red_docente',       'Redes Docentes'),
    ('/apoyo',             'Apoyo Profesoral'),
    ('/beca',              'Becas'),
    ('/docente_departamento', 'Docente Departamento'),
    ('/estudio_ac',        'Estudios AC'),
]

cur.execute("SELECT ruta FROM ruta")
existing = {r[0] for r in cur.fetchall()}

inserted_rutas = []
for ruta, desc in rutas:
    if ruta not in existing:
        cur.execute("INSERT INTO ruta (ruta, descripcion) VALUES (%s, %s) RETURNING id", (ruta, desc))
        rid = cur.fetchone()[0]
        inserted_rutas.append((rid, ruta))
        print(f"  INSERT ruta id={rid}: {ruta}")
    else:
        cur.execute("SELECT id FROM ruta WHERE ruta = %s", (ruta,))
        rid = cur.fetchone()[0]
        inserted_rutas.append((rid, ruta))
        print(f"  EXISTS ruta id={rid}: {ruta}")

# ── 2. Obtener IDs de roles ───────────────────────────────────────────────────
cur.execute("SELECT id, nombre FROM rol ORDER BY id")
roles = {row[1]: row[0] for row in cur.fetchall()}
print(f"\nRoles: {roles}")

# ── 3. Obtener mapa ruta->id ──────────────────────────────────────────────────
ruta_id = {ruta: rid for rid, ruta in inserted_rutas}

# ── 4. Definir asignaciones por rol ──────────────────────────────────────────
todas = [r for _, r in inserted_rutas]

asignaciones = {
    'ADMINISTRADOR':         todas,
    'COORDINADOR_PROFESORAL': todas,
    'DOCENTE':               ['/docentes_estudios', '/experiencia', '/reconocimiento',
                               '/evaluacion', '/apoyo', '/beca'],
    'DECANO':                todas,
    'INVITADO':              ['/docentes_estudios'],
}

# ── 5. Insertar rutarol ───────────────────────────────────────────────────────
cur.execute("SELECT fkidrol, fkidruta FROM rutarol")
existing_rr = set(cur.fetchall())
count = 0
for nombre_rol, rutas_del_rol in asignaciones.items():
    id_rol = roles.get(nombre_rol)
    if id_rol is None:
        print(f"  ROL NO ENCONTRADO: {nombre_rol}")
        continue
    for ruta in rutas_del_rol:
        id_ruta = ruta_id.get(ruta)
        if id_ruta and (id_rol, id_ruta) not in existing_rr:
            cur.execute("INSERT INTO rutarol (fkidrol, fkidruta) VALUES (%s, %s)", (id_rol, id_ruta))
            count += 1

conn.commit()
print(f"\n✓ {len(inserted_rutas)} rutas procesadas, {count} asignaciones rutarol insertadas")

# ── 6. Verificación final ─────────────────────────────────────────────────────
print("\nVerificación:")
cur.execute("SELECT COUNT(*) FROM ruta")
print(f"  ruta: {cur.fetchone()[0]} registros")
cur.execute("SELECT COUNT(*) FROM rutarol")
print(f"  rutarol: {cur.fetchone()[0]} registros")

cur.execute("""
    SELECT ro.nombre AS rol, rt.ruta
    FROM rutarol rr
    JOIN rol ro ON rr.fkidrol = ro.id
    JOIN ruta rt ON rr.fkidruta = rt.id
    ORDER BY ro.nombre, rt.ruta
""")
print("\nAsignaciones rol → ruta:")
current_rol = None
for rol, ruta in cur.fetchall():
    if rol != current_rol:
        print(f"  {rol}:")
        current_rol = rol
    print(f"    {ruta}")

cur.close()
conn.close()
