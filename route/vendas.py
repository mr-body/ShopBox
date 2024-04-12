from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for
from functools import wraps
from flask_session import Session
from classes.easyLite import SQLiteDB
import random
#import win32print
from datetime import datetime

query = SQLiteDB('database/cripeel.db') # instancia de classe SQLiteDB

qtd = 1

def imprimir_ticket(conteudo):
    # Obter a impressora padrão do sistema
    impressora_padrao = win32print.GetDefaultPrinter()

    # Definir as configurações de impressão
    hPrinter = win32print.OpenPrinter(impressora_padrao)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket", None, "RAW"))
        try:
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, conteudo.encode())
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)  

def statusService():
    abetura_feicho = query.select_data(f"SELECT * FROM abertura")
    if abetura_feicho:
        return abetura_feicho[0][0]
    else:
        return False

def update(qtd_nova,barcode):
    List_vendidos = query.select_data(f"SELECT SUM(qtd*preco) as total, SUM(qtd) as quantidade FROM vendidos WHERE id_venda = '{session['id_vendas']}' GROUP BY nome")
    total =  sum([row[0] for row in List_vendidos])
    qtd =  sum([row[1] for row in List_vendidos])
    query.execute_query(f"UPDATE vendas set total = {total} WHERE id_venda = {session['id_vendas']}")
    query.execute_query(f"UPDATE vendas set qtd = {qtd} WHERE id_venda = {session['id_vendas']}")
    query.execute_query(f"UPDATE stock set total_itens = {qtd_nova} WHERE barcode = {barcode}")

vendas_bp = Blueprint('vendas', __name__)

#================================================================================ funcao verificar conta

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
    
#================================================================================ rota pra pagina de vendas

@vendas_bp.route('/')
@login_required
def index():
    if statusService():        
        if 'id_vendas' not in session:
            return redirect(url_for('vendas.new_cart'))
            
        else:
            pro_vendidos = query.select_data(f"SELECT * FROM vendas WHERE cliente = '{session['user']['username']}' ORDER BY id desc")
            consulta = query.select_data(f"SELECT pagamento, sum(total) as total from vendas WHERE cliente = '{session['user']['username']}' GROUP BY pagamento ")
            lista_vendas = query.select_data(f"SELECT nome,preco,sum(qtd) as quantidade,sum(total) as total FROM vendidos WHERE user = '{session['user']['username']}' GROUP BY barcode ORDER BY nome")

            List_vendas= query.select_data(f"SELECT total,pago FROM vendas WHERE cliente = '{session['user']['username']}'")
            List_vendas_dispesas= query.select_data(f"SELECT troco FROM vendas WHERE troco < 0 AND cliente = '{session['user']['username']}'")
            List_entrada= query.select_data(f"SELECT * FROM entrada ORDER BY nome ASC")
            total =  sum([row[0] for row in List_vendas])

            desconto = 0

            for lista in List_vendas_dispesas:
                desconto = desconto + (lista[0] * -1)
            


            pago =  total - desconto


            return render_template('vendas/vendas.html',entrada=List_entrada,lista=lista_vendas, session=session['id_vendas'], user=session['user']['username'], relatorio=consulta, data=pro_vendidos, total=total, vendido=pago, desconto=desconto, keycode=statusService(), string=str,dadosUser = session['user'])
    else:
        return render_template('exception/504.html',string=str,dadosUser = session['user'])


    
#================================================================================ rota para pesquisa de produto

@vendas_bp.route('/pesquisa', methods=['POST'])
@login_required
def pesquisa():
    valor = request.form['valor']
    print(valor)
    resultados = query.select_data(f"SELECT * FROM stock WHERE name LIKE '%{valor}%' OR barcode LIKE '%{valor}%' ORDER BY name ASC")
    print(resultados)
    return jsonify(resultados)
    
#================================================================================ rota para inicar novo carrinho

@vendas_bp.route('/new')
@login_required
def new_cart():
    if 'id_vendas' not in session:
        session['id_vendas'] = random.randint(10000, 80000)          
        current_time = datetime.now().strftime('%d/%m/%y %H:%M:%S')
        create = query.execute_query(f"INSERT INTO vendas VALUES (NULL, '{current_time}', '{session['user']['username']}', 'PGM', 0, 0, 0, 0, '{session['id_vendas']}')")
        if create:
            return redirect(url_for('vendas.carrinho'))
        else:
            return "Erro ao criar o novo carrinho"
    else:     
        return redirect(url_for('vendas.carrinho'))
    
#================================================================================ rota para listar os dados do carrinho

@vendas_bp.route('/carrinho', methods=['GET'])
@login_required
def carrinho():
    List_vendidos = query.select_data(f"SELECT barcode,nome,preco, SUM(qtd) as quantidade, SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{session['id_vendas']}' GROUP BY nome")
    total =  sum([row[4] for row in List_vendidos])

    produtos = query.select_data('SELECT * FROM stock ORDER BY name ASC')
    return render_template('vendas/carrinho.html', data=produtos,lista=List_vendidos, string=str)

#================================================================================ rota que retona total vendido
@vendas_bp.route('/totalVendido', methods=['POST'])
@login_required
def totalVendido():
    List_vendidos = query.select_data(f"SELECT SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{session['id_vendas']}' GROUP BY nome")
    total =  sum([row[0] for row in List_vendidos])
    return jsonify(total)

#================================================================================ rota para adicionar produtos no carrinho

@vendas_bp.route('/add_carrinho', methods=['POST'])
@login_required
def add_carrinho():
    requerid = request.form.get('code')
    qtd = 1

    if "+" in requerid:
        def SeparePalavra(palavra):
            partes = palavra.split('+')
            if len(partes) == 2:
                antes_do_mais, depois_do_mais = partes
                return antes_do_mais, depois_do_mais
            else:
                return palavra, None

        antes, depois = SeparePalavra(requerid)

        if antes != "" and depois != "":
            qtd = int(antes)
            codigo = depois
        elif antes == "" and depois != "":
            codigo = depois
    else:
        codigo = requerid


    pesquisa = query.select_data(f"SELECT * FROM stock WHERE barcode = '{codigo}'")
    if not pesquisa:
        return jsonify(success=False)
    
    # if pesquisa[0][5] < qtd:
    #     return jsonify(success=False)

    nome = pesquisa[0][1]
    categoria= pesquisa[0][2]
    db_qtd = pesquisa[0][5]
    preco = pesquisa[0][6]

    new_qtd =  db_qtd - qtd

    if new_qtd < 0:
        return jsonify(success=False)

    total = preco * int(qtd) if qtd else preco
    
    consulta = query.execute_query(f"INSERT INTO vendidos VALUES (NULL, '{codigo}', '{nome}', '{preco}', '{qtd}', '{total}', '{categoria}', '{session['id_vendas']}','{session['user']['username']}')")
    
    if consulta:
        update(new_qtd,codigo)
    else:
        return "<center><h1>Erro ao salvar as alteracoes no banco de dados</h1></center>"

    return jsonify(success=consulta)
    
#================================================================================ rota para listar dados vendidos AJAX

@vendas_bp.route('/lista', methods=['POST'])
@login_required
def lista():
    List_vendidos = query.select_data(f"SELECT barcode,nome,preco, SUM(qtd) as quantidade, SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{session['id_vendas']}' GROUP BY nome")
    return jsonify(List_vendidos)
    
#================================================================================ rota de deletar proditos

@vendas_bp.route('/delete', methods=['POST'])
@login_required
def delete():
    codigo = request.form.get('code')
    qtd = request.form.get('qtd')

    print(codigo)

    pesquisa = query.select_data(f"SELECT * FROM stock WHERE barcode = '{codigo}'")
    if not pesquisa:
        return jsonify(success=False)

    db_qtd = pesquisa[0][5]
    try:
        qtd = int(qtd)  # Ensure that qtd is a numeric value
    except ValueError:
        return jsonify(success=False, message="Invalid quantity value")

    new_qtd =  db_qtd + qtd

    deletar = query.execute_query(f"DELETE FROM vendidos WHERE barcode = '{codigo}' AND id_venda = '{session['id_vendas']}'")
    
    update(new_qtd,codigo)

    return jsonify(success=deletar)

#================================================================================ rota de deletar proditos

@vendas_bp.route('/deleteVenda/<id>', methods=['GET'])
@login_required
def deleteVenda(id):
    if str(id) != str(session['id_vendas']):
        query.execute_query(f"DELETE FROM vendidos WHERE id_venda = '{id}'")
        query.execute_query(f"DELETE FROM vendas WHERE id_venda = '{id}'")   

    return redirect(url_for('vendas.index'))

#================================================================================ rota para pagina pagamento

@vendas_bp.route('/pagamento')
@login_required
def pagamento():
    List_vendidos = query.select_data(f"SELECT SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{session['id_vendas']}' GROUP BY nome")
    total =  sum([row[0] for row in List_vendidos])
    return render_template('vendas/concluirvenda.html',total = total)
    return redirect(url_for('vendas.new_cart'))

#================================================================================ rota para concluir vendas

@vendas_bp.route('/concluir/<forma>/<clinete>/<check>')
@login_required
def concluir(forma,clinete,check):
    print(forma)
    List_vendidos = query.select_data(f"SELECT SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{session['id_vendas']}' GROUP BY nome")
    total =  sum([row[0] for row in List_vendidos])

    query.execute_query(f"UPDATE vendas set pagamento = '{forma}' WHERE id_venda = {session['id_vendas']}")
    query.execute_query(f"UPDATE vendas set pago = {clinete} WHERE id_venda = {session['id_vendas']}")

    troco = int(clinete) - total

    query.execute_query(f"UPDATE vendas set troco = {troco} WHERE id_venda = {session['id_vendas']}")
      
    List_vendidos = query.select_data(f"SELECT barcode,nome,preco, SUM(qtd) as quantidade, SUM(qtd*preco) as total FROM vendidos WHERE id_venda = '{session['id_vendas']}' GROUP BY nome")
    total =  sum([row[4] for row in List_vendidos])

    current_time = datetime.now().strftime('%d/%m/%y %H:%M:%S')

    conteudo_do_ticket = [
        "\t\t  MATA SEDE\n",
        "\tA melhor loja/Bar do GOLFII\n",
        "\t  https://matasede.web.app\n",
        "==============================================\n",
        f"Vendedor:             {session['user']['fullname']}\n",
        f"DATA:                 {current_time}\n",
        f"NIF:                  \n",
        f"PAGO:                 {forma}\n",
        "==============================================\n",
    ]

    for dados in List_vendidos:
        string = f"{dados[1]}\n     {dados[2]}kz x {dados[3]}\t\t\t{dados[4]}kz\n"
        
        conteudo_do_ticket.append(string)
        
    
    conteudo_do_ticket.append(
        "==============================================\n"
        f"TOTAL:                            {str(total)}kz\n"
        f"PAGO:                             {clinete}kz\n"
        f"DESCONTO:                         0.00\n"
        f"TROCO:                            {str(troco)}kz\n\n"
        "\nObrigado por comprar conosco! \n\n\n\n\n\n\n\n\n\n\n\n\n"
    )

    if check == "true":
        # Imprimir o ticket
        imprimir_ticket('\n'.join(conteudo_do_ticket))
        print('\n'.join(conteudo_do_ticket))

    session.pop('id_vendas', None)
    return redirect(url_for('vendas.new_cart'))

    #================================================================================ rota pra pagina de vendas

@vendas_bp.route('/feicho', methods=['POST'])
@login_required
def feicho():
    pro_vendidos = query.select_data(f"SELECT * FROM vendas WHERE cliente = '{session['user']['username']}' ORDER BY id desc")
    consulta = query.select_data(f"SELECT pagamento, sum(total) as total from vendas WHERE cliente = '{session['user']['username']}' GROUP BY pagamento ")

    List_vendas= query.select_data(f"SELECT total,pago FROM vendas WHERE cliente = '{session['user']['username']}'")
    List_vendas_dispesas= query.select_data(f"SELECT troco FROM vendas WHERE troco < 0 AND cliente = '{session['user']['username']}'")
    total =  sum([row[0] for row in List_vendas])

    desconto = 0

    for lista in List_vendas_dispesas:
        desconto = desconto + (lista[0] * -1)
    


    pago =  total - desconto


    current_time = datetime.now().strftime('%d/%m/%y %H:%M:%S')

    conteudo_do_ticket = [
        "\t\t  MATA SEDE\n",
        "\tA melhor loja/Bar do GOLFII\n",
        "\t  https://matasede.web.app\n",
        "==============================================\n",
        f"Vendedor:         {session['user']['fullname']}\n",
        f"Sessao:           {session['id_vendas']}\n",
        f"Data:             {current_time}\n",
        "-----------------------------------------------\n",
    ]


    for dados in consulta:
        string = f"{dados[0]}:              {dados[1]}kz\n"
        
        conteudo_do_ticket.append(string)
        
    
    conteudo_do_ticket.append(       
        "==============================================\n"
        f"TOTAL:                {total}\n\n"
        f"DIVIDA:               {desconto}\n\n"
        f"VENDIDO:              {pago}\n\n"
        f"Receita de venda\n\n\n\n\n\n\n\n\n"
    )

    # Imprimir o ticket
    imprimir_ticket('\n'.join(conteudo_do_ticket))
    print('\n'.join(conteudo_do_ticket))
    return jsonify(success=True)


@vendas_bp.route('/relatorio', methods=['POST'])
@login_required
def relatorio():
    
    consulta = query.select_data(f"SELECT nome,preco,sum(qtd) as quantidade,sum(total) as total FROM vendidos WHERE user = '{session['user']['username']}' GROUP BY barcode ORDER BY nome")
    total =  sum([row[3] for row in consulta])


    current_time = datetime.now().strftime('%d/%m/%y %H:%M:%S')

    conteudo_do_ticket = [
        "\t\t  MATA SEDE\n",
        "\t Relatorio de vendas feitas \n",
        "==============================================\n",
        f"Vendedor:         {session['user']['fullname']}\n",
        f"Data:             {current_time}\n",
        "-----------------------------------------------\n",
    ]

    for dados in consulta:
        string = f"{dados[0]}:\n    {dados[1]}kz x {dados[2]}\t\t\t{dados[3]}\n"
        
        conteudo_do_ticket.append(string)
        
    
    conteudo_do_ticket.append(       
        "-----------------------------------------------\n"
        f"TOTAL:                {total}\n\n\n\n\n\n"
    )

    # Imprimir o ticket
    imprimir_ticket('\n'.join(conteudo_do_ticket))
    print('\n'.join(conteudo_do_ticket))
    return jsonify(success=True)
    
