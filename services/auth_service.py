import requests


class AuthService:
    _fk_cache = {}

    def __init__(self):
        from config import API_BASE_URL
        self.base_url = API_BASE_URL

    # ── Descubrimiento dinámico de PK/FK ──────────────────────────────────────

    def _obtener_estructura(self, tabla):
        cache_key = f"estructura_{tabla}"
        if cache_key in self._fk_cache:
            return self._fk_cache[cache_key]
        try:
            r = requests.get(f"{self.base_url}/api/estructuras/{tabla}/modelo", timeout=5)
            if r.ok:
                datos = r.json().get("datos", [])
                self._fk_cache[cache_key] = datos
                return datos
        except Exception:
            pass
        return []

    def _obtener_pk(self, tabla):
        cache_key = f"pk_{tabla}"
        if cache_key in self._fk_cache:
            return self._fk_cache[cache_key]
        for col in self._obtener_estructura(tabla):
            if col.get("is_primary_key") in ("YES", True, "true", 1):
                self._fk_cache[cache_key] = col["column_name"]
                return col["column_name"]
        defaults = {"usuario": "id", "rol": "id", "ruta": "id",
                    "rol_usuario": "usuario_id", "rutarol": "id"}
        return defaults.get(tabla, "id")

    def _obtener_fk(self, tabla_origen, tabla_destino):
        cache_key = f"{tabla_origen}->{tabla_destino}"
        if cache_key in self._fk_cache:
            return self._fk_cache[cache_key]
        for col in self._obtener_estructura(tabla_origen):
            fk_table = col.get("foreign_table_name", "") or ""
            if not fk_table:
                constraint = col.get("fk_constraint_name", "") or ""
                if tabla_destino.lower() in constraint.lower():
                    fk_table = tabla_destino
            if fk_table.lower() == tabla_destino.lower():
                self._fk_cache[cache_key] = col["column_name"]
                return col["column_name"]
        defaults = {
            "rol_usuario->usuario": "usuario_id",
            "rol_usuario->rol":     "rol_id",
            "rutarol->rol":         "fkidrol",
            "rutarol->ruta":        "fkidruta",
        }
        return defaults.get(cache_key)

    # ── Login ──────────────────────────────────────────────────────────────────

    def login(self, email, contrasena):
        print(f"[DEBUG auth_service] login llamado para: {email}")
        """
        Autentica via API C#. Si la API no está disponible, autentica
        directo desde PostgreSQL con bcrypt.
        Retorna (True, dict) o (False, mensaje_error).
        """
        token = ""
        nombre = email
        debe_cambiar = False

        # Intentar autenticar via API C#
        try:
            r = requests.post(
                f"{self.base_url}/api/autenticacion/token",
                json={
                    "tabla": "usuario",
                    "campoUsuario": "email",
                    "campoContrasena": "password",
                    "usuario": email,
                    "contrasena": contrasena
                },
                timeout=10
            )
            if r.ok:
                datos_auth = r.json()
                token = datos_auth.get("token", "")
                nombre = (datos_auth.get("nombre_completo")
                          or datos_auth.get("nombre")
                          or email)
                debe_cambiar = datos_auth.get("debe_cambiar_contrasena", False)
            else:
                try:
                    msg = r.json().get("mensaje", r.text[:200])
                except Exception:
                    msg = r.text[:200]
                return (False, msg)

        except requests.RequestException:
            # API no disponible → autenticar directo con PostgreSQL
            exito, resultado = self._login_postgres(email, contrasena)
            if not exito:
                return (False, resultado)
            nombre = resultado
            token = ""
            debe_cambiar = False

        # Obtener roles, rutas y cédula directo desde PostgreSQL
        roles, rutas, rutas_crud, rutas_editar = self._obtener_roles_postgres(email)
        cedula_docente = self._obtener_cedula_postgres(email)

        print(f"[DEBUG auth_service] roles: {roles}")
        print(f"[DEBUG auth_service] rutas: {rutas}")

        return (True, {
            "token": token,
            "nombre": nombre,
            "roles": roles,
            "rutas_permitidas": rutas,
            "rutas_crud": rutas_crud,
            "rutas_editar": rutas_editar,
            "cedula_docente": cedula_docente,
            "debe_cambiar_contrasena": debe_cambiar,
        })

    # ── Autenticación directo PostgreSQL (fallback sin API C#) ────────────────

    def _login_postgres(self, email, contrasena):
        import psycopg2
        import bcrypt
        from config import DB_CONFIG
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_client_encoding('UTF8')
            cur = conn.cursor()
            cur.execute("""
                SELECT password, nombre_completo, activo
                FROM usuario
                WHERE email = %s
            """, (email,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row:
                return (False, "Usuario no encontrado.")

            hash_bd, nombre, activo = row

            if not activo:
                return (False, "Usuario inactivo.")

            if not bcrypt.checkpw(contrasena.encode('utf-8'), hash_bd.encode('utf-8')):
                return (False, "Contraseña incorrecta.")

            return (True, nombre or email)

        except ImportError:
            return (False, "bcrypt no instalado. Ejecuta: pip install bcrypt")
        except Exception as ex:
            return (False, f"Error de conexión: {ex}")

    # ── Roles y rutas directo PostgreSQL ──────────────────────────────────────

    def _obtener_roles_postgres(self, email):
        import psycopg2
        from config import DB_CONFIG
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_client_encoding('UTF8')
            cur = conn.cursor()

            # Roles
            cur.execute("""
                SELECT r.nombre
                FROM rol r
                JOIN rol_usuario ru ON ru.rol_id = r.id
                JOIN usuario u ON u.id = ru.usuario_id
                WHERE u.email = %s AND r.activo = TRUE
            """, (email,))
            roles = [row[0] for row in cur.fetchall()]

            # Rutas permitidas
            try:
                cur.execute("""
                    SELECT DISTINCT rt.ruta,
                           COALESCE(rr.tipo, 'crud') AS tipo
                    FROM ruta rt
                    JOIN rutarol rr ON rr.fkidruta = rt.id
                    JOIN rol r ON r.id = rr.fkidrol
                    JOIN rol_usuario ru ON ru.rol_id = r.id
                    JOIN usuario u ON u.id = ru.usuario_id
                    WHERE u.email = %s AND r.activo = TRUE
                """, (email,))
                filas = cur.fetchall()
            except Exception:
                cur.execute("""
                    SELECT DISTINCT rt.ruta, 'crud' AS tipo
                    FROM ruta rt
                    JOIN rutarol rr ON rr.fkidruta = rt.id
                    JOIN rol r ON r.id = rr.fkidrol
                    JOIN rol_usuario ru ON ru.rol_id = r.id
                    JOIN usuario u ON u.id = ru.usuario_id
                    WHERE u.email = %s AND r.activo = TRUE
                """, (email,))
                filas = cur.fetchall()

            rutas        = [f[0] for f in filas]
            rutas_crud   = [f[0] for f in filas if f[1] == 'crud']
            rutas_editar = [f[0] for f in filas if f[1] == 'editar']

            cur.close()
            conn.close()
            return (roles, rutas, rutas_crud, rutas_editar)

        except Exception as ex:
            print(f"[AuthService] Error obteniendo roles/rutas: {ex}")
            return ([], [], [], [])

    # ── Cédula del docente vinculado al usuario ───────────────────────────────

    def _obtener_cedula_postgres(self, email):
        import psycopg2
        from config import DB_CONFIG
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.set_client_encoding('UTF8')
            cur = conn.cursor()
            cur.execute("SELECT cedula FROM docente WHERE correo = %s", (email,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return str(row[0]) if row else None
        except Exception:
            return None

    # ── Cambiar contraseña ─────────────────────────────────────────────────────

    def actualizar_contrasena(self, email, nueva_contrasena, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            r = requests.put(
                f"{self.base_url}/api/usuario/email/{email}",
                json={"password": nueva_contrasena},
                params={"camposEncriptar": "password"},
                headers=headers,
                timeout=10
            )
            if r.ok:
                return (True, "Contraseña actualizada correctamente.")
            try:
                msg = r.json().get("mensaje", r.text[:200])
            except Exception:
                msg = r.text[:200]
            return (False, msg)
        except requests.RequestException as ex:
            return (False, f"Error de conexión: {ex}")
