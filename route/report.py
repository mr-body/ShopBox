from flask import Blueprint, render_template, session, redirect, url_for,request,jsonify
from functools import wraps
import os
from classes.easyLite import SQLiteDB

report_bp = Blueprint('report', __name__)

query = SQLiteDB('database/cripeel.db')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@report_bp.route('/')
@login_required
def index():
    reportList = query.select_data('SELECT * FROM report order by ID desc ')
    return render_template('report/report.html', data=reportList)

@report_bp.route('/open', methods=['POST'])
@login_required
def open():
    path = request.form['path']
    print("Caminho do arquivo:", os.path.abspath(os.path.dirname(__file__)) + "/" + path)

    # Remove 'reports' directory from the path
    parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    full_path = os.path.join(parent_directory, "", path)

    print("Full path:", full_path)

    if os.path.exists(full_path):
        os.startfile(full_path)
        # os.system(f"open {full_path}")
        return jsonify(success=True)
    else:
        return "erro"
    
