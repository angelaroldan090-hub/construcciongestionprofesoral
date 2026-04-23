from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

apoyo_bp = Blueprint('apoyo', __name__)
api_service = APIService()

@apoyo_bp.route('/')
def listar():
    apoyos = api_service.get_all('apoyo_profesoral')
    return render_template('pages/apoyo_profesoral.html', apoyos=apoyos)

@apoyo_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'estudios': request.form['estudios'],
            'con_apoyo': request.form['con_apoyo'],
            'institucion': request.form['institucion'],
            'tipo': request.form['tipo']
        }
        api_service.create('apoyo_profesoral', data)
        return redirect(url_for('apoyo.listar'))
    
    estudios = api_service.get_all('estudios_realizados')
    return render_template('pages/apoyo_profesoral_form.html', estudios=estudios)

@apoyo_bp.route('/editar/<int:estudios>', methods=['GET', 'POST'])
def editar(estudios):
    if request.method == 'POST':
        data = {
            'con_apoyo': request.form['con_apoyo'],
            'institucion': request.form['institucion'],
            'tipo': request.form['tipo']
        }
        api_service.update('apoyo_profesoral', estudios, data)
        return redirect(url_for('apoyo.listar'))
    
    apoyo = api_service.get_one('apoyo_profesoral', estudios)
    estudios_list = api_service.get_all('estudios_realizados')
    return render_template('pages/apoyo_profesoral_form.html', apoyo=apoyo, estudios=estudios_list)

@apoyo_bp.route('/eliminar/<int:estudios>')
def eliminar(estudios):
    api_service.delete('apoyo_profesoral', estudios)
    return redirect(url_for('apoyo.listar'))