from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import APIService

docentes_estudios_bp = Blueprint('docentes_estudios', __name__)
api_service = APIService()


@docentes_estudios_bp.route('/')
def listar():
    # 1. Obtener relaciones del SP
    exito, relaciones_sp = api_service.llamar_sp('sp_crud_docentes_estudios', ['LISTAR'])
    relaciones_sp = relaciones_sp if exito and isinstance(relaciones_sp, list) else []
    if not exito:
        flash(f'Error al cargar relaciones: {relaciones_sp}', 'danger')

    # 2. Datos auxiliares desde la API REST
    docentes      = api_service.get_all('docente')
    todos_estudios = api_service.get_all('estudios_realizados')

    # 3. Lookup de estudios completos por id
    estudio_by_id = {str(e['id']): e for e in todos_estudios}

    # 4. Ids de estudios ya asignados (para marcar en dropdown)
    asignados_ids = {int(r['estudio']) for r in relaciones_sp}

    # 5. Agrupar estudios por cédula de docente
    estudios_por_docente = defaultdict(list)
    for rel in relaciones_sp:
        cedula     = str(rel['docente'])
        estudio_id = str(rel['estudio'])
        estudio_data = estudio_by_id.get(estudio_id, {
            'id': rel['estudio'],
            'titulo': rel.get('estudio_titulo', ''),
            'universidad': rel.get('estudio_universidad', ''),
            'tipo': '', 'pais': ''
        })
        estudios_por_docente[cedula].append(estudio_data)

    # 6. Inyectar lista de estudios en cada docente
    for docente in docentes:
        docente['estudios'] = estudios_por_docente.get(str(docente['cedula']), [])

    # 7. Marcar estudios asignados en el dropdown
    for e in todos_estudios:
        e['asignado'] = int(e['id']) in asignados_ids

    return render_template(
        'pages/docentes_estudios.html',
        docentes=docentes,
        todos_estudios=todos_estudios
    )


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
    if exito:
        flash('Estudio asignado correctamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')
    return redirect(url_for('docentes_estudios.listar'))


@docentes_estudios_bp.route('/desasignar/<int:docente>/<int:estudio>')
def desasignar(docente, estudio):
    exito, resultado = api_service.llamar_sp(
        'sp_crud_docentes_estudios', ['DELETE', docente, estudio]
    )
    if exito:
        flash('Estudio desasignado correctamente.', 'success')
    else:
        flash(f'Error: {resultado}', 'danger')
    return redirect(url_for('docentes_estudios.listar'))
