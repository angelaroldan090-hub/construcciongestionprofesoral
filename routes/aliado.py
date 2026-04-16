"""
aliado.py - Blueprint para la tabla Aliado.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.api_service import ApiService

bp = Blueprint('aliado', __name__)
api = ApiService()

TABLA = 'aliado'
CLAVE = 'nit'

@bp.route('/aliado')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')
    
    registros = api.listar(TABLA, limite)
    
    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'
    
    registro = None
    alianzas = []
    
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )
        try:
            aliado_id = int(valor_clave)
        except (ValueError, TypeError):
            aliado_id = valor_clave
        alianzas = api.listar_alianzas_aliado(aliado_id)
        
        # Enriquecer alianzas con nombres de departamento y docente
        if alianzas:
            departamentos = api.listar('programa')
            docentes = api.listar('docente')
            deptos_dict = {str(d.get('id')): d.get('nombre', '') for d in departamentos}
            docentes_dict = {str(d.get('cedula')): f"{d.get('nombres', '')} {d.get('apellidos', '')}" for d in docentes}
            for a in alianzas:
                a['departamento_nombre'] = deptos_dict.get(str(a.get('departamento')), a.get('departamento'))
                a['docente_nombre'] = docentes_dict.get(str(a.get('docente')), a.get('docente'))
    
    # Obtener listas para selects
    departamentos = api.listar('programa')
    docentes = api.listar('docente')
    
    return render_template('pages/aliado.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        alianzas=alianzas,
        limite=limite,
        departamentos=departamentos,
        docentes=docentes
    )

@bp.route('/aliado/buscar')
def buscar():
    query = request.args.get('q', '')
    limite = request.args.get('limite', type=int)
    
    registros = api.listar(TABLA, limite)
    
    if query:
        query_lower = query.lower()
        registros = [
            r for r in registros 
            if query_lower in str(r.get('nit', '')).lower()
            or query_lower in r.get('razon_social', '').lower()
            or query_lower in r.get('nombre_contacto', '').lower()
            or query_lower in r.get('correo', '').lower()
            or query_lower in r.get('ciudad', '').lower()
        ]
    
    return render_template('pages/aliado.html',
        registros=registros,
        mostrar_formulario=False,
        editando=False,
        registro=None,
        alianzas=[],
        limite=limite,
        departamentos=api.listar('programa'),
        docentes=api.listar('docente'),
        busqueda=query
    )

@bp.route('/aliado/sugerencias')
def sugerencias():
    query = request.args.get('q', '')
    limite = request.args.get('limite', 10)
    
    registros = api.listar(TABLA)
    
    if query:
        query_lower = query.lower()
        resultados = []
        for r in registros:
            if (query_lower in str(r.get('nit', '')).lower() or
                query_lower in r.get('razon_social', '').lower() or
                query_lower in r.get('nombre_contacto', '').lower()):
                resultados.append({
                    'nit': r.get('nit'),
                    'razon_social': r.get('razon_social'),
                    'nombre_contacto': r.get('nombre_contacto'),
                    'ciudad': r.get('ciudad'),
                    'texto': f"{r.get('nit')} - {r.get('razon_social')}"
                })
        return jsonify(resultados[:limite])
    
    return jsonify([])

@bp.route('/aliado/crear', methods=['POST'])
def crear():
    datos = {
        'nit': request.form.get('nit', ''),
        'razon_social': request.form.get('razon_social', ''),
        'nombre_contacto': request.form.get('nombre_contacto', ''),
        'correo': request.form.get('correo', ''),
        'telefono': request.form.get('telefono', ''),
        'ciudad': request.form.get('ciudad', '')
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('aliado.index'))

@bp.route('/aliado/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('nit', '')
    datos = {
        'razon_social': request.form.get('razon_social', ''),
        'nombre_contacto': request.form.get('nombre_contacto', ''),
        'correo': request.form.get('correo', ''),
        'telefono': request.form.get('telefono', ''),
        'ciudad': request.form.get('ciudad', '')
    }
    
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('aliado.index'))

@bp.route('/aliado/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('nit', '')
    
    if not valor:
        flash('No se proporcionó NIT para eliminar.', 'danger')
        return redirect(url_for('aliado.index'))
    
    # Primero eliminar las alianzas asociadas
    try:
        aliado_id = int(valor)
        alianzas = api.listar_alianzas_aliado(aliado_id)
        for alianza in alianzas:
            api.eliminar_compuesta('alianza', ['aliado', 'departamento'], [alianza.get('aliado'), alianza.get('departamento')])
    except Exception as e:
        print(f"Error al eliminar alianzas: {e}")
    
    # Luego eliminar el aliado
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('aliado.index'))

# ============== RUTAS PARA ALIANZAS ==============

@bp.route('/api/aliado/<int:aliado_id>/alianzas', methods=['GET'])
def obtener_alianzas(aliado_id):
    """Obtener todas las alianzas de un aliado"""
    registros = api.listar_alianzas_aliado(aliado_id)
    return jsonify({'success': True, 'data': registros})

@bp.route('/api/alianza/crear', methods=['POST'])
def crear_alianza():
    """Crear alianza entre aliado y departamento"""
    data = request.json
    datos = {
        'aliado': data.get('aliado'),
        'departamento': data.get('departamento'),
        'fecha_inicio': data.get('fecha_inicio'),
        'fecha_fin': data.get('fecha_fin'),
        'docente': data.get('docente')
    }
    exito, mensaje = api.crear('alianza', datos)
    return jsonify({'success': exito, 'message': mensaje})

@bp.route('/api/alianza/eliminar', methods=['POST'])
def eliminar_alianza():
    """Eliminar alianza"""
    data = request.json
    exito, mensaje = api.eliminar_compuesta('alianza', ['aliado', 'departamento'], [data.get('aliado'), data.get('departamento')])
    return jsonify({'success': exito, 'message': mensaje})

@bp.route('/api/alianza/actualizar', methods=['POST'])
def actualizar_alianza():
    """Actualizar alianza"""
    data = request.json
    datos = {
        'aliado': data.get('aliado'),
        'departamento': data.get('departamento'),
        'fecha_inicio': data.get('fecha_inicio'),
        'fecha_fin': data.get('fecha_fin'),
        'docente': data.get('docente')
    }
    exito, mensaje = api.actualizar_compuesta('alianza', ['aliado', 'departamento'], [data.get('aliado'), data.get('departamento')], datos)
    return jsonify({'success': exito, 'message': mensaje})