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
    
    # Obtener listas para selects
    lineas = api.listar('linea_investigacion')
    departamentos = api.listar('programa')  # Los departamentos son programas
    
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

# ============== NUEVAS RUTAS PARA VINCULACIONES ==============

@bp.route('/api/docente/<int:docente_id>/vinculaciones', methods=['GET'])
def obtener_vinculaciones(docente_id):
    """Obtener todas las vinculaciones de un docente"""
    registros = api.listar_vinculaciones_docente(docente_id)
    return jsonify({'success': True, 'data': registros})

@bp.route('/api/docente_vinculacion/crear', methods=['POST'])
def crear_vinculacion():
    """Crear vinculación docente-departamento"""
    data = request.json
    datos = {
        'docente': data.get('docente'),
        'departamento': data.get('departamento'),
        'dedicacion': data.get('dedicacion'),
        'modalidad': data.get('modalidad'),
        'fecha_ingreso': data.get('fecha_ingreso'),
        'fecha_salida': data.get('fecha_salida')
    }
    exito, mensaje = api.crear('docente_departamento', datos)
    return jsonify({'success': exito, 'message': mensaje})

@bp.route('/api/docente_vinculacion/eliminar', methods=['POST'])
def eliminar_vinculacion():
    """Eliminar vinculación docente-departamento"""
    data = request.json
    exito, mensaje = api.eliminar_compuesta('docente_departamento', ['docente', 'departamento'], [data.get('docente'), data.get('departamento')])
    return jsonify({'success': exito, 'message': mensaje})

@bp.route('/api/docente_vinculacion/actualizar', methods=['POST'])
def actualizar_vinculacion():
    """Actualizar vinculación docente-departamento"""
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