const tamanhos = [
    "pequena",
    "normal",
    "media",
    "grande",
    "maior",
    "enorme",
    "maxima"
];

let tamanhoAtual = 1;

const pagina = document.documentElement;
const botaoDiminuir = document.getElementById("diminuir-fonte");
const botaoAumentar = document.getElementById("aumentar-fonte");

function atualizarFonte() {
    pagina.dataset.fonte = tamanhos[tamanhoAtual];
    botaoDiminuir.disabled = tamanhoAtual === 0;
    botaoAumentar.disabled = tamanhoAtual === tamanhos.length - 1;
}

botaoDiminuir.addEventListener("click", function () {
    if (tamanhoAtual > 0) {
        tamanhoAtual--;
        atualizarFonte();
    }
});

botaoAumentar.addEventListener("click", function () {
    if (tamanhoAtual < tamanhos.length - 1) {
        tamanhoAtual++;
        atualizarFonte();
    }
});

atualizarFonte();
