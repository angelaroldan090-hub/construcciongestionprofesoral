from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

evaluacion_bp = Blueprint('evaluacion', __name__)
api_service = APIService()

@evaluacion_bp.route('/')
def listar():
    evaluaciones = api_service.get_all('evaluacion_docente')
    docentes = api_service.get_all('docente')
    return render_template('pages/evaluacion_docente.html', evaluaciones=evaluaciones, docentes=docentes)

@evaluacion_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'calificacion': float(request.form['calificacion']),
            'semestre': request.form['semestre'],
            'docente': int(request.form['docente'])
        }
        api_service.create('evaluacion_docente', data)
        return redirect(url_for('evaluacion.listar'))
    
    docentes = api_service.get_all('docente')
    return render_template('pages/evaluacion_docente_form.html', docentes=docentes)

@evaluacion_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        data = {
            'calificacion': float(request.form['calificacion']),
            'semestre': request.form['semestre'],
            'docente': int(request.form['docente'])
        }
        api_service.update('evaluacion_docente', id, data)
        return redirect(url_for('evaluacion.listar'))
    
    evaluacion = api_service.get_one('evaluacion_docente', id)
    docentes = api_service.get_all('docente')
    return render_template('pages/evaluacion_docente_form.html', evaluacion=evaluacion, docentes=docentes)

@evaluacion_bp.route('/eliminar/<int:id>')
def eliminar(id):
    api_service.delete('evaluacion_docente', id)
    return redirect(url_for('evaluacion.listar'))