from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from services.api_service import APIService

estudios_bp = Blueprint('estudios', __name__)
api_service = APIService()

@estudios_bp.route('/')
def listar():
    estudios = api_service.get_all('estudios_realizados')
    docentes = api_service.get_all('docente')
    areas = api_service.get_all('area_conocimiento')
    
    # Para cada estudio, obtener sus áreas de conocimiento asociadas
    for estudio in estudios:
        estudio['areas'] = api_service.get_areas_by_estudio(estudio['id'])
    
    return render_template('pages/estudios_realizados.html', 
                          estudios=estudios, 
                          docentes=docentes,
                          areas=areas)

@estudios_bp.route('/crear', methods=['POST'])
def crear():
    data = {
        'id': request.form['id'],
        'titulo': request.form['titulo'],
        'universidad': request.form['universidad'],
        'fecha': request.form['fecha'],
        'tipo': request.form['tipo'],
        'ciudad': request.form['ciudad'],
        'docente': request.form['docente'],
        'ins_acreditada': request.form['ins_acreditada'],
        'metodologia': request.form['metodologia'],
        'perfil_egresado': request.form['perfil_egresado'],
        'pais': request.form['pais']
    }
    api_service.create('estudios_realizados', data)
    return redirect(url_for('estudios.listar'))

@estudios_bp.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    data = {
        'titulo': request.form['titulo'],
        'universidad': request.form['universidad'],
        'fecha': request.form['fecha'],
        'tipo': request.form['tipo'],
        'ciudad': request.form['ciudad'],
        'docente': request.form['docente'],
        'ins_acreditada': request.form['ins_acreditada'],
        'metodologia': request.form['metodologia'],
        'perfil_egresado': request.form['perfil_egresado'],
        'pais': request.form['pais']
    }
    api_service.update('estudios_realizados', id, data)
    return redirect(url_for('estudios.listar'))

@estudios_bp.route('/eliminar/<int:id>')
def eliminar(id):
    api_service.delete('estudios_realizados', id)
    return redirect(url_for('estudios.listar'))

@estudios_bp.route('/ver/<int:id>')
def ver(id):
    estudio = api_service.get_one('estudios_realizados', id)
    estudio['areas'] = api_service.get_areas_by_estudio(id)
    return jsonify(estudio)

@estudios_bp.route('/asignar_area', methods=['POST'])
def asignar_area():
    data = {
        'estudio': request.form['estudio'],
        'area_conocimiento': request.form['area_conocimiento']
    }
    api_service.asignar_area_a_estudio(data)
    return redirect(url_for('estudios.listar'))

@estudios_bp.route('/eliminar_area/<int:estudio>/<int:area>')
def eliminar_area(estudio, area):
    api_service.eliminar_area_de_estudio(estudio, area)
    return redirect(url_for('estudios.listar'))