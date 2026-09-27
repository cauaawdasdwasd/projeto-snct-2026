from author_docs_common import *

DOCS = {
    "case_37": {
        "doc_1": [TM("Relatório de voo do SkyOps", ["missão: entrega no bairro Alto", "causa da queda:", "@Causa", "conclusão: falha humana"]), SL("RELATÓRIO IA", "R", -4)],
        "doc_2": [TL("Ações do operador · terminal 4", [["13:55", "Missão iniciada"], ["14:00", "Último comando enviado"], ["14:02", "@Ações"]]), N("Registro do teclado e do controle do operador.", "R", 1.5)],
        "doc_3": [T("Sensor do drone", ["Campo", "Dado"], [["Status 14:01", "@Status 14:01"], ["Observação", "@Observação"]], [0.3, 0.7])],
    },
    "case_38": {
        "doc_1": [T("Requerimento de saque", ["Campo", "Dado"], [["Nome", "@Nome"], ["CPF", "@CPF"], ["Valor", "$8.400"]], [0.3, 0.7]), CL("Documentos anexados", [["Documento com foto", "x"], ["Comprovante de endereço", "x"]])],
        "doc_2": [T("Cadastro do banco", ["Campo", "Dado"], [["Nome", "@Nome"], ["CPF", "@CPF"], ["Conta aberta", "Há 15 anos"]], [0.3, 0.7]), N("Conta antiga: nunca teve atualização de nome.", "R", 2)],
        "doc_3": [LT("Certidão de casamento", [["Cartório", "2º Ofício de Registro Civil"], ["Alteração", "@Alteração"]], "Certifico que o registro acima foi alterado a pedido da titular."), SL("REGISTRADO", "R", -5)],
    },
    "case_39": {
        "doc_1": [RC("Itens da nota fiscal", [["@Carga", "400 un.", "lote 12"]], [["PESO TOTAL", "", "@Peso Total"]]), N("Fornecedor americano: peso informado na unidade deles.", "R", 2)],
        "doc_2": [T("Regras do porto", ["Item", "Regra"], [["Limite por contêiner", "@Limite por contêiner"], ["Unidade de peso", "Quilogramas"], ["Multa por excesso", "$500 por tonelada"]], [0.45, 0.55])],
        "doc_3": [TM("Cálculo PortoTox", ["peso de entrada:", "@Peso de Entrada", "limite do porto: 2000", "conta feita:", "@Decisão"])],
    },
    "case_40": {
        "doc_1": [BR("Desempenho do desenvolvedor", [["Entregas no prazo", 1.0, "100%"], ["Testes automáticos", 0.92, "92%"]]), T("Resumo do gestor", ["Campo", "Dado"], [["Entregas", "@Entregas"], ["Qualidade do código", "@Qualidade do Código"]], [0.45, 0.55])],
        "doc_2": [T("Relatório TeamFit", ["Campo", "Dado"], [["Signo do candidato", "@Signo do Candidato"], ["Signo do gestor", "@Signo do Gestor"], ["Compatibilidade", "@Compatibilidade"]], [0.5, 0.5]), SL("RECUSADO", "R", -4)],
        "doc_3": [P("Regras de promoção", ["@Critérios de Promoção", "Comitê de pessoas decide", "Recurso em 10 dias"]), SL("DIRETORIA", "R", -4)],
    },
    "case_41": {
        "doc_1": [LT("Notificação de reajuste", [["De", "SaudeMais Seguros"], ["Assunto", "Reajuste da mensalidade"], ["Motivo", "@Motivo"]], "Sua mensalidade será reajustada no próximo ciclo. Em caso de dúvidas, procure a central."), SL("REAJUSTE", "R", -4)],
        "doc_2": [BR("Passos por dia", [["Há 6 meses", 1.0, "10 mil"], ["Hoje", 0.2, "2 mil"]]), T("Resumo do aplicativo", ["Campo", "Dado"], [["Passos diários", "@Passos diários"]], [0.4, 0.6])],
        "doc_3": [P("Política de privacidade do RunFree", ["Coletamos passos e batimentos", "@Privacidade", "Você pode apagar seu histórico"]), SL("v2.4", "R", -4)],
    },
    "case_42": {
        "doc_1": [T("Perfil do cliente", ["Campo", "Dado"], [["Renda mensal", "@Renda Mensal"], ["Atrasos", "@Histórico de Atrasos"], ["Tempo de conta", "8 anos"]], [0.4, 0.6]), N("Cliente paga a fatura sempre em dia.", "R", 2)],
        "doc_2": [T("Relatório GeoCred", ["Campo", "Dado"], [["CEP", "@CEP"], ["Risco regional", "@Risco Regional"], ["Ação", "Reduzir limite"]], [0.34, 0.66]), SL("LIMITE ↓", "R", -4)],
        "doc_3": [BR("Composição do bairro", [["Jardim Alvorada", 0.8, "80%"]]), T("Dado do instituto", ["Bairro", "Dado"], [["Jardim Alvorada", "@Jardim Alvorada"]], [0.34, 0.66])],
    },
    "case_43": {
        "doc_1": [BR("Estoque do almoxarifado", [["Aço", 0.1, "5 t"], ["Cobre", 0.7, "35 t"], ["Alumínio", 0.5, "25 t"]]), T("Alerta de estoque", ["Item", "Situação"], [["Aço", "@Aço"]], [0.3, 0.7])],
        "doc_2": [LT("Aviso da Engenharia", [["Local", "Galpão 3"], ["Situação", "@Galpão 3"]], "Ninguém pode entrar até a conclusão do reparo."), SL("INTERDITADO", "R", -5)],
        "doc_3": [T("Pedido de compra automático", ["Campo", "Dado"], [["Fornecedor", "Aciaria Continental"], ["Quantidade", "@Quantidade"], ["Destino", "@Destino"], ["Prazo", "48 horas"]], [0.34, 0.66])],
    },
    "case_44": {
        "doc_1": [T("Alerta SecurFace", ["Campo", "Dado"], [["ID suspeito", "@ID Suspeito"], ["Fotos associadas", "@Fotos Associadas"]], [0.32, 0.68])],
        "doc_2": [T("Registro funcional", ["Campo", "Dado"], [["Foto", "@Foto"], ["Histórico", "@Histórico"], ["Empresa", "Fábrica Metalis"]], [0.3, 0.7])],
        "doc_3": [T("Registro funcional", ["Campo", "Dado"], [["Foto", "@Foto"], ["Histórico", "@Histórico"], ["Empresa", "Fábrica Metalis"]], [0.3, 0.7])],
    },
    "case_45": {
        "doc_1": [T("Balanço anual da startup", ["Item", "Valor (US$)"], [["Receita total", "@Receita Total"], ["Gasto em P&D", "@Gasto em P&D"], ["Folha de pagamento", "$400k"]], [0.5, 0.5]), BR("Para onde foi o dinheiro", [["Folha", 0.4, "40%"], ["P&D", 0.25, "25%"], ["Outros", 0.35, "35%"]])],
        "doc_2": [P("Lei de incentivo à inovação · art. 4-B", ["@Requisito", "A empresa comprova por balanço", "Vale para todo o país"]), SL("DIÁRIO OFICIAL", "R", -4)],
        "doc_3": [TM("Cálculo TaxGeni", ["receita: $1M · P&D: $250k", "proporção calculada:", "@Proporção Calculada", "veredito:", "@Veredito"])],
    },
    "case_46": {
        "doc_1": [BR("Resultados do diretor", [["Lucro do trimestre", 0.75, "+15%"], ["Retenção da equipe", 0.98, "98%"]]), T("Resumo", ["Campo", "Dado"], [["Lucro no trimestre", "@Lucro no trimestre"], ["Retenção de equipe", "@Retenção de equipe"]], [0.5, 0.5])],
        "doc_2": [T("Relatório CorpCulture", ["Campo", "Dado"], [["Nota cultural", "@Nota cultural"], ["Fatores", "@Fatores"]], [0.3, 0.7]), SL("45/100", "R", -4)],
        "doc_3": [P("Manual de avaliação de liderança", ["@Critérios", "Avaliação por comitê", "Resultados vêm do financeiro"]), SL("DIRETORIA", "R", -4)],
    },
    "case_47": {
        "doc_1": [LT("Reclamação do cliente", [["De", "Cliente"], ["Para", "Atendimento"], ["Assunto", "Cancelar e-mails"]]), P("Mensagem", ["@Mensagem"], False), SL("URGENTE", "R", -4)],
        "doc_2": [TL("Ações registradas no servidor", [["18:02", "Abriu os termos de uso"], ["18:02", "@Ações"], ["18:03", "Conta criada"]]), N("Ficou 8 segundos nos termos.", "R", 2)],
        "doc_3": [P("Termos de uso · página 2", ["Cláusula 3: uso pessoal", "@Cláusula 4", "Cláusula 5: cancelamento"], False), SL("PÁG. 2", "R", -4)],
    },
    "case_48": {
        "doc_1": [T("Avaliação de qualidade · supervisor", ["Atendente", "Resultado"], [["Maria", "@Atendente Maria"], ["Pedro", "Nota 88/100"]], [0.25, 0.75]), N("Escuta de 20 ligações no trimestre.", "R", 2)],
        "doc_2": [T("Relatório SpeechScore", ["Atendente", "Resultado"], [["Maria", "@Atendente Maria"], ["Pedro", "Nota 82/100"]], [0.25, 0.75]), SL("ABAIXO DE 60", "R", -4)],
        "doc_3": [BR("Origem do áudio de treino", [["Sudeste/Sul", 0.9, "90%"], ["Outras regiões", 0.1, "10%"]]), T("Manual de treinamento", ["Campo", "Dado"], [["Base de dados", "@Base de Dados"]], [0.35, 0.65])],
    },
    "case_49": {
        "doc_1": [TL("Registro do avião", [["17:58", "Voo em rota normal"], ["18:00", "@Comando do piloto"]]), N("Registro do computador de bordo.", "R", 1.5)],
        "doc_2": [TL("Registro do AutoRoute", [["18:03", "Calculando economia de combustível"], ["18:05", "@Ação às 18:05"]]), SL("REMOTO", "R", -4)],
        "doc_3": [P("Regulamento de aviação", ["@Regra Mestra", "Toda alteração de rota é registrada", "Descumprir gera multa e suspensão"]), SL("OFICIAL", "R", -4)],
    },
    "case_50": {
        "doc_1": [T("Leitura da câmera", ["Campo", "Dado"], [["Inscrição", "@Inscrição"]], [0.3, 0.7])],
        "doc_2": [TM("Relatório ScanCheck", ["confiança da leitura: 62%", "leitura interpretada:", "@Leitura Interpretada", "veredito:", "@Veredito"])],
        "doc_3": [T("Nota fiscal do fornecedor", ["Campo", "Dado"], [["Lote enviado", "@Lote Enviado"], ["Peças", "300"]], [0.3, 0.7]), N("Lista os números de série de cada peça enviada.", "R", 2)],
    },
    "case_51": {
        "doc_1": [T("Fatura da Kyoto Tech", ["Campo", "Dado"], [["Serviço", "@Serviço"], ["Valor", "@Valor"], ["Observação", "@Observação"]], [0.3, 0.7]), SL("VENCE NO FIM DO MÊS", "R", -3)],
        "doc_2": [T("Alerta PaySafe", ["Campo", "Dado"], [["Média do serviço", "@Média do Serviço"], ["Cálculo", "@Cálculo"]], [0.34, 0.66]), SL("BLOQUEAR", "R", -4)],
        "doc_3": [T("Cadastro de fornecedores", ["Empresa", "Dado"], [["Kyoto Tech", "@Kyoto Tech"], ["Alpha Peças", "Sede: São Paulo · reais"]], [0.3, 0.7]), N("Cada fornecedor tem uma moeda de pagamento.", "R", 2)],
    },
    "case_52": {
        "doc_1": [T("Currículo do piloto", ["Campo", "Dado"], [["Horas de voo", "@Horas de voo"], ["Condecorações", "@Condecorações"]], [0.35, 0.65]), N("Trinta anos de carreira e muitos elogios.", "R", 2)],
        "doc_2": [T("Licença de piloto", ["Campo", "Dado"], [["Categoria", "Comercial · jatos"], ["Validade médica", "@Validade Médica"]], [0.35, 0.65]), SL("LICENÇA", "R", -4)],
        "doc_3": [P("Regulamento de aviação", ["@Permissão de Voo", "Multa e suspensão para quem descumprir"]), SL("OFICIAL", "R", -4)],
    },
    "case_53": {
        "doc_1": [T("Histórico da conta", ["Evento", "Data"], [["Última compra", "Domingo"], ["Pedido de cancelamento", "@Pedido de cancelamento"]], [0.45, 0.55]), N("Pedido feito pelo formulário do site.", "R", 2)],
        "doc_2": [T("Histórico de disparo", ["Evento", "Data"], [["Campanha", "Liquidação de fim de mês"], ["Envio da oferta", "@Envio da Oferta"]], [0.4, 0.6]), SL("AUTOMÁTICO", "R", -4)],
        "doc_3": [P("Termos de serviço", ["Cláusula 8: conta e cadastro", "@Cláusula de Saída"], False), SL("v5.2", "R", -4)],
    },
    "case_54": {
        "doc_1": [T("Balanço da empresa", ["Campo", "Dado"], [["Crescimento", "@Crescimento"], ["Inadimplência", "@Inadimplência"]], [0.4, 0.6]), N("Balanço auditado por escritório externo.", "R", 2)],
        "doc_2": [LT("Relatório do gerente", [["Veredito", "@Veredito"]]), P("Notas manuais", ["@Notas Manuais"], False), SL("À MÃO", "R", -4)],
        "doc_3": [T("Histórico FairCred", ["Campo", "Dado"], [["Veredito", "@Veredito"]], [0.3, 0.7]), P("Filtro de viés", ["@Filtro de Viés"], False)],
    },
    "case_55": {
        "doc_1": [T("Alerta SecurCore", ["Campo", "Dado"], [["Ameaça", "@Ameaça"], ["Resposta", "@Resposta"]], [0.28, 0.72]), SL("ALERTA", "R", -4)],
        "doc_2": [T("Entradas por crachá · hoje", ["Setor", "Quem"], [["Setor A", "@Presença"], ["Setor B", "Ninguém"]], [0.25, 0.75]), N("Registro automático das catracas.", "R", 2)],
        "doc_3": [P("Manual de emergência", ["@Regra 1", "Regra 2: acione os bombeiros"], False), SL("BOMBEIROS", "R", -4)],
    },
    "case_56": {
        "doc_1": [P("Contrato master de fornecimento", ["@Preço por Peça", "Sem reajuste no período", "Vale para 12 meses"]), SL("ASSINADO", "R", -4)],
        "doc_2": [T("Faturamento anual", ["Campo", "Dado"], [["Volume", "@Volume"], ["Faturado", "@Faturado"]], [0.3, 0.7]), N("Um faturamento por mês, total na última linha.", "R", 2)],
        "doc_3": [TM("Relatório FraudHawk", ["conta feita:", "@Conta certa", "detecção:", "@Detecção"])],
    },
}
