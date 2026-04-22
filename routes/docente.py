"""
docente.py - Blueprint para la tabla Docente.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.api_service import ApiService

bp = Blueprint('docente', __name__)
api = ApiService()

TABLA = 'docente'
CLAVE = 'cedula'

@bp.route('/docente')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')
    
    registros = api.listar(TABLA, limite)
    
    # DEPURACION
    print("=" * 50)
    print(f"URL: {request.url}")
    print(f"Tabla: {TABLA}")
    print(f"Registros recibidos: {len(registros)}")
    if registros:
        print(f"Primer registro: {registros[0]}")
    else:
        print("No hay registros")
    print("=" * 50)
    
    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'
    
    registro = None
    vinculaciones = []
    
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )
        vinculaciones = api.listar_vinculaciones_docente(valor_clave)
        
        # DEPURACION
        print(f"=== DEPURACION VINCULACIONES ===")
        print(f"Docente ID: {valor_clave}")
        print(f"Vinculaciones encontradas: {len(vinculaciones)}")
        for v in vinculaciones:
            print(f"  - {v}")
        print(f"================================")
    
    # Obtener listas para selects
    lineas = api.listar('linea_investigacion')
    departamentos = api.listar('programa')
    
    return render_template('pages/docente.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        vinculaciones=vinculaciones,
        limite=limite,
        lineas=lineas,
        departamentos=departamentos
    )

@bp.route('/docente/buscar')
def buscar():
    query = request.args.get('q', '')
    limite = request.args.get('limite', type=int)
    
    registros = api.listar(TABLA, limite)
    
    if query:
        query_lower = query.lower()
        registros = [
            d for d in registros 
            if query_lower in str(d.get('cedula', '')).lower()
            or query_lower in d.get('nombres', '').lower()
            or query_lower in d.get('apellidos', '').lower()
            or query_lower in d.get('correo', '').lower()
            or query_lower in d.get('cargo', '').lower()
        ]
    
    return render_template('pages/docente.html',
        registros=registros,
        mostrar_formulario=False,
        editando=False,
        registro=None,
        vinculaciones=[],
        limite=limite,
        lineas=api.listar('linea_investigacion'),
        departamentos=api.listar('programa'),
        busqueda=query
    )

@bp.route('/docente/sugerencias')
def sugerencias():
    query = request.args.get('q', '')
    limite = request.args.get('limite', 10)
    
    registros = api.listar(TABLA)
    
    if query:
        query_lower = query.lower()
        resultados = []
        for d in registros:
            if (query_lower in str(d.get('cedula', '')).lower() or
                query_lower in d.get('nombres', '').lower() or
                query_lower in d.get('apellidos', '').lower()):
                resultados.append({
                    'cedula': d.get('cedula'),
                    'nombres': d.get('nombres'),
                    'apellidos': d.get('apellidos'),
                    'cargo': d.get('cargo'),
                    'texto': f"{d.get('cedula')} - {d.get('nombres')} {d.get('apellidos')}"
                })
        return jsonify(resultados[:limite])
    
    return jsonify([])

@bp.route('/docente/crear', methods=['POST'])
def crear():
    datos = {
        'cedula': request.form.get('cedula', ''),
        'nombres': request.form.get('nombres', ''),
        'apellidos': request.form.get('apellidos', ''),
        'genero': request.form.get('genero', ''),
        'cargo': request.form.get('cargo', ''),
        'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
        'correo': request.form.get('correo', ''),
        'telefono': request.form.get('telefono', ''),
        'url_cvlac': request.form.get('url_cvlac', ''),
        'fecha_actualizacion': request.form.get('fecha_actualizacion', ''),
        'escalafon': request.form.get('escalafon', ''),
        'perfil': request.form.get('perfil', ''),
        'cat_minciencia': request.form.get('cat_minciencia', ''),
        'conv_minciencia': request.form.get('conv_minciencia', ''),
        'nacionalidad': request.form.get('nacionalidad', ''),
        'linea_investigacion_principal': request.form.get('linea_investigacion_principal', '') or None
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente.index'))

@bp.route('/docente/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('cedula', '')
    datos = {
        'nombres': request.form.get('nombres', ''),
        'apellidos': request.form.get('apellidos', ''),
        'genero': request.form.get('genero', ''),
        'cargo': request.form.get('cargo', ''),
        'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
        'correo': request.form.get('correo', ''),
        'telefono': request.form.get('telefono', ''),
        'url_cvlac': request.form.get('url_cvlac', ''),
        'fecha_actualizacion': request.form.get('fecha_actualizacion', ''),
        'escalafon': request.form.get('escalafon', ''),
        'perfil': request.form.get('perfil', ''),
        'cat_minciencia': request.form.get('cat_minciencia', ''),
        'conv_minciencia': request.form.get('conv_minciencia', ''),
        'nacionalidad': request.form.get('nacionalidad', ''),
        'linea_investigacion_principal': request.form.get('linea_investigacion_principal', '') or None
    }
    
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente.index'))

@bp.route('/docente/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('cedula', '')
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente.index'))

@bp.route('/api/docente/<int:docente_id>/vinculaciones', methods=['GET'])
def obtener_vinculaciones(docente_id):
    registros = api.listar_vinculaciones_docente(docente_id)
    return jsonify({'success': True, 'data': registros})

@bp.route('/api/docente_vinculacion/crear', methods=['POST'])
def crear_vinculacion():
    try:
        data = request.json
        
        # Validar datos requeridos
        if not data.get('docente'):
            return jsonify({'success': False, 'message': 'Docente es requerido'}), 400
        if not data.get('departamento'):
            return jsonify({'success': False, 'message': 'Departamento es requerido'}), 400
        if not data.get('fecha_ingreso'):
            return jsonify({'success': False, 'message': 'Fecha de ingreso es requerida'}), 400
        
        docente_id = int(data.get('docente'))
        departamento_id = int(data.get('departamento'))
        
        # Validar duplicados antes de enviar al backend
        existentes = api.listar('docente_departamento')
        if any(
            int(r.get('docente', -1)) == docente_id and int(r.get('departamento', -1)) == departamento_id
            for r in existentes
        ):
            return jsonify({'success': False, 'message': 'Ya existe una vinculación para este docente y departamento.'}), 409
        
        datos = {
            'docente': docente_id,
            'departamento': departamento_id,
            'dedicacion': data.get('dedicacion', ''),
            'modalidad': data.get('modalidad', ''),
            'fecha_ingreso': data.get('fecha_ingreso'),
            'fecha_salida': data.get('fecha_salida') or None
        }
        
        print(f"[DEBUG] Creando vinculación con datos: {datos}")
        exito, mensaje = api.crear('docente_departamento', datos)
        print(f"[DEBUG] Resultado: exito={exito}, mensaje={mensaje}")
        
        return jsonify({'success': exito, 'message': mensaje})
    except Exception as e:
        error_msg = f"Error al crear vinculación: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({'success': False, 'message': error_msg}), 500

@bp.route('/api/docente_vinculacion/eliminar', methods=['POST'])
def eliminar_vinculacion():
    data = request.json
    exito, mensaje = api.eliminar_compuesta('docente_departamento', ['docente', 'departamento'], [data.get('docente'), data.get('departamento')])
    return jsonify({'success': exito, 'message': mensaje})

@bp.route('/api/docente_vinculacion/actualizar', methods=['POST'])
def actualizar_vinculacion():
    data = request.json
    datos = {
        'docente': data.get('docente'),
        'departamento': data.get('departamento'),
        'dedicacion': data.get('dedicacion'),
        'modalidad': data.get('modalidad'),
        'fecha_ingreso': data.get('fecha_ingreso'),
        'fecha_salida': data.get('fecha_salida')
    }
    exito, mensaje = api.actualizar_compuesta('docente_departamento', ['docente', 'departamento'], [data.get('docente'), data.get('departamento')], datos)
    return jsonify({'success': exito, 'message': mensaje})