"""
diagnostic_encoding.py - Script para diagnosticar problemas de encoding en la BD
Identifica registros con caracteres problemáticos en UTF-8
"""

import psycopg2
from psycopg2 import sql
from config import DB_CONFIG

def diagnosticar_encoding():
    """Diagnostica problemas de encoding en tablas clave"""
    try:
        # Intentar con diferentes estrategias de encoding
        encodings_to_try = [
            {'client_encoding': 'UTF8'},
            {'client_encoding': 'LATIN1'},
            {}  # Sin especificar (usa configuración por defecto de BD)
        ]
        
        conn = None
        for i, db_config_attempt in enumerate(encodings_to_try):
            try:
                print(f"🔄 Intento {i+1}: Conectando con {db_config_attempt or 'encoding default'}...\n")
                db_config = {**DB_CONFIG, **db_config_attempt}
                conn = psycopg2.connect(**db_config)
                print(f"✅ Conexión exitosa\n")
                break
            except UnicodeDecodeError as e:
                print(f"❌ Error de encoding: {e}\n")
                if conn:
                    conn.close()
                continue
        
        if not conn:
            print("❌ No se pudo conectar con ninguna estrategia de encoding")
            return
        
        cur = conn.cursor()
        
        print("🔍 Diagnosticando encoding en la BD...\n")
        
        # Verificar encoding de la BD
        try:
            cur.execute("SHOW client_encoding;")
            encoding = cur.fetchone()[0]
            print(f"✅ Client encoding: {encoding}")
        except:
            print(f"⚠️  No se pudo obtener client encoding")
        
        # Verificar encoding de la BD
        try:
            cur.execute("SELECT datcollate FROM pg_database WHERE datname = current_database();")
            collate = cur.fetchone()
            print(f"✅ Database collation: {collate[0] if collate else 'N/A'}")
        except:
            print(f"⚠️  No se pudo obtener database collation")
        
        print()
        
        # Tablas a revisar
        tablas = ['docente', 'estudios_realizados']
        
        for tabla in tablas:
            print(f"📋 Revisando tabla: {tabla}")
            try:
                # Obtener información básica de la tabla
                cur.execute(f"SELECT COUNT(*) FROM {tabla};")
                total = cur.fetchone()[0]
                print(f"   📊 Total de registros: {total}")
                
                # Obtener todas las columnas
                cur.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{tabla}'
                    AND data_type IN ('character varying', 'text');
                """)
                columnas = cur.fetchall()
                
                if not columnas:
                    print(f"   ℹ️  No hay columnas de texto\n")
                    continue
                
                # Revisar cada columna de texto
                for col_name, col_type in columnas:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {tabla} WHERE {col_name} IS NOT NULL;")
                        count = cur.fetchone()[0]
                        
                        if count == 0:
                            continue
                        
                        # Intentar obtener valores
                        try:
                            cur.execute(f"SELECT {col_name} FROM {tabla} WHERE {col_name} IS NOT NULL LIMIT 5;")
                            filas = cur.fetchall()
                            print(f"   ✅ Columna '{col_name}': {count} registros (OK)")
                        except UnicodeDecodeError as ue:
                            print(f"   ⚠️  Columna '{col_name}': ERROR DE ENCODING - {str(ue)[:50]}...")
                        
                    except Exception as e:
                        print(f"   ❌ Error en columna '{col_name}': {str(e)[:60]}")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error revisando tabla {tabla}: {str(e)[:60]}\n")
        
        # Probar la función sp_crud_docentes_estudios
        print("🧪 Probando sp_crud_docentes_estudios('LISTAR')...\n")
        try:
            cur.execute("SELECT * FROM sp_crud_docentes_estudios('LISTAR');")
            resultado = cur.fetchone()
            if resultado:
                resultado_json = resultado[0]
                print(f"✅ SP ejecutado correctamente")
                print(f"   Tipo: {type(resultado_json)}")
                if isinstance(resultado_json, (list, dict)):
                    if isinstance(resultado_json, list):
                        print(f"   Registros retornados: {len(resultado_json)}")
                        if len(resultado_json) > 0:
                            print(f"   Primer registro: {resultado_json[0]}")
                    else:
                        print(f"   Claves: {list(resultado_json.keys())}")
            else:
                print(f"⚠️  SP retornó resultado vacío")
        except UnicodeDecodeError as ue:
            print(f"❌ Error de encoding en SP: {ue}")
        except Exception as e:
            print(f"❌ Error al ejecutar SP: {e}")
        
        print("\n" + "="*60)
        print("RECOMENDACIONES:")
        print("="*60)
        print("1. Si la BD tiene LATIN1, necesitas hacer re-encoding de datos")
        print("2. Ejecutar en pgAdmin: SELECT datname, encoding FROM pg_database;")
        print("3. Si es necesario, usar: ALTER DATABASE mapaConocimiento SET client_encoding = 'UTF8';")
        print("="*60)
        
        cur.close()
        conn.close()
        print("\n✅ Diagnóstico completado")
        
    except Exception as e:
        print(f"❌ Error de conexión general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    diagnosticar_encoding()
