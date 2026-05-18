"""
api_service.py - Servicio generico que consume la API REST.

Contiene los 4 metodos CRUD (Listar, Crear, Actualizar, Eliminar)
que se reutilizan en todos los Blueprints/rutas.
Cada metodo retorna los datos o una tupla (exito, mensaje).
"""

import requests
from config import API_BASE_URL


class APIService:

    def _headers(self):
        """Construye los headers HTTP. Agrega JWT si hay sesión activa."""
        from flask import session as flask_session
        h = {"Content-Type": "application/json"}
        token = flask_session.get("token") if flask_session else None
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    # Mapa de tabla → nombre del campo clave primaria
    # Necesario porque la API genérica usa: PUT /api/{tabla}/{campo}/{valor}
    _PK_MAP = {
        'docente': 'cedula',
        'area_conocimiento': 'id',
        'linea_investigacion': 'id',
        'programa': 'id',
        'red': 'idr',
        'evaluacion_docente': 'id',
        'reconocimiento': 'id',
        'experiencia': 'id',
        'experiecia': 'id',   # typo en la BD (nombre real de la tabla)
        'estudios_realizados': 'id',
        'termino_clave': 'termino',
        'apoyo_profesoral': 'estudios',
        'beca': 'estudios',
    }

    def __init__(self):
        self.base_url = API_BASE_URL

    # ──────────────────────────────────────────────
    # LISTAR: GET /api/{tabla}
    # ──────────────────────────────────────────────
    def listar(self, tabla, limite=None):
        """
        Consulta la API y retorna la lista de registros.
        Si la tabla está vacía (HTTP 204) retorna [] sin errores.
        Si hay otro error, imprime en consola y retorna [].
        """
        try:
            url = f"{self.base_url}/api/{tabla}"
            params = {}
            if limite:
                params['limite'] = limite

            respuesta = requests.get(url, params=params, headers=self._headers())

            # Si la respuesta es 204 (No Content) -> tabla vacía
            if respuesta.status_code == 204:
                return []

            # Si no es 200 (éxito con contenido), imprimir error
            if respuesta.status_code != 200:
                print(f"Error HTTP {respuesta.status_code} al listar {tabla}: {respuesta.text[:200]}")
                return []

            # Intentar decodificar JSON
            try:
                datos_json = respuesta.json()
            except ValueError:
                print(f"Respuesta no JSON al listar {tabla}: {respuesta.text[:200]}")
                return []

            return datos_json.get("datos", [])

        except requests.RequestException as ex:
            print(f"Error de conexión al listar {tabla}: {ex}")
            return []

    # ──────────────────────────────────────────────
    # CREAR: POST /api/{tabla}
    # ──────────────────────────────────────────────
    def crear(self, tabla, datos, campos_encriptar=None):
        """
        Crea un nuevo registro.
        Retorna (exito, mensaje)
        """
        try:
            url = f"{self.base_url}/api/{tabla}"
            params = {}
            if campos_encriptar:
                params['camposEncriptar'] = campos_encriptar

            respuesta = requests.post(url, json=datos, params=params, headers=self._headers())

            # Intentar decodificar JSON
            try:
                contenido = respuesta.json()
            except ValueError:
                print(f"Respuesta no JSON al crear en {tabla}: {respuesta.text[:200]}")
                return (False, "La API devolvió una respuesta inválida.")

            mensaje = contenido.get("mensaje", "Operación completada.")
            return (respuesta.ok, mensaje)

        except requests.RequestException as ex:
            return (False, f"Error de conexión: {ex}")

    # ──────────────────────────────────────────────
    # ACTUALIZAR: PUT /api/{tabla}/{nombre_clave}/{valor_clave}
    # ──────────────────────────────────────────────
    def actualizar(self, tabla, nombre_clave, valor_clave, datos, campos_encriptar=None):
        """
        Actualiza un registro existente.
        Retorna (exito, mensaje)
        """
        try:
            url = f"{self.base_url}/api/{tabla}/{nombre_clave}/{valor_clave}"
            params = {}
            if campos_encriptar:
                params['camposEncriptar'] = campos_encriptar

            respuesta = requests.put(url, json=datos, params=params, headers=self._headers())

            try:
                contenido = respuesta.json()
            except ValueError:
                print(f"Respuesta no JSON al actualizar en {tabla}: {respuesta.text[:200]}")
                return (False, "La API devolvió una respuesta inválida.")

            mensaje = contenido.get("mensaje", "Operación completada.")
            return (respuesta.ok, mensaje)

        except requests.RequestException as ex:
            return (False, f"Error de conexión: {ex}")

    # ──────────────────────────────────────────────
    # EJECUTAR SP: POST /api/procedimientos/ejecutarsp
    # ──────────────────────────────────────────────
    def ejecutar_sp(self, nombre_sp, parametros=None):
        """
        Ejecuta un procedimiento almacenado via la API.
        Retorna (exito, resultado)
        """
        try:
            import json as json_mod
            url = f"{self.base_url}/api/procedimientos/ejecutarsp"

            payload = {"nombreSP": nombre_sp}
            if parametros:
                payload.update(parametros)

            respuesta = requests.post(url, json=payload)

            try:
                contenido = respuesta.json()
            except ValueError:
                return (False, "La API devolvió una respuesta inválida.")

            if not respuesta.ok:
                mensaje = contenido.get("mensaje", "Error al ejecutar el procedimiento.")
                return (False, mensaje)

            resultados = contenido.get("resultados", [])
            if resultados:
                p_resultado = resultados[0].get("p_resultado") or resultados[0].get("@p_resultado")
                if p_resultado is not None:
                    if isinstance(p_resultado, str):
                        return (True, json_mod.loads(p_resultado))
                    return (True, p_resultado)

            return (True, contenido)

        except requests.RequestException as ex:
            return (False, f"Error de conexión: {ex}")
        except Exception as ex:
            return (False, f"Error procesando respuesta: {ex}")

    # ──────────────────────────────────────────────
    # ELIMINAR: DELETE /api/{tabla}/{nombre_clave}/{valor_clave}
    # ──────────────────────────────────────────────
    def eliminar(self, tabla, nombre_clave, valor_clave):
        """
        Elimina un registro.
        Retorna (exito, mensaje)
        """
        try:
            url = f"{self.base_url}/api/{tabla}/{nombre_clave}/{valor_clave}"
            respuesta = requests.delete(url, headers=self._headers())

            try:
                contenido = respuesta.json()
            except ValueError:
                print(f"Respuesta no JSON al eliminar en {tabla}: {respuesta.text[:200]}")
                return (False, "La API devolvió una respuesta inválida.")

            mensaje = contenido.get("mensaje", "Operación completada.")
            return (respuesta.ok, mensaje)

        except requests.RequestException as ex:
            return (False, f"Error de conexión: {ex}")

    # ──────────────────────────────────────────────
    # ALIASES en inglés (usados por los routes)
    # ──────────────────────────────────────────────

    def get_all(self, tabla):
        """Alias de listar()"""
        return self.listar(tabla)

    def get_one(self, tabla, id_valor):
        """GET /api/{tabla}/{id_valor}"""
        try:
            url = f"{self.base_url}/api/{tabla}/{id_valor}"
            respuesta = requests.get(url)
            if respuesta.status_code == 404:
                return None
            if not respuesta.ok:
                print(f"Error HTTP {respuesta.status_code} al obtener {tabla}/{id_valor}")
                return None
            try:
                contenido = respuesta.json()
            except ValueError:
                return None
            # Desempaquetar {"datos": {...}} o {"datos": [{...}]}
            datos = contenido.get("datos") if isinstance(contenido, dict) and "datos" in contenido else contenido
            if isinstance(datos, list):
                return datos[0] if datos else None
            return datos
        except requests.RequestException as ex:
            print(f"Error de conexión al obtener {tabla}/{id_valor}: {ex}")
            return None

    def create(self, tabla, datos, campos_encriptar=None):
        """Alias de crear()"""
        return self.crear(tabla, datos, campos_encriptar)

    def update(self, tabla, id_valor, datos, campos_encriptar=None):
        """PUT /api/{tabla}/{campo}/{id_valor} — usa _PK_MAP para el nombre de columna"""
        try:
            campo = self._PK_MAP.get(tabla, 'id')
            url = f"{self.base_url}/api/{tabla}/{campo}/{id_valor}"
            params = {}
            if campos_encriptar:
                params['camposEncriptar'] = campos_encriptar
            respuesta = requests.put(url, json=datos, params=params)
            try:
                contenido = respuesta.json()
            except ValueError:
                return (False, "La API devolvió una respuesta inválida.")
            mensaje = contenido.get("mensaje", "Operación completada.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexión: {ex}")

    def delete(self, tabla, id_valor):
        """DELETE /api/{tabla}/{campo}/{id_valor} — usa _PK_MAP para el nombre de columna"""
        try:
            campo = self._PK_MAP.get(tabla, 'id')
            url = f"{self.base_url}/api/{tabla}/{campo}/{id_valor}"
            respuesta = requests.delete(url)
            try:
                contenido = respuesta.json()
            except ValueError:
                return (False, "La API devolvió una respuesta inválida.")
            mensaje = contenido.get("mensaje", "Operación completada.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexión: {ex}")

    # ──────────────────────────────────────────────
    # Métodos para claves compuestas y relaciones
    # ──────────────────────────────────────────────

    def update_docente_departamento(self, cedula, departamento, datos):
        return self.actualizar('docente_departamento', 'cedula', cedula, datos)

    def delete_docente_departamento(self, cedula, departamento):
        return self.eliminar('docente_departamento', 'cedula', cedula)

    def update_red_docente(self, red, docente, datos):
        return self.actualizar('red_docente', 'id_red', red, datos)

    def get_red_docente(self, red, docente):
        return self.get_one('red_docente', f"{red}/{docente}")

    def delete_red_docente(self, red, docente):
        return self.eliminar('red_docente', 'id_red', red)

    def delete_estudio_ac(self, estudio, area_conocimiento):
        return self.eliminar('estudio_ac', 'id_estudio', estudio)

    def get_estudios_by_docente(self, cedula):
        return self.listar(f"estudios_realizados/docente/{cedula}")

    def get_areas_by_estudio(self, id_estudio):
        return self.listar(f"estudio_ac/estudio/{id_estudio}")

    def asignar_estudio(self, datos):
        return self.crear('docentes_estudios', datos)

    def eliminar_asignacion_estudio(self, docente, estudio):
        return self.eliminar('docentes_estudios', 'cedula_docente', docente)

    def asignar_area_a_estudio(self, datos):
        return self.crear('estudio_ac', datos)

    def eliminar_area_de_estudio(self, estudio, area):
        return self.eliminar('estudio_ac', 'id_estudio', estudio)

    # ──────────────────────────────────────────────
    # LLAMAR SP: invoca una función PostgreSQL directo
    # ──────────────────────────────────────────────

    def llamar_sp(self, nombre_funcion, params: list):
        """
        Llama una función PostgreSQL vía psycopg2.
        Retorna (exito: bool, resultado).
        - exito=True  → resultado es el JSONB devuelto (dict o list)
        - exito=False → resultado es un mensaje de error (str)
        """
        import psycopg2
        from config import DB_CONFIG
        try:
            db_config = {**DB_CONFIG, 'client_encoding': 'UTF8'}
            conn = psycopg2.connect(**db_config)
            cur = conn.cursor()
            placeholders = ', '.join(['%s'] * len(params))
            cur.execute(f"SELECT * FROM {nombre_funcion}({placeholders})", params)
            row = cur.fetchone()
            resultado = row[0] if row else {}
            conn.commit()
            cur.close()
            conn.close()
            if isinstance(resultado, dict) and 'error' in resultado:
                return (False, resultado['error'])
            return (True, resultado)
        except UnicodeDecodeError as ex:
            # Manejo específico para errores de codificación
            return (False, f"Error de codificación en los datos de la BD: {str(ex)}")
        except Exception as ex:
            return (False, str(ex))