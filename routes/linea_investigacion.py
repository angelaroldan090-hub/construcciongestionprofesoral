from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

linea_bp = Blueprint('linea', __name__)
api_service = APIService()

@linea_bp.route('/')
def listar():
    lineas = api_service.get_all('linea_investigacion')
    return render_template('pages/linea_investigacion.html', lineas=lineas)

@linea_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'descripcion': request.form['descripcion']
        }
        api_service.create('linea_investigacion', data)
        return redirect(url_for('linea.listar'))
    return render_template('pages/linea_investigacion_form.html')

@linea_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'descripcion': request.form['descripcion']
        }
        api_service.update('linea_investigacion', id, data)
        return redirect(url_for('linea.listar'))
    
    linea = api_service.get_one('linea_investigacion', id)
    return render_template('pages/linea_investigacion_form.html', linea=linea)

@linea_bp.route('/eliminar/<int:id>')
def eliminar(id):
    api_service.delete('linea_investigacion', id)
    return redirect(url_for('linea.listar'))