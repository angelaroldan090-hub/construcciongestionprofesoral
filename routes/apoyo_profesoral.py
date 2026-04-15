"""
apoyo_profesoral.py - Blueprint para la tabla Apoyo Profesoral (depende de estudios_realizados)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('apoyo_profesoral', __name__)
api = ApiService()

TABLA = 'apoyo_profesoral'
CLAVE = 'estudios'

@bp.route('/apoyo_profesoral')
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
    
    # Obtener datos para selects
    estudios = api.listar('estudios_realizados')
    
    return render_template('pages/apoyo_profesoral.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        estudios=estudios
    )

@bp.route('/apoyo_profesoral/crear', methods=['POST'])
def crear():
    datos = {
        'estudios': request.form.get('estudios', ''),
        'con_apoyo': request.form.get('con_apoyo') == 'true',
        'institucion': request.form.get('institucion', ''),
        'tipo': request.form.get('tipo', '')
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('apoyo_profesoral.index'))

@bp.route('/apoyo_profesoral/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('estudios', '')
    datos = {
        'con_apoyo': request.form.get('con_apoyo') == 'true',
        'institucion': request.form.get('institucion', ''),
        'tipo': request.form.get('tipo', '')
    }
    
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('apoyo_profesoral.index'))

@bp.route('/apoyo_profesoral/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('estudios', '')
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('apoyo_profesoral.index'))