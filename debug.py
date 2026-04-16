# debug.py
from app import app

# Intentar diferentes formas de importar db
db = None
Docente = None

try:
    from extensions import db, Docente
    print("✅ Importado desde extensions")
except:
    pass

try:
    from database import db, Docente
    print("✅ Importado desde database")
except:
    pass

try:
    from models import db, Docente
    print("✅ Importado desde models")
except:
    pass

try:
    from models.docente import db, Docente
    print("✅ Importado desde models.docente")
except:
    pass

# Si encontramos db, consultamos
if db and Docente:
    with app.app_context():
        total = Docente.query.count()
        print(f"\n📊 TOTAL EN BD: {total}")
        
        if total > 0:
            print("\n📝 Lista de docentes:")
            for d in Docente.query.all():
                print(f"- {d.cedula} | {d.nombres} {d.apellidos}")
        else:
            print("⚠️ LA BASE DE DATOS ESTÁ VACÍA")
else:
    print("\n❌ No se pudo encontrar 'db' o 'Docente'")
    print("📁 Archivos en el proyecto:")
    import os
    for root, dirs, files in os.walk('.'):
        if '__pycache__' not in root and 'venv' not in root:
            level = root.replace('.', '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            for file in files[:5]:  # Mostrar primeros 5 archivos
                if file.endswith('.py'):
                    print(f'{indent}  {file}')