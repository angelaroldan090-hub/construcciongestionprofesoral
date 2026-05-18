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
        # Fallbacks con los nombres REALES de la BD
        defaults = {
            "rol_usuario->usuario": "usuario_id",
            "rol_usuario->rol":     "rol_id",
            "rutarol->rol":         "fkidrol",
            "rutarol->ruta":        "fkidruta",
        }
        return defaults.get(cache_key)

    # ── Login ──────────────────────────────────────────────────────────────────

    def login(self, email, contrasena):
        """
        Retorna (True, dict) con token, nombre, roles, rutas_permitidas,
        debe_cambiar_contrasena — o (False, mensaje_error).
        """
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
        except requests.RequestException as ex:
            return (False, f"Error de conexión con la API: {ex}")

        if not r.ok:
            try:
                msg = r.json().get("mensaje", r.text[:200])
            except Exception:
                msg = r.text[:200]
            return (False, msg)

        datos_auth = r.json()
        token = datos_auth.get("token", "")
        nombre = (datos_auth.get("nombre_completo")
                  or datos_auth.get("nombre")
                  or email)
        debe_cambiar = datos_auth.get("debe_cambiar_contrasena", False)

        roles, rutas = self._obtener_roles_y_rutas(email, token)

        return (True, {
            "token": token,
            "nombre": nombre,
            "roles": roles,
            "rutas_permitidas": rutas,
            "debe_cambiar_contrasena": debe_cambiar,
        })

    def _obtener_roles_y_rutas(self, email, token):
        """Intenta ConsultasController; si falla usa fallback de 5 GETs."""
        pk_usuario    = self._obtener_pk("usuario")    # id
        pk_rol        = self._obtener_pk("rol")        # id
        pk_ruta       = self._obtener_pk("ruta")       # id
        fk_ru_usuario = self._obtener_fk("rol_usuario", "usuario")  # usuario_id
        fk_ru_rol     = self._obtener_fk("rol_usuario", "rol")      # rol_id
        fk_rr_rol     = self._obtener_fk("rutarol", "rol")           # fkidrol
        fk_rr_ruta    = self._obtener_fk("rutarol", "ruta")          # fkidruta

        if all([fk_ru_usuario, fk_ru_rol, fk_rr_rol, fk_rr_ruta]):
            # JOIN por email del usuario (campo único, no la PK entera)
            sql = (
                f"SELECT r.nombre AS nombre_rol, ruta_t.ruta "
                f"FROM usuario u "
                f"JOIN rol_usuario rolu ON u.id = rolu.{fk_ru_usuario} "
                f"JOIN rol r ON rolu.{fk_ru_rol} = r.{pk_rol} "
                f"JOIN rutarol rr ON r.{pk_rol} = rr.{fk_rr_rol} "
                f"JOIN ruta ruta_t ON rr.{fk_rr_ruta} = ruta_t.{pk_ruta} "
                f"WHERE u.email = @email"
            )
            try:
                headers = {"Content-Type": "application/json"}
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                r = requests.post(
                    f"{self.base_url}/api/consultas/ejecutarconsultaparametrizada",
                    json={"consulta": sql, "parametros": {"email": email}},
                    headers=headers,
                    timeout=10
                )
                if r.ok:
                    resultados = r.json().get("resultados", [])
                    roles = list({row["nombre_rol"] for row in resultados})
                    rutas = list({row["ruta"] for row in resultados})
                    return (roles, rutas)
            except Exception:
                pass

        return self._obtener_roles_y_rutas_fallback(email, token)

    def _obtener_roles_y_rutas_fallback(self, email, token):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        def get(tabla):
            try:
                r = requests.get(
                    f"{self.base_url}/api/{tabla}",
                    params={"limite": 999999},
                    headers=headers,
                    timeout=10
                )
                return r.json().get("datos", []) if r.ok else []
            except Exception:
                return []

        todos_ru    = get("rol_usuario")
        todos_roles = get("rol")
        todos_rr    = get("rutarol")
        todos_rutas = get("ruta")

        fk_ru_usuario = self._obtener_fk("rol_usuario", "usuario") or "fkemail"
        fk_ru_rol     = self._obtener_fk("rol_usuario", "rol")     or "fkidrol"
        fk_rr_rol     = self._obtener_fk("rutarol", "rol")         or "fkidrol"
        fk_rr_ruta    = self._obtener_fk("rutarol", "ruta")        or "fkidruta"
        pk_rol        = self._obtener_pk("rol")
        pk_ruta       = self._obtener_pk("ruta")

        id_roles_usuario = {
            str(ru[fk_ru_rol])
            for ru in todos_ru
            if str(ru.get(fk_ru_usuario, "")) == str(email)
        }
        rol_by_id = {str(r[pk_rol]): r["nombre"] for r in todos_roles}
        roles = [rol_by_id[rid] for rid in id_roles_usuario if rid in rol_by_id]

        id_rutas = {
            str(rr[fk_rr_ruta])
            for rr in todos_rr
            if str(rr.get(fk_rr_rol, "")) in id_roles_usuario
        }
        ruta_by_id = {str(rt[pk_ruta]): rt["ruta"] for rt in todos_rutas}
        rutas = [ruta_by_id[rid] for rid in id_rutas if rid in ruta_by_id]

        return (roles, rutas)

    # ── Cambiar contraseña ─────────────────────────────────────────────────────

    def actualizar_contrasena(self, email, nueva_contrasena, token=None):
        # Usamos 'email' como campo de búsqueda (es UNIQUE aunque no sea PK)
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
