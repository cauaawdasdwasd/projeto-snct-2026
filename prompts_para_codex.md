# Prompts para gerar as imagens dos captchas (Codex)

> **Atualização:** as seções 1, 2 e 8 (gatos, não-gatos e cientistas extras) **não são mais necessárias**.
> O jogo agora usa 16 fotos reais do Wikimedia Commons (`assets/captcha/tiles/*.jpg`, créditos em
> `assets/captcha/CREDITOS.md`), pixeladas em tempo de execução. Só o resto (VERIFY-9, invasores, Seu Nelson,
> ícones dos pop-ups, verso das cartas) ainda depende de imagens do Codex, e tem desenho reserva.

O jogo **já funciona sem estas imagens**: cada captcha tem um desenho reserva feito em código.
Quando você colocar as imagens abaixo nas pastas certas, o jogo passa a usá-las sozinho (não é
preciso mexer em código). Os **nomes dos arquivos importam**: o jogo procura por eles.

Pasta base de todas as saídas:

```
C:\Users\Meu Computador\Documents\Codex\2026-08-11\eu-preciso-criar-um-jogo-em\sob_analise\assets\captcha\
```

Ordem sugerida (do que mais aparece para o que menos aparece):
1. Gatos e não-gatos (captcha de gatinhos)
2. VERIFY-9 (o vilão, 4 expressões)
3. Invasores (mini Space Invaders)
4. Seu Nelson + ícones dos pop-ups
5. Verso das cartas + retratos extras de cientistas (opcional)

---

## Bloco de estilo (cole no começo de TODO prompt)

```
Estilo: pixel art "pintada" (painterly pixel art), como o retrato pixelado da Grace Hopper que já
existe no jogo: pixels grandes e visíveis, sombreamento suave com poucas cores, contorno escuro
sutil, paleta quente e escura com acentos em verde fósforo de monitor CRT. Visual de jogo retrô
sério, mas com um toque de humor. NÃO escreva nenhum texto, letra ou número dentro da imagem.
Formato PNG. Gere UM arquivo por imagem e salve exatamente no caminho indicado.
```

Se o Codex aceitar imagem de referência, anexe `assets\protocols\grace_hopper.png` para ele copiar o estilo.

---

## 1) Gatos: 6 imagens

Salvar em `assets\captcha\tiles\` com os nomes `cat_01.png` a `cat_06.png`.
Tamanho: **256 x 256**, quadrado, **fundo preenchido** (sem transparência), fundo verde-escuro suave
diferente em cada tile para parecerem fotos de um teste de captcha.

```
[cole o bloco de estilo]
Gere 6 imagens quadradas 256x256, cada uma com o rosto e o peito de UM gato fofo, de frente,
centralizado, com fundo verde-escuro liso ou com um leve gradiente. Gatos diferentes em cada imagem:
cat_01: gato laranja rajado, olhos verdes.
cat_02: gato cinza de olhos amarelos, meio bravo.
cat_03: gato preto de olhos dourados grandes.
cat_04: gato branco de olhos azuis, com um lacinho.
cat_05: gato tricolor (caramelo, preto e branco).
cat_06: gato siamês (bege com máscara marrom), olhos azuis.
Salvar em: ...\assets\captcha\tiles\cat_01.png ... cat_06.png
```

## 2) Não-gatos (as "pegadinhas"): 6 imagens

Salvar em `assets\captcha\tiles\` com os nomes `other_01.png` a `other_06.png`.
**256 x 256**, mesmo formato dos gatos (fundo preenchido, mesma altura de enquadramento).
Devem ser fofos e **parecidos com gato à primeira vista**, mas claramente outra coisa.

```
[cole o bloco de estilo]
Gere 6 imagens quadradas 256x256, mesmo enquadramento e fundo verde-escuro das imagens de gato,
mas mostrando COISAS QUE NÃO SÃO GATOS (pegadinhas de captcha):
other_01: cachorro shiba caramelo de frente.
other_02: um pão de forma dourado, com cara de sonolento (sem boca e sem texto).
other_03: uma coruja marrom de olhos enormes.
other_04: um coelho branco de orelhas longas.
other_05: um robozinho quadrado com antena e olhos azuis.
other_06: uma raposa laranja de frente.
Salvar em: ...\assets\captcha\tiles\other_01.png ... other_06.png
```

---

## 3) VERIFY-9, o vilão: 4 expressões

Salvar em `assets\captcha\verify9\` com os nomes `verify9_neutral.png`, `verify9_suspicious.png`,
`verify9_angry.png`, `verify9_happy.png`. **512 x 512**, **fundo transparente**.

```
[cole o bloco de estilo]
Personagem: VERIFY-9, uma IA de segurança que enlouqueceu. Design: uma moldura HEXAGONAL metálica
verde-escura com detalhes de circuito, e dentro dela UM olho gigante e redondo (branco-esverdeado)
com íris luminosa; embaixo do hexágono, um pequeno cadeado. Fundo transparente, personagem centralizado,
vista frontal. Gere 4 imagens com a MESMA composição e tamanho, mudando só a expressão e a cor do brilho:
verify9_neutral: íris verde fósforo, olhar calmo e vigilante.
verify9_suspicious: íris âmbar, pálpebra pela metade, sobrancelha levantada, olhar desconfiado.
verify9_angry: íris vermelha, sobrancelha inclinada para baixo, faíscas, olhar furioso.
verify9_happy: íris ciano, olho em forma de arco sorridente, com um brilho de derrota-fofa (como
"você me venceu").
Salvar em: ...\assets\captcha\verify9\
```

---

## 4) Space Invaders do captcha: 5 sprites

Salvar em `assets\captcha\invaders\` com os nomes `enemy_01_bug.png`, `enemy_02_virus.png`,
`enemy_03_spam.png`, `enemy_04_bot.png`, `player_ship.png`. **128 x 128**, **fundo transparente**.
Atenção: no jogo eles aparecem **pequenos (46 x 34 pixels)**, então precisam ter silhueta grossa,
legível e poucos detalhes finos.

```
[cole o bloco de estilo]
Gere 5 sprites de jogo de nave, vista frontal, silhueta grossa e legível mesmo bem pequena, fundo
transparente, 128x128, centralizados:
enemy_01_bug: um inseto "bug" de programação (besouro com antenas e perninhas).
enemy_02_virus: um vírus de computador roxo e espinhoso, com olhos maldosos.
enemy_03_spam: um envelope de e-mail com olhinhos e sorriso maldoso (spam), sem texto.
enemy_04_bot: uma cabeça de robô malvado, com antena e um olho vermelho só.
player_ship: a nave do jogador: um cursor de mouse (seta) brilhante amarelo-claro, com chamas azuis
atrás, apontando para cima.
Salvar em: ...\assets\captcha\invaders\
```

---

## 5) Seu Nelson (o técnico de TI de férias)

Salvar em `assets\captcha\nelson\nelson.png`. **512 x 512**, **fundo transparente**, busto (do peito
para cima), no mesmo estilo dos retratos das cientistas.

```
[cole o bloco de estilo]
Retrato em busto do "Seu Nelson", técnico de TI brasileiro de meia-idade, que saiu de férias e deixou o
celular desligado: barriga simpática, bigode, camisa florida havaiana, óculos escuros empurrados para a
testa, um crachá de funcionário pendurado no pescoço (sem texto), sorriso tranquilo, segurando um coco
com canudinho. Expressão de "não me ligue". Fundo transparente, de frente.
Salvar em: ...\assets\captcha\nelson\nelson.png
```

## 6) Ícones dos pop-ups: 4 imagens

Salvar em `assets\captcha\ads\` com os nomes `ad_gift.png`, `ad_pc.png`, `ad_rocket.png`,
`ad_shield.png`. **128 x 128**, **fundo transparente**.

```
[cole o bloco de estilo]
Gere 4 ícones grandes e exagerados, no estilo de anúncios enganosos de internet dos anos 2000,
128x128, fundo transparente, centralizados, sem texto:
ad_gift: uma caixa de presente dourada com laço vermelho e brilhos.
ad_pc: um computador retrô bege com carinha de desespero e uma ampulheta em cima do monitor.
ad_rocket: um foguetinho turbo vermelho e branco com chamas grandes.
ad_shield: um escudo de antivírus azul com uma carinha desconfiada e um olho suspeito.
Salvar em: ...\assets\captcha\ads\
```

---

## 7) Verso das cartas (jogo da memória)

Salvar em `assets\captcha\cards\card_back.png`. **256 x 288** (vertical), **fundo preenchido**.

```
[cole o bloco de estilo]
Verso de uma carta de jogo da memória, vertical 256x288, fundo verde-escuro com padrão geométrico
sutil de circuito, moldura decorada dourada-esverdeada, e no centro o olho hexagonal do VERIFY-9
(hexágono com um olho e um cadeado pequeno), em verde fósforo brilhante. Sem texto.
Salvar em: ...\assets\captcha\cards\card_back.png
```

## 8) (Opcional) Mais cientistas para os quebra-cabeças

Os captchas de girar a foto, quebra-cabeça e memória usam os 6 retratos que já existem. Estes 4 entram
sozinhos no sorteio e dão mais variedade. Salvar em `assets\captcha\portraits\` (qualquer nome `.png`).
**1254 x 1254**, **fundo transparente**, busto de frente, **exatamente o mesmo estilo e enquadramento**
de `assets\protocols\grace_hopper.png`.

```
[cole o bloco de estilo]
Gere um retrato em busto, 1254x1254, fundo transparente, mesmo enquadramento e estilo do retrato pixelado
da Grace Hopper, de cada pessoa abaixo, com aparência respeitosa e reconhecível:
joy_buolamwini.png: Joy Buolamwini, pesquisadora que revelou o viés racial e de gênero em reconhecimento facial.
hedy_lamarr.png: Hedy Lamarr, atriz e inventora do salto de frequência (base do wi-fi).
timnit_gebru.png: Timnit Gebru, pesquisadora de ética e justiça em inteligência artificial.
mae_jemison.png: Mae Jemison, engenheira e primeira mulher negra astronauta.
Salvar em: ...\assets\captcha\portraits\
```

---

## 9) Fotos dos papéis dos casos (as mais importantes agora)

Estes papéis do jogo têm uma **imagem** no meio. Hoje eles usam um desenho feito em código; quando o
arquivo abaixo existir, o jogo passa a usar a imagem sozinho. O jogador pode **clicar na imagem para
circular algo com caneta vermelha**. O jogo cobre os textos importantes (placa, números) por código, então
**as imagens não podem ter nenhuma letra ou número**.

Todas: **1088 x 256 (bem larga, 4,25 : 1)**, PNG, fundo preenchido (sem transparência). O jogo mostra a
imagem em 544 x 128, então o assunto precisa ficar **centralizado e grande**, com margem nas laterais.

Pasta base: `...\sob_analisessets\cases\<pasta do caso>\`

### 9.1) Caso "A Placa Fantasma" → `assets\cases\case_32adar.png`

```
[cole o bloco de estilo]
Foto de câmera de radar de pedágio, tirada de trás e de cima, à tarde. Um sedan prata visto por trás,
centralizado, numa pista de asfalto, com o teto do pórtico do pedágio no alto. A placa do carro está
suja de lama marrom, ILEGÍVEL, sem nenhuma letra ou número visível. Deixe o canto superior direito
vazio (só asfalto ou céu), porque o jogo coloca uma legenda ali. Sem texto na imagem inteira.
Formato 1088x256. Salvar em: ...ssets\cases\case_32adar.png
```

### 9.2) Caso "A Quimera Sindical" → 3 imagens em `assets\cases\case_44\`

```
[cole o bloco de estilo]
crowd.png: foto de câmera de segurança de uma manifestação de trabalhadores na rua, vista de frente,
multidão com cartazes brancos e em branco (sem escrever nada neles), uns de boné, alguns de máscara.
Ninguém deve estar em destaque. Formato 1088x256.

joao.png: foto de crachá (fundo cinza liso) de um homem de uns 40 anos, ROSTO REDONDO, com ÓCULOS
REDONDOS de armação escura, cabelo curto castanho, camisa azul. Busto centralizado, com muito espaço
cinza dos dois lados. Formato 1088x256.

pedro.png: foto de crachá (fundo cinza liso) de um homem de uns 40 anos, ROSTO QUADRADO e queixo forte,
com CAVANHAQUE, sem óculos, cabelo curto castanho, camisa azul. Busto centralizado, com muito espaço
cinza dos dois lados. Formato 1088x256.

Salvar em: ...ssets\cases\case_44\crowd.png, joao.png e pedro.png
```

Os outros papéis com imagem (crachá da portaria, mapa do GPS, planta do shopping, QR da peça, gráfico do
drone e a placa borrada da peça) **ficam desenhados por código** de propósito: o texto e os números deles
são a pista do caso, e uma imagem gerada erraria as letras.

---

## Depois de gerar

1. Confira que os arquivos estão nas pastas com os nomes exatos.
2. Abra o jogo (`JOGAR.bat`), escolha o **modo relógio** e jogue um caso: as imagens aparecem nas
   verificações e nos pop-ups sozinhas.
3. Se alguma ficar ruim (silhueta pequena demais, por exemplo), peça de novo só aquela e substitua o
   arquivo.
