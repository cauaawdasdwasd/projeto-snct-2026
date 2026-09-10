const botoesProtocolos = Array.from(document.querySelectorAll(".resumo-protocolo"));

botoesProtocolos.forEach(function (botao) {
    botao.addEventListener("click", function () {
        const estaAberto = botao.getAttribute("aria-expanded") === "true";
        const detalhe = document.getElementById(botao.getAttribute("aria-controls"));
        const textoAcao = botao.querySelector(".acao-protocolo");

        botao.setAttribute("aria-expanded", String(!estaAberto));
        detalhe.hidden = estaAberto;
        textoAcao.firstChild.textContent = estaAberto ? "ABRIR FICHA " : "FECHAR FICHA ";
        textoAcao.querySelector("span").textContent = estaAberto ? "+" : "−";
    });
});
