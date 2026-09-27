from author_docs_common import *

DOCS = {
    "case_22": {
        "doc_1": [P("Política de acesso · setor restrito", ["Entrada só com crachá ativo", "@Regra Noturna", "Toda entrada é gravada em vídeo"]), SL("SEGURANÇA", "R", -4),
                  N("Exceções precisam de e-mail da diretoria.", "L", -1.5)],
        "doc_2": [T("Registro da porta · entrada B", ["Hora", "Credencial", "Resultado"], [["22:41", "Crachá 3102", "Negado"], ["@Horário", "@Credencial", "Concedido"], ["23:40", "Crachá 1990", "Negado"]], [0.2, 0.5, 0.3]),
                  N("Ninguém da segurança estava de plantão na hora.", "R", 2)],
        "doc_3": [LT("Mensagem arquivada", [["De", "CEO"], ["Para", "Infraestrutura"], ["Assunto", "@Assunto"], ["Anexo", "@Anexo"]], "Precisamos recuperar o servidor esta noite. Segue o token para o acesso. Obrigado."), SL("ENVIADO", "R", -4)],
    },
    "case_23": {
        "doc_1": [P("Como o app ordena os motoristas", ["Ranking atualizado toda semana", "@Prioridade", "Corridas melhores vão para o topo"]), SL("REGRA DO APP", "R", -4)],
        "doc_2": [T("Grupo A · 1.800 motoristas", ["Dado", "Valor"], [["Perfil", "@Perfil"], ["Jornada", "@Jornada"], ["Posição média no ranking", "780 de 3.000"]], [0.4, 0.6]),
                  BR("Horas online por dia", [["Grupo A", 0.71, "10h"], ["Meta do app", 0.86, "12h"]])],
        "doc_3": [T("Grupo B · 2.100 motoristas", ["Dado", "Valor"], [["Perfil", "@Perfil"], ["Jornada", "@Jornada"], ["Posição média no ranking", "410 de 3.000"]], [0.4, 0.6]),
                  BR("Horas online por dia", [["Grupo B", 0.93, "13h"], ["Meta do app", 0.86, "12h"]])],
    },
    "case_24": {
        "doc_1": [TM("Log da Prensa Hidráulica 12", ["06:10  ciclo normal", "09:42  ALERTA:", "@Erro", "09:43  alarme soou (3x neste turno)", "09:44  operador pediu parada"])],
        "doc_2": [P("Manual de segurança · prensas", ["@Regra", "Só o gerente libera a volta", "Registro obrigatório da parada"]), SL("NORMA 12", "R", -4)],
        "doc_3": [LT("Painel FactoryBrain · ordens ativas", [["Meta do mês", "12 mil peças"], ["Ordem", "@Ordem"]], "O sistema prioriza cumprir as metas definidas pela diretoria industrial."), SL("PRIORIDADE", "R", -3)],
        "doc_4": [TM("Comando emitido pela IA", ["decisão tomada às 09:45", "@Decisão", "aprovação humana: nenhuma", "status da máquina: em operação"])],
    },
    "case_25": {
        "doc_1": [T("Leitura do crachá", ["Campo", "Dado"], [["ID", "@ID"], ["Vínculo", "@Vínculo"]], [0.3, 0.7]), N("Foto confere com o portador.", "R", 2)],
        "doc_2": [T("Prefixos de crachá", ["Prefixo", "Quem usa"], [["FUN", "Funcionário da casa"], ["Regra", "@Padrão"], ["VIS", "Visitantes"]], [0.22, 0.78]), SL("CADASTRO RH", "R", -4)],
        "doc_3": [T("Contratos externos", ["Empresa", "Serviço", "Situação"], [["Serviços Integrados", "Limpeza", "@Status"], ["Alpha Segurança", "Portaria", "Ativo"]], [0.3, 0.17, 0.53]), N("Prazo dos contratos de limpeza conferido pelo RH.", "L", -1.5)],
    },
    "case_26": {
        "doc_1": [P("Regras de ponto · vigilantes", ["Registrar entrada na guarita 2", "@Área permitida", "Sair do raio sem aviso vira falta"]), SL("RH", "R", -4)],
        "doc_2": [T("Leitura do celular", ["Campo", "Dado"], [["Posição bruta", "@Posição Bruta"], ["Precisão", "GPS comum"]], [0.34, 0.66])],
        "doc_3": [TM("Cálculo GeoTrack Ponto", ["posição lida: 40 m", "margem de erro: 30 m", "ajuste aplicado:", "@Ajuste de Risco", "resultado: falta grave"])],
    },
    "case_27": {
        "doc_1": [T("Histórico de uso da conta", ["Data", "Ação", "Duração"], [["@Data", "@Ação", "40 segundos"]], [0.24, 0.5, 0.26]), N("O usuário fechou o aplicativo logo depois.", "R", 2)],
        "doc_2": [P("Contrato de uso · versão 2", ["Cláusula 30: dados de navegação", "@Cláusula Adicionada", "Cláusula 32: foro da comarca"]), SL("V.2", "R", -5)],
        "doc_3": [TL("Histórico de publicações", [["V.1", "Publicada há 8 meses"], ["V.2", "@Publicação V.2"]]), N("Publicações automáticas de madrugada.", "R", 1.5)],
    },
    "case_28": {
        "doc_1": [TM("Log do Ponto Eletrônico", ["comando executado:", "@Ação", "registros afetados: ~340", "backup: nenhum"])],
        "doc_2": [T("Rastro de acesso", ["Campo", "Dado"], [["Credencial", "@Credencial Usada"], ["Tipo", "Conta compartilhada"], ["Horário", "Sábado 23:12"]], [0.32, 0.68])],
        "doc_3": [T("Origem da conexão", ["Campo", "Dado"], [["Origem", "@Origem do Acesso Suporte"], ["Tipo", "Acesso remoto"], ["Cidade", "Filial regional"]], [0.3, 0.7])],
        "doc_4": [P("Política de horas", ["@Regra", "Horas extras exigem aprovação", "Correções só com registro"]), SL("RH", "R", -4)],
    },
    "case_29": {
        "doc_1": [BR("Origem dos trainees 2020–2025", [["Faculdade A", 0.45, "45%"], ["Faculdade B", 0.35, "35%"], ["Outras", 0.2, "20%"]]), T("Resumo", ["Dado"], [["@Perfil Passado"]])],
        "doc_2": [T("Resultado do programa 2026", ["Dado"], [["@Perfil Aprovado"]]), BR("Origem dos selecionados 2026", [["Universidades públicas", 0.6, "60%"], ["Privadas", 0.4, "40%"]])],
        "doc_3": [P("Como a análise cega funciona", ["A IA lê só habilidades técnicas", "@Campos Ocultados", "Ranking final por pontuação"]), SL("BLINDHIRE", "R", -4)],
    },
    "case_30": {
        "doc_1": [T("Sensores de fumaça", ["Corredor", "Leitura"], [["Sul", "@Corredor Sul"]], [0.25, 0.75])],
        "doc_2": [T("Sensores de movimento", ["Corredor", "Lotação"], [["Norte", "@Corredor Norte"], ["Leste", "Livre"]], [0.25, 0.75]), BR("Ocupação dos corredores", [["Corredor Norte", 1.0, "100%"], ["Corredor Leste", 0.2, "20%"]])],
        "doc_3": [TM("Comandos dos painéis de saída", ["painéis 1, 2 e 3", "comando enviado:", "@Comando", "status: em execução"])],
    },
    "case_31": {
        "doc_1": [C("Fórum de usuários", [["L", "usuario_1978", "@Reclamação"], ["R", "moderador", "Estamos analisando o caso."], ["L", "tia_da_net", "Comigo também aconteceu!"]])],
        "doc_2": [T("Requisitos da versão 9", ["Item", "Valor"], [["Consumo base", "@Consumo Base"], ["Armazenamento", "4 GB"], ["Processador", "2 núcleos"]], [0.36, 0.64]), SL("V.9", "R", -4)],
        "doc_3": [T("Testes em máquinas antigas", ["Máquina", "Resultado"], [["Menos de 8 GB", "@Teste em máquinas < 8GB"], ["16 GB", "Sem problemas"]], [0.3, 0.7]), N("Testes feitos em duas semanas, 42 modelos.", "R", 2)],
    },
    "case_32": {
        "doc_1": [T("Leitura da câmera", ["Campo", "Dado"], [["Data", "@Data"], ["Placa lida pela IA", "@Placa Lida"], ["Observação", "@Observação"]], [0.32, 0.68])],
        "doc_2": [T("Registro do veículo", ["Campo", "Dado"], [["Placa", "@Placa"], ["Modelo", "@Modelo"], ["Proprietário", "Marcos T. Oliveira"], ["Situação", "Licenciado"]], [0.32, 0.68]), N("Licenciamento em dia, sem multas anteriores.", "R", 2)],
    },
    "case_33": {
        "doc_1": [T("Folha de ponto · novembro", ["Dia", "Registro", "Extras"], [["14/11", "08h–17h", "0h"], ["15/11 (feriado)", "07h–18h", "@Dia 15/11"], ["16/11", "08h–17h", "0h"]], [0.34, 0.33, 0.33]), N("Feriado nacional: trabalho autorizado pelo chefe.", "R", 1.5)],
        "doc_2": [T("Holerite · novembro", ["Item", "Valor"], [["Salário base", "$1.600"], ["Horas extras", "@Valor Extra Pago"], ["Desconto INSS", "-$140"]], [0.3, 0.7])],
        "doc_3": [P("Acordo do sindicato", ["Horas extras normais pagam 1.5x", "@Regra", "Noturnas pagam adicional de 20%"]), SL("SINDICATO", "R", -4)],
    },
    "case_34": {
        "doc_1": [T("Formulário de aluguel", ["Campo", "Dado"], [["Renda mensal", "@Renda"], ["Aluguel", "@Aluguel"], ["Dívidas ativas", "Nenhuma"]], [0.4, 0.6]), CL("Documentos entregues", [["Comprovante de renda", "x"], ["Documento com foto", "x"], ["Fiador", "-"]])],
        "doc_2": [T("Relatório RentaScore", ["Campo", "Dado"], [["Nota de crédito", "@Nota de crédito"], ["Fator de rejeição", "@Fator de Rejeição"]], [0.32, 0.68]), SL("NEGADO", "R", -4)],
        "doc_3": [P("Critérios para aprovar aluguel", ["@Critérios Válidos", "Análise feita por pessoa", "Motivo da negativa por escrito"]), SL("POLÍTICA", "R", -4)],
    },
    "case_35": {
        "doc_1": [CL("Termos de uso da TV (aceite ao ligar)", [["@Captura de Áudio", "x"], ["Atualizações automáticas", "x"], ["Anúncios na tela inicial", "x"]]), N("O termo tem 22 páginas. Ninguém lê.", "R", 2)],
        "doc_2": [T("Histórico da campanha", ["Campo", "Dado"], [["ID do cliente", "@ID Cliente"], ["Gatilho", "@Gatilho"], ["Anúncio", "Xarope e pastilhas"]], [0.3, 0.7])],
        "doc_3": [LT("Contrato de anunciante", [["Anunciante", "Rede de farmácias"], ["Agência", "Mídia Total"], ["Fonte dos dados", "@Fonte dos dados"]], "A agência entrega anúncios ao público definido pela fonte acima, com verba de $40 mil."), SL("CONTRATO", "R", -4)],
    },
    "case_36": {
        "doc_1": [T("Currículo · candidata A", ["Campo", "Dado"], [["Cargo", "@Experiência"], ["Formação", "Engenharia Civil"], ["Lacuna", "@Lacuna"]], [0.3, 0.7]), TL("Trajetória", [["2014–20", "Engenheira Jr. até Pleno"], ["2022–hoje", "Engenheira Pleno"]])],
        "doc_2": [T("Currículo · candidato B", ["Campo", "Dado"], [["Cargo", "@Experiência"], ["Formação", "Engenharia Civil"], ["Lacuna", "@Lacuna"]], [0.3, 0.7]), TL("Trajetória", [["2012–18", "Engenheiro Jr. até Pleno"], ["2020–hoje", "Engenheiro Pleno"]]), SL("APROVADO", "R", -4)],
        "doc_3": [P("Regras do HR-Filter", ["Roda em cerca de 400 currículos por dia", "@Regra Interna"]), SL("FILTRO v3", "R", -4)],
    },
}
