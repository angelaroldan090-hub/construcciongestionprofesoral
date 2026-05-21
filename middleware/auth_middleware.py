from flask import session, redirect, url_for, request, render_template

RUTAS_PUBLICAS = ['/login', '/logout', '/recuperar-contrasena', '/static']


def crear_middleware(app):

    @app.before_request
    def verificar_autenticacion():
        # 1. Rutas públicas → siempre accesibles
        if any(request.path.startswith(r) for r in RUTAS_PUBLICAS):
            return

        # 2. Sin sesión → redirigir a login
        if not session.get('usuario'):
            return redirect(url_for('auth.login'))

        # 3. Debe cambiar contraseña → forzar
        if session.get('debe_cambiar_contrasena') and request.path != '/cambiar-contrasena':
            return redirect(url_for('auth.cambiar_contrasena'))

        # 4. Home siempre accesible
        if request.path == '/':
            return

        # 5. Sin rutas configuradas → permitir todo (sistema nuevo sin configurar)
        rutas_permitidas = set(session.get('rutas_permitidas', []))
        if not rutas_permitidas:
            return

        # 6. Verificar ruta exacta o sub-ruta
        ruta_actual = request.path
        rutas_crud = set(session.get('rutas_crud', []))
        rutas_editar = set(session.get('rutas_editar', []))
        for ruta in rutas_permitidas:
            if ruta_actual == ruta or ruta_actual == ruta + '/':
                return  # Exacta con o sin trailing slash
            if ruta_actual.startswith(ruta + '/'):
                if ruta in rutas_crud:
                    return  # CRUD completo: cualquier sub-ruta permitida
                if ruta in rutas_editar and '/editar/' in ruta_actual:
                    return  # Solo sub-rutas de editar

        # 7. No permitida → 403
        return render_template('pages/sin_acceso.html'), 403

    @app.context_processor
    def inyectar_sesion():
        return {
            'usuario': session.get('usuario', ''),
            'nombre_usuario': session.get('nombre_usuario', ''),
            'roles': session.get('roles', []),
            'rutas_permitidas': set(session.get('rutas_permitidas', [])),
            'rutas_crud': set(session.get('rutas_crud', [])),
            'rutas_editar': set(session.get('rutas_editar', [])),
            'cedula_docente': session.get('cedula_docente'),
        }
