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

    exito, relaciones_sp = api_service.llamar_sp('sp_crud_docentes_estudios', ['LISTAR'])
    relaciones_sp = relaciones_sp if exito and isinstance(relaciones_sp, list) else []
    if not exito:
        flash(f'Error al cargar relaciones: {relaciones_sp}', 'danger')

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
    data = {
        'cedula':                       request.form['cedula'],
        'nombres':                      request.form['nombres'],
        'apellidos':                    request.form['apellidos'],
        'genero':                       request.form['genero'],
        'cargo':                        request.form['cargo'],
        'fecha_nacimiento':             request.form['fecha_nacimiento'],
        'correo':                       request.form['correo'],
        'telefono':                     request.form['telefono'],
        'url_cvlac':                    request.form['url_cvlac'],
        'fecha_actualizacion':          request.form['fecha_actualizacion'],
        'escalafon':                    request.form['escalafon'],
        'perfil':                       request.form['perfil'],
        'cat_minciencia':               request.form.get('cat_minciencia', ''),
        'conv_minciencia':              request.form['conv_minciencia'],
        'nacionalidaad':                request.form['nacionalidaad'],
        'linea_investigacion_principal': request.form.get('linea_investigacion_principal', ''),
    }
    exito, resultado = api_service.create('docente', data)
    flash('Docente creado correctamente.' if exito else f'Error: {resultado}',
          'success' if exito else 'danger')
    return redirect(url_for('docentes_estudios.listar'))


@docentes_estudios_bp.route('/docente/editar/<int:cedula>', methods=['POST'])
def docente_editar(cedula):
    data = {
        'nombres':                      request.form['nombres'],
        'apellidos':                    request.form['apellidos'],
        'genero':                       request.form['genero'],
        'cargo':                        request.form['cargo'],
        'fecha_nacimiento':             request.form['fecha_nacimiento'],
        'correo':                       request.form['correo'],
        'telefono':                     request.form['telefono'],
        'url_cvlac':                    request.form['url_cvlac'],
        'fecha_actualizacion':          request.form['fecha_actualizacion'],
        'escalafon':                    request.form['escalafon'],
        'perfil':                       request.form['perfil'],
        'cat_minciencia':               request.form.get('cat_minciencia', ''),
        'conv_minciencia':              request.form['conv_minciencia'],
        'nacionalidaad':                request.form['nacionalidaad'],
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
    exito, resultado = api_service.delete('estudios_realizados', id)
    flash('Estudio eliminado correctamente.' if exito else f'Error: {resultado}',
          'success' if exito else 'danger')
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
