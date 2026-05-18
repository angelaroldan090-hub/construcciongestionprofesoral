"""
app.py - Versión completa con todos los módulos
"""

from flask import Flask
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

    # Importar blueprints
from routes.auth import auth_bp
from routes.api_proxy import api_proxy_bp
from routes.home import home_bp
from routes.docentes_estudios import docentes_estudios_bp
from routes.area_conocimiento import area_bp
from routes.termino_clave import termino_bp
from routes.linea_investigacion import linea_bp
from routes.programa import programa_bp
from routes.red import red_bp
from routes.evaluacion_docente import evaluacion_bp
from routes.reconocimiento import reconocimiento_bp
from routes.experiencia import experiencia_bp
from routes.red_docente import red_docente_bp
from routes.apoyo_profesoral import apoyo_bp
from routes.beca import beca_bp
from routes.docente_departamento import docente_departamento_bp
from routes.estudio_ac import estudio_ac_bp
    
    # Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_proxy_bp)
app.register_blueprint(home_bp)
app.register_blueprint(docentes_estudios_bp, url_prefix='/docentes_estudios')
app.register_blueprint(area_bp, url_prefix='/area')
app.register_blueprint(termino_bp, url_prefix='/termino')
app.register_blueprint(linea_bp, url_prefix='/linea')
app.register_blueprint(programa_bp, url_prefix='/programa')
app.register_blueprint(red_bp, url_prefix='/red')
app.register_blueprint(evaluacion_bp, url_prefix='/evaluacion')
app.register_blueprint(reconocimiento_bp, url_prefix='/reconocimiento')
app.register_blueprint(experiencia_bp, url_prefix='/experiencia')
app.register_blueprint(red_docente_bp, url_prefix='/red_docente')
app.register_blueprint(apoyo_bp, url_prefix='/apoyo')
app.register_blueprint(beca_bp, url_prefix='/beca')
app.register_blueprint(docente_departamento_bp, url_prefix='/docente_departamento')
app.register_blueprint(estudio_ac_bp, url_prefix='/estudio_ac')

from middleware.auth_middleware import crear_middleware
crear_middleware(app)

if __name__ == '__main__':
    app.run(debug=True, port=5100)