from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for
from functools import wraps
from classes.easyLite import SQLiteDB
import random
from datetime import datetime

query = SQLiteDB('database/cripeel.db') # instance of SQLiteDB class

qtd = 1

revendaID = ""


def set_CodeRevenda(code):
    global revendaID
    revendaID = code

def get_CodeRevenda():
    return revendaID

def statusService():
    abetura_feicho = query.select_data(f"SELECT * FROM abertura")
    if abetura_feicho:
        return abetura_feicho[0][0]
    else:
        return False

def update():
    code_revenda = get_CodeRevenda()
    List_vendidos = query.select_data(f"SELECT SUM(qtd*preco) as total, SUM(qtd) as quantidade FROM vendidos WHERE id_venda = '{code_revenda}' GROUP BY nome")
    total = sum([row[0] for row in List_vendidos])
    qtd = sum([row[1] for row in List_vendidos])
    query.execute_query(f"UPDATE vendas set total = {total} WHERE id_venda = {code_revenda}")
    query.execute_query(f"UPDATE vendas set qtd = {qtd} WHERE id_venda = {code_revenda}")
    query.execute_query(f"UPDATE vendas set pago = 0 WHERE id_venda = {code_revenda}")
    query.execute_query(f"UPDATE vendas set troco = 0 WHERE id_venda = {code_revenda}")

revenda_bp = Blueprint('revenda', __name__)

#================================================================================ funcao verificar conta

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
    
#================================================================================ rota para pesquisa de produto

@revenda_bp.route('/pesquisa', methods=['POST'])
@login_required
def pesquisa():
    valor = request.form['valor']
    print(valor)
    resultados = query.select_data(f"SELECT * FROM stock WHERE name LIKE '%{valor}%' OR barcode LIKE '%{valor}%'")
    print(resultados)
    return jsonify(resultados)
    
    
#================================================================================ rota para listar os dados do carrinho

@revenda_bp.route('/<id>')
@login_required
def carrinho(id):

    if str(id) == str(session['id_vendas']):
        return redirect(url_for('vendas.new_cart'))

    set_CodeRevenda(str(id))

    code_revenda = get_CodeRevenda()
    List_vendidos = query.select_data(f"SELECT barcode,nome,preco, SUM(qtd) as quantidade, SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{code_revenda}' GROUP BY nome")
    total =  sum([row[4] for row in List_vendidos])

    produtos = query.select_data('SELECT * FROM stock ORDER BY name ASC')
    return render_template('vendas/revenda.html', data=produtos, lista=List_vendidos,code=code_revenda, string=str)

#================================================================================ rota que retona total vendido
@revenda_bp.route('/totalVendido', methods=['POST'])
@login_required
def totalVendido():
    code_revenda = get_CodeRevenda()
    List_vendidos = query.select_data(f"SELECT SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{code_revenda}' GROUP BY nome")
    total =  sum([row[0] for row in List_vendidos])
    return jsonify(total)

#================================================================================ rota para adicionar produtos no carrinho

@revenda_bp.route('/add_carrinho', methods=['POST'])
@login_required
def add_carrinho():
    code_revenda = get_CodeRevenda()
    codigo = request.form.get('code')
    qtd = ""
    
    if '+' in codigo:
        qtd, codigo = codigo.split("+")

    if qtd == "":
        qtd = 1


    pesquisa = query.select_data(f"SELECT * FROM stock WHERE barcode = '{codigo}'")
    if not pesquisa:
        return jsonify(success=False)
    
    nome = pesquisa[0][1]
    categoria=pesquisa[0][2]
    db_qtd = pesquisa[0][5]
    preco = pesquisa[0][6]

    new_qtd =  db_qtd - qtd

    total = preco * int(qtd) if qtd else preco
    
    consulta = query.execute_query(f"INSERT INTO vendidos VALUES (NULL, '{codigo}', '{nome}', '{preco}', '{qtd}', '{total}', '{categoria}', '{code_revenda}','{session['user']['username']}')")
    
    if consulta:
        query.execute_query(f"UPDATE stock set total_itens = {new_qtd} WHERE barcode = {codigo}")
        update()
    else:
        return "<center><h1>Erro ao salvar as alteracoes no banco de dados</h1></center>"

    return jsonify(success=consulta)
    
#================================================================================ rota para listar dados vendidos AJAX

@revenda_bp.route('/lista', methods=['POST'])
@login_required
def lista():
    code_revenda = get_CodeRevenda()
    List_vendidos = query.select_data(f"SELECT barcode,nome,preco, SUM(qtd) as quantidade, SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{code_revenda}' GROUP BY nome")
    return jsonify(List_vendidos)
    
#================================================================================ rota de deletar proditos

@revenda_bp.route('/delete', methods=['POST'])
@login_required
def delete():
    code_revenda = get_CodeRevenda()
    codigo = request.form.get('code')
    qtd = request.form.get('qtd')

    pesquisa = query.select_data(f"SELECT * FROM stock WHERE barcode = '{codigo}'")
    if not pesquisa:
        return jsonify(success=False)

    db_qtd = pesquisa[0][5]
    try:
        qtd = int(qtd)  # Ensure that qtd is a numeric value
    except ValueError:
        return jsonify(success=False, message="Invalid quantity value")

    new_qtd =  db_qtd + qtd

    deletar = query.execute_query(f"DELETE FROM vendidos WHERE barcode = '{codigo}' AND id_venda = '{code_revenda}'")
    
    if deletar:
        query.execute_query(f"UPDATE stock set total_itens = {new_qtd} WHERE barcode = {codigo}")
    
    update()
    return jsonify(success=deletar)

#================================================================================ rota para pagina pagamento

@revenda_bp.route('/pagamento/')
@login_required
def pagamento():
    code_revenda = get_CodeRevenda()
    List_vendidos = query.select_data(f"SELECT SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{code_revenda}' GROUP BY nome")
    total =  sum([row[0] for row in List_vendidos])
    return render_template('vendas/refazervenda.html',total = total)

#================================================================================ rota para concluir vendas

@revenda_bp.route('/concluir/<forma>/<clinete>')
@login_required
def concluir(forma,clinete):
    code_revenda = get_CodeRevenda()
    print(forma)
    List_vendidos = query.select_data(f"SELECT SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{code_revenda}' GROUP BY nome")
    total =  sum([row[0] for row in List_vendidos])

    query.execute_query(f"UPDATE vendas set pagamento = '{forma}' WHERE id_venda = {code_revenda}")
    query.execute_query(f"UPDATE vendas set pago = {clinete} WHERE id_venda = {code_revenda}")

    troco = int(clinete) - total

    query.execute_query(f"UPDATE vendas set troco = {troco} WHERE id_venda = {code_revenda}")

    return redirect(url_for('vendas.index'))