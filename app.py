"""
app.py - Versión completa con todos los módulos
"""

from flask import Flask
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Importar blueprints
from routes.home import bp as home_bp
from routes.red import bp as red_bp
from routes.aliado import bp as aliado_bp
from routes.docente import bp as docente_bp
from routes.estudio_ac import bp as estudio_ac_bp
from routes.red_docente import bp as red_docente_bp
from routes.alianza import bp as alianza_bp
from routes.apoyo_profesoral import bp as apoyo_profesoral_bp
from routes.beca import bp as beca_bp
from routes.docente_departamento import bp as docente_departamento_bp
from routes.evaluacion_docente import bp as evaluacion_docente_bp

# Registrar blueprints
app.register_blueprint(home_bp)
app.register_blueprint(red_bp)
app.register_blueprint(aliado_bp)
app.register_blueprint(docente_bp)
app.register_blueprint(estudio_ac_bp)
app.register_blueprint(red_docente_bp)
app.register_blueprint(alianza_bp)
app.register_blueprint(apoyo_profesoral_bp)
app.register_blueprint(beca_bp)
app.register_blueprint(docente_departamento_bp)
app.register_blueprint(evaluacion_docente_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5100)