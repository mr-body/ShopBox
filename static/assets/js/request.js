function requestFunctio(url) {
    var loc = '/' + url;
    var texto = 'ola';
    // Criar uma instância do objeto XMLHttpRequest
    var xhr = new XMLHttpRequest();

    // Definir o tipo de solicitação e a URL de destino
    xhr.open('POST', loc, true);

    // Definir o cabeçalho da solicitação
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

    // Enviar os dados para o servidor
    xhr.send('dados=' + encodeURIComponent(texto));



    // Definir a função de callback para tratar a resposta do servidor
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        // Tratar a resposta do servidor
            return xhr.responseText;
        }
    };
}
