from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

termino_bp = Blueprint('termino', __name__)
api_service = APIService()

@termino_bp.route('/')
def listar():
    terminos = api_service.get_all('termino_clave')
    return render_template('pages/termino_clave.html', terminos=terminos)

@termino_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'termino': request.form['termino'],
            'termino_ingles': request.form.get('termino_ingles', '')
        }
        api_service.create('termino_clave', data)
        return redirect(url_for('termino.listar'))
    return render_template('pages/termino_clave_form.html')

@termino_bp.route('/editar/<string:termino>', methods=['GET', 'POST'])
def editar(termino):
    if request.method == 'POST':
        data = {
            'termino_ingles': request.form.get('termino_ingles', '')
        }
        api_service.update('termino_clave', termino, data)
        return redirect(url_for('termino.listar'))
    
    termino_data = api_service.get_one('termino_clave', termino)
    return render_template('pages/termino_clave_form.html', termino=termino_data)

@termino_bp.route('/eliminar/<string:termino>')
def eliminar(termino):
    api_service.delete('termino_clave', termino)
    return redirect(url_for('termino.listar'))