import re
import secrets
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService
from services.email_service import EmailService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
email_service = EmailService()


# ── Login ──────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET'])
def login():
    if session.get('usuario'):
        return redirect(url_for('home.index'))
    return render_template('pages/login.html')


@auth_bp.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email', '').strip()
    contrasena = request.form.get('contrasena', '')

    if not email or not contrasena:
        flash('Ingrese email y contraseña.', 'danger')
        return render_template('pages/login.html')

    exito, datos = auth_service.login(email, contrasena)
    if not exito:
        flash(f'Credenciales incorrectas: {datos}', 'danger')
        return render_template('pages/login.html')

    session.clear()
    session['usuario'] = email
    session['nombre_usuario'] = datos.get('nombre', email)
    session['token'] = datos.get('token', '')
    session['roles'] = datos.get('roles', [])
    session['rutas_permitidas'] = datos.get('rutas_permitidas', [])
    session['rutas_crud'] = datos.get('rutas_crud', [])
    session['rutas_editar'] = datos.get('rutas_editar', [])
    session['cedula_docente'] = datos.get('cedula_docente')
    session['debe_cambiar_contrasena'] = datos.get('debe_cambiar_contrasena', False)

    if session['debe_cambiar_contrasena']:
        return redirect(url_for('auth.cambiar_contrasena'))

    return redirect(url_for('home.index'))


# ── Logout ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# ── Cambiar contraseña ─────────────────────────────────────────────────────────

@auth_bp.route('/cambiar-contrasena', methods=['GET'])
def cambiar_contrasena():
    if not session.get('usuario'):
        return redirect(url_for('auth.login'))
    return render_template('pages/cambiar_contrasena.html')


@auth_bp.route('/cambiar-contrasena', methods=['POST'])
def cambiar_contrasena_post():
    if not session.get('usuario'):
        return redirect(url_for('auth.login'))

    nueva = request.form.get('nueva', '')
    confirmar = request.form.get('confirmar', '')

    if nueva != confirmar:
        flash('Las contraseñas no coinciden.', 'danger')
        return render_template('pages/cambiar_contrasena.html')
    if len(nueva) < 6:
        flash('Mínimo 6 caracteres.', 'danger')
        return render_template('pages/cambiar_contrasena.html')
    if not re.search(r'[A-Z]', nueva):
        flash('Debe incluir al menos una mayúscula.', 'danger')
        return render_template('pages/cambiar_contrasena.html')
    if not re.search(r'\d', nueva):
        flash('Debe incluir al menos un número.', 'danger')
        return render_template('pages/cambiar_contrasena.html')

    exito, msg = auth_service.actualizar_contrasena(
        session['usuario'], nueva, session.get('token')
    )
    if not exito:
        flash(f'Error al cambiar contraseña: {msg}', 'danger')
        return render_template('pages/cambiar_contrasena.html')

    session.pop('debe_cambiar_contrasena', None)
    flash('Contraseña actualizada correctamente.', 'success')
    return redirect(url_for('home.index'))


# ── Recuperar contraseña ───────────────────────────────────────────────────────

@auth_bp.route('/recuperar-contrasena', methods=['GET'])
def recuperar_contrasena():
    return render_template('pages/recuperar_contrasena.html')


@auth_bp.route('/recuperar-contrasena', methods=['POST'])
def recuperar_contrasena_post():
    from config import API_BASE_URL
    import requests as req

    email = request.form.get('email', '').strip()
    if not email:
        flash('Ingrese su email.', 'danger')
        return render_template('pages/recuperar_contrasena.html')

    # Generar contraseña temporal segura (mínimo 1 mayúscula, 1 número, 8 chars)
    caracteres = string.ascii_letters + string.digits
    temporal = (
        secrets.choice(string.ascii_uppercase) +
        secrets.choice(string.digits) +
        ''.join(secrets.choice(caracteres) for _ in range(6))
    )
    lista = list(temporal)
    secrets.SystemRandom().shuffle(lista)
    temporal = ''.join(lista)

    # Guardar con BCrypt vía API
    exito, msg = auth_service.actualizar_contrasena(email, temporal)
    if not exito:
        flash(f'No se encontró el usuario o error al actualizar: {msg}', 'danger')
        return render_template('pages/recuperar_contrasena.html')

    # Marcar que debe cambiar contraseña (campo email es UNIQUE)
    try:
        req.put(
            f"{API_BASE_URL}/api/usuario/email/{email}",
            json={"debe_cambiar_contrasena": True},
            timeout=10
        )
    except Exception:
        pass

    # Enviar por correo
    enviado = email_service.enviar_contrasena_temporal(email, temporal)
    if enviado:
        flash('Se envió la contraseña temporal a tu correo.', 'success')
    else:
        flash(f'Contraseña temporal (SMTP no configurado): {temporal}', 'warning')

    return render_template('pages/recuperar_contrasena.html')
