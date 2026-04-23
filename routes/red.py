from flask import Blueprint, render_template, request, redirect, url_for
from services.api_service import APIService

red_bp = Blueprint('red', __name__)
api_service = APIService()

@red_bp.route('/')
def listar():
    redes = api_service.get_all('red')
    return render_template('pages/red.html', redes=redes)

@red_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        data = {
            'idr': request.form['idr'],
            'nombre': request.form['nombre'],
            'url': request.form['url'],
            'pais': request.form['pais']
        }
        api_service.create('red', data)
        return redirect(url_for('red.listar'))
    return render_template('pages/red_form.html')

@red_bp.route('/editar/<int:idr>', methods=['GET', 'POST'])
def editar(idr):
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'url': request.form['url'],
            'pais': request.form['pais']
        }
        api_service.update('red', idr, data)
        return redirect(url_for('red.listar'))
    
    red = api_service.get_one('red', idr)
    return render_template('pages/red_form.html', red=red)

@red_bp.route('/eliminar/<int:idr>')
def eliminar(idr):
    api_service.delete('red', idr)
    return redirect(url_for('red.listar'))