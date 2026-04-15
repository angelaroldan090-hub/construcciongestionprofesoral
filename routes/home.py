"""
home.py - Blueprint para la página de inicio.
"""

from flask import Blueprint, render_template

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    return render_template('pages/home.html')