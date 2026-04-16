"""
alianza.py - Blueprint para la tabla Alianza (depende de aliado, docente)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.api_service import ApiService

bp = Blueprint('alianza', __name__)
api = ApiService()

TABLA = 'alianza'
CLAVE_COMPUESTA = ['aliado', 'departamento']

@bp.route('/alianza')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')
    
    registros = api.listar(TABLA, limite)
    
    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'
    
    registro = None
    if editando and valor_clave:
        registro = next(
            (r for r in registros if f"{r.get('aliado')}|{r.get('departamento')}" == valor_clave),
            None
        )
    
    # Obtener datos para selects
    aliados = api.listar('aliado')
    docentes = api.listar('docente')
    departamentos = api.listar('programa')
    
    return render_template('pages/alianza.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        aliados=aliados,
        docentes=docentes,
        departamentos=departamentos
    )

@bp.route('/alianza/buscar')
def buscar():
    query = request.args.get('q', '')
    limite = request.args.get('limite', type=int)
    
    registros = api.listar(TABLA, limite)
    
    if query:
        query_lower = query.lower()
        # Obtener datos relacionados para busqueda
        aliados = api.listar('aliado')
        departamentos = api.listar('programa')
        docentes = api.listar('docente')
        
        # Crear diccionarios para busqueda rapida
        aliados_dict = {str(a.get('nit')): a.get('razon_social', '') for a in aliados}
        deptos_dict = {str(d.get('id')): d.get('nombre', '') for d in departamentos}
        docentes_dict = {str(d.get('cedula')): f"{d.get('nombres', '')} {d.get('apellidos', '')}" for d in docentes}
        
        resultados = []
        for r in registros:
            aliado_str = str(r.get('aliado', ''))
            depto_str = str(r.get('departamento', ''))
            docente_str = str(r.get('docente', ''))
            
            aliado_nombre = aliados_dict.get(aliado_str, '')
            depto_nombre = deptos_dict.get(depto_str, '')
            docente_nombre = docentes_dict.get(docente_str, '')
            
            if (query_lower in aliado_str or
                query_lower in aliado_nombre.lower() or
                query_lower in depto_str or
                query_lower in depto_nombre.lower() or
                query_lower in docente_nombre.lower() or
                query_lower in str(r.get('fecha_inicio', '')).lower() or
                (r.get('fecha_fin') and query_lower in r.get('fecha_fin', '').lower())):
                resultados.append(r)
        registros = resultados
    
    # Obtener datos para selects
    aliados = api.listar('aliado')
    docentes = api.listar('docente')
    departamentos = api.listar('programa')
    
    return render_template('pages/alianza.html',
        registros=registros,
        mostrar_formulario=False,
        editando=False,
        registro=None,
        limite=limite,
        aliados=aliados,
        docentes=docentes,
        departamentos=departamentos,
        busqueda=query
    )

@bp.route('/alianza/sugerencias')
def sugerencias():
    query = request.args.get('q', '')
    limite = request.args.get('limite', 10)
    
    registros = api.listar(TABLA)
    
    if query:
        query_lower = query.lower()
        # Obtener datos relacionados
        aliados = api.listar('aliado')
        departamentos = api.listar('programa')
        docentes = api.listar('docente')
        
        aliados_dict = {str(a.get('nit')): a.get('razon_social', '') for a in aliados}
        deptos_dict = {str(d.get('id')): d.get('nombre', '') for d in departamentos}
        docentes_dict = {str(d.get('cedula')): f"{d.get('nombres', '')} {d.get('apellidos', '')}" for d in docentes}
        
        resultados = []
        for r in registros:
            aliado_str = str(r.get('aliado', ''))
            depto_str = str(r.get('departamento', ''))
            
            aliado_nombre = aliados_dict.get(aliado_str, '')
            depto_nombre = deptos_dict.get(depto_str, '')
            
            if (query_lower in aliado_str or
                query_lower in aliado_nombre.lower() or
                query_lower in depto_str or
                query_lower in depto_nombre.lower()):
                
                docente_id = str(r.get('docente', ''))
                docente_nombre = docentes_dict.get(docente_id, 'Sin docente')
                
                resultados.append({
                    'aliado': r.get('aliado'),
                    'aliado_nombre': aliado_nombre,
                    'departamento': r.get('departamento'),
                    'departamento_nombre': depto_nombre,
                    'docente_nombre': docente_nombre,
                    'fecha_inicio': r.get('fecha_inicio'),
                    'texto': f"{aliado_nombre} - {depto_nombre}"
                })
        
        return jsonify(resultados[:limite])
    
    return jsonify([])

@bp.route('/alianza/crear', methods=['POST'])
def crear():
    aliado = request.form.get('aliado', '')
    departamento = request.form.get('departamento', '')
    
    # Validar y convertir IDs a int
    try:
        aliado_id = int(aliado)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de aliado o departamento inválido.', 'danger')
        return redirect(url_for('alianza.index'))
    
    datos = {
        'aliado': aliado_id,
        'departamento': departamento_id,
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'docente': request.form.get('docente', '') or None
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('alianza.index'))

@bp.route('/alianza/actualizar', methods=['POST'])
def actualizar():
    aliado = request.form.get('aliado', '')
    departamento = request.form.get('departamento', '')

    try:
        aliado_id = int(aliado)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de aliado o departamento inválido.', 'danger')
        return redirect(url_for('alianza.index'))

    datos = {
        'aliado': aliado_id,
        'departamento': departamento_id,
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'docente': request.form.get('docente', '') or None
    }

    # Para claves compuestas, usar DELETE + CREATE
    exito_eliminar, mensaje_eliminar = api.eliminar_compuesta(TABLA, ['aliado', 'departamento'], [aliado_id, departamento_id])

    if exito_eliminar:
        exito_crear, mensaje_crear = api.crear(TABLA, datos)
        if exito_crear:
            flash('Alianza actualizada exitosamente.', 'success')
        else:
            flash(f'Error al recrear: {mensaje_crear}', 'danger')
    else:
        flash(f'Error al actualizar: {mensaje_eliminar}', 'danger')

    return redirect(url_for('alianza.index'))

@bp.route('/alianza/eliminar', methods=['POST'])
def eliminar():
    aliado = request.form.get('aliado', '')
    departamento = request.form.get('departamento', '')
    
    try:
        aliado_id = int(aliado)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de aliado o departamento inválido.', 'danger')
        return redirect(url_for('alianza.index'))
    
    exito, mensaje = api.eliminar_compuesta(TABLA, ['aliado', 'departamento'], [aliado_id, departamento_id])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('alianza.index'))