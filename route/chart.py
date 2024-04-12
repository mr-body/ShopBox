from flask import Flask, Blueprint, render_template, session, redirect, url_for
from functools import wraps
from classes.easyLite import SQLiteDB
from datetime import datetime
import pdfkit
import random
import os


# Replace this with your actual SQLiteDB initialization and other code
query = SQLiteDB('database/cripeel.db')

# Configure pdfkit
#pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

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

    con1 = query.select_data("SELECT sum(total) as total from report")
    con2 = query.select_data("SELECT sum(qtd_padrao*total_itens*preco_venda) as total from stock")
    relatorio = 0
    stock = 0

    category = query.select_data('SELECT * FROM category ORDER BY id ASC')

    return render_template('chart/chart.html', relatorio=relatorio,stock=stock, codigo=codigo, status=status, texto=texto, cat=category)

@chart_bp.route('/abertura/<tipo>/<info>')
@login_required
def openned(tipo,info):
    
    global codigo


    estado = info

    if estado == "FEICHO":

        abetura_feicho = query.select_data(f"SELECT * FROM abertura")

        codigo = abetura_feicho[0][0]

        respo = "Mateus Adriano"
        hora = "20:00"
        dia = "29"
        mes = "07"
        ano = "2023"
        week = "sab"
        tpa = "50000"
        persTpa = "80%"
        pgm = "20000"
        persPgm = "20%"
        total = "70000"

        insert = query.execute_query(f"INSERT into report VALUES ({respo},{hora},{dia},{mes},{ano},{week},{tpa},{persTpa},{pgm},{persPgm},{total}) ")

        consulta_1 = query.select_data("SELECT pagamento, sum(total) as total from vendas GROUP BY pagamento")
        consulta_2 = query.select_data("SELECT categoria,sum(qtd) as quantidade,sum(total) as total FROM vendidos GROUP BY categoria")
        consulta_3 = query.select_data("SELECT barcode,nome,categoria,preco,sum(qtd) as quantidade,sum(total) as total FROM vendidos GROUP BY barcode ORDER BY nome")
        consulta_4 = query.select_data("SELECT cliente, SUM(total) as total from vendas GROUP by cliente")

        dados = []

        total_absoluto = sum(row[1] for row in consulta_1)

        for row in consulta_1:
            pagamento = row[0]
            total = row[1]
            try:
                percentagem = (total * 100) / total_absoluto
            except:
                percentagem = 0
            
            dados.append({"pagamento": pagamento, "percentagem": round(percentagem), "total": total})

        pdfkit_options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
        }

        html_content = render_template('models/reportPdf.html', nome=session['user']['username'], id=codigo, tableUser=consulta_4, table1=dados, total_vendas=total_absoluto, table2=consulta_2, table3=consulta_3)
        temp_html_file = f"temp_report_{random.randint(10000, 80000)}.html"
   
        with open(temp_html_file, 'w') as f:
            f.write(html_content)

        try:
            pdf_file = f"static/reports/{codigo}.pdf"        
            pdfkit.from_file(temp_html_file, pdf_file, options=pdfkit_options, configuration=pdfkit_config)
            # pdfkit.from_file(temp_html_file, pdf_file, options=pdfkit_options)
        except Exception as e:
            print("Error during PDF conversion:", e)

        os.remove(temp_html_file)

        print("feicho")
    
        resultados = query.execute_query(f"DELETE FROM entrada") 
        resultados = query.execute_query(f"DELETE FROM abertura") 
        resultados = query.execute_query(f"DELETE FROM vendas") 
        resultados = query.execute_query(f"DELETE FROM vendidos") 
        session.pop('id_vendas', None)   

        if tipo == "admin":
            return redirect(url_for('chart.dashboard'))
        else:
            return redirect(url_for('vendas.index'))     

    else:
        resultados = query.execute_query(f"INSERT into abertura VALUES ('{random.randint(10000, 80000)}','12/12/12','{session['user']['username']}')")
        
        entrada = query.select_data(f"SELECT * FROM stock")

        for produto in entrada:
            consulta = query.execute_query(f"INSERT into entrada VALUES ('{produto[7]}','{produto[1]}','{produto[6]}','{produto[4]}','{produto[5]}')")
            if consulta:
                print(f"[ok] {produto[7]}")

        print("aberto")

        if tipo == "admin":
            return redirect(url_for('chart.dashboard'))
        else:
            return redirect(url_for('vendas.index'))
