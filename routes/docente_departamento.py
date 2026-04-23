from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import APIService

docente_departamento_bp = Blueprint('docente_departamento', __name__)
api_service = APIService()

@docente_departamento_bp.route('/')
def listar():
    exito, resultado = api_service.llamar_sp('sp_crud_docente_departamento', ['LISTAR'])
    relaciones = resultado if exito and isinstance(resultado, list) else []
    if not exito:
        flash(f'Error al cargar relaciones: {resultado}', 'danger')
    docentes = api_service.get_all('docente')
    programas = api_service.get_all('programa')
    return render_template('pages/docente_departamento.html',
                           relaciones=relaciones, docentes=docentes, programas=programas)

@docente_departamento_bp.route('/crear', methods=['POST'])
def crear():
    docente    = request.form.get('docente', type=int)
    depto      = request.form.get('departamento', type=int)
    dedicacion = request.form.get('dedicacion') or None
    modalidad  = request.form.get('modalidad') or None
    f_ingreso  = request.form.get('fecha_ingreso') or None
    f_salida   = request.form.get('fecha_salida') or None
    exito, resultado = api_service.llamar_sp(
        'sp_crud_docente_departamento',
        ['INSERT', docente, depto, dedicacion, modalidad, f_ingreso, f_salida]
    )
    if exito:
        flash('Asignación creada exitosamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')
    return redirect(url_for('docente_departamento.listar'))

@docente_departamento_bp.route('/editar/<int:docente>/<int:departamento>', methods=['POST'])
def editar(docente, departamento):
    dedicacion = request.form.get('dedicacion') or None
    modalidad  = request.form.get('modalidad') or None
    f_ingreso  = request.form.get('fecha_ingreso') or None
    f_salida   = request.form.get('fecha_salida') or None
    exito, resultado = api_service.llamar_sp(
        'sp_crud_docente_departamento',
        ['UPDATE', docente, departamento, dedicacion, modalidad, f_ingreso, f_salida]
    )
    if exito:
        flash('Asignación actualizada exitosamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')
    return redirect(url_for('docente_departamento.listar'))

@docente_departamento_bp.route('/eliminar/<int:docente>/<int:departamento>')
def eliminar(docente, departamento):
    exito, resultado = api_service.llamar_sp(
        'sp_crud_docente_departamento',
        ['DELETE', docente, departamento, None, None, None, None]
    )
    if exito:
        flash('Asignación eliminada exitosamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')
    return redirect(url_for('docente_departamento.listar'))
