"""
red.py - Blueprint para la tabla Red.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.api_service import ApiService

bp = Blueprint('red', __name__)
api = ApiService()

TABLA = 'red'
CLAVE = 'id'  # Se ajusta automáticamente segun lo que devuelva la API


@bp.route('/red')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')

    registros = api.listar(TABLA, limite)

    # ── DEBUG: imprime las claves del primer registro para ver que nombre usa la API ──
    if registros:
        print(">>> CLAVES DEL REGISTRO:", list(registros[0].keys()))
        print(">>> PRIMER REGISTRO COMPLETO:", registros[0])
    # ─────────────────────────────────────────────────────────────────────────────────

    clave_real = CLAVE
    if registros and 'id' in registros[0] and 'idr' not in registros[0]:
        clave_real = 'id'

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(clave_real)) == valor_clave),
            None
        )

    return render_template('pages/red.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        clave_real=clave_real
    )


@bp.route('/red/buscar')
def buscar():
    query = request.args.get('q', '')
    limite = request.args.get('limite', type=int)
    
    registros = api.listar(TABLA, limite)
    
    if query:
        query_lower = query.lower()
        registros = [
            r for r in registros 
            if query_lower in r.get('nombre', '').lower()
            or query_lower in r.get('pais', '').lower()
            or (r.get('url') and query_lower in r.get('url', '').lower())
        ]
    
    return render_template('pages/red.html',
        registros=registros,
        mostrar_formulario=False,
        editando=False,
        registro=None,
        limite=limite,
        clave_real='id',
        busqueda=query
    )


@bp.route('/red/sugerencias')
def sugerencias():
    query = request.args.get('q', '')
    limite = request.args.get('limite', 10)
    
    registros = api.listar(TABLA)
    
    if query:
        query_lower = query.lower()
        resultados = []
        for r in registros:
            if (query_lower in r.get('nombre', '').lower() or
                query_lower in r.get('pais', '').lower()):
                
                # Determinar la clave correcta
                clave_valor = r.get('id') or r.get('idr')
                
                resultados.append({
                    'id': clave_valor,
                    'nombre': r.get('nombre'),
                    'pais': r.get('pais'),
                    'url': r.get('url'),
                    'texto': f"{r.get('nombre')} ({r.get('pais')})"
                })
        return jsonify(resultados[:limite])
    
    return jsonify([])


@bp.route('/red/crear', methods=['POST'])
def crear():
    datos = {
        'nombre': request.form.get('nombre', ''),
        'url':    request.form.get('url', ''),
        'pais':   request.form.get('pais', '')
    }
    print(">>> CREAR - datos:", datos)
    exito, mensaje = api.crear(TABLA, datos)
    print(">>> RESPUESTA:", exito, mensaje)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red.index'))


@bp.route('/red/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('idr', '') or request.form.get('id', '')
    datos = {
        'nombre': request.form.get('nombre', ''),
        'url':    request.form.get('url', ''),
        'pais':   request.form.get('pais', '')
    }
    print(">>> ACTUALIZAR - clave:", valor, "datos:", datos)
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    print(">>> RESPUESTA:", exito, mensaje)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red.index'))


@bp.route('/red/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('idr', '') or request.form.get('id', '')
    print(">>> ELIMINAR - clave:", valor)
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    print(">>> RESPUESTA:", exito, mensaje)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('red.index'))