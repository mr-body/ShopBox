from flask import Blueprint, render_template, session, redirect, url_for ,request
from functools import wraps
from classes.easyLite import SQLiteDB
import datetime
import shutil
import os
from werkzeug.utils import secure_filename
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

query = SQLiteDB('database/cripeel.db')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        elif session['user']['accounttype'] != "admin":
            return redirect(url_for('vendas.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard/<id>')
@login_required
def dashboard(id):
    if id ==  session['user']['id']:
        return render_template('dashboard.html', id=id, data=session['user'])
    else:
        return "<center><h1>ID do usuario nao encontrado</h1></center>"
        
@admin_bp.route('/users')
@login_required
def users():
    UserList = query.select_data('SELECT * FROM users')
    return render_template('users/users.html',string = str, data = UserList)
    

@admin_bp.route('/newuser', methods=['POST'])
@login_required
def newuser():
    code = request.form.get('code')
    username = request.form.get('username')
    fullname = request.form.get('fullname')
    nivel = request.form.get('type')
    password = request.form.get('pass')
    data = datetime.now().strftime('%d/%m/%y %H:%M:%S')
    imagem = request.files['imagem']

    qu = f"INSERT INTO `users` VALUES ('{code}','{username}', '{nivel}', '{password}', '{fullname}', '{data}')"
    result = query.execute_query(qu)

    if result:        
        if imagem is not None and imagem.filename != "": 
            # Save the provided image
            imagem.save('static/post/users/'+code+'.png')
        else:
            # Copy the default image to the desired location
            default_image_path = 'static/post/users/padrao.png'
            new_image_path = 'static/post/users/' + code + '.png'
            if not os.path.exists(new_image_path):
                shutil.copy(default_image_path, new_image_path)
    else:
        print("erro")

    UserList = query.select_data('SELECT * FROM users')
    return render_template('users/users.html',string = str, data = UserList)

