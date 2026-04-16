"""
api_service.py - Servicio generico que consume la API REST.
Incluye métodos para manejar claves primarias compuestas.
"""

import requests
from config import API_BASE_URL


def _parsear_respuesta(respuesta):
    """
    Intenta parsear el JSON de la respuesta.
    Si la respuesta está vacía o no es JSON válido, retorna un dict vacío.
    """
    try:
        if respuesta.text.strip():
            return respuesta.json()
        return {}
    except Exception:
        return {}


class ApiService:

    def __init__(self):
        self.base_url = API_BASE_URL

    def listar(self, tabla, limite=None):
        try:
            url = f"{self.base_url}/api/{tabla}"
            params = {}
            if limite:
                params['limite'] = limite
            respuesta = requests.get(url, params=params)
            datos_json = _parsear_respuesta(respuesta)
            return datos_json.get("datos", [])
        except requests.RequestException as ex:
            print(f"Error al listar {tabla}: {ex}")
            return []

    def crear(self, tabla, datos, campos_encriptar=None):
        try:
            url = f"{self.base_url}/api/{tabla}"
            params = {}
            if campos_encriptar:
                params['camposEncriptar'] = campos_encriptar
            respuesta = requests.post(url, json=datos, params=params)
            contenido = _parsear_respuesta(respuesta)
            mensaje = contenido.get("mensaje", "Operación completada.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")

    def actualizar(self, tabla, nombre_clave, valor_clave, datos, campos_encriptar=None):
        try:
            url = f"{self.base_url}/api/{tabla}/{nombre_clave}/{valor_clave}"
            params = {}
            if campos_encriptar:
                params['camposEncriptar'] = campos_encriptar
            respuesta = requests.put(url, json=datos, params=params)
            contenido = _parsear_respuesta(respuesta)
            mensaje = contenido.get("mensaje", "Registro actualizado exitosamente." if respuesta.ok else "Error en la operación.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")

    def eliminar(self, tabla, nombre_clave, valor_clave):
        try:
            url = f"{self.base_url}/api/{tabla}/{nombre_clave}/{valor_clave}"
            respuesta = requests.delete(url)
            contenido = _parsear_respuesta(respuesta)
            mensaje = contenido.get("mensaje", "Registro eliminado exitosamente." if respuesta.ok else "Error en la operación.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")

    # ========== MÉTODOS PARA CLAVES PRIMARIAS COMPUESTAS ==========

    def actualizar_compuesta(self, tabla, claves, valores, datos):
        try:
            params = '&'.join([f"{clave}={valor}" for clave, valor in zip(claves, valores)])
            url = f"{self.base_url}/api/{tabla}?{params}"
            respuesta = requests.put(url, json=datos)
            contenido = _parsear_respuesta(respuesta)
            mensaje = contenido.get("mensaje", "Registro actualizado exitosamente." if respuesta.ok else "Error en la operación.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")

    def eliminar_compuesta(self, tabla, claves, valores):
        try:
            params = '&'.join([f"{clave}={valor}" for clave, valor in zip(claves, valores)])
            url = f"{self.base_url}/api/{tabla}?{params}"
            respuesta = requests.delete(url)
            contenido = _parsear_respuesta(respuesta)
            mensaje = contenido.get("mensaje", "Registro eliminado exitosamente." if respuesta.ok else "Error en la operación.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")

    def eliminar_compuesta_bd(self, tabla, filtros):
        """Elimina directamente en PostgreSQL para claves compuestas"""
        import psycopg2
        from config import DB_CONFIG
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            condiciones = ' AND '.join([f'"{k}" = %s' for k in filtros.keys()])
            sql = f'DELETE FROM public."{tabla}" WHERE {condiciones}'
            cur.execute(sql, list(filtros.values()))
            filas = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            return (filas > 0, "Registro eliminado exitosamente." if filas > 0 else "No se encontró el registro.")
        except Exception as ex:
            return (False, f"Error al eliminar: {ex}")

    def ejecutar_procedimiento(self, nombre_proc, parametros):
        try:
            placeholders = ','.join(['%s'] * len(parametros))
            query = f"CALL public.{nombre_proc}({placeholders}, NULL)"
            self.cursor.execute(query, parametros)
            mensaje = self.cursor.fetchone()
            self.conn.commit()
            return True, mensaje[0] if mensaje else "Ejecutado correctamente"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def listar_vinculaciones_docente(self, docente_id):
        try:
            registros = self.listar('docente_departamento')
            return [r for r in registros if str(r.get('docente')) == str(docente_id)]
        except Exception as e:
            print(f"Error al listar vinculaciones de docente: {e}")
            return []

    def listar_alianzas_aliado(self, aliado_id):
        try:
            registros = self.listar('alianza')
            return [r for r in registros if str(r.get('aliado')) == str(aliado_id)]
        except Exception as e:
            print(f"Error al listar alianzas de aliado: {e}")
            return []