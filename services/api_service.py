"""
api_service.py - Servicio generico que consume la API REST.

Contiene los 4 metodos CRUD (Listar, Crear, Actualizar, Eliminar)
que se reutilizan en todos los Blueprints/rutas.
Cada metodo retorna los datos o una tupla (exito, mensaje).
"""

import requests
from config import API_BASE_URL


class ApiService:
    def _init_(self):
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

            respuesta = requests.get(url, params=params)

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

            respuesta = requests.post(url, json=datos, params=params)

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

            respuesta = requests.put(url, json=datos, params=params)

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
            respuesta = requests.delete(url)

            try:
                contenido = respuesta.json()
            except ValueError:
                print(f"Respuesta no JSON al eliminar en {tabla}: {respuesta.text[:200]}")
                return (False, "La API devolvió una respuesta inválida.")

            mensaje = contenido.get("mensaje", "Operación completada.")
            return (respuesta.ok, mensaje)

        except requests.RequestException as ex:
            return (False, f"Error de conexión: {ex}")