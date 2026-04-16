"""
red_docente.py - Blueprint para tabla intermedia (N:N) entre Red y Docente
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.api_service import ApiService

bp = Blueprint('red_docente', __name__)
api = ApiService()

TABLA = 'red_docente'
CLAVE_COMPUESTA = ['red', 'docente']

@bp.route('/red_docente')
def index():
    limite = request.args.get('limite', type=int)
    registros = api.listar(TABLA, limite)
    
    # Obtener datos para selects
    redes = api.listar('red')
    docentes = api.listar('docente')
    
    # Enriquecer registros con nombres
    redes_dict = {str(r.get('id')): r.get('nombre', '') for r in redes}
    docentes_dict = {str(d.get('cedula')): f"{d.get('nombres', '')} {d.get('apellidos', '')}" for d in docentes}
    
    for r in registros:
        r['red_nombre'] = redes_dict.get(str(r.get('red', '')), '')
        r['docente_nombre'] = docentes_dict.get(str(r.get('docente', '')), '')
    
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
            red_id, docente_id = clave.split('|')
            # Buscar el registro correspondiente
            for r in registros:
                if str(r.get('red')) == str(red_id) and str(r.get('docente')) == str(docente_id):
                    registro = r
                    break
            mostrar_formulario = True
            editando = True
        except Exception:
            pass
    
    return render_template('pages/red_docente.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        redes=redes,
        docentes=docentes
    )

@bp.route('/red_docente/buscar')
def buscar():
    query = request.args.get('q', '')
    limite = request.args.get('limite', type=int)
    
    registros = api.listar(TABLA, limite)
    
    if query:
        query_lower = query.lower()
        # Obtener datos relacionados para busqueda
        redes = api.listar('red')
        docentes = api.listar('docente')
        
        # Crear diccionarios para busqueda rapida
        redes_dict = {str(r.get('id')): r.get('nombre', '') for r in redes}
        docentes_dict = {str(d.get('cedula')): f"{d.get('nombres', '')} {d.get('apellidos', '')}" for d in docentes}
        
        resultados = []
        for r in registros:
            red_str = str(r.get('red', ''))
            docente_str = str(r.get('docente', ''))
            
            red_nombre = redes_dict.get(red_str, '')
            docente_nombre = docentes_dict.get(docente_str, '')
            
            if (query_lower in red_str or
                query_lower in red_nombre.lower() or
                query_lower in docente_str or
                query_lower in docente_nombre.lower() or
                (r.get('act_destacadas') and query_lower in r.get('act_destacadas', '').lower())):
                
                # Enriquecer registro con nombres
                r['red_nombre'] = red_nombre
                r['docente_nombre'] = docente_nombre
                resultados.append(r)
        
        registros = resultados
    else:
        # Enriquecer todos los registros con nombres
        redes = api.listar('red')
        docentes = api.listar('docente')
        
        redes_dict = {str(r.get('id')): r.get('nombre', '') for r in redes}
        docentes_dict = {str(d.get('cedula')): f"{d.get('nombres', '')} {d.get('apellidos', '')}" for d in docentes}
        
        for r in registros:
            r['red_nombre'] = redes_dict.get(str(r.get('red', '')), '')
            r['docente_nombre'] = docentes_dict.get(str(r.get('docente', '')), '')
    
    # Obtener datos para selects
    redes = api.listar('red')
    docentes = api.listar('docente')
    
    return render_template('pages/red_docente.html',
        registros=registros,
        mostrar_formulario=False,
        editando=False,
        registro=None,
        limite=limite,
        redes=redes,
        docentes=docentes,
        busqueda=query
    )

@bp.route('/red_docente/sugerencias')
def sugerencias():
    query = request.args.get('q', '')
    limite = request.args.get('limite', 10)
    
    registros = api.listar(TABLA)
    
    if query:
        query_lower = query.lower()
        # Obtener datos relacionados
        redes = api.listar('red')
        docentes = api.listar('docente')
        
        redes_dict = {str(r.get('id')): r.get('nombre', '') for r in redes}
        docentes_dict = {str(d.get('cedula')): f"{d.get('nombres', '')} {d.get('apellidos', '')}" for d in docentes}
        
        resultados = []
        for r in registros:
            red_str = str(r.get('red', ''))
            docente_str = str(r.get('docente', ''))
            
            red_nombre = redes_dict.get(red_str, '')
            docente_nombre = docentes_dict.get(docente_str, '')
            
            if (query_lower in red_str or
                query_lower in red_nombre.lower() or
                query_lower in docente_str or
                query_lower in docente_nombre.lower()):
                
                resultados.append({
                    'red': r.get('red'),
                    'red_nombre': red_nombre,
                    'docente': r.get('docente'),
                    'docente_nombre': docente_nombre,
                    'fecha_inicio': r.get('fecha_inicio'),
                    'fecha_fin': r.get('fecha_fin'),
                    'act_destacadas': r.get('act_destacadas'),
                    'texto': f"{red_nombre} - {docente_nombre}"
                })
        
        return jsonify(resultados[:limite])
    
    return jsonify([])

@bp.route('/red_docente/crear', methods=['POST'])
def crear():
    red = request.form.get('red', '')
    docente = request.form.get('docente', '')
    
    # Validar y convertir IDs a int
    try:
        red_id = int(red)
        docente_id = int(docente)
    except (ValueError, TypeError):
        flash('ID de red o docente inválido.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    datos = {
        'red': red_id,
        'docente': docente_id,
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'act_destacadas': request.form.get('act_destacadas', '')
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/actualizar', methods=['POST'])
def actualizar():
    red = request.form.get('red', '')
    docente = request.form.get('docente', '')
    
    # Validar y convertir a int si es posible
    try:
        red_id = int(red)
        docente_id = int(docente)
    except (ValueError, TypeError):
        flash('ID de red o docente inválido.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    datos = {
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'act_destacadas': request.form.get('act_destacadas', '')
    }
    
    # Para claves compuestas, simular actualización con DELETE + CREATE
    # Paso 1: Eliminar el registro actual
    exito_eliminar, mensaje_eliminar = api.eliminar_compuesta(TABLA, ['red', 'docente'], [red_id, docente_id])
    
    if exito_eliminar:
        # Paso 2: Crear el registro con los datos nuevos
        datos_crear = {
            'red': red_id,
            'docente': docente_id,
            'fecha_inicio': datos['fecha_inicio'],
            'fecha_fin': datos['fecha_fin'],
            'act_destacadas': datos['act_destacadas']
        }
        exito_crear, mensaje_crear = api.crear(TABLA, datos_crear)
        
        if exito_crear:
            flash('Registro actualizado exitosamente.', 'success')
        else:
            flash(f'Error al recrear registro: {mensaje_crear}', 'danger')
    else:
        flash(f'Error al actualizar: {mensaje_eliminar}', 'danger')
    
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/eliminar', methods=['POST'])
def eliminar():
    red = request.form.get('red', '')
    docente = request.form.get('docente', '')
    
    # Validar y convertir a int si es posible
    try:
        red_id = int(red)
        docente_id = int(docente)
    except (ValueError, TypeError):
        flash('ID de red o docente inválido.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    exito, mensaje = api.eliminar_compuesta(TABLA, ['red', 'docente'], [red_id, docente_id])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))