from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

estudio_ac_bp = Blueprint('estudio_ac', __name__)
api_service = APIService()

@estudio_ac_bp.route('/')
def listar():
    relaciones = api_service.get_all('estudio_ac')
    return render_template('pages/estudio_ac.html', relaciones=relaciones)

@estudio_ac_bp.route('/crear', methods=['POST'])
def crear():
    data = {
        'estudio': request.form['estudio'],
        'area_conocimiento': request.form['area_conocimiento']
    }
    api_service.create('estudio_ac', data)
    return redirect(url_for('estudio_ac.listar'))

@estudio_ac_bp.route('/eliminar/<int:estudio>/<int:area_conocimiento>')
def eliminar(estudio, area_conocimiento):
    api_service.delete_estudio_ac(estudio, area_conocimiento)
    return redirect(url_for('estudio_ac.listar'))