"""
test_crud.py - Script universal para probar CRUD de cualquier tabla
Uso: python test_crud.py
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import sys

# ============================================
# CONFIGURACIÓN - Cambia estos valores
# ============================================
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',  # Tu base de datos
    'user': 'postgres',       # Tu usuario
    'password': 'admin',      # Tu contraseña
    'port': 5432
}

# ============================================
# CLASE TESTER UNIVERSAL
# ============================================
class DatabaseTester:
    """Probador universal de CRUD para PostgreSQL"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        
    def conectar(self):
        """Establecer conexión"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Conexión exitosa a PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def desconectar(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Conexión cerrada")
    
    def mostrar_tablas(self):
        """Listar todas las tablas"""
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tablas = self.cursor.fetchall()
        
        print("\n📋 TABLAS DISPONIBLES:")
        print("-" * 40)
        for i, tabla in enumerate(tablas, 1):
            print(f"{i:3}. {tabla['table_name']}")
        return [t['table_name'] for t in tablas]
    
    def mostrar_estructura(self, tabla):
        """Mostrar estructura de una tabla"""
        self.cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default,
                CASE 
                    WHEN column_name IN (
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_name = %s
                    ) THEN 'PK'
                    WHEN column_name IN (
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = %s
                    ) THEN 'FK'
                    ELSE ''
                END as key_type
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (tabla, tabla, tabla))
        
        columnas = self.cursor.fetchall()
        
        print(f"\n📊 ESTRUCTURA DE '{tabla}':")
        print("-" * 80)
        print(f"{'Columna':<25} {'Tipo':<20} {'Key':<5} {'Nullable':<10} {'Default':<20}")
        print("-" * 80)
        
        for col in columnas:
            key = col['key_type'] if col['key_type'] else ''
            nullable = 'YES' if col['is_nullable'] == 'YES' else 'NO'
            default = str(col['column_default']) if col['column_default'] else ''
            print(f"{col['column_name']:<25} {col['data_type']:<20} {key:<5} {nullable:<10} {default:<20}")
        
        return columnas
    
    def test_select(self, tabla, limite=5):
        """Probar SELECT"""
        print(f"\n🔍 TEST SELECT en '{tabla}':")
        print("-" * 60)
        
        try:
            self.cursor.execute(f"SELECT * FROM {tabla} LIMIT %s", (limite,))
            registros = self.cursor.fetchall()
            
            if registros:
                print(f"✅ Encontrados {len(registros)} registros:\n")
                for i, reg in enumerate(registros, 1):
                    print(f"Registro #{i}:")
                    for key, value in reg.items():
                        print(f"  {key}: {value}")
                    print()
            else:
                print(f"⚠️  La tabla '{tabla}' está vacía")
            
            return registros
        except Exception as e:
            print(f"❌ Error en SELECT: {e}")
            return []
    
    def test_insert(self, tabla, datos):
        """Probar INSERT"""
        print(f"\n➕ TEST INSERT en '{tabla}':")
        print("-" * 60)
        
        try:
            columnas = list(datos.keys())
            valores = list(datos.values())
            placeholders = ['%s'] * len(columnas)
            
            query = f"""
                INSERT INTO {tabla} ({', '.join(columnas)})
                VALUES ({', '.join(placeholders)})
                RETURNING *;
            """
            
            self.cursor.execute(query, valores)
            nuevo = self.cursor.fetchone()
            self.conn.commit()
            
            print("✅ Registro insertado exitosamente:")
            for key, value in nuevo.items():
                print(f"  {key}: {value}")
            
            return nuevo
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error en INSERT: {e}")
            return None
    
    def test_update(self, tabla, where_clause, datos):
        """Probar UPDATE"""
        print(f"\n🔄 TEST UPDATE en '{tabla}':")
        print("-" * 60)
        
        try:
            set_clause = ', '.join([f"{k} = %s" for k in datos.keys()])
            valores = list(datos.values()) + list(where_clause.values())
            
            where_condition = ' AND '.join([f"{k} = %s" for k in where_clause.keys()])
            
            query = f"""
                UPDATE {tabla} 
                SET {set_clause}
                WHERE {where_condition}
                RETURNING *;
            """
            
            self.cursor.execute(query, valores)
            actualizado = self.cursor.fetchone()
            self.conn.commit()
            
            if actualizado:
                print("✅ Registro actualizado exitosamente:")
                for key, value in actualizado.items():
                    print(f"  {key}: {value}")
            else:
                print("⚠️  No se encontró el registro para actualizar")
            
            return actualizado
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error en UPDATE: {e}")
            return None
    
    def test_delete(self, tabla, where_clause):
        """Probar DELETE"""
        print(f"\n❌ TEST DELETE en '{tabla}':")
        print("-" * 60)
        
        try:
            where_condition = ' AND '.join([f"{k} = %s" for k in where_clause.keys()])
            valores = list(where_clause.values())
            
            # Primero ver qué vamos a eliminar
            self.cursor.execute(f"SELECT * FROM {tabla} WHERE {where_condition}", valores)
            a_eliminar = self.cursor.fetchone()
            
            if a_eliminar:
                print("Registro a eliminar:")
                for key, value in a_eliminar.items():
                    print(f"  {key}: {value}")
                
                confirmacion = input("\n¿Confirmar eliminación? (s/N): ")
                if confirmacion.lower() != 's':
                    print("❌ Eliminación cancelada")
                    return None
                
                query = f"DELETE FROM {tabla} WHERE {where_condition}"
                self.cursor.execute(query, valores)
                self.conn.commit()
                
                print(f"✅ Registro eliminado ({self.cursor.rowcount} filas afectadas)")
            else:
                print("⚠️  No se encontró el registro para eliminar")
            
            return a_eliminar
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error en DELETE: {e}")
            return None
    
    def test_crud_completo(self, tabla, pk_columna, datos_prueba):
        """Probar CRUD completo automáticamente"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST CRUD COMPLETO - Tabla: {tabla}")
        print(f"{'='*60}")
        
        # 1. INSERT
        print("\n1️⃣  INSERT - Creando registro de prueba...")
        nuevo = self.test_insert(tabla, datos_prueba)
        if not nuevo:
            print("❌ Falló INSERT. Abortando prueba.")
            return
        
        pk_valor = nuevo[pk_columna]
        
        # 2. SELECT (verificar inserción)
        print(f"\n2️⃣  SELECT - Verificando inserción con {pk_columna}={pk_valor}...")
        self.cursor.execute(f"SELECT * FROM {tabla} WHERE {pk_columna} = %s", (pk_valor,))
        verificado = self.cursor.fetchone()
        if verificado:
            print("✅ Registro verificado correctamente")
        
        # 3. UPDATE
        print(f"\n3️⃣  UPDATE - Actualizando registro...")
        datos_update = self._generar_datos_update(datos_prueba)
        where = {pk_columna: pk_valor}
        actualizado = self.test_update(tabla, where, datos_update)
        
        # 4. DELETE
        print(f"\n4️⃣  DELETE - Eliminando registro de prueba...")
        eliminado = self.test_delete(tabla, where)
        
        print(f"\n{'='*60}")
        print("✅ PRUEBA CRUD COMPLETADA EXITOSAMENTE")
        print(f"{'='*60}")
    
    def _generar_datos_update(self, datos_originales):
        """Generar datos modificados para UPDATE"""
        datos_update = {}
        for key, value in datos_originales.items():
            if isinstance(value, str) and key not in ['codigo', 'id', 'cedula']:
                datos_update[key] = f"{value}_ACTUALIZADO"
            elif isinstance(value, int):
                datos_update[key] = value + 1
        return datos_update

# ============================================
# PRUEBAS ESPECÍFICAS PARA TABLAS INTERMEDIAS
# ============================================

def test_relacion_estudio_area():
    """Probar relación estudio - área de conocimiento"""
    tester = DatabaseTester(DB_CONFIG)
    
    if not tester.conectar():
        return
    
    try:
        print("\n🎯 PRUEBA: RELACIÓN ESTUDIO - ÁREA CONOCIMIENTO")
        print("="*60)
        
        # 1. Verificar que existen las tablas
        tablas = tester.mostrar_tablas()
        
        if 'estudio_ac' not in tablas:
            print("\n❌ No existe tabla 'estudio_ac'")
            return
        
        if 'area_conocimiento' not in tablas:
            print("\n❌ No existe tabla 'area_conocimiento'")
            return
        
        # 2. Mostrar estructuras
        tester.mostrar_estructura('estudio_ac')
        tester.mostrar_estructura('area_conocimiento')
        
        # 3. Ver datos existentes
        print("\n📚 ESTUDIOS EXISTENTES:")
        tester.test_select('estudio_ac', 3)
        
        print("\n🔬 ÁREAS DE CONOCIMIENTO:")
        tester.test_select('area_conocimiento', 3)
        
        # 4. Buscar tabla intermedia (puede tener nombres como: estudio_area, rel_estudio_area, etc.)
        tablas_intermedias = [t for t in tablas if 'area' in t.lower() and 'estudio' in t.lower()]
        
        if tablas_intermedias:
            tabla_intermedia = tablas_intermedias[0]
            print(f"\n🔗 TABLA INTERMEDIA ENCONTRADA: {tabla_intermedia}")
            tester.mostrar_estructura(tabla_intermedia)
            tester.test_select(tabla_intermedia, 5)
        else:
            print("\n⚠️  No se encontró tabla intermedia explícita")
            print("   Posiblemente la relación es directa con FK")
            
            # Verificar FK en estudio_ac
            tester.cursor.execute("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name IN ('estudio_ac', 'area_conocimiento');
            """)
            
            fks = tester.cursor.fetchall()
            if fks:
                print("\n🔑 RELACIONES FOREIGN KEY:")
                for fk in fks:
                    print(f"  {fk['table_name']}.{fk['column_name']} -> "
                          f"{fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
    finally:
        tester.desconectar()

def menu_interactivo():
    """Menú interactivo para pruebas"""
    tester = DatabaseTester(DB_CONFIG)
    
    if not tester.conectar():
        return
    
    try:
        while True:
            print("\n" + "="*60)
            print("🧪 MENÚ DE PRUEBAS CRUD - POSTGRESQL")
            print("="*60)
            print("1. 📋 Listar todas las tablas")
            print("2. 📊 Ver estructura de una tabla")
            print("3. 🔍 Ver datos de una tabla")
            print("4. ➕ Insertar registro de prueba")
            print("5. 🔄 Actualizar registro")
            print("6. ❌ Eliminar registro")
            print("7. 🧪 Test CRUD completo automático")
            print("8. 🔗 Probar relación estudio-área")
            print("9. 🚪 Salir")
            print("-"*60)
            
            opcion = input("Seleccione opción (1-9): ").strip()
            
            if opcion == '1':
                tester.mostrar_tablas()
                
            elif opcion == '2':
                tablas = tester.mostrar_tablas()
                nombre = input("\nNombre de la tabla: ").strip()
                if nombre in tablas:
                    tester.mostrar_estructura(nombre)
                else:
                    print("❌ Tabla no encontrada")
                    
            elif opcion == '3':
                tablas = tester.mostrar_tablas()
                nombre = input("\nNombre de la tabla: ").strip()
                if nombre in tablas:
                    limite = input("Límite de registros (Enter=5): ").strip()
                    limite = int(limite) if limite else 5
                    tester.test_select(nombre, limite)
                else:
                    print("❌ Tabla no encontrada")
                    
            elif opcion == '4':
                tablas = tester.mostrar_tablas()
                nombre = input("\nNombre de la tabla: ").strip()
                if nombre in tablas:
                    tester.mostrar_estructura(nombre)
                    print("\nIngrese datos en formato JSON:")
                    print('Ejemplo: {"nombre": "Juan", "edad": 25}')
                    datos_str = input("Datos: ").strip()
                    try:
                        datos = json.loads(datos_str)
                        tester.test_insert(nombre, datos)
                    except:
                        print("❌ Formato JSON inválido")
                else:
                    print("❌ Tabla no encontrada")
                    
            elif opcion == '5':
                tablas = tester.mostrar_tablas()
                nombre = input("\nNombre de la tabla: ").strip()
                if nombre in tablas:
                    print("\nCondición WHERE en JSON:")
                    print('Ejemplo: {"id": 1}')
                    where_str = input("WHERE: ").strip()
                    print("\nDatos a actualizar en JSON:")
                    datos_str = input("Datos: ").strip()
                    try:
                        where = json.loads(where_str)
                        datos = json.loads(datos_str)
                        tester.test_update(nombre, where, datos)
                    except:
                        print("❌ Formato JSON inválido")
                else:
                    print("❌ Tabla no encontrada")
                    
            elif opcion == '6':
                tablas = tester.mostrar_tablas()
                nombre = input("\nNombre de la tabla: ").strip()
                if nombre in tablas:
                    print("\nCondición WHERE en JSON:")
                    print('Ejemplo: {"id": 1}')
                    where_str = input("WHERE: ").strip()
                    try:
                        where = json.loads(where_str)
                        tester.test_delete(nombre, where)
                    except:
                        print("❌ Formato JSON inválido")
                else:
                    print("❌ Tabla no encontrada")
                    
            elif opcion == '7':
                tablas = tester.mostrar_tablas()
                nombre = input("\nNombre de la tabla: ").strip()
                if nombre in tablas:
                    tester.mostrar_estructura(nombre)
                    pk = input("\nNombre de la columna PK: ").strip()
                    print("\nDatos de prueba en JSON:")
                    datos_str = input("Datos: ").strip()
                    try:
                        datos = json.loads(datos_str)
                        tester.test_crud_completo(nombre, pk, datos)
                    except:
                        print("❌ Formato JSON inválido")
                else:
                    print("❌ Tabla no encontrada")
                    
            elif opcion == '8':
                test_relacion_estudio_area()
                
            elif opcion == '9':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                
    finally:
        tester.desconectar()

# ============================================
# DATOS DE PRUEBA PREDEFINIDOS
# ============================================

PRUEBAS_PREDEFINIDAS = {
    'docente': {
        'pk': 'cedula',
        'datos': {
            'cedula': '999999',
            'nombres': 'Profesor Test',
            'apellidos': 'Prueba CRUD',
            'genero': 'Masculino',
            'cargo': 'Tiempo Completo',
            'correo': 'test@prueba.edu.co',
            'nacionalidad': 'Colombiano'
        }
    },
    'estudio_ac': {
        'pk': 'id',
        'datos': {
            'nivel': 'DOCTORADO',
            'titulo': 'Doctor en Ciencias de la Computación',
            'universidad': 'Universidad Nacional',
            'anio_grado': 2020,
            'pais': 'Colombia'
        }
    },
    'area_conocimiento': {
        'pk': 'id',
        'datos': {
            'nombre': 'Inteligencia Artificial',
            'descripcion': 'Área de prueba para CRUD',
            'codigo': 'IA-001'
        }
    }
}

def test_rapido(tabla='docente'):
    """Prueba rápida con datos predefinidos"""
    tester = DatabaseTester(DB_CONFIG)
    
    if not tester.conectar():
        return
    
    try:
        if tabla in PRUEBAS_PREDEFINIDAS:
            config = PRUEBAS_PREDEFINIDAS[tabla]
            tester.test_crud_completo(tabla, config['pk'], config['datos'])
        else:
            print(f"❌ No hay datos predefinidos para '{tabla}'")
            print(f"   Tablas disponibles: {list(PRUEBAS_PREDEFINIDAS.keys())}")
    finally:
        tester.desconectar()

# ============================================
# PUNTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🧪 SISTEMA DE PRUEBAS CRUD - POSTGRESQL")
    print("="*60)
    
    if len(sys.argv) > 1:
        # Modo rápido: python test_crud.py docente
        tabla = sys.argv[1]
        test_rapido(tabla)
    else:
        # Modo interactivo
        menu_interactivo()