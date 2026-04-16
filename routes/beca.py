"""
beca.py - Blueprint para la tabla Beca (depende de estudios_realizados)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('beca', __name__)
api = ApiService()

TABLA = 'beca'
CLAVE = 'estudios'

@bp.route('/beca')
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
    estudios = api.listar('estudios_realizados')
    estudios_por_id = {str(e.get('id')): e for e in estudios}

    # Unir cada beca con el estudio correspondiente para mostrar el título y la universidad
    for registro_beca in registros:
        estudio_id = str(registro_beca.get('estudios') or registro_beca.get('estudio') or '')
        estudio_relacionado = estudios_por_id.get(estudio_id)
        if estudio_relacionado:
            registro_beca['estudio_titulo'] = estudio_relacionado.get('titulo')
            registro_beca['estudio_universidad'] = estudio_relacionado.get('universidad')

    return render_template('pages/beca.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        estudios=estudios
    )

@bp.route('/beca/crear', methods=['POST'])
def crear():
    datos = {
        'estudios': request.form.get('estudios', ''),
        'tipo': request.form.get('tipo', ''),
        'institucion': request.form.get('institucion', ''),
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('beca.index'))

@bp.route('/beca/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('estudios', '')
    datos = {
        'tipo': request.form.get('tipo', ''),
        'institucion': request.form.get('institucion', ''),
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None
    }
    
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('beca.index'))

@bp.route('/beca/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('estudios', '')
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('beca.index'))