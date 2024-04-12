$("#code").focus();

total()

document.getElementById('carrinhoForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Evitar envio do formulário

    var code = document.getElementById('code').value;

    // Fazer uma requisição AJAX
    fetch('/revenda/add_carrinho', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'code=' + encodeURIComponent(code),
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            resetCodeInput();
            refreshIframe(code);
        } else {
            resetCodeInput();
            alert(`O código ${code} não foi encontrado no banco de dados.`);
        }
    })
    .catch(function(error) {
        console.error('Erro:', error);
    });
});

$('#searchText').on('input', function() {
    var valor = $(this).val();

    // Fazer uma requisição AJAX
    $.ajax({
        type: 'POST',
        url: '/revenda/pesquisa',
        data: { valor: valor },
        success: function(data) {
            // Limpar a lista atual
            $('.lista').empty();

            // Iterar sobre os resultados e adicionar à lista
            $.each(data, function(index, string) {
                if(string[5] > 0){
                    let id = string[7];
                    img = "../static/post/produtos/"+id+".png"
                    var caixaHTML = `
                        <div class="caixa" onclick="add('${id}')">
                            <img src="${img}" alt="" class="perfil">
                            <h2>${string[1]}</h2>
                            <h4>${string[2]}</h4>
                            <h1>${string[6].toLocaleString()}</h1>
                        </div>
                    `;
                }
                $('.lista').append(caixaHTML);
            });
        }
    });
});

function add(barcode) {
    // Fazer uma requisição AJAX
    fetch('/revenda/add_carrinho', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'code=' + encodeURIComponent(barcode),
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            resetCodeInput();
            refreshIframe(barcode);
        } else {
            resetCodeInput();
            alert(`O código ${code} não foi encontrado no banco de dados.`);
        }
    })
    .catch(function(error) {
        console.error('Erro:', error);
    });
}

function resetCodeInput() {
    $("#code").val("");
    $("#code").focus();
}

function refreshIframe(code) {
    // Fazer uma requisição AJAX
    $.ajax({
        type: 'POST',
        url: '/revenda/lista',
        data: { valor: code },
        success: function(data) {
            // Limpar a lista atual
            $('.listaAjax').empty();

            // Iterar sobre os resultados e adicionar à lista
            $.each(data, function(index, string) {
                let id = string[0];
                img = "../static/post/produtos/"+id+".png"
                var caixaHTML = `
                    <tr>
                        <td><img src="${img}" id="perfilmin" alt=""></td>
                        <td style="text-align:left">${string[1]}</td>
                        <td style="text-align:left">${string[2].toLocaleString()} kz</td>
                        <td>${string[3]}</td>
                        <td style="text-align:left" >${string[4].toLocaleString()} kz</td>
                        <td><a id="delete" onclick="deleter('${id}','${string[3]}')" title="remover do carrinho"><span class="fi-rr-trash" style="font-size: 15pt;"></span></a></td>
                    </tr>
                `;
                $('.listaAjax').append(caixaHTML);

            });
        }
    });

    // Verificar se a imagem existe
    var imageUrl = "../static/post/produtos/"+code+".png"
    $.get(imageUrl)
    .done(function() {
        // Caso a imagem exista, definir o atributo 'src' do elemento '#preview_image'
        $('#imagemDePerfil').attr('src', imageUrl);
    })
    .fail(function() {
        // Caso a imagem não exista, definir um atributo 'src' de fallback ou mostrar uma imagem padrão
        $('#imagemDePerfil').attr('src', '/static/post/produtos/padrao.png');
        // Ou você pode ocultar o elemento completamente, se preferir:
        // $('#preview_image').hide();
    });
    total()
}


function deleter(barcode, qtd) {
    if (confirm("Deseja Realmente Apagar este Produto")) {
        // Fazer uma requisição AJAX
        fetch('/revenda/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'code=' + encodeURIComponent(barcode) + '&qtd=' + encodeURIComponent(qtd)
        })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
            resetCodeInput();
            refreshIframe(barcode);
            } else {
            resetCodeInput();
            alert(`Erro ao deletar o produto de referencia ${barcode}`);
            }
        })
        .catch(function (error) {
            console.error('Erro:', error);
        });
    }
}

function total()
{
    // Fazer uma requisição AJAX
    $.ajax({
        type: 'POST',
        url: '/revenda/totalVendido',
        data: { valor: "total" },
        success: function(data) {
            // Limpar a lista atual
            $('#total').html(data.toLocaleString()+" kz");
        }
    });
}