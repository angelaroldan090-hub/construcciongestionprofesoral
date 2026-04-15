"""
evaluacion_docente.py - Blueprint para la tabla Evaluacion Docente (depende de docente)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('evaluacion_docente', __name__)
api = ApiService()

TABLA = 'evaluacion_docente'
CLAVE = 'id'

@bp.route('/evaluacion_docente')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')
    
    registros = api.listar(TABLA, limite)
    
    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'
    
    registro = None
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )
    
    # Obtener datos para selects
    docentes = api.listar('docente')
    
    return render_template('pages/evaluacion_docente.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        docentes=docentes
    )

@bp.route('/evaluacion_docente/crear', methods=['POST'])
def crear():
    datos = {
        'docente': request.form.get('docente', ''),
        'calificacion': request.form.get('calificacion', ''),
        'semestre': request.form.get('semestre', '')
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('evaluacion_docente.index'))

@bp.route('/evaluacion_docente/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', '')
    datos = {
        'docente': request.form.get('docente', ''),
        'calificacion': request.form.get('calificacion', ''),
        'semestre': request.form.get('semestre', '')
    }
    
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('evaluacion_docente.index'))

@bp.route('/evaluacion_docente/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('id', '')
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('evaluacion_docente.index'))