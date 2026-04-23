from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

red_docente_bp = Blueprint('red_docente', __name__)
api_service = APIService()

@red_docente_bp.route('/')
def listar():
    redes_docentes = api_service.get_all('red_docente')
    return render_template('pages/red_docente.html', redes_docentes=redes_docentes)

@red_docente_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'red': request.form['red'],
            'docente': request.form['docente'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_fin': request.form.get('fecha_fin', ''),
            'act_destacadas': request.form['act_destacadas']
        }
        api_service.create('red_docente', data)
        return redirect(url_for('red_docente.listar'))
    
    redes = api_service.get_all('red')
    docentes = api_service.get_all('docente')
    return render_template('pages/red_docente_form.html', redes=redes, docentes=docentes)

@red_docente_bp.route('/editar/<int:red>/<int:docente>', methods=['GET', 'POST'])
def editar(red, docente):
    if request.method == 'POST':
        data = {
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_fin': request.form.get('fecha_fin', ''),
            'act_destacadas': request.form['act_destacadas']
        }
        api_service.update_red_docente(red, docente, data)
        return redirect(url_for('red_docente.listar'))
    
    red_docente = api_service.get_red_docente(red, docente)
    redes = api_service.get_all('red')
    docentes = api_service.get_all('docente')
    return render_template('pages/red_docente_form.html', red_docente=red_docente, redes=redes, docentes=docentes)

@red_docente_bp.route('/eliminar/<int:red>/<int:docente>')
def eliminar(red, docente):
    api_service.delete_red_docente(red, docente)
    return redirect(url_for('red_docente.listar'))