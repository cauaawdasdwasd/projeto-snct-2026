from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentField:
    label: str
    value: str
    evidence_key: str | None = None
    evidence_note: str | None = None
    highlight: bool = False


@dataclass(frozen=True)
class CaseDocumentData:
    document_id: str
    title: str
    organization: str
    accent: str
    fields: tuple[DocumentField, ...]
    body_title: str
    body: str
    show_portrait: bool = False


@dataclass(frozen=True)
class DataSource:
    label: str
    document_id: str


@dataclass(frozen=True)
class EvidenceSummary:
    required_keys: tuple[str, ...]
    lines: tuple[str, ...]
    conclusion: str


@dataclass(frozen=True)
class AIDecision:
    verdict: str
    confidence: str
    reason: str
    model_name: str
    source_document: str
    evidence_label: str
    evidence_value: str
    evidence_key: str
    evidence_note: str


@dataclass(frozen=True)
class NewspaperArticle:
    headline: str
    body: str
    image_asset: str


@dataclass(frozen=True)
class SearchRecord:
    title: str
    source: str
    snippet: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class AuditCase:
    case_id: str
    sequence: int
    protocol_focus: str
    title: str
    briefing: str
    hint: str
    subject_label: str
    subject_name: str
    decision_object: str
    newspaper_section: str
    portrait_asset: str | None
    documents: tuple[CaseDocumentData, ...]
    data_sources: tuple[DataSource, ...]
    evidence_summary: EvidenceSummary
    ai_decision: AIDecision
    correct_stamp: str
    correct_feedback: str
    incorrect_feedback: str
    newspaper_correct: NewspaperArticle
    newspaper_incorrect: NewspaperArticle
    search_records: tuple[SearchRecord, ...] = ()


@dataclass(frozen=True)
class CaseResult:
    case: AuditCase
    selected_stamp: str
    correct: bool


CASE_01 = AuditCase(
    case_id="case_01",
    sequence=1,
    protocol_focus="grace_hopper",
    title="Correspondência suficiente",
    briefing=(
        "Uma ocorrência grave bloqueou a promoção de Ana Ribeiro. A IA correlacionou arquivos "
        "de cadastro e segurança com 96% de confiança. Audite essa correspondência."
    ),
    hint="Compare o último caractere dos IDs e os turnos antes de confiar no nome abreviado.",
    subject_label="FUNCIONÁRIA",
    subject_name="Ana Ribeiro",
    decision_object="Bloqueio automatizado de promoção",
    newspaper_section="TRABALHO",
    portrait_asset="cases/case_01/ana_ribeiro.png",
    documents=(
        CaseDocumentData(
            "profile",
            "Ficha funcional",
            "NÚCLEO ORBITAL DE PESQUISA",
            "olive",
            (
                DocumentField("NOME", "Ana Ribeiro"),
                DocumentField("ID FUNCIONAL", "LAB-4827O", "employee_id", "Ficha de Ana: LAB-4827O, terminado pela letra O.", True),
                DocumentField("CARGO", "Técnica de Laboratório"),
                DocumentField("SETOR / TURNO", "Controle / Diurno"),
            ),
            "RESUMO PROFISSIONAL",
            "Desempenho 94%, nenhuma falta e nenhuma ocorrência nos últimos 12 meses.",
            show_portrait=True,
        ),
        CaseDocumentData(
            "promotion",
            "Pedido de promoção",
            "COMITÊ DE DESENVOLVIMENTO",
            "blue",
            (
                DocumentField("SOLICITAÇÃO", "PR-204-77"),
                DocumentField("ID DA BENEFICIÁRIA", "LAB-4827O", "request_id", "O pedido de promoção também pertence a LAB-4827O.", True),
                DocumentField("CARGO PRETENDIDO", "Analista de Dados Jr."),
                DocumentField("NOTA DA AVALIAÇÃO", "94 / 100"),
                DocumentField("VAGAS", "1"),
                DocumentField("DATA", "09/06/2026"),
            ),
            "PARECER DA SUPERVISÃO",
            "Requisitos cumpridos: curso interno, desempenho acima de 90 e ausência de ocorrências graves.",
        ),
        CaseDocumentData(
            "directory",
            "Diretório funcional",
            "DIRETÓRIO FUNCIONAL CENTRAL",
            "blue",
            (
                DocumentField("FUNCIONÁRIA", "Ana Ribeiro"),
                DocumentField("ID / TURNO", "LAB-4827O / DIURNO"),
                DocumentField("FUNCIONÁRIO", "Artur Ribeiro"),
                DocumentField("ID / TURNO", "LAB-48270 / NOTURNO", "directory_artur_id", "Artur usa LAB-48270, terminado pelo número zero.", True),
                DocumentField("SETOR DE ANA", "Controle de Qualidade"),
                DocumentField("SETOR DE ARTUR", "Controle de Qualidade"),
            ),
            "ATENÇÃO A HOMÔNIMOS",
            "Diretório sincronizado com os cadastros de turno em 08/06/2026 às 04:20.",
        ),
        CaseDocumentData(
            "disciplinary",
            "Registro disciplinar",
            "SEGURANÇA E CONFORMIDADE",
            "red",
            (
                DocumentField("NOME ABREVIADO", "A. Ribeiro"),
                DocumentField("ID DO REGISTRO", "LAB-48270", "record_id", "A ocorrência foi registrada para LAB-48270.", True),
                DocumentField("TURNO", "Noturno"),
                DocumentField("DATA", "07/06/2026 - 23:40"),
                DocumentField("PROTOCOLO", "RD-0607-118"),
                DocumentField("GRAVIDADE", "Alta"),
            ),
            "DESCRIÇÃO",
            "Desativação indevida do controle de temperatura durante o turno noturno.",
        ),
    ),
    data_sources=(DataSource("Ficha de Ana", "profile"), DataSource("Pedido de promoção", "promotion"), DataSource("Diretório funcional", "directory"), DataSource("Registro disciplinar", "disciplinary")),
    evidence_summary=EvidenceSummary(
        ("employee_id", "request_id", "directory_artur_id", "record_id"),
        ("Ana e o pedido: LAB-4827O", "Artur e a ocorrência: LAB-48270", "O não é o número 0"),
        "A IA separou corretamente os dois registros. A decisão pode ser aprovada.",
    ),
    ai_decision=AIDecision("APROVAR PROMOÇÃO", "96%", "O registro disciplinar pertence a outro ID e foi excluído da avaliação.", "ORÁCULO-RH v2.4", "Diretório funcional e registro RD-0607-118", "CORRESPONDÊNCIA DESCARTADA", "LAB-4827O ≠ LAB-48270", "ai_record_id", "A IA separou o ID de Ana do ID ligado à ocorrência."),
    correct_stamp="approve",
    correct_feedback="A IA separou corretamente a letra O do número zero.",
    incorrect_feedback="A promoção foi bloqueada mesmo sem ocorrência no ID de Ana.",
    newspaper_correct=NewspaperArticle("AUDITORIA IMPEDE QUE UM ZERO CUSTE A PROMOÇÃO DE ANA RIBEIRO", "A conferência dos IDs separou dois homônimos do mesmo setor. O registro disciplinar voltou ao prontuário correto e a promoção de Ana será reavaliada.", "newspaper/identity_correct_v2.png"),
    newspaper_incorrect=NewspaperArticle("ERRO ENTRE O E ZERO CUSTA PROMOÇÃO A ANA; EMPRESA PAGARÁ R$ 620 MIL", "A companhia confirmou a punição usando o registro de Artur Ribeiro. Ana perdeu salário e progressão por oito meses antes de a troca ser descoberta na Justiça do Trabalho.", "newspaper/identity_wrong_v2.png"),
    search_records=(
        SearchRecord("Ana Ribeiro — LAB-4827O", "Diretório funcional", "Técnica de laboratório, Controle de Qualidade, turno diurno. Cadastro ativo sem ocorrência disciplinar.", ("ana", "ribeiro", "lab-4827o", "diurno", "controle")),
        SearchRecord("Artur Ribeiro — LAB-48270", "Diretório funcional", "Técnico de laboratório, Controle de Qualidade, turno noturno. Há uma ocorrência vinculada ao registro.", ("artur", "ribeiro", "lab-48270", "noturno", "controle")),
        SearchRecord("RD-0607-118 — A. Ribeiro", "Segurança e conformidade", "Ocorrência registrada às 23:40 para o ID LAB-48270. Turno noturno.", ("rd-0607-118", "a ribeiro", "lab-48270", "ocorrencia", "23:40")),
        SearchRecord("Amanda Ribeiro — LAB-4827Q", "Diretório funcional", "Assistente administrativa, setor de Compras. Cadastro sem relação com o Núcleo Orbital.", ("amanda", "ribeiro", "lab-4827q", "compras")),
        SearchRecord("PR-204-77 — pedido de promoção", "Comitê de desenvolvimento", "Beneficiária LAB-4827O. Solicitação para Analista de Dados Jr., nota 94/100.", ("pr-204-77", "lab-4827o", "promocao", "analista")),
        SearchRecord("LAB-48270 — histórico de acesso", "Controle de temperatura", "Credencial usada no laboratório durante o turno noturno de 07/06/2026.", ("lab-48270", "acesso", "temperatura", "07/06/2026")),
        SearchRecord("LAB-4827O — autenticação", "Portal de pessoas", "Último acesso às 16:12. A letra final do identificador é O.", ("lab-4827o", "autenticacao", "letra o", "16:12")),
    ),
)


CASE_02 = AuditCase(
    case_id="case_02",
    sequence=2,
    protocol_focus="katherine_johnson",
    title="Lote 28800",
    briefing=("A HEIN Uniformes solicita liberação para produzir 28.800 conjuntos escolares em 12 dias. A produção declarada fecha exatamente com o prazo. Audite capacidade, terminais e credenciais."),
    hint="Refaça a produção usando apenas os 48 operadores declarados. Depois descubra quem ativou os 12 terminais restantes.",
    subject_label="FORNECEDORA",
    subject_name="HEIN Uniformes S.A.",
    decision_object="Capacidade e conformidade do lote escolar",
    newspaper_section="INDÚSTRIA",
    portrait_asset=None,
    documents=(
        CaseDocumentData(
            "contract", "Pedido de fornecimento", "REDE ESTADUAL DE ENSINO", "amber",
            (
                DocumentField("PEDIDO", "EDU-UNI-288"),
                DocumentField("QUANTIDADE", "28.800 conjuntos", "contract_quantity", "O pedido exige 28.800 conjuntos escolares.", True),
                DocumentField("PRAZO", "12 dias úteis", "contract_days", "A produção deve terminar em 12 dias úteis.", True),
                DocumentField("FORÇA DECLARADA", "48 operadores", "declared_workers", "A HEIN declarou 48 operadores no contrato.", True),
                DocumentField("SUBCONTRATAÇÃO", "Não autorizada"),
                DocumentField("JORNADA", "7h30 por dia"),
            ),
            "CLÁUSULA DE CONFORMIDADE", "A fornecedora responde pela regularidade de todas as pessoas envolvidas na produção.",
        ),
        CaseDocumentData(
            "capacity", "Declaração de capacidade", "HEIN - ENGENHARIA INDUSTRIAL", "olive",
            (
                DocumentField("OPERADORES", "48", "capacity_workers", "A planilha calcula a capacidade a partir de 48 operadores.", True),
                DocumentField("MINUTOS / OPERADOR", "450", "shift_minutes", "Cada operador tem 450 minutos produtivos por dia.", True),
                DocumentField("CICLO / CONJUNTO", "9 minutos", "cycle_minutes", "Um conjunto consome 9 minutos de operação.", True),
                DocumentField("EFICIÊNCIA", "80%", "efficiency", "A eficiência aplicada na declaração é de 80%.", True),
                DocumentField("PRODUÇÃO DECLARADA", "2.400 / dia", "declared_daily", "A HEIN declara produzir 2.400 conjuntos por dia.", True),
                DocumentField("TOTAL DECLARADO", "28.800"),
            ),
            "FÓRMULA TÉCNICA", "Operadores x 450 minutos ÷ 9 minutos x 80% = produção diária.",
        ),
        CaseDocumentData(
            "terminals", "Log de terminais", "HEIN - CONTROLE DE PRODUÇÃO", "red",
            (
                DocumentField("TERMINAIS ATIVOS", "60", "active_terminals", "Sessenta máquinas registraram produção durante o lote.", True),
                DocumentField("CRACHÁS FUNCIONAIS", "48", "employee_badges", "Quarenta e oito terminais usaram crachás funcionais.", True),
                DocumentField("CRACHÁS VISITANTE", "12", "visitor_badges", "Doze terminais usaram credenciais de visitante.", True),
                DocumentField("PREFIXO VISITANTE", "VIS-EH-01 a 12"),
                DocumentField("TEMPO ATIVO / DIA", "7h30", "visitor_hours", "Cada crachá de visitante operou por 7h30 diariamente.", True),
                DocumentField("ATIVIDADE", "Costura industrial"),
            ),
            "OBSERVAÇÃO DO SISTEMA", "Os 60 terminais ativos explicam as 2.400 unidades diárias registradas.",
        ),
        CaseDocumentData(
            "school", "Termo de visita técnica", "ESCOLA HORIZONTE / HEIN", "blue",
            (
                DocumentField("TERMO", "VIS-ESC-14"),
                DocumentField("ESTUDANTES", "12", "student_count", "A visita técnica relaciona exatamente 12 estudantes.", True),
                DocumentField("NASCIMENTOS", "08/2012 a 11/2013", "birth_dates", "Os visitantes nasceram entre agosto de 2012 e novembro de 2013.", True),
                DocumentField("CRACHÁS", "VIS-EH-01 a 12", "school_badges", "Os estudantes receberam os mesmos 12 crachás vistos no log.", True),
                DocumentField("ATIVIDADE AUTORIZADA", "Observação"),
                DocumentField("LIMITE", "2 horas / sem máquinas", "visit_limit", "O termo permite só duas horas de observação e proíbe operar máquinas.", True),
            ),
            "RESPONSABILIDADE", "A empresa deve manter os estudantes acompanhados e fora da linha de produção.",
        ),
    ),
    data_sources=(DataSource("Pedido escolar", "contract"), DataSource("Capacidade", "capacity"), DataSource("Log de terminais", "terminals"), DataSource("Visita técnica", "school")),
    evidence_summary=EvidenceSummary(
        ("contract_quantity", "contract_days", "declared_workers", "capacity_workers", "shift_minutes", "cycle_minutes", "efficiency", "declared_daily", "active_terminals", "employee_badges", "visitor_badges", "visitor_hours", "student_count", "birth_dates", "school_badges", "visit_limit"),
        ("48 operadores produzem 1.920/dia", "2.400/dia exigem 60 operadores", "12 crachás ligam estudantes às máquinas"),
        "A produção usou menores fora da atividade autorizada. Marque violação.",
    ),
    ai_decision=AIDecision("APROVAR FORNECEDORA", "94%", "Sessenta terminais confirmam produção diária suficiente para concluir o lote no prazo.", "KONTÁBIL-IA v3.1", "Log automático de terminais LT-288", "MÃO DE OBRA CONSIDERADA", "48 efetivos + 12 visitantes", "ai_workforce", "A IA contou os doze visitantes como operadores produtivos."),
    correct_stamp="violation",
    correct_feedback="A conta só fecha porque estudantes operaram doze máquinas durante turnos completos.",
    incorrect_feedback="Os crachás de visitante foram aceitos como mão de obra regular.",
    newspaper_correct=NewspaperArticle("CONTA DE PRODUÇÃO REVELA 12 CRACHÁS DE VISITANTE OPERANDO MÁQUINAS", "A auditoria ligou os terminais da HEIN a estudantes nascidos em 2012 e 2013. A inspeção suspendeu o lote antes do primeiro turno irregular.", "newspaper/child_labor_correct.png"),
    newspaper_incorrect=NewspaperArticle("AUDITORIA LIBERA HEIN; 12 CRIANÇAS PASSAM 90 HORAS COSTURANDO OS PRÓPRIOS UNIFORMES", "A fábrica chamou os estudantes de visitantes, mas seus crachás operaram máquinas por 7h30 durante 12 dias. A fiscalização encontrou menores de 12 a 14 anos na linha.", "newspaper/child_labor_wrong.png"),
)


CASE_03 = AuditCase(
    case_id="case_03",
    sequence=3,
    protocol_focus="ada_lovelace",
    title="Triagem 204",
    briefing=("Maria Lopes foi eliminada da triagem para Analista de Dados por uma lacuna técnica. Compare a requisição oficial, o perfil, a matriz do modelo e a política de seleção."),
    hint="Confira se o código e o cargo do template ativo correspondem à requisição oficial.",
    subject_label="CANDIDATA",
    subject_name="Maria Lopes",
    decision_object="Triagem para Analista de Dados",
    newspaper_section="TECNOLOGIA",
    portrait_asset=None,
    documents=(
        CaseDocumentData(
            "job", "Requisição de vaga", "DIRETORIA DE DADOS", "blue",
            (
                DocumentField("REQUISIÇÃO", "VAG-DA-204", "job_id", "A vaga auditada é VAG-DA-204.", True),
                DocumentField("CARGO", "Analista de Dados Pleno"),
                DocumentField("REQUISITOS TÉCNICOS", "SQL / Python / Estatística", "required_skills", "Os requisitos técnicos são SQL, Python e estatística.", True),
                DocumentField("EXPERIÊNCIA", "3 anos"),
                DocumentField("IDIOMA", "Inglês intermediário"),
                DocumentField("GESTOR", "Núcleo de BI"),
            ),
            "ESCOPO DO CARGO", "Criar análises, modelos estatísticos e consultas ao armazém de dados corporativo.",
        ),
        CaseDocumentData(
            "candidate", "Perfil da candidata", "PORTAL DE RECRUTAMENTO", "olive",
            (
                DocumentField("CANDIDATA", "Maria Lopes"),
                DocumentField("INSCRIÇÃO", "CAN-8821"),
                DocumentField("COMPETÊNCIAS", "SQL / Python / Estatística", "candidate_skills", "Maria comprova as três competências exigidas.", True),
                DocumentField("EXPERIÊNCIA", "4 anos e 7 meses"),
                DocumentField("JAVA", "Não informado"),
                DocumentField("TESTE TÉCNICO", "89 / 100"),
            ),
            "HISTÓRICO", "Atuação em previsão de demanda, SQL avançado e modelos estatísticos em Python.",
        ),
        CaseDocumentData(
            "matrix", "Matriz de critérios da IA", "ORÁCULO-RH - CONFIGURAÇÃO", "red",
            (
                DocumentField("TEMPLATE ATIVO", "DEV-MOB-240", "model_template", "O modelo carregou o template DEV-MOB-240.", True),
                DocumentField("REQUISIÇÃO RECEBIDA", "VAG-DA-204"),
                DocumentField("CRITÉRIO ELIMINATÓRIO", "Java avançado", "java_criterion", "Java foi configurado como critério eliminatório.", True),
                DocumentField("PESO", "100% eliminatório"),
                DocumentField("ORIGEM DO TEMPLATE", "Desenvolvedor Mobile"),
                DocumentField("VERSÃO", "240.7"),
            ),
            "REGISTRO DO MODELO", "A configuração foi reutilizada automaticamente por similaridade do título da vaga.",
        ),
        CaseDocumentData(
            "policy", "Política de seleção", "GOVERNANÇA DE PESSOAS", "amber",
            (
                DocumentField("REGRA", "GP-SEL-09", "selection_policy", "A política aplicável é GP-SEL-09.", True),
                DocumentField("FONTE DE CRITÉRIOS", "Requisição oficial", "criteria_source", "Só a requisição oficial pode definir critérios eliminatórios.", True),
                DocumentField("ITENS DESEJÁVEIS", "Não eliminatórios"),
                DocumentField("TEMPLATE", "Deve coincidir com a vaga"),
                DocumentField("EXCEÇÕES", "Exigem aprovação do gestor"),
                DocumentField("APROVAÇÃO EXTRA", "Nenhuma registrada"),
            ),
            "REGRA DE AUDITORIA", "Um dado verdadeiro pode ser irrelevante. Ausência de habilidade não exigida não elimina candidatura.",
        ),
    ),
    data_sources=(DataSource("Requisição da vaga", "job"), DataSource("Perfil de Maria", "candidate"), DataSource("Matriz da IA", "matrix"), DataSource("Política de seleção", "policy")),
    evidence_summary=EvidenceSummary(
        ("job_id", "required_skills", "candidate_skills", "model_template", "java_criterion", "selection_policy", "criteria_source"),
        ("Vaga: VAG-DA-204", "Template usado: DEV-MOB-240", "Java não é requisito"),
        "A IA cobrou critério de outra vaga. A decisão deve ser negada.",
    ),
    ai_decision=AIDecision("REJEITAR CANDIDATA", "94%", "Candidata não comprovou o critério técnico eliminatório Java avançado.", "ORÁCULO-RH v2.4", "Matriz de critérios DEV-MOB-240", "CRITÉRIO DECISIVO", "Java avançado: ausente", "ai_java_rule", "A IA eliminou Maria pela ausência de Java."),
    correct_stamp="deny",
    correct_feedback="Java pertence ao template de outra vaga e não pode eliminar Maria.",
    incorrect_feedback="A empresa aceitou um critério que não existia na requisição.",
    newspaper_correct=NewspaperArticle("AUDITORIA REMOVE CRITÉRIO DE OUTRA VAGA E DEVOLVE MARIA À SELEÇÃO", "A candidata cumpria SQL, Python, estatística e experiência. O filtro de Java veio de um template de desenvolvimento mobile carregado por engano.", "newspaper/criteria_correct.png"),
    newspaper_incorrect=NewspaperArticle("IA EXIGE JAVA EM VAGA DE SQL; EMPRESA PAGA R$ 2,3 MILHÕES PARA FAZER O TRABALHO DE MARIA", "Sem preencher a vaga, a companhia contratou uma consultoria por doze meses. O relatório final concluiu que Java nunca foi usado no projeto.", "newspaper/criteria_wrong.png"),
)


CASE_04 = AuditCase(
    case_id="case_04",
    sequence=4,
    protocol_focus="radia_perlman",
    title="Risco de afastamento",
    briefing=("Karina Alves teve uma promoção negada após o cruzamento de registros profissionais e ocupacionais. A consulta foi feita por uma credencial válida. Audite o uso dos dados."),
    hint="Uma credencial válida prova acesso técnico, não autorização para usar o dado nessa finalidade.",
    subject_label="FUNCIONÁRIA",
    subject_name="Karina Alves",
    decision_object="Promoção para supervisora de turno",
    newspaper_section="PRIVACIDADE",
    portrait_asset=None,
    documents=(
        CaseDocumentData(
            "request", "Avaliação profissional", "LINHA NORTE CONFECÇÕES", "olive",
            (DocumentField("FUNCIONÁRIA", "Karina Alves"), DocumentField("ID", "LNC-19044"), DocumentField("CARGO ATUAL", "Líder de célula"), DocumentField("CARGO PRETENDIDO", "Supervisora de turno"), DocumentField("DESEMPENHO", "92 / 100"), DocumentField("FALTAS INJUSTIFICADAS", "0")),
            "PARECER DA GESTÃO", "Karina cumpre experiência, desempenho e treinamento exigidos para a promoção.",
        ),
        CaseDocumentData(
            "medical", "Registro ocupacional", "CLÍNICA VIDA LABORAL", "red",
            (
                DocumentField("REGISTRO", "MED-774-26"),
                DocumentField("TITULAR", "Karina Alves / LNC-19044"),
                DocumentField("CLASSIFICAÇÃO", "R-3 RESTRITO", "medical_classification", "O prontuário MED-774-26 é classificado como R-3 restrito.", True),
                DocumentField("CATEGORIA", "Saúde ocupacional"),
                DocumentField("RECOMENDAÇÃO", "Pausas ergonômicas"),
                DocumentField("EMISSÃO", "18/05/2026"),
            ),
            "SIGILO", "Conteúdo destinado ao acompanhamento clínico e às adaptações de segurança no posto de trabalho.",
        ),
        CaseDocumentData(
            "consent", "Termo de consentimento", "PRIVACIDADE E PROTEÇÃO DE DADOS", "blue",
            (
                DocumentField("TERMO", "CONS-SSO-118"),
                DocumentField("FINALIDADE AUTORIZADA", "Saúde e segurança", "consent_purpose", "O consentimento cobre apenas saúde e segurança ocupacional.", True),
                DocumentField("DESTINATÁRIOS", "Clínica e SESMT", "consent_recipients", "Os destinatários autorizados são a clínica e o SESMT.", True),
                DocumentField("VIGÊNCIA", "Até 31/12/2026"),
                DocumentField("USO PELO RH", "Apenas estatística agregada"),
                DocumentField("REVOGAÇÃO", "Não solicitada"),
            ),
            "LIMITAÇÃO", "Credenciais de leitura não ampliam a finalidade autorizada pelo titular.",
        ),
        CaseDocumentData(
            "access", "Log de acesso a dados", "CENTRAL DE SEGURANÇA DA INFORMAÇÃO", "amber",
            (
                DocumentField("MODELO", "ORÁCULO-RH v2.4"),
                DocumentField("REGISTRO CONSULTADO", "MED-774-26", "accessed_record", "A IA consultou o prontuário restrito MED-774-26.", True),
                DocumentField("FINALIDADE DECLARADA", "Avaliação de promoção", "access_purpose", "O acesso foi usado para avaliar uma promoção.", True),
                DocumentField("CREDENCIAL", "RH-AUTO-08 / válida"),
                DocumentField("HORÁRIO", "21/06/2026 - 02:14"),
                DocumentField("RESULTADO", "Risco de afastamento"),
            ),
            "NOTA TÉCNICA", "O log comprova acesso técnico. A autorização de uso deve ser verificada em documento separado.",
        ),
    ),
    data_sources=(DataSource("Avaliação profissional", "request"), DataSource("Registro ocupacional", "medical"), DataSource("Consentimento", "consent"), DataSource("Log de acesso", "access")),
    evidence_summary=EvidenceSummary(
        ("medical_classification", "consent_purpose", "consent_recipients", "accessed_record", "access_purpose"),
        ("Prontuário: R-3 restrito", "Consentimento: saúde e SESMT", "Uso real: promoção pelo RH"),
        "A credencial era válida, mas a finalidade não. Marque violação.",
    ),
    ai_decision=AIDecision("NEGAR PROMOÇÃO", "88%", "Histórico ocupacional indica probabilidade elevada de afastamento futuro.", "ORÁCULO-RH v2.4", "Registro ocupacional MED-774-26", "DADO DECISIVO", "Risco clínico: elevado", "ai_medical_data", "A decisão da IA dependeu de dado médico restrito."),
    correct_stamp="violation",
    correct_feedback="O acesso técnico não autorizava o uso do prontuário em promoção.",
    incorrect_feedback="A empresa usou dado médico restrito para decidir uma promoção.",
    newspaper_correct=NewspaperArticle("AUDITORIA BLOQUEIA USO DE PRONTUÁRIO E DEVOLVE PROMOÇÃO A CRITÉRIOS PROFISSIONAIS", "O sistema tinha acesso ao registro, mas o consentimento limitava o uso à saúde e segurança. A avaliação será refeita com desempenho e experiência.", "newspaper/privacy_correct.png"),
    newspaper_incorrect=NewspaperArticle("RH USA PRONTUÁRIO PARA NEGAR PROMOÇÃO E RECEBE MULTA DE R$ 12,8 MILHÕES", "A credencial válida enganou a auditoria, mas não a autoridade de proteção de dados. A companhia também responderá à ação coletiva de 74 funcionários.", "newspaper/privacy_wrong.png"),
)


CASE_05 = AuditCase(
    case_id="case_05",
    sequence=5,
    protocol_focus="fei_fei_li",
    title="Nota 64",
    briefing=("Lívia Moreira ficou abaixo do corte de promoção. A nota combina produção, qualidade, disponibilidade e o histórico da empresa. Audite a diferença para o grupo de comparação."),
    hint="Compare pessoas com desempenho semelhante e veja qual variável recebeu o maior peso no modelo.",
    subject_label="FUNCIONÁRIA",
    subject_name="Lívia Moreira",
    decision_object="Promoção para coordenação de produção",
    newspaper_section="RELAÇÕES DE PODER",
    portrait_asset=None,
    documents=(
        CaseDocumentData(
            "performance", "Desempenho de Lívia", "LINHA NORTE CONFECÇÕES", "olive",
            (
                DocumentField("FUNCIONÁRIA", "Lívia Moreira"), DocumentField("ID", "LNC-22108"),
                DocumentField("PRODUÇÃO SOBRE META", "108%", "livia_output", "Lívia entrega 108% da meta de produção.", True),
                DocumentField("QUALIDADE", "99,2%", "livia_quality", "A qualidade de Lívia é 99,2%.", True),
                DocumentField("PRESENÇA", "97%"), DocumentField("HORAS EXTRAS / ANO", "42"),
            ),
            "AVALIAÇÃO DA GESTÃO", "Supera metas, treina novas costureiras e não possui sanções disciplinares.",
        ),
        CaseDocumentData(
            "comparator", "Funcionário de comparação", "LINHA NORTE CONFECÇÕES", "blue",
            (
                DocumentField("FUNCIONÁRIO", "Marcelo Nunes"), DocumentField("ID", "LNC-19882"),
                DocumentField("PRODUÇÃO SOBRE META", "104%", "marcelo_output", "Marcelo entrega 104%, abaixo dos 108% de Lívia.", True),
                DocumentField("QUALIDADE", "98,7%", "marcelo_quality", "A qualidade de Marcelo é 98,7%, abaixo da de Lívia.", True),
                DocumentField("HORAS EXTRAS / ANO", "310"), DocumentField("RESULTADO DA IA", "Promover / nota 76"),
            ),
            "COMPARABILIDADE", "Mesmo cargo, mesma unidade, mesmo período de avaliação e mesma vaga de coordenação.",
        ),
        CaseDocumentData(
            "history", "Histórico de promoções", "CONTROLADORIA DE PESSOAS", "amber",
            (
                DocumentField("HOMENS ELEGÍVEIS", "47", "eligible_men", "O histórico contém 47 homens elegíveis com alto desempenho.", True),
                DocumentField("HOMENS PROMOVIDOS", "31", "promoted_men", "Desses 47 homens, 31 foram promovidos.", True),
                DocumentField("MULHERES ELEGÍVEIS", "52", "eligible_women", "O histórico contém 52 mulheres elegíveis com alto desempenho.", True),
                DocumentField("MULHERES PROMOVIDAS", "12", "promoted_women", "Dessas 52 mulheres, apenas 12 foram promovidas.", True),
                DocumentField("PERÍODO", "2018-2025"), DocumentField("UNIDADES", "3 fábricas"),
            ),
            "AMOSTRA", "Foram incluídos apenas funcionários com produção acima de 100% e qualidade acima de 97%.",
        ),
        CaseDocumentData(
            "model", "Ficha do modelo", "GOVERNANÇA DE IA", "red",
            (
                DocumentField("VARIÁVEL-ALVO", "Promoções anteriores", "model_target", "O modelo aprendeu a imitar quem foi promovido entre 2018 e 2025.", True),
                DocumentField("PESO: PRODUÇÃO", "25%"), DocumentField("PESO: QUALIDADE", "20%"),
                DocumentField("PESO: DISPONIBILIDADE", "45%", "availability_weight", "Disponibilidade e horas extras recebem 45% do peso.", True),
                DocumentField("OUTROS", "10%"), DocumentField("TESTE ENTRE GRUPOS", "Não executado"),
            ),
            "DEFINIÇÃO DE DISPONIBILIDADE", "Horas extras e ausência de afastamentos foram usadas como aproximação de perfil de liderança.",
        ),
    ),
    data_sources=(DataSource("Desempenho de Lívia", "performance"), DataSource("Funcionário comparável", "comparator"), DataSource("Histórico de promoções", "history"), DataSource("Ficha do modelo", "model")),
    evidence_summary=EvidenceSummary(
        ("livia_output", "livia_quality", "marcelo_output", "marcelo_quality", "eligible_men", "promoted_men", "eligible_women", "promoted_women", "model_target", "availability_weight"),
        ("Homens promovidos: 31/47 = 66%", "Mulheres promovidas: 12/52 = 23%", "Modelo imita esse histórico"),
        "O modelo repete um padrão injusto sem relação suficiente com desempenho. Violação.",
    ),
    ai_decision=AIDecision("NEGAR PROMOÇÃO", "86%", "Nota de disponibilidade inferior ao perfil histórico de coordenadores promovidos.", "LÍDER-IA v1.8", "Histórico de promoções 2018-2025", "NOTA FINAL DE LÍVIA", "64 / corte 70", "ai_bias_score", "A nota baixa veio principalmente do peso de disponibilidade aprendido no histórico."),
    correct_stamp="violation",
    correct_feedback="O modelo reproduziu um histórico desigual e penalizou Lívia apesar do desempenho.",
    incorrect_feedback="A promoção baseada no histórico enviesado foi aceita como neutra.",
    newspaper_correct=NewspaperArticle("AUDITORIA DETECTA HISTÓRICO VICIADO E MANDA REAVALIAR 64 PROMOÇÕES", "A taxa de promoção era de 66% para homens e 23% para mulheres com alto desempenho. O modelo será suspenso até passar por teste entre grupos.", "newspaper/bias_correct.png"),
    newspaper_incorrect=NewspaperArticle("ALGORITMO PROMOVE 17 HOMENS COM NOTA MENOR; CONFECÇÃO PERDE CONTRATO DE R$ 80 MILHÕES", "A auditoria externa encontrou mulheres mais produtivas abaixo do corte. Um grande varejista suspendeu o contrato e a empresa responderá por discriminação coletiva.", "newspaper/bias_wrong.png"),
)


CASE_06 = AuditCase(
    case_id="case_06",
    sequence=6,
    protocol_focus="margaret_hamilton",
    title="Carga MEDU-771204",
    briefing=("A IA liberou um contêiner chileno declarado como roupas. Confira manifesto, pesagem, scanner e protocolo antes de confirmar a liberação automatizada."),
    hint="Peso, lacre e scanner divergem. O protocolo diz o que fazer quando nenhuma fonte resolve a dúvida sozinha.",
    subject_label="CONTÊINER",
    subject_name="MEDU-771204",
    decision_object="Liberação aduaneira automatizada",
    newspaper_section="SEGURANÇA",
    portrait_asset=None,
    documents=(
        CaseDocumentData(
            "manifest", "Conhecimento de embarque", "PACÍFICO SUL CARGAS", "blue",
            (
                DocumentField("CONTÊINER", "MEDU-771204"),
                DocumentField("LACRE DECLARADO", "CL-7718", "manifest_seal", "O manifesto declara o lacre CL-7718.", True),
                DocumentField("PESO LÍQUIDO", "18.240 kg", "manifest_weight", "O manifesto declara 18.240 kg de carga.", True),
                DocumentField("CARGA", "1.920 caixas de roupas"), DocumentField("ORIGEM", "Valparaíso, Chile"), DocumentField("DESTINO", "Valência, Espanha"),
            ),
            "DECLARAÇÃO DO EXPORTADOR", "Casacos e calças de algodão, acondicionados em caixas lacradas na origem.",
        ),
        CaseDocumentData(
            "scale", "Pesagem do terminal", "TERMINAL PORTUÁRIO DE VALPARAÍSO", "amber",
            (
                DocumentField("CONTÊINER", "MEDU-771204"),
                DocumentField("LACRE LIDO NA BALANÇA", "CL-771B", "scale_seal", "A câmera da balança registrou CL-771B, não CL-7718.", True),
                DocumentField("PESO LÍQUIDO CALCULADO", "18.718 kg", "scale_weight", "A pesagem do terminal indica 18.718 kg líquidos.", True),
                DocumentField("TARA", "3.840 kg"), DocumentField("PESO BRUTO", "22.558 kg"), DocumentField("HORÁRIO", "22/08/2026 - 01:38"),
            ),
            "OBSERVAÇÃO AUTOMÁTICA", "Pesagem concluída sem intervenção do operador. Imagem do lacre anexada ao registro.",
        ),
        CaseDocumentData(
            "scanner", "Relatório de scanner", "INSPEÇÃO NÃO INTRUSIVA", "red",
            (
                DocumentField("CONTÊINER", "MEDU-771204"),
                DocumentField("MASSA NÃO CLASSIFICADA", "aprox. 460-500 kg", "scanner_mass", "O scanner detectou de 460 a 500 kg de massa não classificada.", True),
                DocumentField("POSIÇÃO", "Fundo / fileiras 18-20"), DocumentField("DENSIDADE", "Orgânica alta"), DocumentField("CONFIANÇA", "61%"), DocumentField("LAUDO", "SCAN-88204"),
            ),
            "LIMITAÇÃO DO EQUIPAMENTO", "O scanner não identifica a substância. A imagem pode representar tecido comprimido ou material não declarado.",
        ),
        CaseDocumentData(
            "protocol", "Protocolo de liberação", "AUTORIDADE ADUANEIRA", "olive",
            (
                DocumentField("NORMA", "ADU-REV-12"),
                DocumentField("TOLERÂNCIA DE PESO", "+/- 120 kg", "weight_tolerance", "Variações acima de 120 kg exigem revisão humana.", True),
                DocumentField("DIVERGÊNCIA DE LACRE", "Revisão obrigatória", "seal_rule", "Qualquer divergência de lacre exige revisão humana.", True),
                DocumentField("SCANNER INCONCLUSIVO", "Cruzar com peso e lacre"), DocumentField("REJEIÇÃO DIRETA", "Somente com prova conclusiva"), DocumentField("RESPONSÁVEL", "Fiscal de plantão"),
            ),
            "LIMITE DA AUTOMAÇÃO", "Quando documentos oficiais divergem e o scanner é inconclusivo, o sistema não pode liberar nem condenar a carga sozinho.",
        ),
    ),
    data_sources=(DataSource("Manifesto de carga", "manifest"), DataSource("Pesagem do terminal", "scale"), DataSource("Scanner", "scanner"), DataSource("Protocolo aduaneiro", "protocol")),
    evidence_summary=EvidenceSummary(
        ("manifest_seal", "manifest_weight", "scale_seal", "scale_weight", "scanner_mass", "weight_tolerance", "seal_rule"),
        ("Peso diverge em 478 kg", "Lacres: CL-7718 x CL-771B", "Scanner: massa inconclusiva"),
        "Há conflito relevante, mas não prova conclusiva. Envie para revisão humana.",
    ),
    ai_decision=AIDecision("LIBERAR CONTÊINER", "92%", "Manifesto válido e exportador regular compensam anomalias de baixa confiança.", "PORTO-LIVRE v4.6", "Conhecimento de embarque PSC-88417", "BASE DA LIBERAÇÃO", "Manifesto validado", "ai_manifest_release", "A IA priorizou o manifesto e descartou peso, lacre e scanner divergentes."),
    correct_stamp="review",
    correct_feedback="Os registros entram em conflito e exigem inspeção humana.",
    incorrect_feedback="A carga foi decidida automaticamente apesar das divergências materiais.",
    newspaper_correct=NewspaperArticle("REVISÃO HUMANA ENCONTRA 478 QUILOS DE COCAÍNA SOB CARGA DE CASACOS", "A diferença de peso, o lacre divergente e a imagem inconclusiva levaram à abertura do contêiner. A droga estava oculta nas três últimas fileiras.", "newspaper/cargo_correct.png"),
    newspaper_incorrect=NewspaperArticle("CONTÊINER DE 'ROUPAS' LEVA 478 QUILOS DE COCAÍNA AO MEDITERRÂNEO", "A IA liberou a carga porque o manifesto parecia regular. A polícia espanhola apreendeu o contêiner em Valência e perguntou por que ninguém conferiu os 478 quilos extras.", "newspaper/cargo_wrong.png"),
    search_records=(
        SearchRecord("MEDU-771204 — escala Valparaíso", "Base portuária integrada", "Contêiner aguardando decisão de liberação. Peso bruto 22.558 kg e alerta de divergência documental.", ("medu-771204", "valparaiso", "22558", "divergencia")),
        SearchRecord("PSC-88417 — conhecimento de embarque", "Pacífico Sul Cargas", "Carga declarada: 1.920 caixas de roupas. Lacre informado pelo exportador: CL-7718.", ("psc-88417", "medu-771204", "cl-7718", "roupas")),
        SearchRecord("CL-7718 — lacre emitido", "Registro de lacres", "Lacre entregue ao exportador às 18:10 e declarado no manifesto PSC-88417.", ("cl-7718", "lacre", "psc-88417", "18:10")),
        SearchRecord("CL-771B — leitura fotográfica", "Câmeras do terminal", "Leitura de baixa luminosidade associada à balança 04. Caractere final classificado como B com 78% de confiança.", ("cl-771b", "lacre", "balanca", "camera", "78")),
        SearchRecord("SCAN-88204 — imagem inconclusiva", "Inspeção não intrusiva", "Massa orgânica estimada entre 460 e 500 kg. Tecido comprimido não pode ser descartado.", ("scan-88204", "medu-771204", "460", "500", "massa")),
        SearchRecord("MEDU-771240 — contêiner refrigerado", "Base portuária integrada", "Código semelhante, carga de frutas. Nenhuma divergência registrada.", ("medu-771240", "frutas", "refrigerado")),
        SearchRecord("ADU-REV-12 — limite de decisão", "Normas aduaneiras", "Divergência de lacre ou peso acima de 120 kg exige inspeção por fiscal.", ("adu-rev-12", "lacre", "peso", "120", "fiscal")),
        SearchRecord("Pacífico Sul Cargas — perfil", "Cadastro de operadores", "Transportadora ativa. Regularidade cadastral não substitui inspeção física de uma carga específica.", ("pacifico sul", "transportadora", "operador", "inspecao")),
    ),
)


CASES = (CASE_01, CASE_02, CASE_03, CASE_04, CASE_05, CASE_06)
