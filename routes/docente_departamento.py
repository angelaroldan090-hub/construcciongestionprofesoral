from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

docente_departamento_bp = Blueprint('docente_departamento', __name__)
api_service = APIService()

@docente_departamento_bp.route('/')
def listar():
    relaciones = api_service.get_all('docente_departamento')
    return render_template('pages/docente_departamento.html', relaciones=relaciones)

@docente_departamento_bp.route('/crear', methods=['POST'])
def crear():
    data = {
        'docente': request.form['docente'],
        'departamento': request.form['departamento'],
        'dedicacion': request.form['dedicacion'],
        'modalidad': request.form['modalidad'],
        'fecha_ingreso': request.form['fecha_ingreso'],
        'fecha_salida': request.form.get('fecha_salida', '')
    }
    api_service.create('docente_departamento', data)
    return redirect(url_for('docente_departamento.listar'))

@docente_departamento_bp.route('/editar/<int:docente>/<int:departamento>', methods=['POST'])
def editar(docente, departamento):
    data = {
        'dedicacion': request.form['dedicacion'],
        'modalidad': request.form['modalidad'],
        'fecha_ingreso': request.form['fecha_ingreso'],
        'fecha_salida': request.form.get('fecha_salida', '')
    }
    api_service.update_docente_departamento(docente, departamento, data)
    return redirect(url_for('docente_departamento.listar'))

@docente_departamento_bp.route('/eliminar/<int:docente>/<int:departamento>')
def eliminar(docente, departamento):
    api_service.delete_docente_departamento(docente, departamento)
    return redirect(url_for('docente_departamento.listar'))