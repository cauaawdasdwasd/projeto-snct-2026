from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "registro-de-prompts-sob-analise.pdf"
WINDOWS_IMAGE = ROOT / "site" / "imagens" / "galeria-windows.png"
PORTRAIT_IMAGE = ROOT / "site" / "imagens" / "ana-torres.png"
MONITOR_IMAGE = ROOT / "site" / "imagens" / "monitor-menu.png"

PAGE_W, PAGE_H = A4
MARGIN_X = 17 * mm
MARGIN_TOP = 18 * mm
MARGIN_BOTTOM = 17 * mm

INK = colors.HexColor("#111712")
PAPER = colors.HexColor("#F2EBCB")
CREAM = colors.HexColor("#FFF7D6")
GREEN = colors.HexColor("#506B39")
GREEN_DARK = colors.HexColor("#243626")
LIME = colors.HexColor("#A8C86A")
AMBER = colors.HexColor("#D39A2C")
RED = colors.HexColor("#A44335")
MUTED = colors.HexColor("#667064")
LINE = colors.HexColor("#B8B083")


pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))
pdfmetrics.registerFont(TTFont("Consolas-Bold", r"C:\Windows\Fonts\consolab.ttf"))


styles = getSampleStyleSheet()


def style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)


TITLE = style(
    "Title",
    fontName="Consolas-Bold",
    fontSize=30,
    leading=33,
    textColor=CREAM,
    spaceAfter=8,
)
SUBTITLE = style(
    "Subtitle",
    fontName="Arial",
    fontSize=12,
    leading=17,
    textColor=colors.HexColor("#D6DDC8"),
)
KICKER = style(
    "Kicker",
    fontName="Consolas-Bold",
    fontSize=8.5,
    leading=11,
    textColor=AMBER,
    uppercase=True,
)
H1 = style(
    "H1",
    fontName="Consolas-Bold",
    fontSize=20,
    leading=24,
    textColor=GREEN_DARK,
    spaceAfter=5,
)
H2 = style(
    "H2",
    fontName="Consolas-Bold",
    fontSize=10,
    leading=13,
    textColor=GREEN_DARK,
    spaceBefore=3,
    spaceAfter=4,
)
BODY = style(
    "Body",
    fontName="Arial",
    fontSize=9.2,
    leading=13.4,
    textColor=INK,
    spaceAfter=5,
)
BODY_SMALL = style(
    "BodySmall",
    fontName="Arial",
    fontSize=8.1,
    leading=11.2,
    textColor=INK,
)
QUOTE = style(
    "Quote",
    fontName="Arial",
    fontSize=8.3,
    leading=11.8,
    textColor=CREAM,
    leftIndent=4,
    rightIndent=4,
)
OUTPUT_STYLE = style(
    "Output",
    fontName="Arial",
    fontSize=8.7,
    leading=12.3,
    textColor=INK,
)
CODE = style(
    "Code",
    fontName="Consolas",
    fontSize=7.8,
    leading=10.4,
    textColor=GREEN_DARK,
)
CENTER = style(
    "Center",
    parent=BODY,
    alignment=TA_CENTER,
)
FOOTER = style(
    "Footer",
    fontName="Consolas",
    fontSize=7,
    leading=9,
    textColor=MUTED,
)


def p(text, paragraph_style=BODY):
    return Paragraph(text, paragraph_style)


def prompt_box(text):
    content = [[p("PROMPT DO AUTOR - TRANSCRIÇÃO EDITORIAL", KICKER)], [p(f'"{text}"', QUOTE)]]
    table = Table(content, colWidths=[PAGE_W - 2 * MARGIN_X - 12 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_DARK),
                ("BOX", (0, 0), (-1, -1), 1, GREEN),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, GREEN),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def output_box(title, items):
    rows = [[p(title.upper(), H2)]]
    for item in items:
        rows.append([p(f"<font color='#A44335'><b>+</b></font>&nbsp;&nbsp;{item}", OUTPUT_STYLE)])
    table = Table(rows, colWidths=[PAGE_W - 2 * MARGIN_X - 12 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E7E0BC")),
                ("BOX", (0, 0), (-1, -1), 0.8, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def code_box(lines):
    table = Table([[p("<br/>".join(lines), CODE)]], colWidths=[PAGE_W - 2 * MARGIN_X - 12 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#D8D3B3")),
                ("BOX", (0, 0), (-1, -1), 0.7, GREEN),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def stage_heading(number, date, title, lead):
    return [
        p(f"ETAPA {number:02d}  /  {date}", KICKER),
        p(title, H1),
        p(lead, BODY),
        Spacer(1, 3 * mm),
    ]


def project_image(path, width=160 * mm):
    image = Image(str(path))
    image._restrictSize(width, 92 * mm)
    return image


def page_chrome(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN_X, PAGE_H - 11 * mm, PAGE_W - MARGIN_X, PAGE_H - 11 * mm)
        canvas.setFont("Consolas-Bold", 7)
        canvas.setFillColor(GREEN_DARK)
        canvas.drawString(MARGIN_X, PAGE_H - 8.6 * mm, "SOB ANÁLISE  //  REGISTRO DE DESENVOLVIMENTO")
        canvas.setFont("Consolas", 7)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - MARGIN_X, 9 * mm, f"{doc.page:02d}")
    canvas.restoreState()


def build_story():
    story = []

    # Cover
    cover = Table(
        [[
            p("REGISTRO ACADÊMICO  //  AGOSTO-SETEMBRO DE 2026", KICKER),
        ], [p("Sob Análise", TITLE)], [p("Da ideia inicial ao protótipo jogável", SUBTITLE)]],
        colWidths=[PAGE_W - 2 * MARGIN_X],
    )
    cover.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_DARK),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (-1, 0), 16),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
            ]
        )
    )
    story += [Spacer(1, 15 * mm), cover, Spacer(1, 11 * mm)]
    story.append(project_image(MONITOR_IMAGE, 164 * mm))
    story += [Spacer(1, 8 * mm)]
    intro = Table(
        [[p("DIREÇÃO CRIATIVA", KICKER), p("IMPLEMENTAÇÃO ASSISTIDA", KICKER)],
         [p("Conceito, referências, mecânicas, aparência, ritmo e critérios de aprovação definidos pelo autor e sua equipe.", BODY_SMALL),
          p("Programação, integração de assets, testes e documentação realizados pelo Codex conforme as instruções recebidas.", BODY_SMALL)]],
        colWidths=[(PAGE_W - 2 * MARGIN_X) / 2] * 2,
    )
    intro.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E7E0BC")),
        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(intro)
    story.append(PageBreak())

    # Method
    story += stage_heading(0, "COMO LER", "Uma linha do tempo, não um catálogo", "Este documento acompanha a evolução do projeto na ordem em que as decisões foram tomadas. Ajustes pequenos foram retirados para que apareça com clareza o processo: o autor define a direção e o Codex transforma essa direção em software.")
    story.append(output_box("Critério editorial", [
        "Os blocos entre aspas reúnem instruções reais do autor, preservando intenção, sequência e nível de detalhe.",
        "Repetições, hesitações e linguagem imprópria para apresentação acadêmica foram removidas.",
        "Quando várias mensagens pertenciam à mesma etapa, elas foram unidas em uma transcrição editorial contínua. Nenhuma ideia nova foi atribuída ao autor.",
        "Detalhes narrativos internos foram omitidos; o foco é o método de criação do jogo.",
    ]))
    story += [Spacer(1, 5 * mm), p("LINHA DO TEMPO", H2)]
    timeline_rows = [
        ["01", "Ideação", "tema, referências e formato de apresentação"],
        ["02", "Conceito", "auditoria algorítmica e loop de decisão"],
        ["03", "Fundação", "Pygame, resolução virtual e arquitetura"],
        ["04", "Manipulação", "documentos, arraste e profundidade"],
        ["05", "Identidade", "terminal retrô, sprites e feedback físico"],
        ["06", "Jogabilidade", "sequência guiada, comparação e assinatura"],
        ["07", "Atmosfera", "movimento, áudio, menu e pausa"],
        ["08", "Sistema", "login, área de trabalho e aplicativos"],
        ["09", "3D", "pergunta técnica, modelo próprio e inspeção"],
        ["10", "Apresentação", "site, acessibilidade, galeria e Git"],
    ]
    timeline = Table(timeline_rows, colWidths=[12 * mm, 33 * mm, 116 * mm])
    timeline.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (1, -1), "Consolas-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.2),
        ("TEXTCOLOR", (0, 0), (0, -1), RED),
        ("TEXTCOLOR", (1, 0), (-1, -1), INK),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(timeline)
    story.append(PageBreak())

    # Stage 1
    story += stage_heading(1, "11 AGO 2026", "A ideia começou aberta", "O projeto ainda não tinha gênero definido. A primeira decisão do autor foi estabelecer tema, linguagem emocional, referências e limites técnicos antes de escolher uma mecânica.")
    story.append(prompt_box(
        "Eu preciso criar um jogo em Pygame que converse com sociedade e informação e dialogue com o tema de pesquisadoras e inventoras. Ainda não sei qual será o formato. Pensei em plataforma por gostar de Celeste, Hollow Knight e Outer Wilds, mas estou aberto a outras opções. Quero uma experiência com identidade e alguma narrativa, mesmo que precise funcionar em uma apresentação curta. Mostre alternativas além de plataforma e explique como poderíamos desenvolver juntos. Também preciso entender como criar ou gerar sprites 2D, como levá-los para o Python e como eu poderia retrabalhá-los manualmente depois. A proposta deve considerar o tempo de exposição do projeto e o fato de muitas pessoas diferentes jogarem por poucos minutos."
    ))
    story += [Spacer(1, 5 * mm), output_box("Saída desta direção", [
        "Comparação de formatos possíveis: plataforma, investigação e simulação de trabalho.",
        "Escolha posterior de uma experiência curta e repetível, adequada a uma mostra escolar.",
        "Definição inicial de Python e Pygame como base e pixel art como linguagem visual.",
        "O nome Sob Análise foi escolhido pelo autor por ser curto, direto e ter duplo sentido imediato.",
    ])]
    story.append(PageBreak())

    # Stage 2
    story += stage_heading(2, "11 AGO 2026", "O formato foi escolhido pelo contexto", "Ao perceber que o público teria poucos minutos, o autor abandonou a ideia de uma campanha longa e definiu um jogo de verificação inspirado em rotinas de inspeção.")
    story.append(prompt_box(
        "Como a apresentação acontecerá em um único dia e cada pessoa terá pouco tempo, uma história longa não funcionará. Quero seguir a linha de Papers, Please e Contraband Police: receber informações, verificar dados de maneira dinâmica, seguir regras e perceber consequências quando algo passa errado. O tema principal será inteligência artificial no mundo do trabalho. O jogador deve auditar decisões automatizadas enviadas por empresas, abrir documentos, conferir os dados usados e escolher entre aprovar, negar, pedir revisão humana ou registrar violação. Quero que privacidade, relações de poder e ciência de dados apareçam naturalmente, sem transformar a atividade em uma aula escrita. Também preciso decidir entre uma estrutura infinita ou uma rodada curta, com encerramento e feedback criativo sobre as decisões tomadas. A interação precisa ser concreta e compreensível em poucos minutos."
    ))
    story += [Spacer(1, 5 * mm), output_box("Saída desta direção", [
        "Loop central definido: receber, abrir, comparar, decidir e observar o resultado.",
        "Quatro decisões físicas transformadas em carimbos com funções diferentes.",
        "Pitch document preenchido para apresentação ao professor, com público, pilares e escopo.",
        "A responsabilidade do jogador passou a ser o núcleo da experiência, não um texto explicativo.",
    ])]
    story.append(PageBreak())

    # Stage 3
    story += stage_heading(3, "20 AGO 2026", "Primeiro, uma fundação que pudesse crescer", "Depois do conceito, o autor entregou uma especificação técnica extensa. Ela separava claramente o que deveria existir naquele momento e o que deveria ficar para depois.")
    story.append(prompt_box(
        "Crie do zero a estrutura inicial de Sob Análise inteiramente em Python, usando pygame-ce apenas para janela, entrada, áudio e renderização, sem engine externa. A experiência deve acontecer dentro de um terminal corporativo retrô em pixel art, e os elementos finais serão PNGs externos. Neste primeiro passo, faça somente a fundação arquitetural. Use uma resolução virtual fixa de 640 x 360, janela inicial de 1280 x 720, redimensionamento, escala pixel-perfect e letterboxing sem smoothscale. O InputManager deve converter o mouse físico para coordenadas virtuais e invalidar posições nas barras. Crie Scene, SceneManager, MainMenuScene, AuditScene e AssetManager com cache. A Application deve controlar inicialização, loop, delta time, renderização e encerramento. Centralize configurações, mantenha main.py pequeno, use pathlib, type hints e responsabilidades separadas. Quero código de projeto real, mas sem arquiteturas desnecessárias. Ao terminar, explique a árvore, os módulos, como executar e as decisões técnicas."
    ))
    story += [Spacer(1, 4 * mm), code_box([
        "main.py  ->  Application  ->  SceneManager",
        "janela física  ->  viewport  ->  surface virtual",
        "mouse físico  ->  InputManager  ->  mouse virtual",
        "assets/  ->  AssetManager com cache  ->  cenas",
    ]), Spacer(1, 4 * mm), output_box("Execução do Codex", [
        "Criação da estrutura modular em src/core, src/scenes e assets.",
        "Implementação de escala proporcional, barras e conversão de coordenadas.",
        "Menu e tela de auditoria criados como placeholders substituíveis.",
        "README, requirements e comandos de execução preparados para Windows.",
    ])]
    story.append(PageBreak())

    # Stage 4
    story += stage_heading(4, "20-24 AGO 2026", "A mesa passou a responder como objeto físico", "Com a base pronta, a próxima orientação não pediu uma tela pronta: pediu comportamento. A prioridade passou a ser manipular papéis como em uma bancada real.")
    story.append(prompt_box(
        "Continue o projeto existente exatamente a partir do estado atual; não recrie a fundação. Implemente o primeiro sistema real de interação: vários documentos visuais sobre a área de trabalho. O jogador deve clicar, trazer o documento automaticamente para frente, arrastá-lo, soltá-lo e reorganizar a pilha livremente. Crie uma classe Document que receba uma Surface já carregada pelo AssetManager e encapsule imagem, posição, rect, estado de arraste e offset. Ao clicar, procure do último elemento para o primeiro, porque o item visualmente superior deve receber a entrada; remova-o da posição atual e coloque-o no fim da lista. Guarde a diferença entre o mouse e o canto do documento para impedir que ele salte. Restrinja o movimento à área útil e trabalhe somente com coordenadas virtuais. Use PNGs temporários apenas para testar sobreposição, sem desenhar a interface final a cada frame. Preserve a arquitetura simples e explique z-order, drag offset e teste manual."
    ))
    story += [Spacer(1, 4 * mm), output_box("Execução do Codex", [
        "Classe Document criada separadamente da cena principal.",
        "Arraste com offset, sobreposição ordenada e limite de área implementados.",
        "Interação preservada ao redimensionar a janela e ao usar letterboxing.",
        "A abstração ficou preparada para receber imagens finais sem mudar a mecânica.",
    ])]
    story.append(PageBreak())

    # Stage 5
    story += stage_heading(5, "24-26 AGO 2026", "A interface ganhou uma identidade própria", "O autor substituiu os placeholders pela arte do terminal, definiu a ordem de camadas e tratou cada carimbo como um controle físico independente.")
    story.append(prompt_box(
        "Use a arte real do terminal como cenário e remova os painéis provisórios. A imagem completa inclui monitor, moldura, livros, painel inferior e elementos sobre a mesa, então a resolução lógica deve respeitar o asset inteiro. A versão com o interior transparente deve funcionar como foreground: primeiro desenhe o fundo e os elementos dinâmicos, depois os documentos e, por cima, a moldura PNG. Assim, qualquer parte que ultrapasse a tela ficará escondida pelos cantos reais do monitor. Crie regiões nomeadas para documentos, protocolos, decisão automatizada, dados e carimbos. Transforme cada carimbo em um componente com imagem, rect, hover, clique e seleção. O destaque deve seguir a silhueta alfa do PNG, em amarelo pixel-perfect, sem caixa retangular, glow ou blur. A máscara e o outline devem ser calculados uma vez. Mantenha hitbox estável, seleção exclusiva e um piscar digital discreto. Use scene space para a composição inteira e monitor screen space para a interface interna."
    ))
    story += [Spacer(1, 4 * mm), code_box([
        "cena completa: mesa + monitor + controles",
        "tela interna: interface do aplicativo",
        "physical -> virtual scene -> monitor local",
        "fundo -> conteúdo -> documentos -> moldura -> carimbos",
    ]), Spacer(1, 4 * mm), output_box("Execução do Codex", [
        "Arte externa integrada sem redesenhar o cenário com primitivas genéricas.",
        "Camadas reorganizadas para usar a transparência da moldura como recorte visual.",
        "StampButton recebeu hover, seleção e contorno derivado do alpha.",
        "Regiões lógicas e conversão scene_to_monitor ficaram explícitas no código.",
    ])]
    story.append(PageBreak())

    # Stage 6
    story += stage_heading(6, "FIM DE AGO 2026", "Beleza visual virou uma sequência jogável", "Depois de observar pessoas se perdendo na interface, o autor redefiniu a experiência pela ação: menos informação ornamental, passos visíveis e comparação direta.")
    story.append(prompt_box(
        "Quero deixar o jogo muito mais intuitivo e jogável. Reduza documentos que não ajudam e use palavras mais simples, sem empobrecer o conteúdo. O jogador precisa reconhecer uma sequência clara: abrir a decisão, colocar os documentos úteis na mesa, comparar informações, escolher uma resposta, assinar e enviar. Transforme a primeira rodada em treinamento: cada etapa deve indicar exatamente onde clicar, com a região necessária destacada e uma animação discreta. A comparação não pode exigir memorizar um valor, fechar uma tela e abrir outra. O jogador deve clicar em um campo de um documento e depois no campo correspondente do outro; uma linha deve ligar os dois e informar visualmente se combinam, usando verde ou vermelho. O campo de assinatura deve existir desde o início no papel. Ao clicar nele, abra uma visão ampliada para desenhar com o mouse, com traço que pareça tinta de caneta. O objetivo é que a investigação aconteça pelos gestos, e não apenas pela leitura de janelas."
    ))
    story += [Spacer(1, 4 * mm), output_box("Execução do Codex", [
        "Fluxo guiado por etapas com destaque do próximo ponto de interação.",
        "Sistema de seleção de campos e linha de comparação visual.",
        "Lista de documentos reorganizada para indicar o que já está sobre a mesa.",
        "Painel de assinatura desenhável integrado ao fechamento da decisão.",
    ])]
    story.append(PageBreak())

    # Stage 7
    story += stage_heading(7, "FIM DE AGO 2026", "Movimento e som deveriam sustentar a presença", "O autor avaliou a sensação do jogo em execução, não apenas capturas estáticas. Isso levou a ajustes de câmera, navegação, nitidez, trilha, cliques e pausa.")
    story.append(prompt_box(
        "A área central precisa continuar navegável mesmo com zoom alto. Segurando o botão direito, o jogador deve arrastar o espaço de trabalho como no diário de bordo de Outer Wilds, e o zoom deve chegar a 180%. Quero também um movimento sutil de cabeça: o ambiente inteiro se desloca levemente com o mouse, como se a pessoa estivesse diante do monitor. Não mova somente os pixels internos, não deixe textos cortados e reduza um pouco a nitidez fora dos protocolos para estabilizar a leitura. Adicione uma música de ambiente que misture tranquilidade de cafeteria com tensão de trabalho, além de efeitos curtos e mais graves para botões, documentos, páginas e confirmações. O som de digitação não pode continuar tocando depois que a pessoa para. No menu, use a estética de uma televisão antiga; dentro do jogo, Esc deve abrir uma pausa com continuar, configurações e sair, enquanto o encerramento direto fica apenas para Alt+F4."
    ))
    story += [Spacer(1, 4 * mm), output_box("Execução do Codex", [
        "Pan com botão direito e zoom interno com limites definidos.",
        "Efeito de cabeça aplicado à composição para preservar alinhamento entre camadas.",
        "AudioManager passou a separar música, clique, papel, digitação e confirmação.",
        "Menu, transições e pausa foram conectados ao fluxo principal.",
    ])]
    story.append(PageBreak())

    # Stage 8
    story += stage_heading(8, "INÍCIO DE SET 2026", "Sob Análise virou um aplicativo dentro do computador", "A maior mudança de estrutura veio de uma direção explícita: o terminal não seria somente uma moldura. Ele teria um sistema operacional interativo.")
    story.append(prompt_box(
        "Quero que Sob Análise seja um aplicativo do computador, e não a tela inteira. Antes dele, deve existir uma entrada inspirada no Windows XP, com usuário e senha digitáveis e uma dica física no post-it de coração. Depois do login, o jogador entra em uma área de trabalho clara e reconhecível. O botão do sistema deve funcionar; os ícones podem ser arrastados; o botão direito deve permitir criar pasta e documento de texto. Inclua Sob Análise, navegador, calculadora e meus documentos. A calculadora será necessária para verificações numéricas. Todas as aplicações devem abrir em janelas como no Windows: mover, minimizar, fechar e alterar tamanho. Não use os controles físicos do aplicativo de auditoria fora dele. Preserve exatamente o sprite pronto do monitor, incluindo os livros e post-its, e use os pacotes de ícones e GUI que forneci para evitar uma aparência improvisada. Gere somente os recursos que realmente estiverem faltando."
    ))
    story += [Spacer(1, 4 * mm), project_image(WINDOWS_IMAGE, 158 * mm), Spacer(1, 2 * mm), p("Registro atual da área de trabalho simulada, exibida dentro do monitor original.", CENTER), Spacer(1, 3 * mm), output_box("Execução do Codex", [
        "Login digitável com validação, dica e credenciais alternativas de teste.",
        "Desktop com ícones móveis, menu, criação de itens e relógio.",
        "DesktopWindow tornou as aplicações móveis, minimizáveis, redimensionáveis e fecháveis.",
        "Calculadora e arquivos passaram a coexistir com o aplicativo principal.",
    ])]
    story.append(PageBreak())

    # Stage 9
    story += stage_heading(9, "INÍCIO DE SET 2026", "Uma pergunta técnica abriu a inspeção 3D", "Nesta etapa, o autor não pediu uma ideia ao Codex. Ele apresentou uma solução híbrida, perguntou se era viável e depois forneceu o próprio modelo GLB.")
    story.append(prompt_box(
        "Conseguimos manter o Pygame responsável por menu, documentos, post-its, carimbos, interface, sons, cenas e entrada, e usar ModernGL somente em uma tela de inspeção? Minha ideia é capturar a tela atual, aplicar um fundo escuro ou um fade, renderizar o modelo 3D no centro e desenhar a interface Pygame por cima. O objeto pode vir em .obj ou .glb. Segurando o botão esquerdo e arrastando o mouse, o jogador deve girá-lo nos eixos; a rolagem controla o zoom. Quero que certas informações possam existir em lados diferentes, para transformar a análise em interação física. A referência visual é a inspeção de itens de Enigma do Medo: fundo mais escuro, objeto isolado e controle direto. Eu vou produzir o modelo 3D e entregar no formato que funcionar melhor. Quando ele for integrado, deve abrir no zoom mínimo atual, porque essa entrada é mais estética."
    ))
    story += [Spacer(1, 4 * mm), code_box([
        "Pygame: cenas + entrada + áudio + UI",
        "ModernGL: contexto + câmera + shader + modelo GLB",
        "botão esquerdo + movimento -> rotação",
        "roda do mouse -> zoom com limites",
    ]), Spacer(1, 4 * mm), output_box("Execução do Codex", [
        "Teste de viabilidade confirmado sem converter o jogo inteiro para OpenGL.",
        "Modelo fornecido pelo autor copiado para assets/models.",
        "GLBRenderer e ItemInspector criados com rotação, zoom e overlay escuro.",
        "Integração isolada para que uma falha 3D não comprometesse as cenas em Pygame.",
    ])]
    story.append(PageBreak())

    # Stage 10
    story += stage_heading(10, "SET 2026", "O projeto ganhou apresentação e continuidade", "A última frente reuniu comunicação acadêmica, acessibilidade, galeria visual e colaboração em equipe.")
    story.append(prompt_box(
        "Agora preciso de uma página para contar a história do jogo. Não é uma página de vendas: ela deve apresentar o universo, a protagonista Ana Torres e o motivo que a levou a criar uma empresa de auditoria. O visual precisa conversar com o jogo, mas o HTML e o CSS devem continuar compatíveis com o conteúdo básico e intermediário estudado em AW1, porque eu preciso explicar como tudo funciona. Organize os textos em seções, alinhe melhor os títulos e use animações simples de zoom e faixa contínua que possam ser demonstradas pelo código. No cabeçalho fixo, coloque controles discretos de fonte, com aumento amplo sem alterar a distribuição dos elementos. A imagem do jogo deve abrir em tela cheia e fazer parte de um carrossel com duas setas, usando capturas diferentes e sem revelar informações decisivas. Depois, publique a versão no repositório da equipe, mantenha README e scripts fáceis para atualizar e enviar mudanças."
    ))
    story += [Spacer(1, 4 * mm), output_box("Execução do Codex", [
        "Site estático criado em HTML, CSS e JavaScript, sem framework.",
        "Controles de fonte, animações explicáveis, carrossel e visualização em tela cheia.",
        "Capturas geradas diretamente do jogo para manter fidelidade visual.",
        "Repositório sincronizado, documentação atualizada e versão consolidada em commit.",
    ]), Spacer(1, 4 * mm), code_box([
        "site/index.html      estrutura e conteúdo",
        "site/estilos.css    layout, zoom e faixa animada",
        "site/fonte.js       níveis de acessibilidade",
        "site/carrossel.js   índice, setas e tela cheia",
    ])]
    story.append(PageBreak())

    # Closing
    story += stage_heading(11, "RESULTADO", "O que esta linha do tempo demonstra", "O desenvolvimento não ocorreu por uma solicitação genérica do tipo 'faça um jogo'. O projeto avançou por ciclos de direção, implementação, observação e correção.")
    closing_rows = [
        [p("AUTOR / EQUIPE", KICKER), p("CODEX", KICKER)],
        [p("Escolheu o tema, as referências e o formato de exposição.", BODY_SMALL), p("Transformou as decisões em arquitetura e código.", BODY_SMALL)],
        [p("Definiu o que o jogador faria com mouse e teclado.", BODY_SMALL), p("Implementou entrada, cenas, componentes e estados.", BODY_SMALL)],
        [p("Aprovou ou recusou visuais, sons, escalas e comportamentos.", BODY_SMALL), p("Ajustou assets, coordenadas, renderização e áudio.", BODY_SMALL)],
        [p("Propôs o sistema operacional e a inspeção 3D.", BODY_SMALL), p("Integrau o desktop simulado e o pipeline ModernGL.", BODY_SMALL)],
        [p("Determinou como o projeto deveria ser apresentado.", BODY_SMALL), p("Construiu o site, testes e documentação técnica.", BODY_SMALL)],
    ]
    closing = Table(closing_rows, colWidths=[(PAGE_W - 2 * MARGIN_X) / 2] * 2)
    closing.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(closing)
    story += [Spacer(1, 7 * mm)]
    story.append(output_box("Evidências do projeto", [
        "Código organizado em cenas, núcleo, interface, renderização e dados.",
        "Integração de assets próprios e pacotes externos documentados.",
        "Suíte automatizada com 13 testes aprovados na versão registrada.",
        "Commit 7d7b25d: feat: adiciona desktop interativo e site do projeto.",
        "Repositório: github.com/cauaawdasdwasd/projeto-snct-2026",
    ]))
    story += [Spacer(1, 8 * mm), p("CONCLUSÃO", KICKER)]
    story.append(p(
        "O autor atuou como diretor do desenvolvimento: apresentou a visão, detalhou o comportamento esperado, indicou referências, avaliou resultados e pediu revisões específicas. O Codex atuou como ferramenta de execução técnica. A autoria das decisões criativas não foi transferida à IA; a programação foi produzida de forma assistida e continuamente orientada.",
        style("Conclusion", parent=BODY, fontName="Arial-Bold", fontSize=11, leading=16, textColor=GREEN_DARK),
    ))
    story += [Spacer(1, 7 * mm)]
    portrait = Image(str(PORTRAIT_IMAGE))
    portrait._restrictSize(42 * mm, 42 * mm)
    bio = Table([[portrait, p("<b>ANA TORRES</b><br/>Protagonista apresentada no site do projeto. Sua presença visual conecta a narrativa pública ao ambiente de trabalho construído no jogo.", BODY)]], colWidths=[48 * mm, 112 * mm])
    bio.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E7E0BC")),
        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(bio)
    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frame = Frame(
        MARGIN_X,
        MARGIN_BOTTOM,
        PAGE_W - 2 * MARGIN_X,
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    template = PageTemplate(id="main", frames=[frame], onPage=page_chrome)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="Sob Análise - Linha do tempo de desenvolvimento",
        author="Equipe Sob Análise",
        subject="Registro acadêmico de direção criativa e implementação assistida",
    )
    doc.addPageTemplates([template])
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
