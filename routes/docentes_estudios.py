# En routes/docente_estudios.py

@bp.route('/docente/crear', methods=['POST'])
def crear():
    # Recibir datos del formulario
    cedula = request.form.get('cedula', 0, type=int)
    nombres = request.form.get('nombres', '')
    apellidos = request.form.get('apellidos', '')
    # ... otros campos del docente
    
    # Recibir estudios dinámicos
    titulos = request.form.getlist('estudio_titulo[]')
    universidades = request.form.getlist('estudio_universidad[]')
    fechas = request.form.getlist('estudio_fecha[]')
    tipos = request.form.getlist('estudio_tipo[]')
    ciudades = request.form.getlist('estudio_ciudad[]')
    paises = request.form.getlist('estudio_pais[]')
    
    # Construir array de estudios
    estudios_lista = []
    for tit, uni, fec, tip, ciu, pai in zip(titulos, universidades, fechas, tipos, ciudades, paises):
        if tit and uni:
            estudios_lista.append({
                "titulo": tit,
                "universidad": uni,
                "fecha": fec,
                "tipo": tip,
                "ciudad": ciu,
                "pais": pai,
                "metodologia": "Presencial",
                "ins_acreditada": True,
                "perfil_egresado": "Perfil por defecto"
            })
    
    # Llamar al SP
    exito, datos = api.ejecutar_sp("sp_insertar_docente_y_estudios", {
        "p_cedula": cedula,
        "p_nombres": nombres,
        "p_apellidos": apellidos,
        "p_estudios": json.dumps(estudios_lista),
        "p_resultado": None
    })
    
    if exito:
        flash("Docente creado exitosamente", "success")
    else:
        flash(f"Error: {datos}", "danger")
    
    return redirect(url_for('docente_estudios.index'))