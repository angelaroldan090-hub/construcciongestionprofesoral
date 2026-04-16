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
    registros = api.listar(TABLA, limite)
    
    # Obtener datos para selects
    docentes = api.listar('docente')
    programas = api.listar('programa')
    
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
            docente_id, departamento_id = clave.split('|')
            # Buscar el registro correspondiente
            for r in registros:
                if str(r.get('docente')) == str(docente_id) and str(r.get('departamento')) == str(departamento_id):
                    registro = r
                    break
            mostrar_formulario = True
            editando = True
        except Exception:
            pass
    
    return render_template('pages/docente_departamento.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        docentes=docentes,
        programas=programas
    )

@bp.route('/docente_departamento/crear', methods=['POST'])
def crear():
    docente = request.form.get('docente', '')
    departamento = request.form.get('departamento', '')
    
    # Validar y convertir IDs a int
    try:
        docente_id = int(docente)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de docente o departamento inválido.', 'danger')
        return redirect(url_for('docente_departamento.index'))
    
    datos = {
        'docente': docente_id,
        'departamento': departamento_id,
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
    
    # Validar y convertir a int si es posible
    try:
        docente_id = int(docente)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de docente o departamento inválido.', 'danger')
        return redirect(url_for('docente_departamento.index'))
    
    datos = {
        'dedicacion': request.form.get('dedicacion', ''),
        'modalidad': request.form.get('modalidad', ''),
        'fecha_ingreso': request.form.get('fecha_ingreso', ''),
        'fecha_salida': request.form.get('fecha_salida', '') or None
    }
    
    # Para claves compuestas, simular actualización con DELETE + CREATE
    # Paso 1: Eliminar el registro actual
    exito_eliminar, mensaje_eliminar = api.eliminar_compuesta(TABLA, ['docente', 'departamento'], [docente_id, departamento_id])
    
    if exito_eliminar:
        # Paso 2: Crear el registro con los datos nuevos
        datos_crear = {
            'docente': docente_id,
            'departamento': departamento_id,
            'dedicacion': datos['dedicacion'],
            'modalidad': datos['modalidad'],
            'fecha_ingreso': datos['fecha_ingreso'],
            'fecha_salida': datos['fecha_salida']
        }
        exito_crear, mensaje_crear = api.crear(TABLA, datos_crear)
        
        if exito_crear:
            flash('Registro actualizado exitosamente.', 'success')
        else:
            flash(f'Error al recrear registro: {mensaje_crear}', 'danger')
    else:
        flash(f'Error al actualizar: {mensaje_eliminar}', 'danger')
    
    return redirect(url_for('docente_departamento.index'))

@bp.route('/docente_departamento/eliminar', methods=['POST'])
def eliminar():
    docente = request.form.get('docente', '')
    departamento = request.form.get('departamento', '')
    
    # Validar y convertir a int si es posible
    try:
        docente_id = int(docente)
        departamento_id = int(departamento)
    except (ValueError, TypeError):
        flash('ID de docente o departamento inválido.', 'danger')
        return redirect(url_for('docente_departamento.index'))
    
    exito, mensaje = api.eliminar_compuesta(TABLA, ['docente', 'departamento'], [docente_id, departamento_id])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('docente_departamento.index'))