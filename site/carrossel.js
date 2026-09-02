const slides = Array.from(document.querySelectorAll(".slide-carrossel"));
const botaoAnterior = document.querySelector(".seta-anterior");
const botaoProximo = document.querySelector(".seta-proxima");
const contador = document.getElementById("captura-atual");
const visualizador = document.getElementById("visualizador");
const imagemAmpliada = document.getElementById("imagem-ampliada");
const legendaAmpliada = document.getElementById("legenda-ampliada");
const fecharVisualizador = document.getElementById("fechar-visualizador");

let slideAtual = 0;
let ultimoFoco = null;

function mostrarSlide(indice) {
    slideAtual = (indice + slides.length) % slides.length;

    slides.forEach(function (slide, posicao) {
        slide.hidden = posicao !== slideAtual;
    });

    contador.textContent = String(slideAtual + 1).padStart(2, "0");
}

function abrirImagem(slide) {
    const imagem = slide.querySelector("img");
    const legenda = slide.querySelector("figcaption");

    ultimoFoco = document.activeElement;
    imagemAmpliada.src = imagem.src;
    imagemAmpliada.alt = imagem.alt;
    legendaAmpliada.textContent = legenda.textContent;
    visualizador.hidden = false;
    document.body.classList.add("sem-rolagem");
    fecharVisualizador.focus();
}

function fecharImagem() {
    visualizador.hidden = true;
    imagemAmpliada.src = "";
    document.body.classList.remove("sem-rolagem");

    if (ultimoFoco) {
        ultimoFoco.focus();
    }
}

botaoAnterior.addEventListener("click", function () {
    mostrarSlide(slideAtual - 1);
});

botaoProximo.addEventListener("click", function () {
    mostrarSlide(slideAtual + 1);
});

slides.forEach(function (slide) {
    slide.querySelector(".abrir-captura").addEventListener("click", function () {
        abrirImagem(slide);
    });
});

fecharVisualizador.addEventListener("click", fecharImagem);

visualizador.addEventListener("click", function (evento) {
    if (evento.target === visualizador) {
        fecharImagem();
    }
});

document.addEventListener("keydown", function (evento) {
    if (!visualizador.hidden && evento.key === "Escape") {
        fecharImagem();
        return;
    }

    if (visualizador.hidden && evento.key === "ArrowLeft") {
        mostrarSlide(slideAtual - 1);
    }

    if (visualizador.hidden && evento.key === "ArrowRight") {
        mostrarSlide(slideAtual + 1);
    }
});

mostrarSlide(0);
