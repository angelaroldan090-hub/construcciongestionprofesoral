from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

programa_bp = Blueprint('programa', __name__)
api_service = APIService()

@programa_bp.route('/')
def listar():
    programas = api_service.get_all('programa')
    return render_template('pages/programa.html', programas=programas)

@programa_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'id': request.form['id'],
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'nivel': request.form['nivel'],
            'fecha_creacion': request.form['fecha_creacion'],
            'fecha_cierre': request.form.get('fecha_cierre', ''),
            'numero_cohortes': request.form['numero_cohortes'],
            'cant_graduados': request.form['cant_graduados'],
            'fecha_actualizacion': request.form['fecha_actualizacion'],
            'ciudad': request.form['ciudad'],
            'facultad': request.form['facultad']
        }
        api_service.create('programa', data)
        return redirect(url_for('programa.listar'))
    return render_template('pages/programa_form.html')

@programa_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'nivel': request.form['nivel'],
            'fecha_creacion': request.form['fecha_creacion'],
            'fecha_cierre': request.form.get('fecha_cierre', ''),
            'numero_cohortes': request.form['numero_cohortes'],
            'cant_graduados': request.form['cant_graduados'],
            'fecha_actualizacion': request.form['fecha_actualizacion'],
            'ciudad': request.form['ciudad'],
            'facultad': request.form['facultad']
        }
        api_service.update('programa', id, data)
        return redirect(url_for('programa.listar'))
    
    programa = api_service.get_one('programa', id)
    return render_template('pages/programa_form.html', programa=programa)

@programa_bp.route('/eliminar/<int:id>')
def eliminar(id):
    api_service.delete('programa', id)
    return redirect(url_for('programa.listar'))