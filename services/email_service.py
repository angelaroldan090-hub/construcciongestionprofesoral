import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    def enviar_contrasena_temporal(self, destinatario, contrasena_temporal):
        from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM
        if not SMTP_USER or not SMTP_PASS:
            return False
        try:
            msg = MIMEMultipart()
            msg["From"] = SMTP_FROM
            msg["To"] = destinatario
            msg["Subject"] = "Recuperación de contraseña - Gestión Profesoral"
            body = (
                f"Hola,\n\n"
                f"Tu contraseña temporal es: {contrasena_temporal}\n\n"
                f"Por seguridad, deberás cambiarla al iniciar sesión.\n\n"
                f"Si no solicitaste esto, ignora este correo."
            )
            msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_FROM, destinatario, msg.as_string())
            return True
        except Exception:
            return False
