"""
api_proxy.py - Proxy generico para llamadas AJAX desde los templates.

Los templates hacen fetch('/api/tabla/id') en JavaScript.
Este blueprint captura esas rutas y las reenvía a la API REST de C#,
devolviendo el JSON directamente al frontend.
"""

import requests
from flask import Blueprint, jsonify
from config import API_BASE_URL

api_proxy_bp = Blueprint('api_proxy', __name__)


@api_proxy_bp.route('/api/<tabla>/<path:identificador>')
def proxy_get_one(tabla, identificador):
    """Proxy: GET /api/{tabla}/{id} → C# API → JSON al template."""
    try:
        url = f"{API_BASE_URL}/api/{tabla}/{identificador}"
        resp = requests.get(url, timeout=10)
        if not resp.ok:
            return jsonify({}), resp.status_code
        contenido = resp.json()
        # La API C# devuelve {"datos": {...}} o directamente el objeto
        datos = contenido.get("datos") if isinstance(contenido, dict) and "datos" in contenido else contenido
        return jsonify(datos)
    except requests.RequestException as ex:
        return jsonify({"error": str(ex)}), 503


@api_proxy_bp.route('/api/<tabla>')
def proxy_get_all(tabla):
    """Proxy: GET /api/{tabla} → C# API → JSON al template."""
    try:
        url = f"{API_BASE_URL}/api/{tabla}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 204:
            return jsonify([])
        if not resp.ok:
            return jsonify([]), resp.status_code
        contenido = resp.json()
        datos = contenido.get("datos", []) if isinstance(contenido, dict) else contenido
        return jsonify(datos)
    except requests.RequestException as ex:
        return jsonify({"error": str(ex)}), 503
