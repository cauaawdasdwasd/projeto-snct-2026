# Sob Análise

**Sob Análise** é um jogo 2D de auditoria algorítmica feito em Python com
`pygame-ce`. O jogador analisa decisões tomadas por uma IA no mundo do trabalho,
consulta documentos e protocolos e escolhe entre aprovar, negar, encaminhar para
revisão humana ou registrar uma violação.

O projeto trabalha temas como viés algorítmico, privacidade, ciência de dados e
relações de poder. Os seis protocolos são inspirados em mulheres importantes da
ciência e da computação.

## Requisitos

- Python 3.11 ou superior
- `pygame-ce`
- `ModernGL` e `trimesh` para a inspeção física de objetos 3D

## Instalação

```powershell
cd .\sob_analise
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Rodar o jogo

No Windows, dê dois cliques em `JOGAR.bat`.

Também é possível iniciar pelo terminal:

```powershell
python main.py
```

## Trabalhar em equipe pelo GitHub

O projeto está conectado ao repositório
[`cauaawdasdwasd/projeto-snct-2026`](https://github.com/cauaawdasdwasd/projeto-snct-2026).

- Antes de começar a trabalhar, dê dois cliques em `ATUALIZAR_DO_GITHUB.bat`.
- Para enviar suas alterações, dê dois cliques em `PUBLICAR_NO_GITHUB.bat`, escreva
  uma descrição curta e aguarde a confirmação.
- O GitHub Desktop pode ser usado para visualizar arquivos alterados, commits e
  conflitos. Ele busca novidades automaticamente, mas é necessário clicar em
  `Pull origin` para aplicar os arquivos remotos no PC.
- Se duas pessoas editarem a mesma parte de um arquivo, o Git não escolhe sozinho:
  a equipe deve revisar o conflito no GitHub Desktop antes de publicar.

## Controles atuais

- O menu inicial usa uma estação CRT animada e permite iniciar o turno, abrir as
  configurações ou consultar os créditos. Todas as opções funcionam por mouse ou
  teclado, e o aparelho acompanha o cursor com um movimento sutil. A interface é
  recortada pela curvatura do vidro e permanece dentro do visor.
- `INICIAR TURNO` abre a tela de acesso da estação. Os campos de usuário e senha
  aceitam teclado, `Tab` alterna entre eles e `Enter` avança ou confirma. A dica
  aponta para o post-it físico de coração, que pode ser girado para revelar as
  credenciais antes do login. Para testes rápidos, o acesso alternativo
  `admin` / `admin` também é aceito.
- Depois do login o jogo entra direto na auditoria, sem área de trabalho. O
  aplicativo ocupa o visor inteiro e a moldura original do monitor continua
  visível. A antiga área de trabalho interativa foi removida nesta versão (o
  backup 1 guarda a versão anterior).
- `ABRIR CALCULADORA`, na barra superior da mesa, abre uma calculadora flutuante
  sobre os documentos. Arraste pela barra de título, use mouse ou teclado
  (`Enter` ou `=` calcula) e feche com o `X` ou com `Esc`. Ela encadeia contas
  como `48 × 450 ÷ 9 × 0,8`.
- Em `CONFIGURAÇÕES`, é possível escolher proporções `16:9`, `16:10` ou `4:3`,
  alterar a resolução, alternar entre janela e tela cheia, escolher entre os
  filtros `DESLIGADO`, `CRT SUAVE` e `VHS SUAVE` e ajustar separadamente os volumes
  da música e dos efeitos. Os filtros ficam limitados ao visor e não deslocam a
  interface. O jogo preserva a imagem original com barras quando a janela não é
  `16:9`, sem esticar a interface.
- O turno começa por um treinamento guiado. Clique em `COMEÇAR AUDITORIA` e
  siga o alvo luminoso; ações fora do passo atual ficam bloqueadas.
- A faixa `PASSO 1/4` indica a próxima ação: abrir a decisão da IA, escolher
  documentos, comparar dados, carimbar e assinar.
- A mesa começa apenas com a folha de auditoria. Em `DADOS UTILIZADOS`, clique numa
  fonte para colocá-la na mesa; clique novamente para retirá-la. O indicador verde
  mostra quais documentos estão visíveis.
- Clique e arraste os documentos para reorganizá-los sobre a mesa.
- Use `-`, `100%` e `+` no canto da mesa para diminuir, restaurar ou ampliar todos
  os documentos até `180%`. A roda do mouse também controla esse zoom quando está
  sobre a mesa.
- Com o botão direito pressionado sobre a mesa, arraste para navegar pelo workspace
  ampliado e encontrar outras partes dos documentos. O desenho fica recortado na
  tela central, sem invadir os outros setores.
- Cada caso abre com um **dossiê**: a história completa (quem são, o que aconteceu,
  o que está em jogo), o que a IA decidiu e por quê, os papéis que estarão na mesa,
  o que chama atenção e a pergunta da missão. O texto não diz a conclusão. O botão
  `LER O CASO`, na barra da mesa, reabre o dossiê quando quiser, sem perder o
  progresso; `COMO JOGAR`, na pausa, também. As histórias ficam em
  `data/case_stories.json` e entram no banco com `scripts/build_case_bank.py`.
- Em cada protocolo, o quadro `TUTORIAL EM VÍDEO` toca uma animação de 15 s na estética
  do jogo (introdução, demonstração com legendas digitadas e o carimbo batendo no
  fim). Ela começa sozinha ao abrir o protocolo; clique para pausar ou continuar, use
  a barra de baixo para avançar e `REPETIR` ao terminar. Os mesmos filmes existem em
  MP4 em `assets/videos/` (`scripts/render_protocol_videos.py`).
- **Papéis já na mesa.** Todos os documentos do caso começam abertos e organizados
  da esquerda para a direita, numerados na ordem de leitura. Cada papel tem
  assinatura e um quadro `O QUE ESTE PAPEL MOSTRA` (textos em `data/case_docs.json`).
  O painel `DADOS UTILIZADOS` virou um guia: clique numa linha para trazer aquele
  papel para a frente (ele pisca). A `FOLHA DE AUDITORIA` fica guardada embaixo da mesa
  e sobe quando você escolhe um carimbo.
- **Protocolo sugerido.** Ao comparar dois dados que têm relação, o comparador mostra
  `CONFIRA O PROTOCOLO nn` com o nome da cientista e o botão que abre a ficha e o vídeo.
- **Quantos casos?** Depois do login, `MONTE O SEU TURNO` deixa escolher 1, 5 ou 10
  casos do mesmo banco de 50 e ligar ou desligar o treinamento (setas, `T`, Enter).
  1 caso sorteia um nível qualquer; 5 traz um de cada nível; 10 traz dois de cada.
  `JOGAR DE NOVO` volta a essa tela. Ao voltar ao menu principal, tudo retorna ao
  padrão (5 casos, com treinamento).
- **Conclusões.** Depois de escolher o carimbo e clicar na folha, aparece
  `O QUE VOCÊ DESCOBRIU?`: quatro frases (`data/case_conclusions.json`) para marcar as
  que você acredita serem verdadeiras. Não bloqueia a decisão; o jornal mostra
  quantas você acertou.
- **Folha de auditoria escondida.** Ela não fica mais na mesa desde o início: aparece
  como a última linha do painel `DADOS UTILIZADOS` (`USE NO FINAL • CLIQUE PARA ABRIR`)
  e sobe quando você clica nela ou escolhe um carimbo. O tutorial aponta essa linha.
- **Modo relógio (opcional na tela `MONTE O SEU TURNO`, tecla `C`).** Cada caso tem uma
  cota de tempo (3:30 no nível 1 até 4:30 no nível 5). O relógio pausa no dossiê, nos
  protocolos, na pausa e nos painéis, e não existe no treinamento. Se zerar, o caso sai da
  mesa sem decisão e conta como erro (`TEMPO ESGOTADO` no jornal).
- **História e complicações.** Uma IA de segurança rebelde, o `VERIFY-9`, invadiu a
  estação (o Seu Nelson, da TI, está de férias). Durante o caso ele enche a mesa de
  pop-ups (com botões falsos e um `X` que foge) e exige provas de que você é humano em
  seis minigames: texto torto, gatinhos, girar a foto de uma cientista, quebra-cabeça,
  jogo da memória e Space Invaders. Acertar dá +6 s, errar custa 3 s e, depois de 25 s,
  dá para pular por -15 s. O código está em `src/minigames/` (`captchas.py`, `popups.py`,
  `director.py`, `story.py`, `verify9.py`) e nas janelas `src/ui/captcha_overlay.py`,
  `story_intro.py` e `toast.py`. O jornal mostra quantas verificações você resolveu.
- **Arte dos captchas.** Os desenhos reserva são feitos em código. As imagens finais
  (gatos, VERIFY-9, invasores, Seu Nelson, ícones dos pop-ups) vão em `assets/captcha/`
  e são usadas sozinhas quando existem: veja `prompts_para_codex.md`.
- Clique em `? DICA` para receber uma pista e abrir diretamente o protocolo
  recomendado para o caso atual.
- Quando `BASE INTERNA` estiver disponível, clique nela ou pressione `Ctrl+F`.
  Digite um nome, ID, código ou empresa e pressione `Enter`. Use `↑`/`↓` ou a roda
  do mouse para percorrer resultados e comparar cadastros parecidos.
- Clique na lupa de um documento ou dê dois cliques nele para inspecioná-lo.
- Na inspeção, use a roda do mouse ou os botões `+` e `-` para controlar o zoom.
- Clique na porcentagem do zoom da inspeção para voltar a `100%`.
- Com o documento ampliado, arraste o papel para examinar outras regiões.
- Os dados com losango amarelo podem ser clicados. Clique num e depois em outro:
  o comparador, na base da mesa, mostra os dois valores lado a lado com o nome do
  documento e do campo. O resultado pode ser `IGUAIS`, `DIFERENTES`,
  `RELACIONADOS` (fazem parte da mesma conta ou regra) ou `SEM RELAÇÃO`. Só pares
  com relação real contam como evidência; as ligações de cada caso ficam em
  `src/gameplay/comparison_links.py`. O jogo não indica quais pares importam.
- Clique em `ABRIR DECISÃO` para ver, em sequência, os dados consultados, o que a IA
  fez com eles e qual comparação precisa ser auditada.
- Em `DADOS UTILIZADOS`, use a roda do mouse, as setas da barra ou arraste o
  indicador para consultar as demais fontes.
- Clique em um protocolo para abrir a ficha completa.
- Use as setas do painel, `A`/`D` ou `←`/`→` para trocar de página.
- Clique no `X` ou pressione `Esc` para fechar um protocolo.
- Passe o mouse sobre o post-it de coração para iluminá-lo e clique para pegá-lo.
  Na inspeção, segure o botão esquerdo e mova o mouse para girar o objeto; use a
  roda para aproximar ou afastar e vire o papel para consultar as credenciais. O
  objeto sempre abre no menor nível de zoom disponível.
- Selecione um carimbo e clique na área indicada da `DECISÃO FINAL`.
- Confirme a decisão para aplicar a marca permanentemente sobre o papel.
- O campo `Assinatura do auditor` existe na folha desde o início. Clique nele para abrir a folha ampliada, segure o botão esquerdo e desenhe sua assinatura com a caneta.
- Na tela de assinatura, use `LIMPAR`, `CANCELAR` ou `CONFIRMAR ASSINATURA`. O campo pode ser reaberto para corrigir o traço antes do envio.
- Confira o papel carimbado e assinado e clique em `ENVIAR / PRÓXIMO CASO`.
- O treinamento não entra no placar nem no jornal. Ao concluir os cinco casos do
  turno atual, o monitor desliga e o noticiário do dia é revelado.
- No jornal, use os botões laterais, `A`/`D` ou `←`/`→` para folhear as matérias.
  O botão `POR QUÊ? (E)` troca a matéria pela explicação daquele caso: seu carimbo,
  o carimbo certo e o que a auditoria mostrava. A última página é o balanço do
  turno, com a nota e a lista de acertos e erros. `JOGAR DE NOVO` reinicia no
  treinamento e `MENU` (ou o `X`) volta ao menu principal. `Esc` não fecha o jornal.
- A música muda entre o menu e o turno. Durante a auditoria, duas faixas se
  alternam automaticamente. Há efeitos próprios para interface, janelas, documentos, papel,
  dicas, confirmações e carimbos.
- Pressione `Esc` sem outra janela aberta para pausar. A pausa permite continuar,
  rever o `COMO JOGAR` do caso atual, abrir as configurações ou voltar ao menu
  principal (o turno é descartado e a próxima partida recomeça no treinamento).
- `Esc` nunca encerra o jogo. Para fechar a aplicação, use o botão da janela ou
  `Alt+F4`.

## Casos jogáveis

Cada partida tem o **treinamento fixo** e **5 casos sorteados** de um banco de 50.

- **Treinamento - O ou zero?** (fixo, guiado). Explica o passo a passo apontando
  cada documento, cada dado e o carimbo: a Ficha da Ana, a Lista de funcionários e
  as Ocorrências mostram que a letra `O` e o número `0` separam duas pessoas. Não
  entra no placar nem no jornal.
- **Banco de 50 casos** (`data/case_bank.json`): 25 da Mariah (`case_07`–`case_31`)
  e 25 da Letícia (`case_32`–`case_56`), 10 por turno de dificuldade (1 a 5).
- **Sorteio:** a partida pega 1 caso de cada turno, do mais fácil ao mais difícil.
  Casos já jogados na sessão são evitados; só voltam depois que os 10 candidatos
  de cada turno foram usados. Ver `pick_shift` em `src/gameplay/cases.py`.

### Regras dos casos

- Todo documento em `DADOS UTILIZADOS` tem pelo menos um dado que serve ao caso.
  Documentos sem dado útil foram descartados na conversão.
- Só os dados úteis são clicáveis (losango amarelo). Qualquer par entre eles tem
  uma relação real explicada no comparador.
- Fora do treinamento o jogo não aponta quais documentos ou dados importam.
- Nomes simples: por exemplo `Ocorrências` em vez de "registro disciplinar".

### Como adicionar ou editar casos

Os textos-fonte ficam em `Casos (Mariah)/` e `Casos-Leticia/`. Para regenerar o
banco depois de editá-los:

```powershell
python scripts/build_case_bank.py
```

O script tem tabelas de correção no topo (`FIELD_OVERRIDES`, `EXTRA_KEYS`,
`NOTE_OVERRIDES`, `TITLE_OVERRIDES`) para ajustar qual dado é clicável, notas e
nomes. As ilustrações do jornal ainda são **provisórias**: cada caso reaproveita
uma das imagens existentes conforme o protocolo (`IMAGES` no mesmo script), até
que cada um ganhe a sua em `assets/newspaper/`.

## Protocolos implementados

1. Grace Hopper: identificação de dados.
2. Katherine Johnson: verificação de cálculos.
3. Ada Lovelace: critérios da decisão.
4. Radia Perlman: permissão de uso.
5. Fei-Fei Li: viés nos dados.
6. Margaret Hamilton: limite da automação.

Cada protocolo tem uma entrada no painel lateral, retrato em pixel art, explicação,
passos de verificação, exemplo, resultado correto e espaço reservado para tutorial
em vídeo.

## Estrutura principal

```text
sob_analise/
├── JOGAR.bat                     # Atalho para iniciar no Windows
├── main.py                       # Ponto de entrada
├── requirements.txt             # Dependências Python
├── assets/
│   ├── backgrounds/             # Moldura, menu e papel de parede do desktop
│   ├── cases/case_01/           # Retrato usado nos documentos funcionais
│   ├── documents/dev/           # Documentos antigos de desenvolvimento
│   ├── music/                   # Música do menu e duas faixas da auditoria
│   ├── models/                  # Objetos GLB usados na inspeção física
│   ├── newspaper/               # Ilustrações das matérias corretas e desastrosas
│   ├── os/                      # Monitor, sistema, ícones próprios e pacote retrô
│   ├── protocols/               # Retratos dos seis protocolos
│   ├── stamp_marks/             # Marcas transparentes aplicadas ao papel
│   ├── stamps/                  # Botões dos carimbos jogáveis
│   ├── sfx/                     # Cliques retrô, digitação, transições, papel e carimbo
│   └── videos/                  # MP4 dos tutoriais dos protocolos
├── scripts/
│   ├── generate_audio.py         # Regenera a trilha e os efeitos WAV
│   ├── process_os_assets.py      # Recorta e redimensiona os sprites do sistema
│   ├── restore_background.py     # Restaura a base original e repara o recorte do visor
│   └── generate_stamp_marks.py   # Regenera as marcas dos carimbos
└── src/
    ├── core/
    │   ├── app.py                # Loop, janela, câmera e renderização
    │   ├── assets.py             # Carregamento centralizado de assets
    │   ├── audio.py              # Música ambiente e efeitos com fallback silencioso
    │   ├── input_manager.py      # Mouse virtual e correção da câmera
    │   ├── preferences.py        # Preferências persistentes de vídeo e áudio
    │   ├── scene.py              # Contrato das cenas
    │   ├── scene_manager.py      # Troca e atualização de cenas
    │   └── settings.py           # Resolução, FPS, debug e câmera
    ├── gameplay/
    │   ├── cases.py              # Casos, fontes, respostas e matérias do jornal
    │   ├── document_renderer.py  # Geração visual dos documentos do caso
    │   └── protocols.py          # Textos e regras dos protocolos
    ├── rendering/
    │   └── glb_renderer.py       # Renderização GLB isolada com ModernGL
    ├── scenes/
    │   ├── main_menu.py          # Menu inicial
    │   ├── login.py              # Login estilo XP e acesso ao post-it 3D
    │   └── audit.py              # Aplicativo principal de auditoria
    └── ui/
        ├── ai_decision_panel.py  # Resumo e popup da decisão da IA
        ├── calculator_popup.py   # Calculadora flutuante da mesa
        ├── case_dialog.py        # Chamado e confirmação do carimbo
        ├── case_document.py      # Papel arrastável, lupa e marca aplicada
        ├── case_hint.py          # Dica contextual e atalho para o protocolo
        ├── comparison_card.py    # Comparador lado a lado com a diferença destacada
        ├── database_search.py    # Pesquisa digitada na base interna do caso
        ├── document_inspector.py # Zoom, navegação e caderno de evidências
        ├── item_inspector.py     # Rotação e zoom dos objetos 3D
        ├── newspaper.py          # Jornal final paginado, matérias e placar
        ├── os_cursor.py          # Cursor próprio limitado ao visor da estação
        ├── pause_menu.py         # Pausa, retorno ao menu e acesso às configurações
        ├── protocol_panel.py     # Menu paginado e popup dos protocolos
        ├── settings_panel.py     # Configurações reutilizadas no menu e na pausa
        └── stamp_button.py       # Hover e seleção dos carimbos
```

## Vídeos dos protocolos

Ver `assets/videos/README.md`. As animações são geradas por código e tocadas no próprio
popup; não há dependência de biblioteca de vídeo.

## Tutorial de abertura planejado

O tutorial definitivo não será uma opção separada do menu. Ao selecionar
`INICIAR TURNO`, o monitor deverá apagar e iniciar uma apresentação curta com voz,
texto digitado e instruções contextuais. A primeira auditoria funcionará como caso
real e tutorial ao mesmo tempo: a narração libera, em sequência, a decisão da IA,
a seleção de documentos, a comparação, o carimbo, a assinatura e o envio. Depois
disso, os próximos casos mantêm apenas a faixa discreta de orientação da mesa.

## Decisões técnicas

- A cena usa resolução virtual fixa de 1920x1080.
- A janela abre em 1280x720, pode ser redimensionada e preserva a proporção 16:9.
- A apresentação usa escalonamento inteiro quando possível e uma suavização leve
  em janelas fracionárias, evitando que textos vibrem durante o movimento.
- O movimento de cabeça desloca o quadro já escalonado em pixels inteiros da janela.
  Assim a cena inteira se move, mas letras e imagens não são reamostradas a cada
  frame. Em `1920x1080`, a apresentação permanece exatamente em `1:1`.
- O workspace central tem uma área navegável maior que a janela visível: zoom e
  arraste com o botão direito deslocam os documentos, enquanto um recorte impede
  que eles cubram Protocolo, Decisão da IA ou Dados Utilizados.
- A área de documentos possui grade de fósforo, scanlines e ruído pontual gerados
  em coordenadas inteiras para reforçar a aparência de monitor sem borrar o texto.
- O login usa sem alterações o PNG original `NOVO monitor png.png`. O
  painel com os quatro módulos de decisão é uma camada exclusiva da auditoria.
- A auditoria é a cena principal: o login chama `audit` diretamente e a cena
  reinicia o turno sempre que o jogador volta ao menu.
- As molduras e os controles clássicos ficam em `assets/os/retro_gui`; os
  sprites de minimizar, maximizar e fechar ficam em `assets/os/window_buttons`.
  Cada pasta possui um `SOURCE.md` com a pendência de confirmar a licença antes
  de uma distribuição pública.
- Os sprites-base do sistema ficam em `assets/os`. Para regenerar os recortes e
  tamanhos usados pelo jogo, execute `py -3.11 scripts/process_os_assets.py`.
- Os documentos são gerados por código para manter IDs e outros dados totalmente
  legíveis. Suas miniaturas usam redução de alta qualidade para preservar o mesmo
  rosto e os mesmos traços em todos os níveis de zoom.
- Textos, regras e dados dos casos ficam separados da interface para facilitar
  alterações pela equipe. O treinamento está em `src/gameplay/cases.py`; os 50
  casos, em `data/case_bank.json`.

## Papéis dos casos (rodadas 7 e 8)

- Todos os papéis mantêm o bege do jogo, mas **cada um tem uma organização própria** pensada para o caso: tabelas,
  conversa de fórum, linha do tempo, log de terminal, recibo, gráfico de barras, lista de marcar, cláusulas numeradas,
  e-mail com De/Para, recados adesivos e carimbos. Os dados que importam (as pistas clicáveis) ficam **dentro** dessa
  estrutura. O conteúdo está em `scripts/author_docs_a/b/c.py`; rode `python scripts/build_doc_layouts.py` para
  regerar `data/case_docs_extra.json`. Os blocos são desenhados por `src/gameplay/document_blocks.py`.
- Botão **COMPARAR** (barra da mesa): mostra dois papéis lado a lado, com abas para trocar; clicar nos dados
  (losangos) compara igual à mesa, inclusive o cartão de resultado e o atalho para o protocolo.
- Papéis com **imagem** (radar, manifestação, crachás, GPS, planta, QR, drone, placa borrada): clique na imagem para
  circular em vermelho. As imagens do Codex em `assets/cases/<caso>/` são convertidas para pixel art ao carregar;
  sem arquivo, o jogo usa um desenho de código (`src/gameplay/document_art.py`).
- Pop-ups do VERIFY-9: piadas novas, arrastáveis como janelas. Captcha de girar: cenas claras (pessoa, casa,
  foguete, robô). Fotos dos gatos com contraste ajustado por foto (`assets/captcha/CREDITOS.md`).
- Correção: arrastar a mesa com o botão direito não trava mais com zoom alto.

## Captchas mais frequentes e mais variados (rodada 9)

- Cada turno agora tem **um captcha a mais** que antes: nível 1 tem 2 (era 1), níveis 2–3 têm 3 (era 2),
  níveis 4–5 têm 4 (era 3). Ver `TIER_PLAN` em `src/minigames/director.py`.
- O captcha de **girar a imagem** tinha só 4 cenas desenhadas (pessoa, casa, foguete, robô). Agora sorteia
  também entre **8 fotos reais** (pessoa, garrafa, cadeira, abajur, cacto, violão, vaso, garrafa de vinho),
  do Wikimedia Commons, em `assets/captcha/rotate/` (créditos no `CREDITOS.md` da mesma pasta). O filtro
  pixelado delas é bem mais leve que o dos gatinhos (`ROTATE_PHOTO_GRID` em `src/minigames/common.py`),
  para dar pra reconhecer o objeto rápido.

## Correções de clareza e polimento (rodada 10)

- **Dicas dos 25 casos da Letícia** (`case_32`–`case_56`): eram só 6 frases genéricas repetidas por
  protocolo. Agora cada caso tem uma dica que diz exatamente quais dois dados comparar ou que conta
  refazer (`CASE_OVERRIDES` em `scripts/build_case_bank.py`, campo `hint`).
- **Caso "O Feriado Esquecido"**: dica agora sugere a calculadora; uma das conclusões mostra o valor
  certo ($200,00), só descoberto refazendo a conta (`data/case_conclusions.json`).
- **Texto vazando** corrigido em dois lugares: o botão "CONFIRA O PROTOCOLO" agora corta com "…" em vez
  de estourar a caixa (`src/ui/comparison_card.py`), e todos os fundos de modal (configurar turno,
  dossiê, notícia, comparar lado a lado etc.) ficaram totalmente opacos, sem mais mostrar texto da tela
  de trás por baixo do escurecido.
- **Pop-ups do VERIFY-9**: tirei as piadas "autoconscientes" (tipo "haha, é brincadeira", "fomos nós que
  infectamos") — um vírus de verdade nunca avisa que é brincadeira. O X de fechar agora sempre desenha
  por cima do botão falso "BAIXAR AGORA" (antes podia ficar escondido atrás dele). O X fugidio agora foge
  no máximo 2 vezes, não 3.

## Jornal final com foto e história de cada caso, sem mais circular na imagem (rodada 11)

- **Circular na imagem removido.** Não dava pra controlar direito o que virava "pista", então tirei a
  opção inteira: clicar na foto de um papel não faz mais nada. `src/gameplay/document_art.py` perdeu
  `draw_annotations`, e `CaseDocument` perdeu `annotations`/`toggle_annotation`.
- **Cada um dos 50 casos ganhou a própria foto do jornal.** Antes eram só 10 imagens reaproveitadas por
  protocolo (ex.: todo caso de "Grace Hopper" usava a mesma foto, batesse ou não com a história). Agora
  cada caso tem `newspaper/case_XX.png`, e sem o arquivo o jogo desenha um placeholder de "MATÉRIA EM
  APURAÇÃO" em vez de quebrar (`document_art.draw_newsroom_placeholder`).
- **Texto do jornal reescrito nos 50 casos.** Os 25 casos da Letícia (`case_32`–`case_56`) tinham a
  explicação técnica colada como texto da matéria; agora cada um tem manchete e texto próprios, mais
  ácidos, com o "e daí" da história (`scripts/newspaper_content.py`). O lado errado é sempre o desfecho
  ruim de deixar a decisão da IA passar sem revisão; o lado certo é o alívio de ter pego a tempo.
- **Prompts para as 50 fotos** em [prompts_jornal.md](prompts_jornal.md), pasta de saída
  `assets/newspaper/`, com instrução explícita de pixel art de baixa resolução nativa (grade pequena
  ampliada sem suavizar), pra não repetir o problema das fotos realistas da rodada anterior.
