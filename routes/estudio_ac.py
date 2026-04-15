"""
estudio_ac.py - Blueprint para la tabla intermedia estudio_ac (N:N entre estudios_realizados y area_conocimiento)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.api_service import ApiService

bp = Blueprint('estudio_ac', __name__)
api = ApiService()

TABLA = 'estudio_ac'
CLAVE_COMPUESTA = ['estudio', 'area_conocimiento']

@bp.route('/estudio_ac')
def index():
    limite = request.args.get('limite', type=int)
    registros = api.listar(TABLA, limite)
    
    # Obtener datos para selects
    estudios = api.listar('estudios_realizados')
    areas_conocimiento = api.listar('area_conocimiento')
    
    return render_template('pages/estudio_ac.html',
        registros=registros,
        limite=limite,
        estudios=estudios,
        areas_conocimiento=areas_conocimiento
    )

@bp.route('/estudio_ac/crear', methods=['POST'])
def crear():
    datos = {
        'estudio': request.form.get('estudio', ''),
        'area_conocimiento': request.form.get('area_conocimiento', '')
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('estudio_ac.index'))

@bp.route('/estudio_ac/eliminar', methods=['POST'])
def eliminar():
    estudio = request.form.get('estudio', '')
    area_conocimiento = request.form.get('area_conocimiento', '')
    
    # Para eliminar en tabla con PK compuesta, enviamos ambos valores
    exito, mensaje = api.eliminar_compuesta(TABLA, ['estudio', 'area_conocimiento'], [estudio, area_conocimiento])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('estudio_ac.index'))