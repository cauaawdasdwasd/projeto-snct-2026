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
- Em `CONFIGURAÇÕES`, é possível escolher proporções `16:9`, `16:10` ou `4:3`,
  alterar a resolução, alternar entre janela e tela cheia e ajustar separadamente
  os volumes da música e dos efeitos. O jogo preserva a imagem original com barras
  quando a janela não é `16:9`, sem esticar a interface.
- Leia o chamado e clique em `ABRIR CASO`.
- A faixa `PASSO 1/5` indica a próxima ação: abrir a decisão da IA, escolher
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
- Clique em `? DICA` para receber uma pista e abrir diretamente o protocolo
  recomendado para o caso atual.
- Quando `BASE INTERNA` estiver disponível, clique nela ou pressione `Ctrl+F`.
  Digite um nome, ID, código ou empresa e pressione `Enter`. Use `↑`/`↓` ou a roda
  do mouse para percorrer resultados e comparar cadastros parecidos.
- Clique na lupa de um documento ou dê dois cliques nele para inspecioná-lo.
- Na inspeção, use a roda do mouse ou os botões `+` e `-` para controlar o zoom.
- Clique na porcentagem do zoom da inspeção para voltar a `100%`.
- Com o documento ampliado, arraste o papel para examinar outras regiões.
- Clique em campos relevantes, como os IDs, para anotá-los no caderno de evidências.
- Clique em `ABRIR DECISÃO` para ver, em sequência, os dados consultados, o que a IA
  fez com eles e qual comparação precisa ser auditada.
- Em `DADOS UTILIZADOS`, use a roda do mouse, as setas da barra ou arraste o
  indicador para consultar as demais fontes.
- Clique em um protocolo para abrir a ficha completa.
- Use as setas do painel, `A`/`D` ou `←`/`→` para trocar de página.
- Clique no `X` ou pressione `Esc` para fechar um protocolo.
- Passe o mouse sobre o post-it de coração para iluminá-lo. Clique nele para virar
  o papel e consultar as credenciais da estação.
- Selecione um carimbo e clique na área indicada da `DECISÃO FINAL`.
- Confirme a decisão para aplicar a marca permanentemente sobre o papel.
- O campo `Assinatura do auditor` existe na folha desde o início. Clique nele para abrir a folha ampliada, segure o botão esquerdo e desenhe sua assinatura com a caneta.
- Na tela de assinatura, use `LIMPAR`, `CANCELAR` ou `CONFIRMAR ASSINATURA`. O campo pode ser reaberto para corrigir o traço antes do envio.
- Confira o papel carimbado e assinado e clique em `ENVIAR / PRÓXIMO CASO`.
- Ao concluir o sexto caso, o monitor desliga e o noticiário do dia é revelado.
- No jornal, use os botões laterais, `A`/`D` ou `←`/`→` para folhear as matérias.
- A música muda entre o menu e o turno. Durante a auditoria, duas faixas se
  alternam automaticamente. Há efeitos próprios para interface, documentos,
  papel, dicas, confirmações e carimbos.
- Pressione `Esc` sem outra janela aberta para pausar. A pausa permite continuar,
  abrir as configurações ou voltar ao menu principal.
- `Esc` nunca encerra o jogo. Para fechar a aplicação, use o botão da janela ou
  `Alt+F4`.

## Casos jogáveis

O turno atual tem seis casos, um para cada protocolo. Todos exigem cruzar vários
documentos e encontrar a informação decisiva entre dados que parecem coerentes:

1. **Correspondência suficiente:** a IA separa corretamente dois códigos quase
   idênticos; o jogador precisa confirmar que o registro disciplinar é de Artur,
   não de Ana, antes de aceitar a promoção. A base interna permite pesquisar os
   homônimos, o pedido e o registro de segurança.
2. **Lote 28800:** a capacidade declarada pela HEIN só fecha quando doze crachás de
   visitante entram na conta. Log de máquinas, datas de nascimento e um termo de
   visita revelam estudantes operando a linha de uniformes escolares.
3. **Triagem 204:** uma candidata de dados é eliminada por um requisito que veio
   do modelo de vaga errado.
4. **Risco de afastamento:** um prontuário médico restrito é usado numa decisão
   de promoção, embora a autorização cubra apenas saúde e segurança.
5. **Nota 64:** o sistema aprende com dez anos de promoções desiguais
   e reduz a nota de uma funcionária com desempenho superior.
6. **Carga MEDU-771204:** lacre, peso e scanner entram em conflito numa
   carga de casacos; há suspeita séria, mas não prova suficiente para decisão
   automática. A base interna inclui códigos de carga quase idênticos e registros
   de scanner, aduana e transportadora.

Os casos privilegiam IDs, datas, quantidades, contratos, permissões e contas
verificáveis. As escolhas não são corrigidas imediatamente. Ao fim do turno, o
monitor desliga e cada decisão vira uma página do noticiário, com ilustração em
pixel art e uma consequência plausível: indenizações, demissões, contratos
perdidos, multas ou uma apreensão policial. O humor vem do contraste entre um
detalhe aparentemente pequeno e o tamanho real do estrago.

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
│   ├── backgrounds/             # Moldura e cenário da auditoria (novo_sprite_teste.png)
│   ├── cases/case_01/           # Retrato usado nos documentos funcionais
│   ├── documents/dev/           # Documentos antigos de desenvolvimento
│   ├── music/                   # Música do menu e duas faixas da auditoria
│   ├── newspaper/               # Ilustrações das matérias corretas e desastrosas
│   ├── protocols/               # Retratos dos seis protocolos
│   ├── stamp_marks/             # Marcas transparentes aplicadas ao papel
│   ├── stamps/                  # Botões dos carimbos jogáveis
│   ├── sfx/                     # Cliques retrô, digitação, transições, papel e carimbo
│   └── videos/                  # Futuros tutoriais em vídeo
├── scripts/
│   ├── generate_audio.py         # Regenera a trilha e os efeitos WAV
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
    ├── scenes/
    │   ├── main_menu.py          # Menu inicial
    │   └── audit.py              # Tela principal de auditoria
    └── ui/
        ├── ai_decision_panel.py  # Resumo e popup da decisão da IA
        ├── case_dialog.py        # Chamado e confirmação do carimbo
        ├── case_document.py      # Papel arrastável, lupa e marca aplicada
        ├── case_hint.py          # Dica contextual e atalho para o protocolo
        ├── database_search.py    # Pesquisa digitada na base interna do caso
        ├── document_inspector.py # Zoom, navegação e caderno de evidências
        ├── newspaper.py          # Jornal final paginado, matérias e placar
        ├── pause_menu.py         # Pausa, retorno ao menu e acesso às configurações
        ├── protocol_panel.py     # Menu paginado e popup dos protocolos
        ├── settings_panel.py     # Configurações reutilizadas no menu e na pausa
        └── stamp_button.py       # Hover e seleção dos carimbos
```

## Vídeos dos protocolos

A interface já reserva um quadro 16:9 para os tutoriais. Os arquivos finais devem
seguir os nomes documentados em `assets/videos/README.md`. A reprodução dentro do
PyGame será ligada quando os vídeos estiverem disponíveis.

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
- A moldura principal foi refeita em pixel art nítida, preservando a geometria da
  interface e removendo os elementos decorativos que cobriam a área útil.
- Os documentos são gerados por código para manter IDs e outros dados totalmente
  legíveis. Suas miniaturas usam redução de alta qualidade para preservar o mesmo
  rosto e os mesmos traços em todos os níveis de zoom.
- Textos, regras e dados dos casos ficam separados da interface para facilitar
  alterações pela equipe.
