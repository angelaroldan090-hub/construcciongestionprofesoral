"""
docente_departamento.py - Blueprint para la tabla Docente Departamento (depende de docente)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.api_service import ApiService

bp = Blueprint('docente_departamento', __name__)
api = ApiService()

TABLA = 'docente_departamento'
CLAVE_COMPUESTA = ['docente', 'departamento']

@bp.route('/docente_departamento')
def index():
    limite = request.args.get('limite', type=int)
    registros = api.listar(TABLA, limite)
    
    # Obtener datos para selects
    docentes = api.listar('docente')
    programas = api.listar('programa')
    
    # Manejo de formulario modal
    accion = request.args.get('accion')
    clave = request.args.get('clave')
    mostrar_formulario = False
    editando = False
    registro = None
    
    if accion == 'nuevo':
        mostrar_formulario = True
        editando = False
    elif accion == 'editar' and clave:
        try:
            docente_id, departamento_id = clave.split('|')
            # Buscar el registro correspondiente
            for r in registros:
                if str(r.get('docente')) == str(docente_id) and str(r.get('departamento')) == str(departamento_id):
                    registro = r
                    break
            mostrar_formulario = True
            editando = True
        except Exception:
            pass
    
    return render_template('pages/docente_departamento.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        docentes=docentes,
        programas=programas
    )

@bp.route('/docente_departamento/buscar')
def buscar():
    query = request.args.get('q', '')
    limite = request.args.get('limite', type=int)
    
    registros = api.listar(TABLA, limite)
    
    if query:
        query_lower = query.lower()
        # Obtener datos relacionados para busqueda
        docentes = api.listar('docente')
        programas = api.listar('programa')
        
        # Crear diccionarios para busqueda rapida
        docentes_dict = {}
        for d in docentes:
            cedula = str(d.get('cedula', ''))
            nombre = f"{d.get('nombres', '')} {d.get('apellidos', '')}"
            docentes_dict[cedula] = nombre
        
        programas_dict = {}
        for p in programas:
            pid = str(p.get('id', ''))
            nombre = p.get('nombre', '')
            programas_dict[pid] = nombre
        
        resultados = []
        for r in registros:
            docente_str = str(r.get('docente', ''))
            depto_str = str(r.get('departamento', ''))
            
            docente_nombre = docentes_dict.get(docente_str, '')
            depto_nombre = programas_dict.get(depto_str, '')
            
            if (query_lower in docente_str or
                query_lower in docente_nombre.lower() or
                query_lower in depto_str or
                query_lower in depto_nombre.lower() or
                query_lower in r.get('dedicacion', '').lower() or
                query_lower in r.get('modalidad', '').lower()):
                
                # Enriquecer registro con nombres
                r['docente_nombre'] = docente_nombre
                r['departamento_nombre'] = depto_nombre
                resultados.append(r)
        
        registros = resultados
    else:
        # Enriquecer todos los registros con nombres
        docentes = api.listar('docente')
        programas = api.listar('programa')
        
        docentes_dict = {str(d.get('cedula')): f"{d.get('nombres', '')} {d.get('apellidos', '')}" for d in docentes}
        programas_dict = {str(p.get('id')): p.get('nombre', '') for p in programas}
        
        for r in registros:
            r['docente_nombre'] = docentes_dict.get(str(r.get('docente', '')), '')
            r['departamento_nombre'] = programas_dict.get(str(r.get('departamento', '')), '')
    
    # Obtener datos para selects
    docentes = api.listar('docente')
    programas = api.listar('programa')
    
    return render_template('pages/docente_departamento.html',
        registros=registros,
        mostrar_formulario=False,
        editando=False,
        registro=None,
        limite=limite,
        docentes=docentes,
        programas=programas,
        busqueda=query
    )

@bp.route('/docente_departamento/sugerencias')
def sugerencias():
    query = request.args.get('q', '')
    limite = request.args.get('limite', 10)
    
    registros = api.listar(TABLA)
    
    if query:
        query_lower = query.lower()
        # Obtener datos relacionados
        docentes = api.listar('docente')
        programas = api.listar('programa')
        
        docentes_dict = {}
        for d in docentes:
            cedula = str(d.get('cedula', ''))
            nombre = f"{d.get('nombres', '')} {d.get('apellidos', '')}"
            docentes_dict[cedula] = {'nombre': nombre, 'cedula': cedula}
        
        programas_dict = {}
        for p in programas:
            pid = str(p.get('id', ''))
            nombre = p.get('nombre', '')
            programas_dict[pid] = {'nombre': nombre, 'id': pid}
        
        resultados = []
        for r in registros:
            docente_str = str(r.get('docente', ''))
            depto_str = str(r.get('departamento', ''))
            
            docente_info = docentes_dict.get(docente_str, {})
            depto_info = programas_dict.get(depto_str, {})
            
            docente_nombre = docente_info.get('nombre', '')
            depto_nombre = depto_info.get('nombre', '')
            
            if (query_lower in docente_str or
                query_lower in docente_nombre.lower() or
                query_lower in depto_str or
                query_lower in depto_nombre.lower()):
                
                resultados.append({
                    'docente': r.get('docente'),
                    'docente_nombre': docente_nombre,
                    'departamento': r.get('departamento'),
                    'departamento_nombre': depto_nombre,
                    'dedicacion': r.get('dedicacion'),
                    'modalidad': r.get('modalidad'),
                    'fecha_ingreso': r.get('fecha_ingreso'),
                    'texto': f"{docente_nombre} - {depto_nombre}"
                })
        
        return jsonify(resultados[:limite])
    
    return jsonify([])

@bp.route('/docente_departamento/crear', methods=['POST'])
def crear():
    docente = request.form.get('docente', '')
    departamento = request.form.get('departamento', '')
    
    # Validar y convertir IDs a int
    try:
        docente_id = int(docente)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de docente o departamento inválido.', 'danger')
        return redirect(url_for('docente_departamento.index'))
    
    datos = {
        'docente': docente_id,
        'departamento': departamento_id,
        'dedicacion': request.form.get('dedicacion', ''),
        'modalidad': request.form.get('modalidad', ''),
        'fecha_ingreso': request.form.get('fecha_ingreso', ''),
        'fecha_salida': request.form.get('fecha_salida', '') or None
    }
    
    exito, mensaje = api.ejecutar_procedimiento_mensaje('insert_docente_departamento', [
        docente_id,
        departamento_id,
        datos['dedicacion'],
        datos['modalidad'],
        datos['fecha_ingreso'],
        datos['fecha_salida']
    ])
    if not exito:
        exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente_departamento.index'))

@bp.route('/docente_departamento/actualizar', methods=['POST'])
def actualizar():
    docente = request.form.get('docente', '')
    departamento = request.form.get('departamento', '')
    
    # Validar y convertir a int si es posible
    try:
        docente_id = int(docente)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de docente o departamento inválido.', 'danger')
        return redirect(url_for('docente_departamento.index'))
    
    datos = {
        'dedicacion': request.form.get('dedicacion', ''),
        'modalidad': request.form.get('modalidad', ''),
        'fecha_ingreso': request.form.get('fecha_ingreso', ''),
        'fecha_salida': request.form.get('fecha_salida', '') or None
    }
    
    exito, mensaje = api.ejecutar_procedimiento_mensaje('update_docente_departamento', [
        docente_id,
        departamento_id,
        datos['dedicacion'],
        datos['modalidad'],
        datos['fecha_ingreso'],
        datos['fecha_salida']
    ])

    if not exito:
        # Fallback para backends sin SP
        exito_eliminar, mensaje_eliminar = api.eliminar_compuesta(TABLA, ['docente', 'departamento'], [docente_id, departamento_id])
        if exito_eliminar:
            datos_crear = {
                'docente': docente_id,
                'departamento': departamento_id,
                'dedicacion': datos['dedicacion'],
                'modalidad': datos['modalidad'],
                'fecha_ingreso': datos['fecha_ingreso'],
                'fecha_salida': datos['fecha_salida']
            }
            exito, mensaje = api.crear(TABLA, datos_crear)
        else:
            exito, mensaje = False, mensaje_eliminar

    flash(mensaje, 'success' if exito else 'danger')
    
    return redirect(url_for('docente_departamento.index'))

@bp.route('/docente_departamento/eliminar', methods=['POST'])
def eliminar():
    docente = request.form.get('docente', '')
    departamento = request.form.get('departamento', '')
    
    # Validar y convertir a int si es posible
    try:
        docente_id = int(docente)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de docente o departamento inválido.', 'danger')
        return redirect(url_for('docente_departamento.index'))
    
    exito, mensaje = api.ejecutar_procedimiento_mensaje('delete_docente_departamento', [docente_id, departamento_id])
    if not exito:
        exito, mensaje = api.eliminar_compuesta(TABLA, ['docente', 'departamento'], [docente_id, departamento_id])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente_departamento.index'))