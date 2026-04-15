"""
docente.py - Blueprint para la tabla Docente.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
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
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )
    
    # Obtener listas para selects (líneas de investigación)
    lineas = api.listar('linea_investigacion')
    
    return render_template('pages/docente.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        lineas=lineas
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