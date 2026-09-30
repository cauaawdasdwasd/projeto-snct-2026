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

- O menu inicial usa uma estação CRT animada e permite iniciar o turno, entrar na
  `ARENA VERIFY-9`, abrir as configurações ou consultar os créditos. Todas as opções
  funcionam por mouse ou teclado, e o aparelho acompanha o cursor com um movimento
  sutil. A interface é recortada pela curvatura do vidro e permanece dentro do visor.
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
    ├── minigames/
    │   ├── captchas.py           # As verificações "prove que é humano" em si
    │   ├── arcade.py             # Regras da Arena VERIFY-9: ondas, vidas, combo, ranks
    │   ├── director.py           # Escala quais captchas aparecem durante um caso
    │   ├── popups.py             # Enxame de pop-ups falsos do VERIFY-9
    │   ├── story.py              # Falas do VERIFY-9
    │   └── verify9.py            # Avatar do VERIFY-9
    ├── scenes/
    │   ├── main_menu.py          # Menu inicial
    │   ├── login.py              # Login estilo XP e acesso ao post-it 3D
    │   ├── audit.py              # Aplicativo principal de auditoria
    │   └── arcade.py             # Arena VERIFY-9: fase arcade separada dos casos
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

## Arena VERIFY-9: fase arcade separada dos casos (rodada 13)

- **O que é.** Um modo à parte, sem casos, sem documentos, sem jornal: só VERIFY-9
  jogando verificações "prove que é humano" na sua cara, uma atrás da outra, num ritmo
  de fliperama. Acessível pelo menu principal em `ARENA VERIFY-9`. Todo o código vive em
  `src/minigames/arcade.py` (regras, pontuação, placar) e `src/scenes/arcade.py` (tela).
- **Não é aleatório à toa.** A dificuldade sobe em **ondas fixas de 3 verificações**: a
  cada onda o cronômetro fica um pouco mais curto (de 26 s até um piso de 12 s) e, em
  marcos definidos (`WAVE_UNLOCKS` em `arcade.py`), um novo tipo de verificação entra no
  jogo — o repertório só cresce, nunca troca de uma hora para outra.
- **Vidas e combo.** Começa com 3 vidas (até 5 no total). Zerar o cronômetro de uma
  verificação custa 1 vida e zera o combo; errar dentro da verificação custa 2 s mas não
  quebra a sequência. Cada acerto empilha **combo** (multiplicador de pontos de x1 até
  x3) e soma pontos com bônus por velocidade — quanto mais sobra de tempo, mais vale.
- **OVERCLOCK.** Sequências limpas (sem erro) enchem um medidor; ao lotar, devolve
  1 vida automaticamente. É o principal jeito de sobreviver às ondas mais avançadas, e é
  puramente proporcional a jogar bem, não a sorte.
- **Grind entre partidas.** O placar (recorde, onda máxima, maior combo, total de
  verificações resolvidas) fica salvo em `data/arcade_stats.json` (git-ignorado, é save
  local) e desbloqueia **ranks** cumulativos, de `ESTAGIÁRIO(A) DE TI` até
  `LENDA ANTI-VERIFY-9`, mostrados na tela de início e na de fim de partida.
- **Verificações novas** criadas para a arena (funcionam soltas, chamáveis por
  `create_captcha` como qualquer outra): `traffic` (selecionar os quadrados com
  semáforo), `simon` (repetir uma sequência de cores que pisca), `whackabot` (clicar só
  nos robôs que aparecem, sem acertar os humanos) e `chimp` (Teste do Macaco, rodada 14).
  Somadas às 6 verificações que já existiam nos casos (texto torto, gatinhos, girar foto,
  quebra-cabeça, memória e Space Invaders), a arena tem 12 tipos ao todo.
- `Esc` durante a arena pausa (continuar, reiniciar ou voltar ao menu); no resumo final
  e na tela de entrada, volta direto ao menu principal.

## Ranking local, teste do macaco e ajustes de layout da arena (rodada 14)

- **Placar com nome, ao estilo fliperama antigo.** Fica salvo em
  `data/arcade_leaderboard.json` (git-ignorado, é save local da máquina) e aparece em
  dois lugares: um TOP 5 compacto direto na tela inicial da arena, e um botão
  `VER RANKING COMPLETO` que abre o TOP 10 inteiro (nome, onda e pontos). É pensado para
  várias pessoas jogarem no mesmo computador e tentarem se superar. Regras e persistência
  em `Leaderboard`/`LeaderboardEntry` (`src/minigames/arcade.py`). Nesta rodada o nome
  era pedido só no fim da partida (se a pontuação entrasse no TOP 10); a rodada 15 mudou
  isso para pedir o nome **antes** de jogar.
- **Verificação nova: Teste do Macaco** (`chimp`, kind `"chimp"`). Mostra alguns números
  espalhados num grid, esconde todos depois de ~1,7s e pede para clicar na ordem certa,
  de 1 até o último — cresce um número a cada rodada, 4 rodadas para vencer. O nome é uma
  piada de propósito: é o teste em que chimpanzés treinados costumam vencer humanos.
  Some entre as verificações liberadas a partir da onda 4.
- **Sequência de cores corrigida.** Um clique errado reiniciava a sequência
  instantaneamente, sem nenhum retorno visual — parecia travado. Agora entra numa pausa
  de ~1,1s mostrando a cor errada em vermelho e a certa em verde antes de recomeçar. O
  destaque de quem está piscando também ficou bem mais evidente (brilho branco, borda
  grossa) e o ritmo ficou um pouco mais lento para dar tempo de acompanhar.
- **Captchas da arena recentralizados.** O quadro de verificação ficava colado no topo
  do painel, com um vão vazio enorme embaixo. `CANVAS_ORIGIN`, em
  `src/scenes/arcade.py`, agora centraliza o conteúdo no espaço disponível do painel.

## Nome do jogador no início, corta-fio e terminal hackeado (rodada 15)

- **Fluxo do placar invertido: nome primeiro, depois joga.** A Arena agora abre com
  `QUEM ESTÁ JOGANDO?` antes de qualquer coisa — digita o nome, aperta `CONTINUAR`
  (ou `Enter`) e só então vê as regras e o botão `ENTRAR NA ARENA`. Todo turno é
  gravado no placar local automaticamente ao terminar (sem precisar entrar no TOP 10
  para isso pedir o nome, como era antes); o nome fica visível durante o turno
  (`JOGANDO: <nome>` no HUD) e pode ser trocado a qualquer momento pelo botão
  `JOGANDO: <nome> (trocar)` na tela inicial — pensado para várias pessoas jogarem
  na mesma estação sem passar pelo menu principal a cada troca.
- **Verificação nova: Cortar o Fio** (`wires`, kind `"wires"`), inspirada em *Keep
  Talking and Nobody Explodes*. Nasceu nesta rodada com fios verticais e uma regra
  simples ("corte o único fio AZUL"); a rodada 16 reformulou visual e regra por
  completo — ver lá.
- **Verificação nova: Terminal Hackeado** (`terminal`), ao estilo do hack de senhas do
  Fallout. Ficou ruim (senha embaralhada sem nenhuma pista jogável de verdade) e foi
  **removida** na rodada 16, substituída pelo Termo.

## Termo, fio com código, curva de tempo sem platô e final aos 100 (rodada 16)

- **Termo** substitui o Terminal Hackeado: um Wordle em português, grade 5x5, cores
  verde/amarelo/cinza por letra. Banco de 52 palavras de 5 letras ligado ao tema do jogo
  (`TERMO_WORDS` em `src/minigames/captchas.py`). Agora navegável com `←`/`→` para
  corrigir uma letra sem apagar tudo, e ganhou **tempo extra** por ser mais demorado que
  as outras verificações — ver `KIND_TIME_MULTIPLIER` em `src/minigames/arcade.py`
  (valor aumentado de novo na rodada 17).
- **Cortar o Fio reformulado**, agora mais parecido com *Keep Talking* de verdade: cada
  rodada sorteia um **código** de 6 caracteres (letras e números) e uma regra que lê uma
  propriedade dele — "último dígito ÍMPAR", "soma dos dígitos PAR", "tem VOGAL", "mais
  letras que números" — para decidir entre dois fios que garantidamente só aparecem uma
  vez cada no tabuleiro (sem ambiguidade possível). Os fios agora são **horizontais**,
  com terminais metálicos, brilho/sombra de cabo e faísca ao cortar.
- **Girar a Foto**: removidos os 4 desenhos feitos em código (pessoa, casa, foguete,
  robô); usa só as fotos reais de `assets/captcha/rotate/`.
- **Curva de tempo sem platô.** Antes, o tempo caía direto até um piso fixo (12s) por
  volta da onda 25 e ficava **parado** ali pro resto da partida — cerca de 75 ondas sem
  nenhuma escalada, o que ficava monótono num modo que devia ser frenético. Agora
  `time_limit_for_wave` usa decaimento exponencial: continua apertando, cada vez menos,
  até bem perto do fim (piso teórico de 9s, nunca alcançado de verdade) — sempre dá a
  sensação de que está ficando mais difícil, sem nunca virar injogável.
- **Final: derrote o VERIFY-9.** Sobreviver até a onda 100 (`FINAL_WAVE`) encerra a
  partida em vitória — tela própria ("VOCÊ DERROTOU O VERIFY-9!"), falas exclusivas do
  VERIFY-9 derrotado, e uma contagem de vitórias salva no placar local, visível na tela
  inicial da arena. Não é fácil (100 ondas = 300 verificações), então fica como o
  desafio final para quem realmente disputar o ranking a sério.

## Cofre numérico, desbloqueios mais cedo e mais tempo pras verificações lentas (rodada 17)

- **Verificação nova: Abrir o Cofre** (`cofre`, kind `"cofre"`), estilo o cofre de arma
  do Lockdown Protocol: senha numérica de 4 dígitos, 9 tentativas, cada uma mostra
  quantos dígitos estão certos e na posição certa (pino verde) e quantos existem na
  senha mas em outra posição (pino amarelo) — dedução Mastermind clássica. Dá pra digitar
  no teclado ou clicar num teclado numérico na tela. Liberava na onda 5 (a rodada 18
  reorganizou de novo, ver lá).
- **Desbloqueios reorganizados para trazer o que é mais dinâmico mais cedo**: Caça-Robôs
  e Cortar o Fio agora liberam na onda 4 (eram 6 e 7); Teste do Macaco e o Cofre novo vêm
  logo depois, na onda 5; Quebra-cabeça e Jogo da Memória empurrados pra 6 e 7. A ideia é
  não deixar a primeira metade da partida só com os testes mais simples.
- **Mais tempo pras verificações que exigem mais raciocínio.** Termo subiu de 1,8x para
  **2,5x** o tempo padrão da onda (ainda parecia curto para um Wordle completo); Cortar o
  Fio ganhou **1,6x** (ler código + regra + tabuleiro); o Cofre novo entra com **2,2x**
  (9 tentativas de dedução não cabem no tempo de uma verificação comum).

## Segure e Solte, Labirinto Oculto, e mais tempo de novo (rodada 18)

- **Verificação nova: Segure e Solte** (`botao`, kind `"botao"`), ao estilo do módulo
  "The Button" de *Keep Talking and Nobody Explodes*: clique e segure um botão grande;
  um número de 0 a 9 fica trocando enquanto você segura, e uma regra sorteada ("solte
  quando for PAR", "ÍMPAR", "MAIOR QUE 6", "MENOR QUE 3") diz o momento certo de soltar.
  Precisa segurar pelo menos 1 segundo antes — soltar cedo demais ou no número errado
  reinicia a rodada. 3 acertos para vencer.
- **Verificação nova: Labirinto Oculto** (`labirinto`, kind `"labirinto"`), inspirado no
  módulo "Maze" do mesmo jogo: um labirinto 6x5 gerado do zero a cada tentativa (sempre
  com exatamente um caminho possível), você move um ponto verde até a saída vermelha
  (sempre a célula mais distante do início, pra garantir que dê trabalho de verdade) com
  as setas do teclado.
- **Desbloqueios reorganizados outra vez**: Segure e Solte e Labirinto Oculto entram na
  onda 4 (o lugar mais cedo até agora); Caça-Robôs e Cortar o Fio, que estavam lá, passam
  pra onda 5; Teste do Macaco e Cofre pra onda 6; e assim por diante — tudo desbloqueado
  até a onda 11 agora (era 10). Com essas duas, a arena chega a 17 tipos de verificação.
- Labirinto Oculto também ganhou tempo extra (1,4x) por exigir navegação, não só reação.

## Arena virou campanha com chefe final, pontuação por velocidade, dois jogos novos e mais correções (rodada 19)

- **Mudança de direção: a Arena agora é uma campanha curta com fim, não um grind infinito.**
  Em vez de tentar sobreviver até a onda 100 (o que virava uma partida excessivamente longa
  e sem sensação real de dificuldade crescente), `FINAL_WAVE` caiu para **13**: 12 ondas de
  introdução/escalada (começo e meio) e a onda 13 é o **confronto final** contra o VERIFY-9,
  que exige `BOSS_CAPTCHAS` = **5 verificações seguidas** (em vez das 3 de uma onda normal),
  sorteadas só entre os testes mais "vivos" do jogo — Cortar o Fio, Cofre, Segure e Solte,
  Labirinto, Termo e os dois novos desta rodada (ver abaixo). Vencer essa onda encerra a
  partida em vitória de verdade, com tela e falas próprias do VERIFY-9 derrotado (isso já
  existia; só o alvo mudou de "onda 100" pra "onda 13, mas é osso").
- **Pontuação agora é principalmente sobre velocidade.** `score_for_solve` trocou um bônus
  pequeno de velocidade (1,0x–1,5x) por um multiplicador que vai de **0,5x a 2,0x** conforme
  o tempo sobrando na hora de resolver — quanto mais rápido, mais pontos, de forma bem mais
  sentida do que antes. O crescimento de pontos por onda ficou mais discreto de propósito
  (`WAVE_SCORE_STEP` de 18 para 14) pra velocidade ser realmente o fator principal, como
  pedido.
- **Curva de tempo recalibrada pra uma partida curta.** Como a campanha agora dura ~13
  ondas em vez de 100, o decaimento antigo (`0.965`, pensado pra esticar por um jogo bem
  mais longo) mal apertava nesse intervalo curto — dava a impressão de que "o tempo não
  diminui". Agora `TIME_LIMIT_DECAY` é `0.82` (base 24s, piso 8s): o aperto é sentido onda a
  onda dentro de uma única partida.
- **Segure e Solte não troca mais de número de forma desigual.** O número sorteado a cada
  0,4s podia repetir o valor anterior (1 em cada 10 sorteios), fazendo aquele número
  específico "grudar" na tela por 0,8s, 1,2s etc. enquanto os outros só ficavam 0,4s —
  parecia que uns números saíam mais rápido que outros porque, na prática, saíam mesmo.
  `_roll_digit` agora exclui o número atual do próximo sorteio: todo número fica exatamente
  um passo na tela, sem exceção.
- **Termo com ainda mais tempo.** O multiplicador subiu de 2,5x para **3,2x** o tempo padrão
  da onda — ainda é o teste mais generoso em tempo, de propósito, por ser o mais lento de
  ler e digitar.
- **Cofre com feedback por posição, igual o Termo de letras.** Antes mostrava só uma conta
  agregada ("2 certos, 1 quase") com pontinhos verdes/amarelos soltos. Agora cada uma das 4
  caixinhas da tentativa fica colorida individualmente — verde (dígito certo, posição
  certa), amarelo (dígito existe, lugar errado) ou cinza (não está na senha) — usando o
  mesmo algoritmo do Termo (`_score_sequence`, compartilhado pelas duas verificações em vez
  de duplicado). O cofre também ganhou mais tempo (2,2x → **2,6x**), por segurança.
- **Dois jogos novos inspirados em "Don't Panic! It's Just a Turbulence"**, escolhidos com o
  Cauã entre as opções de mecânica descritas (painel de instrumentos e rádio da torre):
  - **Painel de Instrumentos** (`instrumentos`): dois ponteiros de cockpit (ALTITUDE e
    INCLINAÇÃO) que ficam à deriva sozinhos; segure as setas (↑/↓ para um, ←/→ para o
    outro) pra trazer **os dois ao mesmo tempo** pra dentro da faixa verde seguro e
    manter por ~2,2s. É um jogo de "malabarismo" — cuidar de um deixa o outro derivar.
  - **Rádio da Torre** (`radio`): a torre soletra um codinome de 4 caracteres no alfabeto
    fonético ICAO de verdade (ALFA, BRAVO, KILO... e os números "aeronáuticos" ZERO, WUN,
    TOO, TREE, FOWER, FIFE, NINER etc.) e você digita de volta as letras/números
    correspondentes antes do tempo acabar. 2 rodadas certas pra vencer; errar reinicia a
    contagem.
  - Ambos entram cedo (onda 7), junto com o resto dos testes "dinâmicos", e valem mais
    tempo (1,6x e 1,7x) por exigirem leitura com atenção.
- **Quebra-cabeça, girar foto e os testes "diferentes" aparecem com mais frequência.** A
  escolha de qual verificação sortear deixou de ser uniforme: `KIND_WEIGHT` dá peso extra
  pros quebra-cabeças, pro girar-foto e pra todos os testes ao estilo Keep
  Talking/Turbulence (fio, cofre, botão, labirinto, termo, instrumentos, rádio), então eles
  aparecem bem mais do que os testes rápidos de reflexo/leitura ao longo de uma partida —
  sem deixar de existir, só menos repetidos.
- **Textos e elementos da tela da Arena aumentados** (HUD, regras, telas de nome/fim de
  partida, botões) em ~15–20%: ficou pedido que tudo estivesse "pequeno demais" pra ler de
  longe. Não mexi no tamanho de texto **dentro** de cada verificação (o canvas de 720x360 de
  cada uma tem posições calculadas a dedo; aumentar a fonte ali sem redesenhar cada layout
  arriscava cortar texto/sobrepor elementos em alguma das 19 verificações).
- **Sobre "mais imagens" no girar-foto/quebra-cabeça:** o jogo já escaneia sozinho tudo que
  existir em `assets/captcha/rotate/` (girar) e `assets/captcha/tiles/` (quebra-cabeça,
  gatos e memória) — não precisa mexer em código pra adicionar fotos reais novas, só soltar
  o arquivo `.jpg` na pasta (pro girar, adicionar o nome do objeto em
  `ROTATE_PHOTO_INSTRUCTIONS` é opcional; sem isso ele usa uma instrução genérica). Hoje são
  7 fotos no girar e 16 fotos no banco de quebra-cabeça/gatos/memória — não gerei fotos
  novas nesta rodada porque são fotos reais, não desenhos, e não tenho como fotografar nada.

## Campanha bem mais curta, captchas clássicos viram raridade, jogo novo e dois bugs visuais corrigidos (rodada 20)

- **Campanha reduzida pra caber em ~5 minutos pra quem já manja.** A rodada 19 já tinha
  cortado de 100 ondas pra 13, mas ainda estava longa demais na prática. Agora
  `CAPTCHAS_PER_WAVE` caiu de 3 para **2** e `FINAL_WAVE` de 13 para **6** (5 ondas de
  introdução/escalada + a onda 6 é o confronto final com `BOSS_CAPTCHAS` = **4**
  verificações seguidas) — a partida inteira, do início ao chefe final, agora tem **14**
  verificações no total em vez de 41.
- **Captchas "clássicos" (texto torto, ache os gatos, semáforo, girar a foto,
  quebra-cabeça) viraram os mais raros, não os mais comuns.** Isso é o oposto do que a
  rodada 19 tinha feito (tinha aumentado a frequência de girar/quebra-cabeça por engano).
  `KIND_WEIGHT` agora dá peso **0.4–0.5** pra esses (são os mais chatos, tipo captcha de
  verdade) e peso **1.2–1.9** pros jogos dinâmicos (Simon, Macaco, Caça-Robôs, Invasores,
  Memória, e principalmente os estilo Keep Talking/Turbulence: fio, cofre, botão,
  labirinto, termo, instrumentos, rádio e o novo Memória Visual).
- **Garantia de que um teste recém-liberado realmente aparece.** Antes, o aviso "novo
  teste liberado: X" podia nunca ser seguido de um X de verdade dentro da partida (sorteio
  ponderado entre 20 tipos é traiçoeiro numa partida curta) — foi exatamente o que
  aconteceu no playtest, o Painel de Instrumentos e o Rádio da Torre nunca apareceram.
  Agora `ArcadeRun` guarda qual teste acabou de ser liberado e força ele a ser a
  **próxima** verificação sorteada, sempre.
- **Verificação nova: Memória Visual** (`padrao`, kind `"padrao"`), inspirada no teste
  "Visual Memory" do Human Benchmark: uma grade acende alguns quadrados por ~1,6s, apaga,
  e você clica de volta nos que estavam acesos — 3 rodadas crescendo de 3x3 para 4x4 e
  5x5. Errar reinicia do 3x3.
- **Corrigido: o aviso "MEMORIZE A SEQUÊNCIA..." do Simon (Sequência de Cores) ficava
  literalmente em cima dos quadrados coloridos** — ele ocupava uma faixa fixa no topo que
  cruzava com as duas primeiras casas do tabuleiro. Meio pro painel de texto mudou de
  lugar (coluna à esquerda, sem sobrepor nada) e os quadrados deslocaram um pouco pra
  direita.
- **Destaque exagerado do Simon reduzido.** O quadrado aceso tinha um anel de brilho
  branco grosso (6px) mais uma borda preta de 10px por cima — ficava chamativo demais pra
  um jogo de memorizar cores. Agora é só uma borda escura simples de 5px, igual o resto do
  visual do jogo.
- **Cada cor do Simon tem seu próprio som**, que é como o brinquedo "Simon" de verdade
  funciona: 4 tons (notas Mi/Dó/Lá/Mi de oitavas diferentes) gerados na hora com
  `numpy`/`pygame.sndarray` — não precisa de nenhum arquivo de áudio novo.
- **Corrigido o texto que sobrepunha os painéis na tela inicial da Arena** ("SEU
  PROGRESSO" / "RANKING — TOP 5" ficavam cobertos pelo fim das regras). As regras foram
  reescritas bem mais curtas (cabem numa linha cada) e o espaçamento entre elas agora se
  ajusta ao texto de verdade, em vez de um valor fixo que quebrava se o texto crescesse.
- **Trilha própria da Arena, gerada na hora.** A Arena tocava a mesma música do modo
  auditoria (`audit_1`/`audit_2`) — nada errado com ela, só que não combinava com "humano
  vs. IA" e repetia o que já se ouve no resto do jogo. Perguntei ao Cauã como resolver e
  ele preferiu uma trilha procedural (sem depender de baixar nada, sem dúvida de
  licença): `_generate_arena_theme` em `src/core/audio.py` sintetiza um loop de um compasso
  (baixo de onda quadrada + arpejo frenético + chimbal de ruído, ~168 BPM) com
  `numpy`/`pygame.sndarray`, tocado num canal próprio (não é `pygame.mixer.music`, que só
  aceita arquivo) — começa ao entrar na Arena e para ao sair, sem se sobrepor à música de
  outras telas.

## Boss fight de verdade (3 tarefas, relógio único, pode resetar), fila garante cobertura, fio estilo Among Us (rodada 21)

- **O confronto final virou um "boss fight" de verdade, não só uma onda mais difícil.**
  Antes o chefe sorteava `BOSS_CAPTCHAS` verificações de um pool, uma de cada vez, cada
  uma com seu próprio cronômetro. Agora `draw_boss_tasks` monta uma sequência **fixa de 3
  tarefas**: 2 verificações distintas sorteadas (nunca repetem entre si) do pool
  "assinatura" (fio, cofre, botão, labirinto, termo, instrumentos, rádio, conectar os
  fios) e a **Memória Visual sempre por último**, como pedido. As 3 correm contra **um
  único relógio compartilhado de 120s** (`BOSS_TIME_LIMIT`) em vez de um cronômetro por
  tarefa — o `time_limit`/`time_left` do `ArcadeRun` só são reiniciados uma vez, na
  primeira tarefa, e seguem contando direto pelas 3.
- **Perder o confronto reseta a tentativa, não a partida.** Se o relógio de 120s zerar,
  custa uma vida (igual qualquer outro tempo esgotado) mas, se ainda sobrar vida,
  `_start_boss()` sorteia 3 tarefas novas e reinicia o relógio do zero — a onda continua
  sendo a 6, você não volta pra onda 1. Só acaba de vez se as vidas zerarem. Banner
  próprio ("CONFRONTO REINICIADO") avisa quando isso acontece.
- **Verificação nova: Conectar os Fios** (`conectar_fios`), a tarefa clássica de fiação do
  Among Us: 4 conectores coloridos à esquerda, os mesmos 4 embaralhados à direita, clique
  um de cada lado pra ligar a cor certa. Errar reinicia o quadro (embaralha de novo).
- **As 5 ondas normais agora garantem cobertura, não só frequência.** Na rodada 20, dar
  mais peso aos jogos dinâmicos ainda deixava a seleção aleatória de verdade — dava pra
  terminar uma partida sem NUNCA ver o Painel de Instrumentos ou o Rádio, como aconteceu
  num playtest. Agora `build_campaign_queue` embaralha as 15 verificações "dinâmicas"
  (tudo, exceto os 6 captchas clássicos, que saíram de vez da rotação normal) numa fila
  única por partida — as 5 ondas (3 verificações cada) consomem essa fila em ordem, então
  toda verificação aparece **exatamente uma vez**, em posição aleatória, garantido. Se uma
  tentativa falhar (tempo esgotado), a mesma verificação é sorteada de novo até ser
  resolvida — a fila só avança em acertos, então a garantia de cobertura nunca é furada
  por um erro.
- **`CAPTCHAS_PER_WAVE` voltou a 3** (era 2 na rodada 20) pra caber as 15 verificações
  dinâmicas exatamente em 5 ondas (3×5=15). O confronto final agora é seu próprio bloco de
  ritmo (~2 min), separado do resto da campanha.
- **Memória Visual com mais tempo** (multiplicador 1,9x → **2,4x**) — o motivo real do
  "pouco tempo" era estrutural: ela tem 3 rodadas (3x3, 4x4, 5x5) e cada uma pede uma
  pausa de leitura antes de poder clicar, então precisa de bem mais tempo que uma
  verificação de resposta única.
- **Corrigido: `MemoryCaptcha`/`SwapPuzzleCaptcha` sempre reportavam o mesmo `kind`
  independente da variante.** `MemoryCaptcha(pairs=6)` (Memória Avançada) tinha
  `.kind == "memory"` em vez de `"memory6"`, e o mesmo valia pro Quebra-cabeça 3x3
  reportando `"puzzle"`. Não dava pra perceber isso antes porque nada comparava o `kind`
  do objeto contra o que foi pedido; a fila de cobertura desta rodada comparou, e o bug
  apareceu direto nos testes. Corrigido guardando o `kind` certo por instância; como
  efeito colateral, o rótulo "QUEBRA-CABEÇA 3X3" no HUD agora aparece certo também (antes
  sempre mostrava só "QUEBRA-CABEÇA").
- **Sobre a música:** a trilha procedural da rodada 20 não agradou. Combinamos que eu
  mandaria um prompt pronto pra gerar no Suno uma trilha "8-bit meio terror arcade" de
  verdade — o prompt está na mensagem da entrega desta rodada (não em arquivo, já que
  depende do Cauã gerar e mandar o .mp3 de volta pra eu encaixar no jogo). Resolvido na
  rodada 22, com a faixa real gerada no Suno.

## Trilha real da Arena (Suno) e botão jogável de verdade (rodada 22)

- **Trilha procedural trocada pela faixa gerada no Suno** ("Glitching Guardian.mp3", a
  partir do prompt "8-bit chiptune horror" da rodada anterior). Como agora é um arquivo
  de verdade, `ArcadeScene` voltou a usar o mecanismo padrão de música do jogo
  (`play_music_sequence`, o mesmo que toca `audit_1`/`menu`/etc.) em vez do canal
  separado que a síntese por `numpy` exigia — `_generate_arena_theme` e todo o código
  do canal dedicado (`arena_theme_channel`, `start_arena_theme`, `stop_arena_theme`)
  foram removidos por não terem mais uso. Arquivo em `assets/music/arena_theme.mp3`.
- **Segure e Solte corrigido: estava genuinamente injogável.** O número trocava a cada
  `DIGIT_STEP_SECONDS = 0.4s` — tempo real demais curto pra ler o dígito, lembrar a regra
  (par, ímpar, maior que 6, menor que 3) e decidir soltar ou não. Subiu para **0,9s**, mais
  que o dobro, tempo suficiente pra realmente raciocinar em vez de só reagir por sorte.

## Termo com uma tentativa a mais, banco de palavras mais claro e só aceita palavra de verdade (rodada 23)

- **Uma tentativa a mais:** `MAX_GUESSES` de 5 para **6**, igual o Termo/Wordle de
  verdade.
- **Banco de palavras revisado: fora as "estranhas" com letras que o português quase não
  usa fora de empréstimos** — `QUARK` (tinha Q e K), `BYTES` (tinha Y), `GRAFO` e `NODOS`
  (termos técnicos pouco óbvios) saíram; entraram `FORTE`, `LIVRO`, `MUNDO`, `VERDE` e
  `CERTO` — palavras comuns, sem letra estranha, fáceis de reconhecer e menos
  confundíveis entre si. Banco final com 53 palavras, nenhuma com K, W ou Y.
- **Só aceita palavra de verdade, não deixa mais digitar qualquer sequência de letras.**
  Antes `TermoCaptcha` aceitava qualquer combinação de 5 letras como tentativa válida —
  agora `_submit` confere se a palavra está em `TERMO_WORDS` antes de aceitar. Uma
  tentativa que não é palavra é recusada de graça (como no Wordle de verdade): não gasta
  uma das tentativas, não custa tempo, e as letras digitadas continuam na tela pra
  corrigir só a que errou. Sem filtro de "tabu": o banco já é só palavras reais do
  português, sem restrição de palavrão nem nada do tipo.

## Termo volta a aceitar digitação livre; banco fica ainda mais fácil (rodada 24)

- **O filtro "só palavra do banco" da rodada 23 voltou atrás.** Na prática, o banco de
  53 palavras era pequeno demais pra servir como dicionário de tentativas válidas —
  palavras comuns de verdade como CARRO e CLIMA (testadas pelo Cauã) eram recusadas só
  por não estarem nas 53 escolhidas como possíveis respostas. `_submit` voltou a aceitar
  qualquer sequência de 5 letras como tentativa, exatamente como antes da rodada 23.
- **Banco de respostas ficou ainda mais fácil**, já que agora é só isso que ele controla
  (o que pode ser sorteado como resposta, não mais o que pode ser digitado): saíram
  `VETOR`, `CIFRA`, `MODEM`, `FOTON` e `GENES` (termos menos do dia a dia); entraram
  `CARRO`, `CLIMA`, `TEMPO`, `NOITE`, `PONTE`, `FESTA` e `GRUPO` — palavras bem comuns,
  do cotidiano. Banco final com 55 palavras, ainda nenhuma com K, W ou Y.

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

## Humor mais ácido no jornal, popups em card e assinatura única (rodada 12)

- **Jornal mais ácido.** Os 100 textos (manchete + corpo dos 50 casos) foram reescritos de novo, bem
  mais afiados. O caso da fábrica de tecido expõe trabalho infantil, o caso do porto termina com uma
  piada de contrabando, os casos de demissão por gravidez e crédito negado por preconceito ficaram
  explicitamente mais duros sobre machismo — só nos casos em que isso já fazia parte da história, sem
  forçar em todo caso. Um teste novo (`tests/test_newspaper_content.py`) garante que a manchete e o
  texto nunca repetem entre os dois lados do mesmo caso e nunca ficam cortados.
- **Popups pequenos** (dica, conclusões, configurar turno, entrada da história, verificação do
  VERIFY-9, assinatura) agora são cards com **bordas arredondadas** sobre um fundo **levemente
  transparente** (a mesa aparece de leve atrás), em vez de uma caixa preta sólida cobrindo a tela.
  Telas de tela cheia (dossiê, jornal, inspecionar documento, lado a lado, protocolo, decisão da IA)
  continuam opacas, porque ali o objetivo é ler sem distração.
- **Assinatura dos documentos:** era sempre o mesmo rabisco pra qualquer papel emitido por "RH" (16
  papéis diferentes, em 16 casos diferentes, com a assinatura idêntica) porque a semente do desenho
  usava só o nome do órgão. Agora a semente usa caso + documento + emissor, e o desenho tem três
  estilos (cursivo, ziguezague, letra de forma), então cada um dos 144 documentos assina diferente.
