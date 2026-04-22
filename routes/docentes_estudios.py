"""
docentes_estudios.py - Modulo maestro-detalle Docente + Estudios Realizados.
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.api_service import ApiService

bp = Blueprint('docentes_estudios', __name__)
api = ApiService()


def _to_int(value):
    if value in (None, ''):
        return None
    return int(value)


def _parsear_estudios(form):
    titulos = form.getlist('estudio_titulo[]')
    universidades = form.getlist('estudio_universidad[]')
    fechas = form.getlist('estudio_fecha[]')
    tipos = form.getlist('estudio_tipo[]')
    ciudades = form.getlist('estudio_ciudad[]')
    paises = form.getlist('estudio_pais[]')
    metodologias = form.getlist('estudio_metodologia[]')
    acreditadas = form.getlist('estudio_ins_acreditada[]')
    perfiles = form.getlist('estudio_perfil_egresado[]')

    estudios = []
    for titulo, universidad, fecha, tipo, ciudad, pais, metodologia, acreditada, perfil in zip(
        titulos,
        universidades,
        fechas,
        tipos,
        ciudades,
        paises,
        metodologias,
        acreditadas,
        perfiles,
    ):
        if not titulo or not universidad:
            continue

        estudios.append({
            'titulo': titulo,
            'universidad': universidad,
            'fecha': fecha or None,
            'tipo': tipo or None,
            'ciudad': ciudad or None,
            'pais': pais or None,
            'metodologia': metodologia or None,
            'ins_acreditada': acreditada == 'true',
            'perfil_egresado': perfil or None,
        })

    return estudios


def _listar_docentes_estudios_fallback(limite=None):
    docentes = api.listar('docente', limite)
    estudios = api.listar('estudios_realizados')

    estudios_por_docente = {}
    for estudio in estudios:
        key = str(estudio.get('docente'))
        estudios_por_docente.setdefault(key, []).append(estudio)

    for docente in docentes:
        docente['estudios'] = estudios_por_docente.get(str(docente.get('cedula')), [])

    return docentes


@bp.route('/docentes_estudios')
def index():
    limite = request.args.get('limite', type=int)
    busqueda = (request.args.get('q') or '').strip()
    accion = request.args.get('accion', '')
    cedula_editar = request.args.get('cedula', type=int)

    exito, resultado = api.ejecutar_funcion_json('sp_listar_docentes_y_estudios', [])
    if exito and isinstance(resultado, list):
        registros = resultado
    else:
        registros = _listar_docentes_estudios_fallback(limite)

    if limite:
        registros = registros[:limite]

    if busqueda:
        q = busqueda.lower()
        filtrados = []
        for r in registros:
            textos = [
                str(r.get('cedula', '')),
                r.get('nombres', ''),
                r.get('apellidos', ''),
                r.get('correo', ''),
            ]
            estudios = r.get('estudios') or []
            textos.extend([
                e.get('titulo', '') for e in estudios if isinstance(e, dict)
            ])
            if any(q in str(t).lower() for t in textos):
                filtrados.append(r)
        registros = filtrados

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'
    registro = None

    if editando and cedula_editar:
        exito, detalle = api.ejecutar_funcion_json('sp_consultar_docente_y_estudios', [cedula_editar])
        if exito and isinstance(detalle, dict) and detalle.get('docente'):
            registro = detalle.get('docente')
            registro['estudios'] = detalle.get('estudios') or []
        else:
            registro = next((d for d in registros if int(d.get('cedula', -1)) == cedula_editar), None)

    lineas = api.listar('linea_investigacion')

    return render_template(
        'pages/docentes_estudios.html',
        registros=registros,
        limite=limite,
        busqueda=busqueda,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        lineas=lineas,
    )


@bp.route('/docentes_estudios/crear', methods=['POST'])
def crear():
    try:
        estudios = _parsear_estudios(request.form)
        params = [
            _to_int(request.form.get('cedula')),
            request.form.get('nombres', ''),
            request.form.get('apellidos', ''),
            request.form.get('genero', ''),
            request.form.get('cargo', ''),
            request.form.get('fecha_nacimiento') or None,
            request.form.get('correo', ''),
            request.form.get('telefono', ''),
            request.form.get('url_cvlac', ''),
            request.form.get('fecha_actualizacion') or None,
            request.form.get('escalafon', ''),
            request.form.get('perfil', ''),
            request.form.get('cat_minciencia', ''),
            request.form.get('conv_minciencia', ''),
            request.form.get('nacionalidad', ''),
            _to_int(request.form.get('linea_investigacion_principal')),
            json.dumps(estudios),
        ]

        exito, resultado = api.ejecutar_funcion_json('sp_insertar_docente_y_estudios', params)
        mensaje = resultado.get('mensaje', 'Operacion completada.') if isinstance(resultado, dict) else 'Operacion completada.'
        ok = exito and (not isinstance(resultado, dict) or resultado.get('exito', True))
        flash(mensaje, 'success' if ok else 'danger')
    except Exception as ex:
        flash(f'Error al crear docente y estudios: {ex}', 'danger')

    return redirect(url_for('docentes_estudios.index'))


@bp.route('/docentes_estudios/actualizar', methods=['POST'])
def actualizar():
    try:
        estudios = _parsear_estudios(request.form)
        params = [
            _to_int(request.form.get('cedula')),
            request.form.get('nombres', ''),
            request.form.get('apellidos', ''),
            request.form.get('genero', ''),
            request.form.get('cargo', ''),
            request.form.get('fecha_nacimiento') or None,
            request.form.get('correo', ''),
            request.form.get('telefono', ''),
            request.form.get('url_cvlac', ''),
            request.form.get('fecha_actualizacion') or None,
            request.form.get('escalafon', ''),
            request.form.get('perfil', ''),
            request.form.get('cat_minciencia', ''),
            request.form.get('conv_minciencia', ''),
            request.form.get('nacionalidad', ''),
            _to_int(request.form.get('linea_investigacion_principal')),
            json.dumps(estudios),
        ]

        exito, resultado = api.ejecutar_funcion_json('sp_actualizar_docente_y_estudios', params)
        mensaje = resultado.get('mensaje', 'Operacion completada.') if isinstance(resultado, dict) else 'Operacion completada.'
        ok = exito and (not isinstance(resultado, dict) or resultado.get('exito', True))
        flash(mensaje, 'success' if ok else 'danger')
    except Exception as ex:
        flash(f'Error al actualizar docente y estudios: {ex}', 'danger')

    return redirect(url_for('docentes_estudios.index'))


@bp.route('/docentes_estudios/eliminar', methods=['POST'])
def eliminar():
    try:
        cedula = _to_int(request.form.get('cedula'))
        exito, resultado = api.ejecutar_funcion_json('sp_borrar_docente_y_estudios', [cedula])
        mensaje = resultado.get('mensaje', 'Operacion completada.') if isinstance(resultado, dict) else 'Operacion completada.'
        ok = exito and (not isinstance(resultado, dict) or resultado.get('exito', True))
        flash(mensaje, 'success' if ok else 'danger')
    except Exception as ex:
        flash(f'Error al eliminar docente y estudios: {ex}', 'danger')

    return redirect(url_for('docentes_estudios.index'))


@bp.route('/docentes_estudios/detalle/<int:cedula>')
def detalle(cedula):
    exito, resultado = api.ejecutar_funcion_json('sp_consultar_docente_y_estudios', [cedula])
    if not exito:
        return jsonify({'exito': False, 'mensaje': 'No fue posible consultar el detalle.'}), 500
    return jsonify({'exito': True, 'datos': resultado})
