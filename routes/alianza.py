"""
alianza.py - Blueprint para la tabla Alianza (depende de aliado, docente)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('alianza', __name__)
api = ApiService()

TABLA = 'alianza'
CLAVE_COMPUESTA = ['aliado', 'departamento']

@bp.route('/alianza')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')
    
    registros = api.listar(TABLA, limite)
    
    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'
    
    registro = None
    if editando and valor_clave:
        # Buscar por clave compuesta (aliado|departamento)
        registro = next(
            (r for r in registros if f"{r.get('aliado')}|{r.get('departamento')}" == valor_clave),
            None
        )
    
    # Obtener datos para selects
        aliados = api.listar('aliado')
        docentes = api.listar('docente')
        departamentos = api.listar('programa')
        
        
        return render_template('pages/alianza.html',
            registros=registros,
            mostrar_formulario=mostrar_formulario,
            editando=editando,
            registro=registro,
            limite=limite,
            aliados=aliados,
            docentes=docentes,
            departamentos=departamentos
        )

@bp.route('/alianza/crear', methods=['POST'])
def crear():
    datos = {
        'aliado': request.form.get('aliado', ''),
        'departamento': request.form.get('departamento', ''),
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'docente': request.form.get('docente', '') or None
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('alianza.index'))

@bp.route('/alianza/actualizar', methods=['POST'])
def actualizar():
    aliado = request.form.get('aliado', '')
    departamento = request.form.get('departamento', '')

    try:
        aliado_id = int(aliado)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de aliado o departamento inválido.', 'danger')
        return redirect(url_for('alianza.index'))

    datos = {
        'aliado': aliado_id,
        'departamento': departamento_id,
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', '') or None,
        'docente': request.form.get('docente', '') or None
    }

    exito_eliminar, _ = api.eliminar_compuesta(TABLA, ['aliado', 'departamento'], [aliado_id, departamento_id])

    if exito_eliminar:
        exito_crear, mensaje = api.crear(TABLA, datos)
        flash('Alianza actualizada exitosamente.' if exito_crear else f'Error al recrear: {mensaje}',
              'success' if exito_crear else 'danger')
    else:
        flash('Error al actualizar la alianza.', 'danger')

    return redirect(url_for('alianza.index'))

@bp.route('/alianza/eliminar', methods=['POST'])
def eliminar():
    aliado = request.form.get('aliado', '')
    departamento = request.form.get('departamento', '')
    
    exito, mensaje = api.eliminar_compuesta(TABLA, ['aliado', 'departamento'], [aliado, departamento])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('alianza.index'))