from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from services.api_service import APIService

# Crear el blueprint con el nombre correcto
docente_bp = Blueprint('docente', __name__)
api_service = APIService()

@docente_bp.route('/')
def listar():
    docentes = api_service.get_all('docente')
    lineas = api_service.get_all('linea_investigacion')
    return render_template('pages/docente.html', docentes=docentes, lineas=lineas)

@docente_bp.route('/crear', methods=['POST'])
def crear():
    data = {
        'cedula': request.form['cedula'],
        'nombres': request.form['nombres'],
        'apellidos': request.form['apellidos'],
        'genero': request.form['genero'],
        'cargo': request.form['cargo'],
        'fecha_nacimiento': request.form['fecha_nacimiento'],
        'correo': request.form['correo'],
        'telefono': request.form['telefono'],
        'url_cvlac': request.form['url_cvlac'],
        'fecha_actualizacion': request.form['fecha_actualizacion'],
        'escalafon': request.form['escalafon'],
        'perfil': request.form['perfil'],
        'cat_minciencia': request.form.get('cat_minciencia', ''),
        'conv_minciencia': request.form['conv_minciencia'],
        'nacionalidaad': request.form['nacionalidaad'],
        'linea_investigacion_principal': request.form.get('linea_investigacion_principal', '')
    }
    api_service.create('docente', data)
    return redirect(url_for('docente.listar'))

@docente_bp.route('/editar/<int:cedula>', methods=['POST'])
def editar(cedula):
    data = {
        'nombres': request.form['nombres'],
        'apellidos': request.form['apellidos'],
        'genero': request.form['genero'],
        'cargo': request.form['cargo'],
        'fecha_nacimiento': request.form['fecha_nacimiento'],
        'correo': request.form['correo'],
        'telefono': request.form['telefono'],
        'url_cvlac': request.form['url_cvlac'],
        'fecha_actualizacion': request.form['fecha_actualizacion'],
        'escalafon': request.form['escalafon'],
        'perfil': request.form['perfil'],
        'cat_minciencia': request.form.get('cat_minciencia', ''),
        'conv_minciencia': request.form['conv_minciencia'],
        'nacionalidaad': request.form['nacionalidaad'],
        'linea_investigacion_principal': request.form.get('linea_investigacion_principal', '')
    }
    api_service.update('docente', cedula, data)
    return redirect(url_for('docente.listar'))

@docente_bp.route('/eliminar/<int:cedula>')
def eliminar(cedula):
    api_service.delete('docente', cedula)
    return redirect(url_for('docente.listar'))

@docente_bp.route('/ver/<int:cedula>')
def ver(cedula):
    docente = api_service.get_one('docente', cedula)
    return jsonify(docente)