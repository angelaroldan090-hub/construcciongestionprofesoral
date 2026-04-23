from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

area_bp = Blueprint('area', __name__)
api_service = APIService()

@area_bp.route('/')
def listar():
    areas = api_service.get_all('area_conocimiento')
    return render_template('pages/area_conocimiento.html', areas=areas)

@area_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'id': request.form['id'],
            'gran_area': request.form['gran_area'],
            'area': request.form['area'],
            'disciplina': request.form['disciplina']
        }
        api_service.create('area_conocimiento', data)
        return redirect(url_for('area.listar'))
    return render_template('pages/area_conocimiento_form.html')

@area_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        data = {
            'gran_area': request.form['gran_area'],
            'area': request.form['area'],
            'disciplina': request.form['disciplina']
        }
        api_service.update('area_conocimiento', id, data)
        return redirect(url_for('area.listar'))
    
    area = api_service.get_one('area_conocimiento', id)
    return render_template('pages/area_conocimiento_form.html', area=area)

@area_bp.route('/eliminar/<int:id>')
def eliminar(id):
    api_service.delete('area_conocimiento', id)
    return redirect(url_for('area.listar'))