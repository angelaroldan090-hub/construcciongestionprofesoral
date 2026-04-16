"""
estudio_ac.py - Blueprint para la tabla intermedia estudio_ac (N:N entre estudios_realizados y area_conocimiento)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
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
            estudio_id, area_id = clave.split('|')
            # Buscar el registro correspondiente
            for r in registros:
                if str(r.get('estudio')) == str(estudio_id) and str(r.get('area_conocimiento')) == str(area_id):
                    registro = r
                    break
            mostrar_formulario = True
            editando = True
        except Exception:
            pass
    
    return render_template('pages/estudio_ac.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
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

@bp.route('/estudio_ac/actualizar', methods=['POST'])
def actualizar():
    estudio = request.form.get('estudio', '')
    area_conocimiento = request.form.get('area_conocimiento', '')
    
    # Para claves compuestas, usar DELETE + CREATE
    exito_eliminar, _ = api.eliminar_compuesta(TABLA, ['estudio', 'area_conocimiento'], [estudio, area_conocimiento])
    
    if exito_eliminar:
        datos = {
            'estudio': estudio,
            'area_conocimiento': area_conocimiento
        }
        exito_crear, mensaje = api.crear(TABLA, datos)
        flash('Registro actualizado exitosamente.' if exito_crear else f'Error: {mensaje}',
              'success' if exito_crear else 'danger')
    else:
        flash('Error al actualizar el registro.', 'danger')
    
    return redirect(url_for('estudio_ac.index'))

@bp.route('/estudio_ac/eliminar', methods=['POST'])
def eliminar():
    estudio = request.form.get('estudio', '')
    area_conocimiento = request.form.get('area_conocimiento', '')
    
    exito, mensaje = api.eliminar_compuesta(TABLA, ['estudio', 'area_conocimiento'], [estudio, area_conocimiento])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('estudio_ac.index'))