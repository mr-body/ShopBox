const disabledKeys = ["u", "I"];

const showAlert = e => {
    e.preventDefault();
    return alert("Sorry, you can't view or copy source codes this way!");
}

document.addEventListener("contextmenu", e => {
    showAlert(e);
});

document.addEventListener("keydown", e => {
    if (e.ctrlKey && disabledKeys.includes(e.key) || e.key === "F12") {
        showAlert(e);
    }
});







$('body').keypress(function (e) { 
    if(e.keyCode === 13){
        console.log("clicado")
        document.querySelector('#btn-open-modal').click()
    }
});