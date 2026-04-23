from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

beca_bp = Blueprint('beca', __name__)
api_service = APIService()

@beca_bp.route('/')
def listar():
    becas = api_service.get_all('beca')
    return render_template('pages/beca.html', becas=becas)

@beca_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'estudios': request.form['estudios'],
            'tipo': request.form['tipo'],
            'institucion': request.form['institucion'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_fin': request.form.get('fecha_fin', '')
        }
        api_service.create('beca', data)
        return redirect(url_for('beca.listar'))
    
    estudios = api_service.get_all('estudios_realizados')
    return render_template('pages/beca_form.html', estudios=estudios)

@beca_bp.route('/editar/<int:estudios>', methods=['GET', 'POST'])
def editar(estudios):
    if request.method == 'POST':
        data = {
            'tipo': request.form['tipo'],
            'institucion': request.form['institucion'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_fin': request.form.get('fecha_fin', '')
        }
        api_service.update('beca', estudios, data)
        return redirect(url_for('beca.listar'))
    
    beca = api_service.get_one('beca', estudios)
    estudios_list = api_service.get_all('estudios_realizados')
    return render_template('pages/beca_form.html', beca=beca, estudios=estudios_list)

@beca_bp.route('/eliminar/<int:estudios>')
def eliminar(estudios):
    api_service.delete('beca', estudios)
    return redirect(url_for('beca.listar'))