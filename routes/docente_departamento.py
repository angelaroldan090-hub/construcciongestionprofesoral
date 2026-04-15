"""
docente_departamento.py - Blueprint para la tabla Docente Departamento (depende de docente)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('docente_departamento', __name__)
api = ApiService()

TABLA = 'docente_departamento'
CLAVE_COMPUESTA = ['docente', 'departamento']

@bp.route('/docente_departamento')
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
            (r for r in registros if f"{r.get('docente')}|{r.get('departamento')}" == valor_clave),
            None
        )
    
    # Obtener datos para selects
    docentes = api.listar('docente')
    
    return render_template('pages/docente_departamento.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        docentes=docentes
    )

@bp.route('/docente_departamento/crear', methods=['POST'])
def crear():
    datos = {
        'docente': request.form.get('docente', ''),
        'departamento': request.form.get('departamento', ''),
        'dedicacion': request.form.get('dedicacion', ''),
        'modalidad': request.form.get('modalidad', ''),
        'fecha_ingreso': request.form.get('fecha_ingreso', ''),
        'fecha_salida': request.form.get('fecha_salida', '') or None
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente_departamento.index'))

@bp.route('/docente_departamento/actualizar', methods=['POST'])
def actualizar():
    docente = request.form.get('docente', '')
    departamento = request.form.get('departamento', '')
    datos = {
        'dedicacion': request.form.get('dedicacion', ''),
        'modalidad': request.form.get('modalidad', ''),
        'fecha_ingreso': request.form.get('fecha_ingreso', ''),
        'fecha_salida': request.form.get('fecha_salida', '') or None
    }
    
    exito, mensaje = api.actualizar_compuesta(TABLA, ['docente', 'departamento'], [docente, departamento], datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente_departamento.index'))

@bp.route('/docente_departamento/eliminar', methods=['POST'])
def eliminar():
    docente = request.form.get('docente', '')
    departamento = request.form.get('departamento', '')
    
    exito, mensaje = api.eliminar_compuesta(TABLA, ['docente', 'departamento'], [docente, departamento])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente_departamento.index'))