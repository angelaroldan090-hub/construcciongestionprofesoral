from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

reconocimiento_bp = Blueprint('reconocimiento', __name__)
api_service = APIService()

@reconocimiento_bp.route('/')
def listar():
    reconocimientos = api_service.get_all('reconocimiento')
    docentes = api_service.get_all('docente')
    return render_template('pages/reconocimiento.html', reconocimientos=reconocimientos, docentes=docentes)

@reconocimiento_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'tipo': request.form['tipo'],
            'fecha': request.form['fecha'],
            'institucion': request.form['institucion'],
            'nombre': request.form['nombre'],
            'ambito': request.form['ambito'],
            'docente': request.form['docente']
        }
        api_service.create('reconocimiento', data)
        return redirect(url_for('reconocimiento.listar'))
    
    docentes = api_service.get_all('docente')
    return render_template('pages/reconocimiento_form.html', docentes=docentes)

@reconocimiento_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        data = {
            'tipo': request.form['tipo'],
            'fecha': request.form['fecha'],
            'institucion': request.form['institucion'],
            'nombre': request.form['nombre'],
            'ambito': request.form['ambito'],
            'docente': request.form['docente']
        }
        api_service.update('reconocimiento', id, data)
        return redirect(url_for('reconocimiento.listar'))
    
    reconocimiento = api_service.get_one('reconocimiento', id)
    docentes = api_service.get_all('docente')
    return render_template('pages/reconocimiento_form.html', reconocimiento=reconocimiento, docentes=docentes)

@reconocimiento_bp.route('/eliminar/<int:id>')
def eliminar(id):
    api_service.delete('reconocimiento', id)
    return redirect(url_for('reconocimiento.listar'))
