from author_docs_common import *

DOCS = {
    "case_07": {
        "doc_1": [LT("Ordem de bloqueio", [["De", "Central de Alertas"], ["Para", "ShieldAI · Firewall"], ["Assunto", "Bloquear rede suspeita"], ["Alvo", "@Alvo Suspeito"]],
                     "Tráfego incomum detectado na filial às 02h10. Bloqueie apenas a rede apontada acima e avise o plantão."), SL("URGENTE")],
        "doc_2": [TM("Registro da execução", ["02:14:03  ordem recebida", "02:14:05  varrendo redes do cliente", "02:14:09  bloqueio aplicado em:", "@Rede Bloqueada", "02:14:10  aprovação humana: nenhuma"])],
    },
    "case_08": {
        "doc_1": [RC("Itens da nota fiscal", [["Algodão cru 30/1", "", "R$ 18,00 / rolo"], ["Fita de acabamento", "", "R$ 4,50 / rolo"], ["Frete", "", "incluso"]], [["ROLOS DE ALGODÃO", "", "@Volume Declarado"]])],
        "doc_2": [T("Carga do caminhão (conferida na doca 3)", ["Item", "Descrição", "Rolos"], [["A", "Algodão cru", "@Item A"], ["B", "Algodão cru", "@Item B"], ["C", "Fita de amarração", "2 caixas"]], [0.12, 0.5, 0.38]),
                  N("Conferido pelo Sr. Amaro às 21h. Caminhão saiu lacrado.", "L", -1.5)],
    },
    "case_09": {
        "doc_1": [P("Requisitos da vaga · Analista de Logística Jr.", ["Ter 18 anos ou mais", "@Escolaridade", "Disponibilidade para turnos", "Noções de planilhas"]), SL("EDITAL 44", "R", -5)],
        "doc_2": [T("Formação declarada", ["Curso", "Nível", "Ano"], [["@Formação", "Superior", "2022"], ["Excel avançado", "Curso livre", "2021"]], [0.5, 0.28, 0.22]),
                  TL("Experiência", [["2022–24", "Auxiliar de armazém"], ["2024–hoje", "Conferente de cargas"]])],
    },
    "case_10": {
        "doc_1": [CL("Você autoriza? (termo assinado na matrícula)", [["@Uso de Biometria", "x"], ["Receber promoções por e-mail", "-"], ["Apagar meus dados ao cancelar", "x"]]),
                  N("Termo 3.1 · assinado na recepção, com caneta emprestada.", "R", 2)],
        "doc_2": [T("Origem dos dados da campanha", ["Fonte", "Uso"], [["Cadastro", "Nome e e-mail"], ["Base da campanha", "@Base da Campanha"], ["Pesquisa de satisfação", "Nota do aluno"]], [0.36, 0.64]),
                  SL("SEMANA DO SUPLEMENTO", "R", -3)],
    },
    "case_11": {
        "doc_1": [T("Ficha do cliente · Perfil A", ["Item", "Dado"], [["Bairro", "Centro"], ["Renda mensal", "@Renda"], ["Limite do cartão", "@Limite"], ["Atrasos", "Nenhum"]], [0.45, 0.55])],
        "doc_2": [T("Ficha do cliente · Perfil B", ["Item", "Dado"], [["Bairro", "Periferia"], ["Renda mensal", "@Renda"], ["Limite do cartão", "@Limite"], ["Atrasos", "Nenhum"]], [0.45, 0.55])],
        "doc_3": [TM("Relatório do modelo RiscoBank v4", ["confiança do modelo: 91%", "regra aplicada:", "@Regra Aplicada", "clientes afetados: 1.240"])],
    },
    "case_12": {
        "doc_1": [T("Leitura dos sensores da válvula", ["Sensor", "Situação"], [["1", "Sinal OK"], ["2", "Sinal OK"], ["3", "Sinal OK"], ["4", "@Sensor 4"]], [0.18, 0.82]),
                  N("Técnico Dalton: cabo do sensor 4 é velho. Já pedi troca.", "R", 1.5)],
        "doc_2": [T("Painel de segurança", ["Sensor", "Status"], [["1", "Normal"], ["2", "Normal"], ["3", "Normal"], ["4", "@Status Sensor 4"]], [0.18, 0.82]), SL("TUDO VERDE", "R", -3)],
    },
    "case_13": {
        "doc_1": [T("Tabela de conversão da fábrica", ["Unidade", "Equivale a"], [["Quilo", "1.000 gramas"], ["Litro", "1.000 mililitros"], ["Galão", "@Proporção"], ["Tonelada", "1.000 quilos"]], [0.35, 0.65])],
        "doc_2": [T("Ficha da mistura · aditivo Q-204", ["Ingrediente", "Quantidade"], [["Base exigida", "@Base Exigida"], ["Adicionado", "@Adicionado"], ["Água", "40 litros"]], [0.4, 0.6]),
                  CL("Conferência do operador", [["Balança calibrada", "x"], ["Lote misturado", "x"], ["Conferência final", "-"]])],
    },
    "case_14": {
        "doc_1": [P("Regras para desligamento", ["Desligar exige motivo escrito", "@Foco", "Um humano precisa concordar", "Toda decisão precisa ser explicável"]), SL("RH · 2026", "R", -5)],
        "doc_2": [T("Avaliação de desempenho · Marta F.", ["Critério", "Nota"], [["Prazos", "4,5 / 5"], ["Qualidade", "4 / 5"], ["Desempenho geral", "@Desempenho"]], [0.45, 0.55]),
                  N("Gerente: Marta é a pessoa que mais ajuda o time. Nota 4 no ano.", "R", -1.5)],
        "doc_3": [TL("Buscas recentes do titular", [["Seg", "Receitas de sopa"], ["Qua", "@Buscas recentes"], ["Sex", "Convênio: consulta marcada"]]), SL("CONFIDENCIAL", "R", -4)],
    },
    "case_15": {
        "doc_1": [TM("Log do servidor Central-01", ["02:58  login: conta de manutenção", "horário do processo:", "@Hora", "processo iniciado:", "@Processo", "uso de CPU: 98%"])],
        "doc_2": [T("Contas de administrador", ["Conta", "Pode fazer"], [["Admin-Backup", "Cópias de segurança"], ["Admin-Manutenção", "@Admin-Manutenção"], ["Admin-Redes", "Alterar firewall"]], [0.34, 0.66]),
                  N("Revisar a lista todo trimestre. Ninguém revisa.", "R", 2)],
    },
    "case_16": {
        "doc_1": [T("Cadastro do cliente · perfil 1", ["Campo", "Dado"], [["Nome", "@Nome"], ["Endereço", "@Endereço"], ["Cliente desde", "12 anos"], ["Cartão", "Crédito final 4402"]], [0.34, 0.66])],
        "doc_2": [T("Cadastro do cliente · perfil 2", ["Campo", "Dado"], [["Nome", "@Nome"], ["Endereço", "@Endereço"], ["Cliente desde", "2 anos"], ["Cartão", "Débito final 8815"]], [0.34, 0.66])],
        "doc_3": [TM("Limpeza de cadastros · duplicados", ["comparando perfis 1 e 2...", "nome e endereço parecidos: 96%", "motivo da fusão:", "@Motivo", "resultado: perfis mesclados"])],
    },
    "case_17": {
        "doc_1": [T("Composição da nota final", ["Critério", "Situação / peso"], [["Vendas", "@Vendas"], ["Fluência nativa", "@Fluência Nativa"], ["Trabalho em equipe", "Peso 20%"]], [0.38, 0.62])],
        "doc_2": [T("Resultado da filial América Latina", ["Critério", "Resultado"], [["Vendas", "@Vendas"], ["Fluência nativa", "@Fluência Nativa"], ["Trabalho em equipe", "Boa"]], [0.38, 0.62]), SL("BÔNUS: NEGADO", "R", -4)],
        "doc_3": [P("Como a IA aprendeu a avaliar", ["Conversas de trabalho nota 10", "@Treinamento", "Idioma padrão dos exemplos: inglês"])],
    },
    "case_18": {
        "doc_1": [TL("Rota do drone", [["14:00", "Decolagem no galpão"], ["14:08", "@Caminho"], ["14:20", "Pouso no destino"]]), SL("ROTA PADRÃO", "R", -4)],
        "doc_2": [LT("Aviso oficial · Prefeitura", [["Evento", "@Evento"], ["Local", "Praça Central"], ["Restrição", "@Restrição"]], "Fica proibido qualquer sobrevoo na área durante o período. Descumprir gera multa."), SL("OFICIAL", "R", -5)],
        "doc_3": [T("Manutenção dos mapas", ["Item", "Situação"], [["Clima hoje", "Céu limpo"], ["Tráfego aéreo", "Livre no mapa"], ["Atualização de mapas", "@Atualização de mapas"]], [0.4, 0.6])],
    },
    "case_19": {
        "doc_1": [T("Leitura do scanner", ["Campo", "Valor"], [["Código QR", "@Código QR"]], [0.35, 0.65])],
        "doc_2": [T("Números de série liberados no lote", ["Série", "Situação"], [["XJ-992A-43", "liberado"], ["@Lote Aprovado", "liberado"], ["XJ-992A-45", "liberado"]], [0.5, 0.5])],
        "doc_3": [TM("Consulta ao banco global de peças", ["consultando série...", "resultado:", "@Status do Serial", "última atualização: hoje 04:00"])],
    },
    "case_20": {
        "doc_1": [LT("Contrato de vendas · CLT", [["Documento", "Contrato de trabalho"], ["Cláusula", "4 de 9"]]), P("Texto da cláusula", ["@Cláusula 4"], False), SL("ASSINADO", "R", -5)],
        "doc_2": [LT("Contrato de vendas · CLT", [["Documento", "Contrato de trabalho"], ["Cláusula", "5 de 9"]]), P("Texto da cláusula", ["@Cláusula 5"], False), SL("ASSINADO", "R", -5)],
        "doc_3": [BR("Vendas: fevereiro x março", [["Fevereiro", 0.5, "100"], ["Março", 1.0, "200"]]), T("Fechamento do mês", ["Situação"], [["@Vendas"]])],
    },
    "case_21": {
        "doc_1": [T("Resultados do exame", ["Exame", "Resultado", "Referência"], [["Colesterol", "@Colesterol", "até 200"], ["Pressão", "@Pressão", "até 12x8"], ["Glicose", "Normal", "até 99"]], [0.34, 0.33, 0.33])],
        "doc_2": [T("Como o risco foi calculado", ["Fonte", "Peso"], [["Exames do cliente", "10%"], ["@Fonte de Risco", "70%"], ["Idade", "20%"]], [0.62, 0.38]), SL("REAJUSTE 40%", "R", -4)],
        "doc_3": [T("Itens mais comprados no cartão fidelidade", ["Ranking", "Itens"], [["Mais frequentes", "@Itens Frequentes"], ["Frutas", "2 vezes"], ["Verduras", "3 vezes"]], [0.34, 0.66])],
    },
}
