from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import APIService

red_docente_bp = Blueprint('red_docente', __name__)
api_service = APIService()

@red_docente_bp.route('/')
def listar():
    exito, resultado = api_service.llamar_sp('sp_crud_red_docente', ['LISTAR'])
    redes_docentes = resultado if exito and isinstance(resultado, list) else []
    if not exito:
        flash(f'Error al cargar relaciones: {resultado}', 'danger')
    redes    = api_service.get_all('red')
    docentes = api_service.get_all('docente')
    return render_template('pages/red_docente.html',
                           redes_docentes=redes_docentes, redes=redes, docentes=docentes)

@red_docente_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        red           = request.form.get('red', type=int)
        docente       = request.form.get('docente', type=int)
        fecha_inicio  = request.form.get('fecha_inicio') or None
        fecha_fin     = request.form.get('fecha_fin') or None
        act_destacadas = request.form.get('act_destacadas') or None
        exito, resultado = api_service.llamar_sp(
            'sp_crud_red_docente',
            ['INSERT', red, docente, fecha_inicio, fecha_fin, act_destacadas]
        )
        if exito:
            flash('Relación red-docente creada exitosamente.', 'success')
        else:
            flash(f'Error: {resultado}', 'danger')
        return redirect(url_for('red_docente.listar'))

    redes   = api_service.get_all('red')
    docentes = api_service.get_all('docente')
    return render_template('pages/red_docente_form.html', redes=redes, docentes=docentes)

@red_docente_bp.route('/editar/<int:red>/<int:docente>', methods=['GET', 'POST'])
def editar(red, docente):
    if request.method == 'POST':
        fecha_inicio   = request.form.get('fecha_inicio') or None
        fecha_fin      = request.form.get('fecha_fin') or None
        act_destacadas = request.form.get('act_destacadas') or None
        exito, resultado = api_service.llamar_sp(
            'sp_crud_red_docente',
            ['UPDATE', red, docente, fecha_inicio, fecha_fin, act_destacadas]
        )
        if exito:
            flash('Relación red-docente actualizada exitosamente.', 'success')
        else:
            flash(f'Error: {resultado}', 'danger')
        return redirect(url_for('red_docente.listar'))

    # Cargar datos actuales para prellenar el formulario
    exito, relaciones = api_service.llamar_sp('sp_crud_red_docente', ['LISTAR'])
    red_docente_data = None
    if exito and isinstance(relaciones, list):
        matches = [r for r in relaciones if r['red'] == red and r['docente'] == docente]
        red_docente_data = matches[0] if matches else None
    redes   = api_service.get_all('red')
    docentes = api_service.get_all('docente')
    return render_template('pages/red_docente_form.html',
                           red_docente=red_docente_data, redes=redes, docentes=docentes)

@red_docente_bp.route('/eliminar/<int:red>/<int:docente>')
def eliminar(red, docente):
    exito, resultado = api_service.llamar_sp(
        'sp_crud_red_docente',
        ['DELETE', red, docente, None, None, None]
    )
    if exito:
        flash('Relación red-docente eliminada exitosamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')
    return redirect(url_for('red_docente.listar'))
