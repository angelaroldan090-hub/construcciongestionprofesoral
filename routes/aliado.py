"""
aliado.py - Blueprint para la tabla Aliado.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('aliado', __name__)
api = ApiService()

TABLA = 'aliado'
CLAVE = 'nit'  # Cambia a 'alc_id' si ese es el nombre en tu API

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
    
    return render_template('pages/aliado.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
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