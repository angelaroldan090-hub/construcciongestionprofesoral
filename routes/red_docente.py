"""
red_docente.py - Blueprint para la tabla intermedia red_docente (N:N entre red y docente)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
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
    
    return render_template('pages/red_docente.html',
        registros=registros,
        limite=limite,
        redes=redes,
        docentes=docentes
    )

@bp.route('/red_docente/crear', methods=['POST'])
def crear():
    datos = {
        'red': request.form.get('red', ''),
        'docente': request.form.get('docente', ''),
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
    datos = {
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'act_destacadas': request.form.get('act_destacadas', '')
    }
    
    exito, mensaje = api.actualizar_compuesta(TABLA, ['red', 'docente'], [red, docente], datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/eliminar', methods=['POST'])
def eliminar():
    red = request.form.get('red', '')
    docente = request.form.get('docente', '')
    
    exito, mensaje = api.eliminar_compuesta(TABLA, ['red', 'docente'], [red, docente])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))