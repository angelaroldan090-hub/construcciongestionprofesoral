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
        """
        Actualiza un registro con clave primaria compuesta.
        
        Args:
            tabla: nombre de la tabla
            claves: lista de nombres de las columnas que forman la PK (ej: ['red', 'docente'])
            valores: lista de valores correspondientes (ej: [1, 12345678])
            datos: diccionario con los campos a actualizar
        
        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            # Construir URL con los parámetros en la query string
            params = '&'.join([f"{clave}={valor}" for clave, valor in zip(claves, valores)])
            url = f"{self.base_url}/api/{tabla}?{params}"
            
            respuesta = requests.put(url, json=datos)
            contenido = _parsear_respuesta(respuesta)
            mensaje = contenido.get("mensaje", "Registro actualizado exitosamente." if respuesta.ok else "Error en la operación.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")

    def eliminar_compuesta(self, tabla, claves, valores):
        """
        Elimina un registro con clave primaria compuesta.
        
        Args:
            tabla: nombre de la tabla
            claves: lista de nombres de las columnas que forman la PK (ej: ['red', 'docente'])
            valores: lista de valores correspondientes (ej: [1, 12345678])
        
        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            # Construir URL con los parámetros en la query string
            params = '&'.join([f"{clave}={valor}" for clave, valor in zip(claves, valores)])
            url = f"{self.base_url}/api/{tabla}?{params}"
            
            respuesta = requests.delete(url)
            contenido = _parsear_respuesta(respuesta)
            mensaje = contenido.get("mensaje", "Registro eliminado exitosamente." if respuesta.ok else "Error en la operación.")
            return (respuesta.ok, mensaje)
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")