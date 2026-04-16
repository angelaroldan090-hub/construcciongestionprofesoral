"""
red_docente.py - Blueprint para la tabla intermedia red_docente (N:N entre red y docente)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('red_docente', __name__)
api = ApiService()

TABLA = 'red_docente'
CLAVE_COMPUESTA = ['red', 'docente']

@bp.route('/red_docente')
def index():
    limite = request.args.get('limite', type=int)
    registros = api.listar(TABLA, limite)
    redes = api.listar('red')
    docentes = api.listar('docente')

    # Manejo de formulario modal
    accion = request.args.get('accion')
    clave = request.args.get('clave')
    mostrar_formulario = False
    editando = False
    registro = None

    if accion == 'nuevo':
        mostrar_formulario = True
        editando = False
    elif accion == 'editar' and clave:
        try:
            red_id, docente_id = clave.split('|')
            # Buscar el registro correspondiente
            for r in registros:
                if str(r.get('red')) == str(red_id) and str(r.get('docente')) == str(docente_id):
                    registro = r
                    break
            mostrar_formulario = True
            editando = True
        except Exception:
            pass

    return render_template('pages/red_docente.html',
        registros=registros,
        limite=limite,
        redes=redes,
        docentes=docentes,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro
    )

@bp.route('/red_docente/crear', methods=['POST'])
def crear():
    datos = {
        'red': request.form.get('red', ''),
        'docente': request.form.get('docente', ''),
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'act_destacadas': request.form.get('act_destacadas', '')
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/actualizar', methods=['POST'])
def actualizar():
    red = request.form.get('red', '')
    docente = request.form.get('docente', '')
    datos = {
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'act_destacadas': request.form.get('act_destacadas', '')
    }
    
    exito, mensaje = api.actualizar_compuesta(TABLA, ['red', 'docente'], [red, docente], datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/eliminar', methods=['POST'])
def eliminar():
    red = request.form.get('red', '')
    docente = request.form.get('docente', '')
    
    exito, mensaje = api.eliminar_compuesta(TABLA, ['red', 'docente'], [red, docente])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))