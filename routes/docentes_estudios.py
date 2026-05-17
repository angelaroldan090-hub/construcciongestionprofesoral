from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import APIService

docentes_estudios_bp = Blueprint('docentes_estudios', __name__)
api_service = APIService()


@docentes_estudios_bp.route('/')
def listar():
    docentes       = api_service.get_all('docente')
    lineas         = api_service.get_all('linea_investigacion')
    todos_estudios = api_service.get_all('estudios_realizados')
    estudio_by_id  = {str(e['id']): e for e in todos_estudios}

    exito, resultado_sp = api_service.llamar_sp('sp_crud_docentes_estudios', ['LISTAR'])
    if not exito:
        flash(f'Error al cargar relaciones: {resultado_sp}', 'danger')
        relaciones_sp = []
    else:
        relaciones_sp = resultado_sp if isinstance(resultado_sp, list) else []

    asignados_ids = {int(r['estudio']) for r in relaciones_sp}

    estudios_por_docente = defaultdict(list)
    for rel in relaciones_sp:
        cedula     = str(rel['docente'])
        estudio_id = str(rel['estudio'])
        estudio_data = estudio_by_id.get(estudio_id, {
            'id': rel['estudio'],
            'titulo': rel.get('estudio_titulo', ''),
            'universidad': rel.get('estudio_universidad', ''),
            'tipo': '', 'pais': '', 'fecha': '',
            'ciudad': '', 'ins_acreditada': '',
            'metodologia': '', 'perfil_egresado': '', 'docente': rel['docente']
        })
        estudios_por_docente[cedula].append(estudio_data)

    for docente in docentes:
        docente['estudios'] = estudios_por_docente.get(str(docente['cedula']), [])

    for e in todos_estudios:
        e['asignado'] = int(e['id']) in asignados_ids

    return render_template(
        'pages/docentes_estudios.html',
        docentes=docentes,
        todos_estudios=todos_estudios,
        lineas=lineas
    )


# ── DOCENTE CRUD ──────────────────────────────────────────────────────────────

@docentes_estudios_bp.route('/docente/crear', methods=['POST'])
def docente_crear():
    cedula = request.form['cedula']

    data = {
        'cedula':                        cedula,
        'nombres':                       request.form['nombres'],
        'apellidos':                     request.form['apellidos'],
        'genero':                        request.form['genero'],
        'cargo':                         request.form['cargo'],
        'fecha_nacimiento':              request.form['fecha_nacimiento'],
        'correo':                        request.form['correo'],
        'telefono':                      request.form['telefono'],
        'url_cvlac':                     request.form['url_cvlac'],
        'fecha_actualizacion':           request.form['fecha_actualizacion'],
        'escalafon':                     request.form['escalafon'],
        'perfil':                        request.form['perfil'],
        'cat_minciencia':                request.form.get('cat_minciencia', ''),
        'conv_minciencia':               request.form['conv_minciencia'],
        'nacionalidaad':                 request.form['nacionalidaad'],
        'linea_investigacion_principal': request.form.get('linea_investigacion_principal', ''),
    }
    exito, resultado = api_service.create('docente', data)
    if not exito:
        flash(f'Error al crear docente: {resultado}', 'danger')
        return redirect(url_for('docentes_estudios.listar'))

    flash('Docente creado correctamente.', 'success')

    # Crear nuevo estudio si se llenaron los campos (opcional)
    estudio_id     = request.form.get('estudio_id', '').strip()
    estudio_titulo = request.form.get('estudio_titulo', '').strip()
    if estudio_id and estudio_titulo:
        data_estudio = {
            'id':              estudio_id,
            'titulo':          estudio_titulo,
            'universidad':     request.form.get('estudio_universidad', ''),
            'fecha':           request.form.get('estudio_fecha', ''),
            'tipo':            request.form.get('estudio_tipo', ''),
            'ciudad':          request.form.get('estudio_ciudad', ''),
            'docente':         cedula,
            'ins_acreditada':  request.form.get('estudio_ins_acreditada', '0'),
            'metodologia':     request.form.get('estudio_metodologia', 'Presencial'),
            'perfil_egresado': request.form.get('estudio_perfil_egresado', ''),
            'pais':            request.form.get('estudio_pais', ''),
        }
        exito_e, resultado_e = api_service.create('estudios_realizados', data_estudio)
        if exito_e:
            flash('Estudio creado y asignado correctamente.', 'success')
            api_service.llamar_sp('sp_crud_docentes_estudios', ['INSERT', int(cedula), int(estudio_id)])
        else:
            flash(f'Docente creado pero error al crear estudio: {resultado_e}', 'warning')

    # Asignar estudio existente si se seleccionó (opcional)
    estudio_asignar = request.form.get('estudio_asignar', '').strip()
    if estudio_asignar:
        exito_a, resultado_a = api_service.llamar_sp(
            'sp_crud_docentes_estudios', ['INSERT', int(cedula), int(estudio_asignar)]
        )
        if exito_a:
            flash('Estudio existente asignado correctamente.', 'success')
        else:
            flash(f'Docente creado pero error al asignar estudio: {resultado_a}', 'warning')

    return redirect(url_for('docentes_estudios.listar'))


@docentes_estudios_bp.route('/docente/editar/<int:cedula>', methods=['POST'])
def docente_editar(cedula):
    data = {
        'nombres':                       request.form['nombres'],
        'apellidos':                     request.form['apellidos'],
        'genero':                        request.form['genero'],
        'cargo':                         request.form['cargo'],
        'fecha_nacimiento':              request.form['fecha_nacimiento'],
        'correo':                        request.form['correo'],
        'telefono':                      request.form['telefono'],
        'url_cvlac':                     request.form['url_cvlac'],
        'fecha_actualizacion':           request.form['fecha_actualizacion'],
        'escalafon':                     request.form['escalafon'],
        'perfil':                        request.form['perfil'],
        'cat_minciencia':                request.form.get('cat_minciencia', ''),
        'conv_minciencia':               request.form['conv_minciencia'],
        'nacionalidaad':                 request.form['nacionalidaad'],
        'linea_investigacion_principal': request.form.get('linea_investigacion_principal', ''),
    }
    exito, resultado = api_service.update('docente', cedula, data)
    flash('Docente actualizado correctamente.' if exito else f'Error: {resultado}',
          'success' if exito else 'danger')
    return redirect(url_for('docentes_estudios.listar'))


@docentes_estudios_bp.route('/docente/eliminar/<int:cedula>')
def docente_eliminar(cedula):
    exito, resultado = api_service.delete('docente', cedula)
    flash('Docente eliminado correctamente.' if exito else f'Error: {resultado}',
          'success' if exito else 'danger')
    return redirect(url_for('docentes_estudios.listar'))


# ── ESTUDIOS REALIZADOS CRUD ──────────────────────────────────────────────────

@docentes_estudios_bp.route('/estudio/crear', methods=['POST'])
def estudio_crear():
    data = {
        'id':              request.form['id'],
        'titulo':          request.form['titulo'],
        'universidad':     request.form['universidad'],
        'fecha':           request.form['fecha'],
        'tipo':            request.form['tipo'],
        'ciudad':          request.form['ciudad'],
        'docente':         request.form['docente'],
        'ins_acreditada':  request.form['ins_acreditada'],
        'metodologia':     request.form['metodologia'],
        'perfil_egresado': request.form['perfil_egresado'],
        'pais':            request.form['pais'],
    }
    exito, resultado = api_service.create('estudios_realizados', data)
    flash('Estudio creado correctamente.' if exito else f'Error: {resultado}',
          'success' if exito else 'danger')
    return redirect(url_for('docentes_estudios.listar'))


@docentes_estudios_bp.route('/estudio/editar/<int:id>', methods=['POST'])
def estudio_editar(id):
    data = {
        'titulo':          request.form['titulo'],
        'universidad':     request.form['universidad'],
        'fecha':           request.form['fecha'],
        'tipo':            request.form['tipo'],
        'ciudad':          request.form['ciudad'],
        'docente':         request.form['docente'],
        'ins_acreditada':  request.form['ins_acreditada'],
        'metodologia':     request.form['metodologia'],
        'perfil_egresado': request.form['perfil_egresado'],
        'pais':            request.form['pais'],
    }
    exito, resultado = api_service.update('estudios_realizados', id, data)
    flash('Estudio actualizado correctamente.' if exito else f'Error: {resultado}',
          'success' if exito else 'danger')
    return redirect(url_for('docentes_estudios.listar'))


@docentes_estudios_bp.route('/estudio/eliminar/<int:id>')
def estudio_eliminar(id):
    # Eliminar relaciones en todas las tablas que referencian estudios_realizados
    api_service.eliminar('apoyo_profesoral', 'estudios', id)
    api_service.eliminar('beca', 'estudios', id)
    api_service.eliminar('estudio_ac', 'estudio', id)

    # Eliminar relaciones en docentes_estudios via SP
    docentes = api_service.get_all('docente')
    for docente in docentes:
        api_service.llamar_sp('sp_crud_docentes_estudios', ['DELETE', docente['cedula'], id])

    # Finalmente eliminar el estudio
    exito, resultado = api_service.delete('estudios_realizados', id)

    if exito:
        flash('Estudio eliminado correctamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')

    return redirect(url_for('docentes_estudios.listar'))


# ── RELACIÓN DOCENTES_ESTUDIOS (tabla intermedia) ─────────────────────────────

@docentes_estudios_bp.route('/asignar', methods=['POST'])
def asignar():
    cedula     = request.form.get('docente', type=int)
    estudio_id = request.form.get('estudio', type=int)
    if not cedula or not estudio_id:
        flash('Debe seleccionar docente y estudio.', 'danger')
        return redirect(url_for('docentes_estudios.listar'))
    exito, resultado = api_service.llamar_sp(
        'sp_crud_docentes_estudios', ['INSERT', cedula, estudio_id]
    )
    flash('Estudio asignado correctamente.' if exito else f'Error: {resultado}',
          'success' if exito else 'danger')
    return redirect(url_for('docentes_estudios.listar'))


@docentes_estudios_bp.route('/desasignar/<int:docente>/<int:estudio>')
def desasignar(docente, estudio):
    exito, resultado = api_service.llamar_sp(
        'sp_crud_docentes_estudios', ['DELETE', docente, estudio]
    )
    flash('Estudio desasignado correctamente.' if exito else f'Error: {resultado}',
          'success' if exito else 'danger')
    return redirect(url_for('docentes_estudios.listar'))