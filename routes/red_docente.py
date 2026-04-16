"""
red_docente.py - Blueprint para la tabla intermedia red_docente (N:N entre red y docente)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('red_docente', __name__)
api = ApiService()

TABLA = 'red_docente'
CLAVES = ['red', 'docente']  # Nombres de las columnas de la PK compuesta

@bp.route('/red_docente')
def index():
    limite = request.args.get('limite', type=int)
    registros = api.listar(TABLA, limite)
    
    # Obtener datos para selects
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
            # La clave viene como "red|docente"
            partes = clave.split('|')
            if len(partes) == 2:
                red_id = int(partes[0])
                docente_id = int(partes[1])
                # Buscar el registro en la lista
                for r in registros:
                    if r.get('red') == red_id and r.get('docente') == docente_id:
                        registro = r
                        break
                mostrar_formulario = True
                editando = True
        except (ValueError, TypeError, IndexError) as e:
            print(f"Error al parsear clave: {e}")
    
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
    red = request.form.get('red', '')
    docente = request.form.get('docente', '')
    fecha_inicio = request.form.get('fecha_inicio', '')
    fecha_fin = request.form.get('fecha_fin', '')
    act_destacadas = request.form.get('act_destacadas', '')
    
    # Validar que los campos requeridos no estén vacíos
    if not red or not docente:
        flash('Debe seleccionar una red y un docente.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    # Validar fechas
    if not fecha_inicio:
        flash('La fecha de inicio es requerida.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    datos = {
        'red': int(red),
        'docente': int(docente),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin if fecha_fin else None,
        'act_destacadas': act_destacadas
    }
    
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/actualizar', methods=['POST'])
def actualizar():
    # Obtener la clave original (red y docente originales)
    red_original = request.form.get('red_original', '')
    docente_original = request.form.get('docente_original', '')
    
    # Obtener los nuevos valores
    red_nueva = request.form.get('red', '')
    docente_nuevo = request.form.get('docente', '')
    fecha_inicio = request.form.get('fecha_inicio', '')
    fecha_fin = request.form.get('fecha_fin', '')
    act_destacadas = request.form.get('act_destacadas', '')
    
    # Validar campos requeridos
    if not red_nueva or not docente_nuevo:
        flash('Debe seleccionar una red y un docente.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    if not fecha_inicio:
        flash('La fecha de inicio es requerida.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    try:
        red_original_int = int(red_original)
        docente_original_int = int(docente_original)
        red_nueva_int = int(red_nueva)
        docente_nuevo_int = int(docente_nuevo)
    except (ValueError, TypeError):
        flash('ID de red o docente inválido.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    # Si la clave compuesta cambió (se seleccionó otra red u otro docente)
    if red_original_int != red_nueva_int or docente_original_int != docente_nuevo_int:
        # Opción 1: Eliminar el antiguo y crear el nuevo
        exito_eliminar, mensaje_eliminar = api.eliminar_compuesta(
            TABLA, CLAVES, [red_original_int, docente_original_int]
        )
        
        if exito_eliminar:
            datos_nuevos = {
                'red': red_nueva_int,
                'docente': docente_nuevo_int,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin if fecha_fin else None,
                'act_destacadas': act_destacadas
            }
            exito_crear, mensaje_crear = api.crear(TABLA, datos_nuevos)
            
            if exito_crear:
                flash('Registro actualizado exitosamente.', 'success')
            else:
                flash(f'Error al actualizar: {mensaje_crear}', 'danger')
        else:
            flash(f'Error al actualizar: {mensaje_eliminar}', 'danger')
    else:
        # La clave no cambió, solo actualizar los campos
        datos_actualizar = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin if fecha_fin else None,
            'act_destacadas': act_destacadas
        }
        exito, mensaje = api.actualizar_compuesta(
            TABLA, CLAVES, [red_original_int, docente_original_int], datos_actualizar
        )
        flash(mensaje, 'success' if exito else 'danger')
    
    return redirect(url_for('red_docente.index'))

@bp.route('/red_docente/eliminar', methods=['POST'])
def eliminar():
    red = request.form.get('red', '')
    docente = request.form.get('docente', '')
    
    if not red or not docente:
        flash('Datos de red o docente no proporcionados.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    try:
        red_id = int(red)
        docente_id = int(docente)
    except (ValueError, TypeError):
        flash('ID de red o docente inválido.', 'danger')
        return redirect(url_for('red_docente.index'))
    
    exito, mensaje = api.eliminar_compuesta(TABLA, CLAVES, [red_id, docente_id])
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red_docente.index'))