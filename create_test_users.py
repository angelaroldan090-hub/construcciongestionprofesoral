import psycopg2
import bcrypt

try:
    conn = psycopg2.connect(host='localhost', port=5432, database='mapaConocimiento', user='postgres', password='adminsanny')
    cur = conn.cursor()

    # Test users: (username, email, nombre_completo, plaintext_password, rol_nombre)
    test_users = [
        ('test_admin',    'test_admin@test.com',    'Test Administrador', 'Admin123',    'ADMINISTRADOR'),
        ('test_docente',  'test_docente@test.com',  'Test Docente',       'Docente123',  'DOCENTE'),
        ('test_invitado', 'test_invitado@test.com', 'Test Invitado',      'Invitado123', 'INVITADO'),
    ]

    # Get role IDs
    cur.execute("SELECT id, nombre FROM rol")
    roles = {r[1]: r[0] for r in cur.fetchall()}
    print(f"Roles disponibles: {roles}")

    for username, email, nombre, password, rol_nombre in test_users:
        # Check if user already exists
        cur.execute("SELECT id FROM usuario WHERE email = %s", (email,))
        existing = cur.fetchone()
        if existing:
            cur.execute("DELETE FROM rol_usuario WHERE usuario_id = %s", (existing[0],))
            cur.execute("DELETE FROM usuario WHERE id = %s", (existing[0],))

        # Hash password with BCrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')

        # Insert user
        cur.execute("""
            INSERT INTO usuario (username, email, nombre_completo, password, activo, debe_cambiar_contrasena)
            VALUES (%s, %s, %s, %s, true, false)
            RETURNING id
        """, (username, email, nombre, hashed))
        user_id = cur.fetchone()[0]

        # Assign role
        rol_id = roles.get(rol_nombre)
        if rol_id:
            cur.execute("INSERT INTO rol_usuario (usuario_id, rol_id) VALUES (%s, %s)", (user_id, rol_id))

        print(f"  ✓ {username} | email: {email} | password: {password} | rol: {rol_nombre}")

    conn.commit()
    print("\nUsuarios de prueba creados exitosamente.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
