"""
config.py - Configuracion centralizada de la aplicacion Flask.

Contiene las constantes que se usan en toda la aplicacion:
la URL de la API y la clave secreta para sesiones/flash.
"""

# ──────────────────────────────────────────────
# URL base de la API REST que consume este frontend.
# La API generica en C# corre en el puerto 5034.
# Se usa en ApiService para construir las URLs de cada peticion HTTP.
# Ejemplo: f"{API_BASE_URL}/api/producto" genera "http://localhost:5034/api/producto"
# ──────────────────────────────────────────────
API_BASE_URL = "http://apiconstrucciongestionprofesoral.runasp.net"

# ──────────────────────────────────────────────
# Clave secreta para el manejo de sesiones y mensajes flash.
# Flask la necesita para firmar las cookies de sesion de forma segura.
# Sin esta clave, flash() lanza un error porque no puede guardar mensajes en la sesion.
# En produccion deberia ser un valor aleatorio largo guardado en variable de entorno.
# ──────────────────────────────────────────────
SECRET_KEY = "clave-secreta-flask-frontend-2024"

# ──────────────────────────────────────────────
# Configuración de conexión directa a PostgreSQL.
# Los valores se leen del archivo .env (no se sube al git).
# ──────────────────────────────────────────────
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'mapaConocimiento'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'adminsanny')
}

# ──────────────────────────────────────────────
# Configuración SMTP para recuperación de contraseña.
# Completar con los datos de Gmail (App Password).
# ──────────────────────────────────────────────
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASS = os.getenv('SMTP_PASS', '')
SMTP_FROM = os.getenv('SMTP_FROM', '')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'apoyo_profesoral'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'client_encoding': 'UTF8'
}