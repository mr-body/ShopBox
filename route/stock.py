from flask import Blueprint, render_template, session, redirect, request, url_for, jsonify
from functools import wraps
from classes.easyLite import SQLiteDB
import shutil
from werkzeug.utils import secure_filename
import os

stock_bp = Blueprint('stock', __name__)

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

@stock_bp.route('/')
@login_required
def index():
    SumTotal = 19000
    reportList = query.select_data('SELECT * FROM stock')
    category = query.select_data('SELECT * FROM category ORDER BY id ASC')
    return render_template('stock/stock.html', data=reportList,cat=category ,total=SumTotal, string=str)

@stock_bp.route('/pesquisa', methods=['POST'])
@login_required
def pesquisa():
    valor = request.form['valor']
    print(valor)
    resultados = query.select_data(f"SELECT * FROM stock WHERE name LIKE '%{valor}%' OR barcode LIKE '%{valor}%'")
    print(resultados)
    return jsonify(resultados)

@stock_bp.route('/upgrade', methods=['POST'])
@login_required
def upgrade_stock():
    codigo = request.form.get('code')
    tipo = request.form.get('tipo')
    qtd = request.form.get('qtd')
    print(codigo)

    pesquisa = query.select_data(f"SELECT * FROM stock WHERE barcode = '{codigo}'")
    if not pesquisa:
        print("error")
        return jsonify(success=False, message="Produto não encontrado.")

    db_qtd = pesquisa[0][4]
    db_qtd_total = pesquisa[0][5]

    print("quantidade:"+ str(db_qtd))
    print("total:"+ str(db_qtd_total))
    try:
        qtd = int(qtd)  # Ensure that qtd is a numeric value
    except ValueError:
        return jsonify(success=False, message="Quantidade inválida.")
    if tipo == "t":
        upgrade = query.execute_query(f"UPDATE stock SET total_itens = '{qtd}' WHERE barcode = '{codigo}'")
    elif tipo == "i":
        new_qtd = db_qtd_total + qtd
        print("nova:"+ str(new_qtd))
        upgrade = query.execute_query(f"UPDATE stock SET total_itens = '{new_qtd}' WHERE barcode = '{codigo}'")
    else:
        mult = qtd * db_qtd
        new_qtd = db_qtd_total + mult
        print("nova:"+ str(new_qtd))
        upgrade = query.execute_query(f"UPDATE stock SET total_itens = '{new_qtd}' WHERE barcode = '{codigo}'")

    if upgrade:
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Erro ao atualizar itens no stock.")


@stock_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar():
    barcode = request.form.get('barcode')
    nome = request.form.get('nome')
    preco_compra = request.form.get('preco_compra')
    qtd = request.form.get('qtd')
    caixas = request.form.get('qtd_caixas')
    cat = request.form.get('categoria')
    preco_vendas = request.form.get('preco_venda')
    imagem = request.files.get('imagem')

    qu = f"INSERT INTO `stock`(`barcode`, `name`, `category`, `preco_Compra`, `qtd_padrao`, `total_itens`,`preco_venda`) VALUES ('{barcode}', '{nome}', '{cat}', '{preco_compra}', '{qtd}', '{str(int(caixas)*int(qtd))}', '{preco_vendas}')"
    result = query.execute_query(qu)

    if result:       
        if imagem is not None and imagem.filename != "": 
            # Save the provided image
            imagem.save('static/post/produtos/' + barcode + '.png')
        else:
            # Copy the default image to the desired location
            default_image_path = 'static/post/produtos/padrao1.png'
            new_image_path = 'static/post/produtos/' + barcode + '.png'
            if not os.path.exists(new_image_path):
                shutil.copy(default_image_path, new_image_path)
    else:
        print("erro")

    reportList = query.select_data('SELECT * FROM stock')
    category = query.select_data('SELECT * FROM category ORDER BY id ASC')
    return render_template('stock/stock.html', data=reportList,cat=category , string=str)


@stock_bp.route('/editarProduto', methods=['POST'])
@login_required
def editarProduto():
    barcode = request.form.get('input_add_cod')
    nome = request.form.get('input_add_nome')
    preco_compra = request.form.get('input_add_cromp')
    preco_venda = request.form.get('input_add_preco_venda')
    cat = request.form.get('input_add_cat')
    qtd = request.form.get('input_add_qtd')
    imagem = request.files['input_add_file']

    pathImg = 'static/post/produtos/' + barcode + '.png'

    # Corrija a consulta SQL para atualizar os campos corretos na tabela stock
    qu = f"UPDATE stock SET barcode = '{barcode}', name = '{nome}', preco_compra = '{preco_compra}', qtd_padrao = '{qtd}', preco_venda = '{preco_venda}', category = '{cat}' WHERE barcode = '{barcode}'"
    result = query.execute_query(qu)

    if result:
        if imagem is not None and imagem.filename != "": 
            if os.path.exists(pathImg):
                os.remove(pathImg)
            
            imagem.save('static/post/produtos/' + barcode + '.png')
    
    return redirect(url_for('stock.index'))


@stock_bp.route('/deletarProduto', methods=['GET'])
@login_required
def deletarProduto():
    barcode = request.args.get('barcode')
    print(f"code: {barcode}")
    nameImg = str(barcode) 
    
    pathImg =  'static/post/produtos/'+ nameImg+ '.png'
    
    if os.path.exists(pathImg):
        consulta = f"delete from `stock` where barcode = '{barcode}'"
        result = query.execute_query(consulta)
        os.remove(pathImg)
    else:
        consulta = f"delete from `stock` where barcode = '{barcode}'"
        result = query.execute_query(consulta)
        
    reportList = query.select_data('SELECT * FROM stock')
    category = query.select_data('SELECT * FROM category ORDER BY id ASC')
    return render_template('stock/stock.html', data=reportList,cat=category , string=str)    

    

    




@stock_bp.route('/newcategory', methods=['POST'])
@login_required
def newcategory():
    name = request.form.get('nome')

    consulta = f"INSERT INTO `category`(`nome`) VALUES ('{name}')"
    result = query.execute_query(consulta)

    reportList = query.select_data('SELECT * FROM stock')
    category = query.select_data('SELECT * FROM category ORDER BY id ASC')
    return render_template('stock/stock.html', data=reportList,cat=category , string=str)

    
