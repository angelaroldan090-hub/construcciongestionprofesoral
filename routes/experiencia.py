from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

experiencia_bp = Blueprint('experiencia', __name__)
api_service = APIService()

@experiencia_bp.route('/')
def listar():
    experiencias = api_service.get_all('experiecia')  # Nota: typo en el nombre de la tabla
    return render_template('pages/experiencia.html', experiencias=experiencias)

@experiencia_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'nombre_cargo': request.form['nombre_cargo'],
            'institucion': request.form['institucion'],
            'tipo': request.form['tipo'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_fin': request.form.get('fecha_fin', ''),
            'docente': request.form['docente']
        }
        api_service.create('experiecia', data)
        return redirect(url_for('experiencia.listar'))
    
    docentes = api_service.get_all('docente')
    return render_template('pages/experiencia_form.html', docentes=docentes)

@experiencia_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        data = {
            'nombre_cargo': request.form['nombre_cargo'],
            'institucion': request.form['institucion'],
            'tipo': request.form['tipo'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_fin': request.form.get('fecha_fin', ''),
            'docente': request.form['docente']
        }
        api_service.update('experiecia', id, data)
        return redirect(url_for('experiencia.listar'))
    
    experiencia = api_service.get_one('experiecia', id)
    docentes = api_service.get_all('docente')
    return render_template('pages/experiencia_form.html', experiencia=experiencia, docentes=docentes)

@experiencia_bp.route('/eliminar/<int:id>')
def eliminar(id):
    api_service.delete('experiecia', id)
    return redirect(url_for('experiencia.listar'))