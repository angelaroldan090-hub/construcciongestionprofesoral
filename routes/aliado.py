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
    
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )
    
    # Obtener listas para selects
    departamentos = api.listar('programa')
    docentes = api.listar('docente')
    
    return render_template('pages/aliado.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        departamentos=departamentos,
        docentes=docentes
    )

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
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('aliado.index'))

# ============== NUEVAS RUTAS PARA ALIANZAS ==============

@bp.route('/api/aliado/<int:aliado_id>/alianzas', methods=['GET'])
def obtener_alianzas(aliado_id):
    """Obtener todas las alianzas de un aliado"""
    exito, resultado = api.ejecutar_procedimiento('select_alianza', [aliado_id, None])
    if exito:
        return jsonify({'success': True, 'data': resultado})
    return jsonify({'success': False, 'error': resultado})

@bp.route('/api/alianza/crear', methods=['POST'])
def crear_alianza():
    """Crear alianza entre aliado y departamento"""
    data = request.json
    params = [
        data.get('aliado'),
        data.get('departamento'),
        data.get('fecha_inicio'),
        data.get('fecha_fin'),
        data.get('docente')
    ]
    exito, mensaje = api.ejecutar_procedimiento('insert_alianza', params)
    return jsonify({'success': exito, 'message': mensaje})

@bp.route('/api/alianza/eliminar', methods=['POST'])
def eliminar_alianza():
    """Eliminar alianza"""
    data = request.json
    params = [data.get('aliado'), data.get('departamento')]
    exito, mensaje = api.ejecutar_procedimiento('delete_alianza', params)
    return jsonify({'success': exito, 'message': mensaje})

@bp.route('/api/alianza/actualizar', methods=['POST'])
def actualizar_alianza():
    """Actualizar alianza"""
    data = request.json
    params = [
        data.get('aliado'),
        data.get('departamento'),
        data.get('fecha_inicio'),
        data.get('fecha_fin'),
        data.get('docente')
    ]
    exito, mensaje = api.ejecutar_procedimiento('update_alianza', params)
    return jsonify({'success': exito, 'message': mensaje})