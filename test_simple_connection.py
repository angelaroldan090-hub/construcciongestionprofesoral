"""
test_simple_connection.py - Test simple de conexión sin queries
"""

import psycopg2
from config import DB_CONFIG

print("🔍 Intentando conexión básica sin queries...")

try:
    conn = psycopg2.connect(**DB_CONFIG, client_encoding='UTF8')
    print("✅ Conexión establecida")
    
    cur = conn.cursor()
    print("✅ Cursor creado")
    
    # Query más simple posible
    cur.execute("SELECT 1;")
    result = cur.fetchone()
    print(f"✅ Query simple exitosa: {result}")
    
    cur.close()
    conn.close()
    print("✅ Desconectado")
    
except UnicodeDecodeError as ue:
    print(f"❌ UnicodeDecodeError: {ue}")
    print(f"   Posición del error: {ue.start}-{ue.end}")
    print(f"   Bytes problemáticos: {ue.object[max(0, ue.start-10):ue.end+10]}")
except psycopg2.Error as pe:
    print(f"❌ PostgreSQL Error: {pe}")
    print(f"   Tipo: {type(pe).__name__}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"   Tipo: {type(e).__name__}")
    import traceback
    traceback.print_exc()
