const totalInput = document.getElementById("total");
const pagamentoInput = document.getElementById("pagamento");
const descontoInput = document.getElementById("desconto");
const trocoSpan = document.getElementById("troco");
const boxtroco = document.getElementById("boxtroco");
const totalComDescontoSpan = document.getElementById("total-com-desconto");
const valorBtns = document.querySelectorAll(".valor-btn");
const digitoBtns = document.querySelectorAll(".digito-btn");
const ceBtn = document.querySelector(".ce-btn");
const cBtn = document.querySelector(".c-btn");

function calcular() {
  const total = parseFloat(totalInput.value);
  const pagamento = parseFloat(pagamentoInput.value);
  const desconto = parseFloat(descontoInput.value) / 100;
  
  const totalComDesconto = total * (1 - desconto);
  const troco = pagamento - totalComDesconto;
  
  trocoSpan.textContent = troco+ ",00";
  boxtroco.value = troco;
  totalComDescontoSpan.textContent = totalComDesconto+ ",00";
}

totalInput.addEventListener("keyup", calcular);
pagamentoInput.addEventListener("keyup", calcular);
descontoInput.addEventListener("keyup", calcular);

for (let i = 0; i < valorBtns.length; i++) {
  valorBtns[i].addEventListener("click", function() {
    const valor = parseFloat(valorBtns[i].value);
    pagamentoInput.value = parseFloat(pagamentoInput.value) + valor;
    calcular();
  });
}

for (let i = 0; i < digitoBtns.length; i++) {
  digitoBtns[i].addEventListener("click", function() {
    pagamentoInput.value += digitoBtns[i].value;
    calcular();
  });
}

ceBtn.addEventListener("click", function() {
  pagamentoInput.value = pagamentoInput.value.slice(0, -1);
  calcular();
});

cBtn.addEventListener("click", function() {
  pagamentoInput.value = "0";
  descontoInput.value = "0";
  trocoSpan.textContent = "0";
  totalComDescontoSpan.textContent = "0";
});
