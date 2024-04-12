from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from datetime import datetime
import random
from flask_session import Session
from classes.easyLite import SQLiteDB
from route.admin import admin_bp
from route.report import report_bp
from route.chart import chart_bp
from route.vendas import vendas_bp
from route.revenda import revenda_bp
from route.js_routes import js_routes_bp
from route.stock import stock_bp

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configurar a extensão Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(report_bp, url_prefix='/report')
app.register_blueprint(chart_bp, url_prefix='/chart')
app.register_blueprint(vendas_bp, url_prefix='/vendas')
app.register_blueprint(revenda_bp, url_prefix='/revenda')
app.register_blueprint(stock_bp, url_prefix='/stock')
app.register_blueprint(js_routes_bp)

query = SQLiteDB('database/cripeel.db')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return redirect(url_for('admin.dashboard', id=session['user']['id']))

@app.route('/clienteAdd', methods=['POST'])
def addCliente():
    current_time = datetime.now().strftime('%d/%m/%y %H:%M:%S')
    username = request.form.get('username')
    id = random.randint(1000, 8000)
    insert = query.execute_query(f"insert into cliente Values ('{current_time}','{username}','{session['user']['username']}','1122','{id}')")

    if insert:
        dados = query.select_data(f"SELECT barcode,nome,preco, SUM(qtd) as quantidade, SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{session['id_vendas']}' GROUP BY nome")

        for linha in dados:
            query.execute_query(f"insert into lista_divitas values ('{id}','{linha[0]}','{linha[1]}','{linha[2]}','{linha[3]}','{linha[4]}','{current_time}')")
        return "ok"
    else:
        return "erro"
    
@app.route('/login', methods=['GET'])
def login():
    if 'logged_in' not in session:
        return render_template('login.html')
    else:
        return redirect(url_for('admin.dashboard', id=session['user']['id']))

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user_data = query.login(username, password)
    if user_data:
        session['logged_in'] = True
        session['user'] = user_data
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error=True)
        
@app.route('/login2', methods=['POST'])
def login_post_card():
    code = request.form.get('code')
    
    info = query.select_data(f"SELECT username,password from users WHERE id = '{code}'")
    try:
        user_data = query.login(info[0][0], info[0][1])
        if user_data:
            session['logged_in'] = True
            session['user'] = user_data
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error=True)
    except Exception as e:
        return render_template('login.html', error=True)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None) 
    session.pop('id_vendas', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=1913)
