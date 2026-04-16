"""
red_docente.py - Blueprint para tabla intermedia (N:N)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('red_docente', __name__)
api = ApiService()

TABLA = 'red_docente'
CLAVES = ['red', 'docente']  # Nombres de las columnas PK

@bp.route('/red_docente')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion')
    clave = request.args.get('clave')
    
    # Obtener datos principales
    registros = api.listar(TABLA, limite)
    redes = api.listar('red')
    docentes = api.listar('docente')
    
    # Configurar modal
    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'
    registro = None
    
    if editando and clave:
        try:
            red_id, docente_id = clave.split('|')
            for r in registros:
                if str(r.get('red')) == red_id and str(r.get('docente')) == docente_id:
                    registro = r
                    break
        except:
            pass
    
    return render_template('pages/red_docente.html',
        registros=registros,
        redes=redes,
        docentes=docentes,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/red_docente/crear', methods=['POST'])
def crear():
    """Crear nueva relación"""
    datos = {
        'red': request.form.get('red'),
        'docente': request.form.get('docente'),
        'fecha_inicio': request.form.get('fecha_inicio'),
        'fecha_fin': request.form.get('fecha_fin') or None,
        'act_destacadas': request.form.get('act_destacadas')
    }
    
    # Validaciones básicas
    if not datos['red'] or not datos['docente']:
        flash('Debe seleccionar una red y un docente', 'danger')
        return redirect(url_for('red_docente.index'))
    
    if not datos['fecha_inicio']:
        flash('La fecha de inicio es requerida', 'danger')
        return redirect(url_for('red_docente.index'))
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/actualizar', methods=['POST'])
def actualizar():
    """Actualizar relación existente"""
    red_original = request.form.get('red_original')
    docente_original = request.form.get('docente_original')
    red_nueva = request.form.get('red')
    docente_nuevo = request.form.get('docente')
    
    # Validar campos requeridos
    if not red_nueva or not docente_nuevo:
        flash('Debe seleccionar una red y un docente', 'danger')
        return redirect(url_for('red_docente.index'))
    
    # Datos a actualizar
    datos_actualizar = {
        'fecha_inicio': request.form.get('fecha_inicio'),
        'fecha_fin': request.form.get('fecha_fin') or None,
        'act_destacadas': request.form.get('act_destacadas')
    }
    
    # Si la clave primaria cambió
    if red_original != red_nueva or docente_original != docente_nuevo:
        # Método: eliminar antiguo + crear nuevo
        exito_eliminar, _ = api.eliminar_compuesta(
            TABLA, CLAVES, [red_original, docente_original]
        )
        
        if exito_eliminar:
            datos_nuevos = {
                'red': red_nueva,
                'docente': docente_nuevo,
                **datos_actualizar
            }
            exito_crear, mensaje = api.crear(TABLA, datos_nuevos)
            flash(mensaje, 'success' if exito_crear else 'danger')
        else:
            flash('Error al actualizar la relación', 'danger')
    else:
        # La clave no cambió, solo actualizar atributos
        exito, mensaje = api.actualizar_compuesta(
            TABLA, CLAVES, [red_original, docente_original], datos_actualizar
        )
        flash(mensaje, 'success' if exito else 'danger')
    
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/eliminar', methods=['POST'])
def eliminar():
    """Eliminar relación"""
    red = request.form.get('red')
    docente = request.form.get('docente')
    
    if not red or not docente:
        flash('Datos incompletos para eliminar', 'danger')
        return redirect(url_for('red_docente.index'))
    
    exito, mensaje = api.eliminar_compuesta(TABLA, CLAVES, [red, docente])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))