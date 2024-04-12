from flask import Flask, Blueprint, render_template, session, redirect, url_for
from functools import wraps
from classes.easyLite import SQLiteDB
import pdfkit
import random
import os


# Replace this with your actual SQLiteDB initialization and other code
query = SQLiteDB('database/cripeel.db')

chart_bp = Blueprint('chart', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@chart_bp.route('/')
@login_required
def dashboard():
    global codigo

    abetura_feicho = query.select_data(f"SELECT * FROM abertura")
    if abetura_feicho:
        status = "Online"
        codigo = abetura_feicho[0][0]
        texto = "FEICHO"
    else:
        status = "Offline"
        codigo = "fora de servico"
        texto = "ABERTURA"
    category = query.select_data('SELECT * FROM category ORDER BY id ASC')

    return render_template('chart/chart.html', relatorio=10000, codigo=codigo, status=status, texto=texto, cat=category)

@chart_bp.route('/abertura/<info>')
@login_required
def openned(info):
    global codigo

    estado = info

    if estado == "FEICHO":
        consulta_1 = query.select_data("SELECT pagamento, sum(total) as total from vendas GROUP BY pagamento")
        consulta_2 = query.select_data("SELECT categoria,sum(qtd) as quantidade,sum(total) as total FROM vendidos GROUP BY categoria")
        consulta_3 = query.select_data("SELECT barcode,nome,categoria,preco,sum(qtd) as quantidade,sum(total) as total FROM vendidos GROUP BY barcode ORDER BY nome")

        dados = []

        total_absoluto = sum(row[1] for row in consulta_1)

        for row in consulta_1:
            pagamento = row[0]
            total = row[1]
            percentagem = (total * 100) / total_absoluto
            
            dados.append({"pagamento": pagamento, "percentagem": percentagem, "total": total})

        resultados = query.execute_query(f"DELETE FROM abertura") 
        resultados = query.execute_query(f"DELETE FROM vendas") 
        resultados = query.execute_query(f"DELETE FROM vendidos") 
        session.pop('id_vendas', None)   

        return render_template('models/reportPdf.html', nome=session['user']['username'], id=codigo, table1=dados, total_vendas=total_absoluto, table2=consulta_2, table3=consulta_3)  

    else:
        resultados = query.execute_query(f"INSERT into abertura VALUES ('{random.randint(10000, 80000)}','12/12/12','{session['user']['username']}')")
        return redirect(url_for('chart.dashboard'))
