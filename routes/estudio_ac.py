from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import APIService

estudio_ac_bp = Blueprint('estudio_ac', __name__)
api_service = APIService()

@estudio_ac_bp.route('/')
def listar():
    exito, resultado = api_service.llamar_sp('sp_crud_estudio_ac', ['LISTAR'])
    relaciones = resultado if exito and isinstance(resultado, list) else []
    if not exito:
        flash(f'Error al cargar relaciones: {resultado}', 'danger')

    estudios = api_service.get_all('estudios_realizados')
    areas    = api_service.get_all('area_conocimiento')

    # Agrupar áreas por estudio (para la vista acordeón)
    areas_por_estudio = defaultdict(list)
    for rel in relaciones:
        areas_por_estudio[rel['estudio']].append({
            'id':         rel['area_conocimiento'],
            'gran_area':  rel.get('gran_area', ''),
            'area':       rel.get('area_nombre', ''),
            'disciplina': rel.get('disciplina', ''),
        })
    for estudio in estudios:
        estudio['areas'] = areas_por_estudio.get(estudio['id'], [])

    return render_template('pages/estudio_ac.html',
                           relaciones=relaciones, estudios=estudios, areas=areas)

@estudio_ac_bp.route('/crear', methods=['POST'])
def crear():
    estudio         = request.form.get('estudio', type=int)
    area_conocimiento = request.form.get('area_conocimiento', type=int)
    exito, resultado = api_service.llamar_sp(
        'sp_crud_estudio_ac', ['INSERT', estudio, area_conocimiento]
    )
    if exito:
        flash('Relación estudio-área creada exitosamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')
    return redirect(url_for('estudio_ac.listar'))

@estudio_ac_bp.route('/eliminar/<int:estudio>/<int:area_conocimiento>')
def eliminar(estudio, area_conocimiento):
    exito, resultado = api_service.llamar_sp(
        'sp_crud_estudio_ac', ['DELETE', estudio, area_conocimiento]
    )
    if exito:
        flash('Relación estudio-área eliminada exitosamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')
    return redirect(url_for('estudio_ac.listar'))
