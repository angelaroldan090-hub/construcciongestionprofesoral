from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from services.api_service import APIService

docentes_estudios_bp = Blueprint('docentes_estudios', __name__)
api_service = APIService()

@docentes_estudios_bp.route('/')
def listar():
    # Obtener todos los docentes con sus estudios
    docentes = api_service.get_all('docente')
    for docente in docentes:
        docente['estudios'] = api_service.get_estudios_by_docente(docente['cedula'])
    return render_template('pages/docentes_estudios.html', docentes=docentes)

@docentes_estudios_bp.route('/asignar', methods=['POST'])
def asignar():
    data = {
        'docente': request.form['docente'],
        'estudio': request.form['estudio']
    }
    api_service.asignar_estudio(data)
    return redirect(url_for('docentes_estudios.listar'))

@docentes_estudios_bp.route('/eliminar_asignacion/<int:docente>/<int:estudio>')
def eliminar_asignacion(docente, estudio):
    api_service.eliminar_asignacion_estudio(docente, estudio)
    return redirect(url_for('docentes_estudios.listar'))