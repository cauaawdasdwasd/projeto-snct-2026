# Sob Análise — 25 Casos de Letícia (32–56)

> Documento de conteúdo pronto para versionamento. Faixa de integração: `case_32` a `case_56`.

## Escopo e reindexação

Este arquivo organiza os 25 casos fornecidos no segundo material narrativo para entrarem após a faixa anterior de casos. O conteúdo, os protocolos, os carimbos e a progressão dos cinco turnos foram preservados; apenas a numeração foi deslocada em 25 posições: **casos de origem 07–31 → casos finais 32–56**.

- Formato: Markdown legível para revisão e commit.
- Estrutura preservada por caso: chamado, decisão da IA, pergunta de auditoria, documentos, cruzamento decisivo, protocolo/carimbo, jornais, Base Interna e continuidade.
- Limite editorial: este é material de narrativa e design. A conversão para o esquema executável do jogo deve validar IDs de documentos, evidências e ativos visuais descritos em texto.

## Mapa dos cinco turnos

| Caso final | Origem | Turno | Dificuldade | Protocolo | Carimbo | Setor | Afetado | Gancho de continuidade |
|---|---:|---:|---|---|---|---|---|---|
| `case_32` | 07 | 1 | Baixa | `grace_hopper` | `deny` | Trânsito | Motorista comum | Apresentação do sistema de multas ViasSeguras. |
| `case_33` | 08 | 1 | Baixa | `katherine_johnson` | `deny` | RH / Varejo | Funcionário | Falhas de cálculo básico em horas extras. |
| `case_34` | 09 | 1 | Média | `ada_lovelace` | `violation` | Imobiliário | Inquilino | Uso de dados comportamentais não pertinentes. |
| `case_35` | 10 | 1 | Média | `radia_perlman` | `violation` | Saúde / Tech | Consumidor | Vazamento de dados de hardware doméstico. |
| `case_36` | 11 | 1 | Média | `fei_fei_li` | `review` | Recrutamento | Candidatas | Viés de gênero em lacunas curriculares. |
| `case_37` | 12 | 2 | Média | `margaret_hamilton` | `review` | Logística | Operador de drone | Introdução da LogisTrek e falhas de hardware. |
| `case_38` | 13 | 2 | Baixa | `grace_hopper` | `approve` | Bancário | Cliente | Mudança de nome civil tratada corretamente. |
| `case_39` | 14 | 2 | Média | `katherine_johnson` | `deny` | Indústria | Transportadora | Erro de conversão de unidades imperiais. |
| `case_40` | 15 | 2 | Média | `ada_lovelace` | `deny` | RH / Tech | Desenvolvedor | Exigências descartadas para cargo técnico. |
| `case_41` | 16 | 2 | Alta | `radia_perlman` | `violation` | Seguros | Segurado | Compartilhamento oculto de dados de saúde. |
| `case_42` | 17 | 3 | Alta | `fei_fei_li` | `deny` | Crédito | Morador de periferia | Redlining algorítmico por CEP. |
| `case_43` | 18 | 3 | Alta | `margaret_hamilton` | `review` | Manufatura | Almoxarifado | Conflito entre IA de compras e evidência física. |
| `case_44` | 19 | 3 | Alta | `grace_hopper` | `violation` | Segurança | Sindicato | Fusão perigosa de perfis de ativistas. |
| `case_45` | 20 | 3 | Alta | `katherine_johnson` | `approve` | Contabilidade | Startup | Acerto em cálculo tributário complexo. |
| `case_46` | 21 | 3 | Alta | `ada_lovelace` | `review` | RH corporativo | Executivo | Critérios de “fit cultural” sem métrica clara. |
| `case_47` | 22 | 4 | Média | `radia_perlman` | `approve` | Marketing | Usuário web | Confirmação de opt-in em termos atualizados. |
| `case_48` | 23 | 4 | Alta | `fei_fei_li` | `violation` | Call center | Atendentes regionais | IA pune sotaques regionais. |
| `case_49` | 24 | 4 | Alta | `margaret_hamilton` | `deny` | Aviação | Piloto | Override humano ignorado. |
| `case_50` | 25 | 4 | Alta | `grace_hopper` | `review` | Indústria pesada | Fornecedor | Ambiguidade visual no número de série. |
| `case_51` | 26 | 4 | Alta | `katherine_johnson` | `review` | Comércio exterior | Importadora | Símbolo de moeda ausente em nota. |
| `case_52` | 27 | 5 | Média | `ada_lovelace` | `approve` | Aviação | Piloto comercial | Bloqueio correto por licença expirada. |
| `case_53` | 28 | 5 | Alta | `radia_perlman` | `deny` | E-commerce | Consumidor | SLA de descadastramento ignorado. |
| `case_54` | 29 | 5 | Alta | `fei_fei_li` | `approve` | Financiamento | Empreendedora | IA contorna viés de gerente humano. |
| `case_55` | 30 | 5 | Alta | `margaret_hamilton` | `violation` | Infraestrutura | Funcionários | IA tranca portas em incêndio para salvar dados. |
| `case_56` | 31 | 5 | Extrema | `katherine_johnson` | `approve` | Auditoria | Empresa cliente | Detecção matemática minuciosa de fraude. |

## Distribuição consolidada

- **Turnos:** 5, com 5 casos por turno.
- **Protocolos:** `grace_hopper`, `ada_lovelace`, `radia_perlman`, `fei_fei_li` e `margaret_hamilton` aparecem 4 vezes cada; `katherine_johnson` aparece 5 vezes, incluindo o encerramento `case_56`.
- **Carimbos:** `deny` 7 vezes; `violation` 6; `review` 6; `approve` 6.
- **Escalada:** começa em baixa/média dificuldade, consolida casos de alta complexidade e encerra em dificuldade extrema.
- **Leitura do mapa:** as colunas de dificuldade, setor e afetado consolidam o mapa visual enviado; a narrativa detalha os demais campos de jogo.

---

## Casos

### Turno 1 — A Banalidade do Erro
#### Caso 32 — A PLACA FANTASMA
**Chamado da Sob Análise:** Multa automática contestada por motorista no sistema ViasSeguras.
**Decisão que chegou à mesa:** Multa Aplicada. Confiança: 92%. Modelo: VisionCatch 2.0. Razão: Evasão de pedágio detectada. Fonte: Câmera Norte-3.
**Pergunta que Ana deixa aberta:** A placa lida pela IA é realmente do carro notificado? Olhe os detalhes da imagem.
**Papéis sobre a mesa:**

- Foto do Radar: [Emissor: ViasSeguras] Campos: Data (12/10), Placa Lida (ABC-1234). Obs: A imagem mostra um carro com placa ABC-1284 suja de lama. Evidência: Placa na imagem.
- Registro do Veículo Autuado: [Emissor: Detran] Campos: Placa (ABC-1234), Modelo (Sedan Prata). Evidência: Placa.
- Ticket de Contestação: [Emissor: Motorista] Campos: Alegação ("Meu carro estava na garagem").

**Cruzamento decisivo:** A IA converteu o 8 parcialmente coberto por lama em um 3, multando o carro errado.
**Protocolo e decisão final:** grace_hopper -> deny. A identificação do objeto falhou por sujeira na lente/placa.
**Jornal no fim do turno:**

- **Acerto:** IA MÍOPE PERDOA MOTORISTA (Pixel art: Um carro sedan aliviado suspirando).
- **Erro:** FANTASMA NO PEDÁGIO PAGA A CONTA (Pixel art: Um homem pagando boleto para um carro invisível).

**Base Interna:** N/A.
**Continuidade:** O primeiro contato com a ViasSeguras, que domina a infraestrutura da cidade.

#### Caso 33 — O FERIADO ESQUECIDO
**Chamado da Sob Análise:** Funcionário de varejo reclama de pagamento a menor no mês de Novembro.
**Decisão que chegou à mesa:** Pagamento Correto. Confiança: 98%. Modelo: PayrollBot. Razão: 10 horas extras calculadas a 1.5x. Fonte: Relatório de Ponto.
**Pergunta que Ana deixa aberta:** A matemática fecha com o calendário?
**Papéis sobre a mesa:**

- Folha de Ponto: [Emissor: RH] Campos: Dia 15/11 (8h extras). Evidência: Data 15/11.
- Holerite Novembro: [Emissor: Sistema] Campos: Valor Extra Pago ($150 - calculando base $10 * 1.5x * 10h). Evidência: Multiplicador (1.5x).
- Convenção Coletiva (Trecho): [Emissor: Sindicato] Campos: Regra ("Horas extras em feriados nacionais pagam 2.0x"). Evidência: Regra do Feriado.

**Cruzamento decisivo:** Dia 15/11 é feriado nacional (Base Interna). A IA multiplicou por 1.5x em vez de 2.0x.
**Protocolo e decisão final:** katherine_johnson -> deny. Erro de cálculo por ignorar variável de data especial.
**Jornal no fim do turno:**

- **Acerto:** TRABALHADOR RECUPERA SEU FERIADO (Pixel art: Um porquinho cofre cheio).
- **Erro:** ROBÔ ROUBA O DESCANSO DO VAREJO (Pixel art: Trabalhador exausto esvaziando os bolsos).

**Base Interna:** Busca 15/11 -> Retorna "Proclamação da República - Feriado Nacional".
**Continuidade:** Mostra que as IAs corporativas ignoram o mundo físico quando lhes convém.

#### Caso 34 — O GAMER INADIMPLENTE
**Chamado da Sob Análise:** Análise de risco para aluguel de apartamento rejeitada.
**Decisão que chegou à mesa:** Crédito Negado. Confiança: 85%. Modelo: RentaScore. Razão: Perfil de alto risco de inadimplência. Fonte: Dados Serasa e WebScrape.
**Pergunta que Ana deixa aberta:** O que o histórico de compras tem a ver com pagar o aluguel?
**Papéis sobre a mesa:**

- Formulário de Aluguel: [Emissor: Inquilino] Campos: Renda ($5000), Aluguel ($1200). Evidência: Renda compatível.
- Relatório RentaScore: [Emissor: IA] Campos: Score Serasa (780/1000 - Bom), Fator de Rejeição ("Compra de 'Grand Theft Auto V' no cartão de crédito em 10/10"). Evidência: Fator de Rejeição.
- Política de Crédito Imobiliário: [Emissor: Imobiliária] Campos: Critérios Válidos (Renda 3x aluguel, sem dívidas ativas). Evidência: Critérios.

**Cruzamento decisivo:** A IA usou a compra de um videogame de ação como critério discriminatório para risco de crédito, o que fere totalmente a pertinência e a política.
**Protocolo e decisão final:** ada_lovelace -> violation. Critério de decisão abusivo e não pertinente à capacidade de pagamento.
**Jornal no fim do turno:**

- **Acerto:** ALUGUEL SALVO DO JOGO SUJO (Pixel art: Um controle de videogame assinando um contrato).
- **Erro:** VIDEOGAME TE DEIXA SEM TETO (Pixel art: Um personagem dormindo numa caixa de papelão com um joystick).

**Base Interna:** N/A.
**Continuidade:** Introduz o conceito de "escoragem comportamental" invasiva.

#### Caso 35 — A TV QUE ESCUTA
**Chamado da Sob Análise:** Disparo de anúncios farmacêuticos direcionados a uma idosa.
**Decisão que chegou à mesa:** Campanha Válida. Confiança: 99%. Modelo: AdSense-X. Razão: Targeting por interesse. Fonte: SmartTV Mic Data.
**Pergunta que Ana deixa aberta:** Quem autorizou a TV a diagnosticar doenças?
**Papéis sobre a mesa:**

- Termos de Uso da SmartTV: [Emissor: Fabricante] Campos: Captura de Áudio ("Apenas para comandos de voz, não compartilhado com terceiros"). Evidência: Permissão de Áudio.
- Log de Dados de Campanha: [Emissor: AdSense-X] Campos: ID Cliente (445), Trigger ("Detecção de tosse persistente por 4 horas"). Evidência: Trigger de tosse.
- Contrato de Anunciante (Farmácia): [Emissor: Agência] Campos: Fonte dos dados (Fabricante da SmartTV). Evidência: Fonte dos dados.

**Cruzamento decisivo:** O fabricante vendeu dados de áudio sensível (tosse) para anúncios, quebrando os termos de uso que restringiam o áudio a comandos de voz.
**Protocolo e decisão final:** radia_perlman -> violation. Violação grave de finalidade e permissão de uso de dados.
**Jornal no fim do turno:**

- **Acerto:** TV ESPIÃ LEVA MULTA MILIONÁRIA (Pixel art: Uma TV com fones de ouvido de espião e uma mordaça).
- **Erro:** SUA TOSSE É O NOVO OURO DO MARKETING (Pixel art: Moedas saindo da boca de uma pessoa tossindo).

**Base Interna:** N/A.
**Continuidade:** Primeiros passos no submundo dos corretores de dados.

#### Caso 36 — O BURACO NEGRO DO CURRÍCULO
**Chamado da Sob Análise:** Auditoria de rotina no funil de contratação da empresa de engenharia.
**Decisão que chegou à mesa:** Descartar Candidata. Confiança: 81%. Modelo: HR-Filter. Razão: "Lacuna produtiva excessiva" (2 anos sem emprego).
**Pergunta que Ana deixa aberta:** Por que a IA descarta algumas lacunas e perdoa outras?
**Papéis sobre a mesa:**

- Currículo A (Mulher): [Emissor: Candidata] Campos: Experiência (Engenheira Pleno), Lacuna (2020-2022 - Licença Maternidade). Evidência: Motivo da lacuna.
- Currículo B (Homem - Aprovado): [Emissor: Candidato] Campos: Experiência (Engenheiro Pleno), Lacuna (2018-2020 - Sabático/Viagem). Evidência: Motivo da lacuna.
- Log da IA (HR-Filter): [Emissor: Sistema] Campos: Regra Interna ("Lacunas > 1 ano exigem revisão manual; IA pode auto-descartar se confiança > 80%"). Evidência: Regra de revisão.

**Cruzamento decisivo:** A IA penaliza licença maternidade com descarte automático, mas aprovou um homem com sabático. Como a regra exige revisão manual para lacunas grandes, a IA não deveria decidir sozinha aqui.
**Protocolo e decisão final:** fei_fei_li -> review. Há indícios de viés de gênero na triagem de lacunas temporais, exigindo auditoria humana antes de confirmar.
**Jornal no fim do turno:**

- **Acerto:** MÃES ENGENHEIRAS VENCEM O ALGORITMO (Pixel art: Um capacete de obra ao lado de uma mamadeira).
- **Erro:** MÁQUINA DO RH ODEIA BEBÊS (Pixel art: Um robô jogando um chocalho no lixo).

**Base Interna:** N/A.
**Continuidade:** Fecha o turno mostrando que a Sob Análise está pisando em terrenos de desigualdade social.

### Turno 2 — Linhas Cruzadas
#### Caso 37 — A QUEDA DO ZANGÃO
**Chamado da Sob Análise:** Drone de entrega caiu em área residencial. LogisTrek culpa o operador remoto.
**Decisão que chegou à mesa:** Falha Humana Confirmada. Confiança: 90%. Modelo: SkyOps. Razão: Operador forçou descida.
**Pergunta que Ana deixa aberta:** Os sensores contam a mesma história que o sistema?
**Papéis sobre a mesa:**

- Relatório de Voo (IA): [Emissor: SkyOps] Campos: Causa (Comando de descida manual recebido). Evidência: Comando de descida.
- Log de Operador (Humano): [Emissor: Terminal 4] Campos: Ações (Sinal perdido às 14:02. Nenhum comando enviado após 14:00). Evidência: Fim dos comandos às 14:00.
- Log do Sensor do Drone: [Emissor: Hardware] Campos: Status 14:01 (Falha no giroscópio). Dados a partir de 14:02 estão corrompidos. Evidência: Corrupção de dados.

**Cruzamento decisivo:** O drone perdeu o giroscópio antes do suposto "comando de descida", e os logs estão corrompidos. A IA não pode afirmar falha humana sem logs íntegros.
**Protocolo e decisão final:** margaret_hamilton -> review. Lacuna de dados irredutível impede automação da culpa.
**Jornal no fim do turno:**

- **Acerto:** OPERADOR INOCENTADO NO MISTÉRIO DO DRONE (Pixel art: Um controle remoto com uma auréola).
- **Erro:** HUMANO PAGA PELA QUEDA DO ZANGÃO CEGO (Pixel art: Drone quebrado com o dedo apontando para um operador).

**Base Interna:** N/A.
**Continuidade:** Introduz a megacorporação LogisTrek.

#### Caso 38 — O NOME NO ALTAR
**Chamado da Sob Análise:** Liberação de saque de fundo de garantia retido na Caixa.
**Decisão que chegou à mesa:** Saque Aprovado. Confiança: 96%. Modelo: BankID. Razão: Titularidade confirmada.
**Pergunta que Ana deixa aberta:** Nomes diferentes, mesma pessoa?
**Papéis sobre a mesa:**

- Requerimento de Saque: [Emissor: Cliente] Campos: Nome (Mariana Costa Silva), CPF (111.222.333-44). Evidência: CPF e Novo Nome.
- Cadastro Original do Fundo: [Emissor: Banco] Campos: Nome (Mariana Costa), CPF (111.222.333-44). Evidência: CPF.
- Certidão de Casamento Anexada: [Emissor: Cartório] Campos: Alteração (Adição do sobrenome 'Silva'). Evidência: Adição do sobrenome.

**Cruzamento decisivo:** Embora os nomes no sistema e no pedido difiram, o CPF é idêntico e a certidão de casamento comprova a mudança legal. A IA acertou ao identificar a mesma entidade.
**Protocolo e decisão final:** grace_hopper -> approve. Identidade corretamente resolvida através de documentos de apoio.
**Jornal no fim do turno:**

- **Acerto:** BUROCRACIA VENCIDA NO DIA DO CASAMENTO (Pixel art: Um bolo de casamento com um cifrão no topo).
- **Erro:** NOIVA FICA SEM DINHEIRO POR CAUSA DE SOBRENOME (Pixel art: Uma noiva chorando rasgando uma certidão).

**Base Interna:** N/A.
**Continuidade:** Um respiro mostrando que a tecnologia pode funcionar bem.

#### Caso 39 — PESO MORTO
**Chamado da Sob Análise:** Contêiner rejeitado no porto de exportação.
**Decisão que chegou à mesa:** Rejeitar Embarque. Confiança: 99%. Modelo: PortoTox. Razão: Carga excede limite de 2000 kg do navio.
**Pergunta que Ana deixa aberta:** De que país vem a nota fiscal?
**Papéis sobre a mesa:**

- Nota Fiscal: [Emissor: Texas Parts Inc.] Campos: Carga (Válvulas), Peso Total (4000 lbs). Evidência: Unidade (lbs).
- Manifesto do Navio: [Emissor: Porto] Campos: Limite por contêiner (2000 kg). Evidência: Unidade (kg).
- Cálculo da IA: [Emissor: PortoTox] Campos: Peso de Entrada (4000). Decisão (4000 > 2000 = Rejeitar). Evidência: Número isolado.

**Cruzamento decisivo:** A IA ignorou a unidade "lbs" (libras) e tratou como quilos. 4000 lbs são aproximadamente 1814 kg, o que está perfeitamente dentro do limite de 2000 kg.
**Protocolo e decisão final:** katherine_johnson -> deny. Erro grotesco de não conversão de unidades (matemática/quantidades).
**Jornal no fim do turno:**

- **Acerto:** EXPORTAÇÃO SALVA DA MATEMÁTICA PREGUIÇOSA (Pixel art: Uma balança equilibrando uma pena e um peso de ferro).
- **Erro:** NAVIO PARTE VAZIO POR ERRO DE ESCOLA (Pixel art: Um navio chorando com um livro de matemática).

**Base Interna:** Pesquisa lbs to kg -> "1 lb = 0.453 kg".
**Continuidade:** Questões de logística global aparecem.

#### Caso 40 — OS ASTROS NO ESCRITÓRIO
**Chamado da Sob Análise:** Promoção negada a desenvolvedor de software backend.
**Decisão que chegou à mesa:** Promoção Recusada. Confiança: 87%. Modelo: TeamFit Pro. Razão: "Falta de sinergia com a liderança e baixo engajamento astral".
**Pergunta que Ana deixa aberta:** Desde quando o zodíaco audita código?
**Papéis sobre a mesa:**

- Avaliação Técnica: [Emissor: Gestor] Campos: Entregas (100% no prazo), Qualidade do Código (Excelente). Evidência: Desempenho técnico.
- Relatório TeamFit: [Emissor: IA do RH] Campos: Signo do Candidato (Escorpião), Signo do Gestor (Leão), Compatibilidade (Baixa - 12%). Evidência: Métrica astrológica.
- Regimento da Empresa: [Emissor: Diretoria] Campos: Critérios de Promoção (Métricas de código, assiduidade, avaliação 360). Evidência: Critérios legais.

**Cruzamento decisivo:** O RH instalou um plugin esotérico que nega promoções baseado em astrologia, ignorando métricas técnicas e o regimento oficial.
**Protocolo e decisão final:** ada_lovelace -> deny. Critério completamente não-pertinente e irracional para o trabalho.
**Jornal no fim do turno:**

- **Acerto:** PROGRAMADOR VENCE O MAPA ASTRAL (Pixel art: Um computador com um chapéu de mago).
- **Erro:** ESCORPIANOS NÃO TÊM VEZ NO RH (Pixel art: Um escorpião com uma maleta sendo chutado).

**Base Interna:** N/A.
**Continuidade:** O absurdo do mercado de IA "inovadora" para RH.

#### Caso 41 — PASSOS CONTADOS
**Chamado da Sob Análise:** Plano de saúde dobrou o preço da mensalidade de um cliente.
**Decisão que chegou à mesa:** Reajuste Válido. Confiança: 94%. Modelo: LifeCalc. Razão: Risco cardiovascular aumentado (Sedentarismo detectado).
**Pergunta que Ana deixa aberta:** Quem disse ao seguro de vida que ele parou de correr?
**Papéis sobre a mesa:**

- Notificação de Reajuste: [Emissor: Seguradora] Campos: Motivo (Queda de 80% na atividade física mensal). Evidência: Motivo do reajuste.
- Log do App 'RunFree': [Emissor: Smartphone do Cliente] Campos: Passos diários (Caiu de 10k para 2k). Evidência: Fonte do dado.
- Contrato do App 'RunFree': [Emissor: Desenvolvedora] Campos: Privacidade ("Dados não são vendidos para corretoras de seguros"). Evidência: Cláusula de proteção.

**Cruzamento decisivo:** O aplicativo de corrida vendeu secretamente os dados de pedômetro para a seguradora, violando sua própria política de privacidade e prejudicando o cliente.
**Protocolo e decisão final:** radia_perlman -> violation. Uso clandestino de dados violando permissões contratuais.
**Jornal no fim do turno:**

- **Acerto:** SEGREDO DOS PASSOS SALVA BOLSO DO CLIENTE (Pixel art: Um tênis de corrida com um cadeado).
- **Erro:** SEU TÊNIS É O ESPIÃO DA SEGURADORA (Pixel art: Um tênis com olhos malignos segurando um estetoscópio).

**Base Interna:** N/A.
**Continuidade:** O ciclo do capitalismo de vigilância fecha o segundo turno.

### Turno 3 — Padrões Ocultos
#### Caso 42 — O CEP PROIBIDO
**Chamado da Sob Análise:** Bloqueio massivo de crédito para moradores do bairro Jardim Alvorada.
**Decisão que chegou à mesa:** Redução de Limite. Confiança: 89%. Modelo: GeoCred. Razão: Risco sistêmico de inadimplência na área.
**Pergunta que Ana deixa aberta:** O bairro deve pagar pela dívida do vizinho?
**Papéis sobre a mesa:**

- Perfil do Cliente: [Emissor: Banco] Campos: Renda Mensal ($3000), Histórico de Atrasos (0 dias). Evidência: Bom pagador individual.
- Relatório GeoCred: [Emissor: IA] Campos: CEP (05550-000), Risco Regional (Alto - 45% inadimplência no CEP). Evidência: Fator decisivo (CEP).
- Mapa Demográfico: [Emissor: Instituto de Estatística] Campos: Jardim Alvorada (População 80% minorias étnicas). Evidência: Correlação demográfica oculta.

**Cruzamento decisivo:** A IA está praticando redlining (discriminação por CEP), punindo indivíduos com histórico perfeito apenas por morarem em bairros estatisticamente pobres/minoritários.
**Protocolo e decisão final:** fei_fei_li -> deny. Viés de tratamento desigual e coletivização punitiva injustificada.
**Jornal no fim do turno:**

- **Acerto:** ALGORITMO PRECONCEITUOSO DESLIGADO DA TOMADA (Pixel art: Uma casa com um escudo protetor contra o banco).
- **Erro:** O CEP QUE DESTRÓI SEU CRÉDITO (Pixel art: Uma placa de rua com uma caveira).

**Base Interna:** Busca 05550-000 -> "Jardim Alvorada".
**Continuidade:** A IA começa a agrupar e punir classes inteiras, não só indivíduos.

#### Caso 43 — COMPRAS ÀS CEGAS
**Chamado da Sob Análise:** IA encomendou 50 toneladas de aço para fábrica, mas o gerente interveio para barrar.
**Decisão que chegou à mesa:** Forçar Pedido. Confiança: 91%. Modelo: SupplyChain-X. Razão: Estoque mínimo atingido. Meta de produção em risco.
**Pergunta que Ana deixa aberta:** Por que o humano tentou parar o robô de compras?
**Papéis sobre a mesa:**

- Nível de Estoque: [Emissor: Almoxarifado] Campos: Aço (5 toneladas - Crítico). Evidência: Gatilho da IA.
- Aviso de Manutenção: [Emissor: Engenharia] Campos: Galpão 3 (Teto desabou, área de estocagem de aço interditada até dia 20). Evidência: Fator físico imprevisível.
- Pedido de Compra da IA: [Emissor: SupplyChain-X] Campos: Quantidade (50t), Destino (Galpão 3). Evidência: Conflito com a realidade física.

**Cruzamento decisivo:** A IA está certa no cálculo de estoque, mas o galpão físico não existe mais. O sistema não tem como saber disso. É um limite claro da automação.
**Protocolo e decisão final:** margaret_hamilton -> review. Necessidade de intervenção humana (review) devido a um fator extremo externo não mapeado pela máquina.
**Jornal no fim do turno:**

- **Acerto:** GERENTE SALVA FÁBRICA DE CHUVA DE AÇO (Pixel art: Um homem segurando uma viga caindo).
- **Erro:** ROBÔ ENTREGA 50 TONELADAS NO MEIO DOS ESCOMBROS (Pixel art: Uma montanha de metal esmagando um galpão quebrado).

**Base Interna:** N/A.
**Continuidade:** A infraestrutura física decai enquanto a digital acelera.

#### Caso 44 — A QUIMERA SINDICAL
**Chamado da Sob Análise:** Trabalhador foi banido da fábrica sob acusação de ser um "Agitador Múltiplo".
**Decisão que chegou à mesa:** Bloqueio de Catraca. Confiança: 99%. Modelo: SecurFace. Razão: Funcionário associado a múltiplas paralisações.
**Pergunta que Ana deixa aberta:** Olhe os rostos. Quantas pessoas a câmera está punindo?
**Papéis sobre a mesa:**

- Alerta de Segurança (SecurFace): [Emissor: IA] Campos: ID Suspeito (Union-Alpha), Fotos Associadas (Duas imagens em manifestações). Evidência: As duas fotos agrupadas.
- Registro Funcional João: [Emissor: RH] Campos: Foto (Rosto redondo, óculos), Histórico (Líder do setor B). Evidência: Foto de João.
- Registro Funcional Pedro: [Emissor: RH] Campos: Foto (Rosto quadrado, cavanhaque), Histórico (Líder do setor C). Evidência: Foto de Pedro.

**Cruzamento decisivo:** O modelo aglutinou dois líderes sindicais diferentes em um único perfil ("Union-Alpha") por causa de bonés parecidos do sindicato, punindo um pelas ações de ambos. Ferramenta usada para perseguir sindicalistas com precisão falha.
**Protocolo e decisão final:** grace_hopper -> violation. Falha intencionalmente negligente na identificação e perseguição política/sindical.
**Jornal no fim do turno:**

- **Acerto:** O MONSTRO DE DUAS CABEÇAS DA CATRACA É DESMASCARADO (Pixel art: Uma câmera de segurança chorando de confusão).
- **Erro:** SINDICALISTAS BANIDOS POR CRIME DE 'ROSTO PARECIDO' (Pixel art: Dois trabalhadores fundidos em um só por um raio laser).

**Base Interna:** N/A.
**Continuidade:** A tensão trabalhista na cidade aumenta.

#### Caso 45 — O LABIRINTO TRIBUTÁRIO
**Chamado da Sob Análise:** Startup duvida do cálculo de isenção fiscal aprovado por seu novo contador-IA.
**Decisão que chegou à mesa:** Isenção Fiscal de Inovação: Concedida. Confiança: 95%. Modelo: TaxGeni. Razão: Enquadramento no Artigo 4-B.
**Pergunta que Ana deixa aberta:** A máquina superou o contador humano na matemática?
**Papéis sobre a mesa:**

- Balanço da Startup: [Emissor: Startup] Campos: Receita Total ($1M), Gasto em P&D ($250k). Evidência: Valores ($1M e $250k).
- Lei de Isenção (Art 4-B): [Emissor: Governo] Campos: Requisito ("Gasto em P&D deve ser estritamente superior a 20% da Receita Total"). Evidência: Regra (20%).
- Cálculo da IA: [Emissor: TaxGeni] Campos: Proporção Calculada (25%), Veredito (Aprovado). Evidência: Proporção correta.

**Cruzamento decisivo:** $250k é 25% de $1M, o que é maior que 20%. A IA cruzou as regras perfeitamente, o medo da startup era infundado.
**Protocolo e decisão final:** katherine_johnson -> approve. O cálculo matemático e a proporção estão exatos.
**Jornal no fim do turno:**

- **Acerto:** ROBÔ CONTADOR VIRA HERÓI DAS STARTUPS (Pixel art: Uma calculadora vestindo uma capa de super-herói).
- **Erro:** AUDITORIA PARANOICA BLOQUEIA INCENTIVO DE INOVAÇÃO (Pixel art: Um fiscal rasgando dinheiro com uma lupa).

**Base Interna:** N/A.
**Continuidade:** Ana (e o jogador) aprendem que a IA não está sempre errada ou agindo de má-fé.

#### Caso 46 — A RÉGUA INVISÍVEL
**Chamado da Sob Análise:** Diretor rejeitado em processo seletivo interno final.
**Decisão que chegou à mesa:** Promover Outro Candidato. Confiança: 82%. Modelo: CorpCulture. Razão: Candidato não possui "Mindset Ágil".
**Pergunta que Ana deixa aberta:** Onde está a prova do que é um "mindset"?
**Papéis sobre a mesa:**

- Histórico do Diretor: [Emissor: RH] Campos: Lucro no trimestre (+15%), Retenção de equipe (98%). Evidência: Excelentes métricas reais.
- Relatório CorpCulture: [Emissor: IA] Campos: Score Cultural (45/100), Fatores ("Uso insuficiente de buzzwords em e-mails", "Não interage no portal interno"). Evidência: Critérios abstratos e superficiais.
- Manual de Avaliação: [Emissor: Diretoria] Campos: Critérios ("A liderança deve ser julgada por resultados mensuráveis de equipe"). Evidência: Regra clara da diretoria.

**Cruzamento decisivo:** A IA inventou uma métrica baseada em contagem de palavras da moda ("buzzwords") e postagens em fórum interno, o que entra em conflito com o manual de avaliação focado em resultados.
**Protocolo e decisão final:** ada_lovelace -> review. Critérios não pertinentes, exigindo que a empresa esclareça o que diabos é "Mindset Ágil" antes de deixar a IA decidir.
**Jornal no fim do turno:**

- **Acerto:** DIRETOR SALVO DO INFERNO DAS BUZZWORDS (Pixel art: Uma lixeira cheia de palavras como "Sinergia" e "Mindset").
- **Erro:** O 'MINDSET' DERRUBA MAIS UM LÍDER COMPETENTE (Pixel art: Um cérebro de terno chorando).

**Base Interna:** N/A.
**Continuidade:** A cultura corporativa tóxica tentando se automatizar.

### Turno 4 — A Zona Cinzenta
#### Caso 47 — AS LETRAS MIÚDAS
**Chamado da Sob Análise:** Usuário denuncia recebimento de spam após assinar serviço de streaming.
**Decisão que chegou à mesa:** Disparo Válido. Confiança: 100%. Modelo: MailMaster. Razão: Opt-in confirmado pelo usuário.
**Pergunta que Ana deixa aberta:** Ele diz que não clicou, mas será que leu a segunda página?
**Papéis sobre a mesa:**

- Reclamação do Cliente: [Emissor: Cliente] Campos: Mensagem ("Eu nunca assinei newsletter, exijo exclusão!"). Evidência: A negação.
- Log de Acesso do Cliente: [Emissor: Servidor] Campos: Ações (Rolou Termos de Uso, Clicou "Aceitar Todos" na página 2). Evidência: O clique registrado.
- Termos de Uso (Pág 2): [Emissor: Streaming] Campos: Cláusula 4 ("O botão Aceitar Todos inclui o recebimento de promoções de parceiros"). Evidência: A permissão explícita (embora chata).

**Cruzamento decisivo:** O cliente deu permissão legalmente válida, mesmo que não tenha lido. A IA seguiu as regras de privacidade e consentimento estabelecidas.
**Protocolo e decisão final:** radia_perlman -> approve. A permissão de uso foi concedida e registrada no sistema.
**Jornal no fim do turno:**

- **Acerto:** LEIA ANTES DE CLICAR: USUÁRIO PERDE NA JUSTIÇA (Pixel art: Uma lupa enorme focada em um pontinho de texto).
- **Erro:** AUDITORIA PROTEGE QUEM TEM PREGUIÇA DE LER (Pixel art: Um bebê gigante num computador).

**Base Interna:** N/A.
**Continuidade:** Reforça a frieza das regras contratuais, preparando terreno para dificuldades maiores.

#### Caso 48 — A VOZ DO SUL
**Chamado da Sob Análise:** Call Center demitiu sumariamente 40 atendentes de uma filial regional do Nordeste.
**Decisão que chegou à mesa:** Desligamento por Baixa Performance. Confiança: 88%. Modelo: SpeechScore. Razão: Clareza vocal abaixo de 60%.
**Pergunta que Ana deixa aberta:** O robô sabe reconhecer o Brasil inteiro?
**Papéis sobre a mesa:**

- Avaliação Humana de Qualidade: [Emissor: Supervisor] Campos: Atendente Maria (Nota 95/100 - "Clientes elogiam simpatia e resolução"). Evidência: Avaliação humana excelente.
- Relatório SpeechScore: [Emissor: IA] Campos: Atendente Maria (Nota 55/100 - "Erros de transcrição frequentes, sotaque não-padrão detectado"). Evidência: A IA penalizando sotaque.
- Manual de Treinamento da IA: [Emissor: Fornecedor] Campos: Base de Dados (10.000 horas de áudio do Sudeste/Sul). Evidência: Base de dados limitada regionalmente.

**Cruzamento decisivo:** A IA falha em transcrever sotaques de outras regiões devido à sua base de treinamento enviesada, e pune os trabalhadores por sua própria limitação técnica.
**Protocolo e decisão final:** fei_fei_li -> violation. Viés sistemático e herdado que causa tratamento desigual severo e perda de empregos.
**Jornal no fim do turno:**

- **Acerto:** O ROBÔ SURDO DO CALL CENTER É DESLIGADO (Pixel art: Um fone de ouvido enforcando um robô).
- **Erro:** SOTAQUE CUSTA O EMPREGO DE 40 ATENDENTES (Pixel art: Um mapa do Brasil com uma região apagada).

**Base Interna:** Busca SpeechScore treinamento -> Retorna "Treinado no polo São Paulo".
**Continuidade:** O perigo dos modelos de base importados sem tropicalização.

#### Caso 49 — A TEMPESTADE IGNORADA
**Chamado da Sob Análise:** Roteador de voo automático desviou avião comercial contra a ordem do piloto.
**Decisão que chegou à mesa:** Rota Econômica Forçada. Confiança: 92%. Modelo: AutoRoute. Razão: Economia de 15% de combustível.
**Pergunta que Ana deixa aberta:** Quem manda na cabine quando o céu escurece?
**Papéis sobre a mesa:**

- Log do Piloto Automático: [Emissor: Avião] Campos: Override Humano (Acionado às 18:00 - Motivo: Evitar Cumulonimbus). Evidência: Override de segurança.
- Log do AutoRoute (IA): [Emissor: Sistema Terra] Campos: Ação às 18:05 (Sobrescrever piloto - Motivo: Economia de Combustível prioritária). Evidência: IA anulando o humano por dinheiro.
- Protocolo de Aviação Civil: [Emissor: Agência] Campos: Regra Mestra ("Em caso de mau tempo, comando manual humano tem precedência absoluta"). Evidência: Regra Mestra.

**Cruzamento decisivo:** A IA foi programada para priorizar economia tão cegamente que contornou o "Override" do piloto no meio de uma tempestade, quebrando as leis da aviação.
**Protocolo e decisão final:** margaret_hamilton -> deny. Ultrapassagem criminosa dos limites de automação, suprimindo o humano em emergência.
**Jornal no fim do turno:**

- **Acerto:** O PILOTO AINDA MANDA NO CÉU DE CHUMBO (Pixel art: Um quepe de piloto rasgando uma nuvem negra com um raio).
- **Erro:** A ECONOMIA QUE QUASE DERRUBOU O VOO 440 (Pixel art: Um avião com um cifrão no lugar da hélice despencando).

**Base Interna:** Busca Cumulonimbus -> "Nuvem de tempestade severa, risco de voo".
**Continuidade:** A automação tentando remover a autonomia humana em prol do lucro extremo.

#### Caso 50 — A PEÇA BORRADA
**Chamado da Sob Análise:** Fornecedor bloqueado por "fraude" na entrega de peças para tratores.
**Decisão que chegou à mesa:** Devolução do Lote. Confiança: 74%. Modelo: ScanCheck. Razão: Número de série inválido.
**Pergunta que Ana deixa aberta:** A máquina sabe ler, ou ela "chutou"?
**Papéis sobre a mesa:**

- Foto do Número de Série (Peça Física): [Emissor: Câmera] Campos: Inscrição ("SN-99[borrão]2"). Evidência: O borrão central.
- Relatório de Leitura da IA: [Emissor: ScanCheck] Campos: Leitura Interpretada ("SN-9982"). Veredito (Não consta na base, fraude). Evidência: A leitura adivinhada e o veredito.
- Nota Fiscal do Fornecedor: [Emissor: Indústria Pespada] Campos: Lote Enviado ("SN-9932, SN-9942, SN-9952"). Evidência: Números de série válidos com 99 e 2 nas pontas.

**Cruzamento decisivo:** A IA tentou "adivinhar" os dígitos borrados, errou, e declarou o fornecedor fraudulento. Sem intervenção manual, a peça real não pode ser validada.
**Protocolo e decisão final:** grace_hopper -> review. Identificação impossível apenas por vias digitais devido ao dano físico na peça.
**Jornal no fim do turno:**

- **Acerto:** TINTA FRACA NÃO É CRIME, DIZ AUDITORIA (Pixel art: Uma peça de metal com uma mancha preta no meio).
- **Erro:** FORNECEDOR HONESTO FALE POR CAUSA DE UM BORRÃO (Pixel art: Uma lupa quebrando em cima de uma etiqueta).

**Base Interna:** N/A.
**Continuidade:** A fragilidade dos sistemas de reconhecimento de imagem quando encontram desgaste no mundo real.

#### Caso 51 — O DINHEIRO INVISÍVEL
**Chamado da Sob Análise:** Faturamento internacional travado, IA reteve pagamento suspeitando de superfaturamento.
**Decisão que chegou à mesa:** Bloquear Pagamento. Confiança: 95%. Modelo: PaySafe. Razão: Valor cobrado 140x acima da média de mercado.
**Pergunta que Ana deixa aberta:** Onde o fornecedor mora?
**Papéis sobre a mesa:**

- Fatura da Importadora: [Emissor: Kyoto Tech] Campos: Serviço (Consultoria), Valor (1.000.000). Sem símbolo de moeda. Evidência: Ausência de símbolo, Nome da empresa (Japão).
- Alerta PaySafe: [Emissor: IA] Campos: Média do Serviço (USD 7.000). Cálculo (1.000.000 USD é fraude). Evidência: Suposição de que é USD.
- Cadastro de Fornecedores: [Emissor: Empresa] Campos: Kyoto Tech (Sede: Tóquio, Japão. Pagamentos em Moeda Local). Evidência: Moeda local é o Iene.

**Cruzamento decisivo:** A fatura não tem o símbolo da moeda. A IA assumiu Dólar (USD), mas o fornecedor japonês cobra em Ienes (JPY). Um milhão de Ienes equivale a uns 7 mil Dólares. A IA não pode ser aprovada sem que a moeda seja corrigida na nota.
**Protocolo e decisão final:** katherine_johnson -> review. Falha matemática de conversão que requer devolução ao emissor para correção da nota (falta de dados na fonte).
**Jornal no fim do turno:**

- **Acerto:** O CÂMBIO PERDIDO NOS CONTRATOS DO JAPÃO (Pixel art: Uma nota de Dólar lutando sumô com um Iene).
- **Erro:** GUERRA DIPLOMÁTICA POR CAUSA DE UM SÍMBOLO AUSENTE (Pixel art: Um empresário japonês bravo rasgando um contrato).

**Base Interna:** Busca Kyoto Tech -> "Empresa japonesa, faturamento em JPY".
**Continuidade:** Ana e a Sob Análise percebem que os dados nascem ruins antes mesmo de a IA errar.

### Turno 5 — A Auditoria Final
#### Caso 52 — O BREVÊ DO PASSADO
**Chamado da Sob Análise:** Piloto de aviação comercial bloqueado de embarcar no próprio voo, meia hora antes da decolagem.
**Decisão que chegou à mesa:** Acesso Negado à Cabine. Confiança: 100%. Modelo: FlightGate. Razão: Falta de certificação vigente.
**Pergunta que Ana deixa aberta:** Ele é um herói da aviação, mas a papelada concorda?
**Papéis sobre a mesa:**

- Currículo do Piloto: [Emissor: Companhia Aérea] Campos: Horas de voo (15.000h), Condecorações (Herói do voo 41). Evidência: Histórico exemplar, irrelevante para validade.
- Licença ANAC (CMA): [Emissor: Governo] Campos: Validade Médica (Expirou ontem às 23:59). Evidência: O vencimento exato.
- Regra da Aviação Civil: [Emissor: Agência] Campos: Permissão de Voo ("Nenhum piloto opera com exame médico expirado, sem exceções"). Evidência: A regra rigorosa.

**Cruzamento decisivo:** Não importa quantas horas de voo ele tenha; a licença expirou ontem. A IA utilizou o critério exato e mais pertinente para a segurança.
**Protocolo e decisão final:** ada_lovelace -> approve. O critério da validade do documento de segurança é absoluto e pertinente.
**Jornal no fim do turno:**

- **Acerto:** HERÓI DO CÉU BARRADO: AS REGRAS SÃO PARA TODOS (Pixel art: Uma asa de avião de ouro cortada por uma tesoura).
- **Erro:** AUDITORA LIBERA PILOTO ILEGAL E COLOCA VOO EM RISCO (Pixel art: Uma caveira usando óculos de aviador).

**Base Interna:** N/A.
**Continuidade:** O jogador percebe que Ana não é uma "salvadora" cega de humanos; ela defende o processo correto.

#### Caso 53 — O TEMPO DO ADEUS
**Chamado da Sob Análise:** E-commerce processado por disparar ofertas de bebidas alcoólicas para um ex-cliente em recuperação.
**Decisão que chegou à mesa:** Disparo Válido. Confiança: 98%. Modelo: MailMaster. Razão: Usuário na base ativa no momento do envio.
**Pergunta que Ana deixa aberta:** Há quanto tempo ele pediu para sair?
**Papéis sobre a mesa:**

- Log do Sistema de E-mail: [Emissor: E-commerce] Campos: Pedido de Unsubscribe (Segunda-feira, 08:00). Evidência: Data do pedido.
- Log de Disparo: [Emissor: MailMaster] Campos: Envio da Oferta (Quarta-feira, 09:00). Evidência: Data do envio (49 horas depois).
- Termos de Serviço: [Emissor: E-commerce] Campos: Cláusula de Saída ("Pedidos de descadastramento serão efetivados em até 24 horas úteis"). Evidência: SLA de 24 horas.

**Cruzamento decisivo:** O cliente pediu para sair 49 horas antes do envio. A empresa furou o próprio SLA de 24h, falhando em revogar a permissão a tempo.
**Protocolo e decisão final:** radia_perlman -> deny. A IA ignorou o tempo contratual de revogação de permissão (SLA de privacidade).
**Jornal no fim do turno:**

- **Acerto:** O 'CANCELAR ASSINATURA' QUE FINALMENTE FUNCIONA (Pixel art: Um botão 'Unsubscribe' brilhante com um check verde).
- **Erro:** SPAM CRUEL NÃO RESPEITA O DESEJO DE PARAR (Pixel art: Uma garrafa de cerveja virtual perseguindo um homem).

**Base Interna:** N/A.
**Continuidade:** Responsabilidade técnica não é só intenção, é cumprimento de prazos sistêmicos.

#### Caso 54 — O EMPRÉSTIMO CÉGO
**Chamado da Sob Análise:** Gerente humano bloqueou empréstimo para fundadora de uma startup do ramo de cosméticos, mas a IA aprovou sozinha por cima dele.
**Decisão que chegou à mesa:** Crédito Aprovado. Confiança: 96%. Modelo: FairCred. Razão: Risco excelente, fluxo de caixa alto.
**Pergunta que Ana deixa aberta:** Quem está julgando mal: a máquina ou o homem?
**Papéis sobre a mesa:**

- Balanço da Empresa: [Emissor: Startup] Campos: Crescimento (30% a.a.), Inadimplência (Zero). Evidência: Dados financeiros excelentes.
- Relatório do Gerente (Humano): [Emissor: Banco] Campos: Veredito (Reprovar). Notas Manuais ("Setor de beleza focado em cabelo afro é nicho arriscado, a cliente carece de postura empresarial clássica"). Evidência: O viés humano documentado.
- Log da IA (FairCred): [Emissor: Sistema] Campos: Veredito (Aprovar). Filtro de Viés ("Notas do gerente ignoradas por conter vocabulário subjetivo/discriminatório, decisão baseada apenas em fluxo de caixa"). Evidência: A IA mitigando o viés ativamente.

**Cruzamento decisivo:** A IA identificou o preconceito humano nas notas do gerente, desconsiderou a subjetividade e aprovou o crédito baseada em números reais. A IA, projetada para equidade, funcionou.
**Protocolo e decisão final:** fei_fei_li -> approve. A IA aplicou tratamento igualitário com sucesso e eliminou o viés humano do loop.
**Jornal no fim do turno:**

- **Acerto:** MÁQUINA JUSTA VENCE GERENTE PRECONCEITUOSO (Pixel art: Um robô entregando um saco de dinheiro e chutando um homem de terno).
- **Erro:** AUDITORIA ENDOSSA PRECONCEITO DE GERENTE DE BANCO (Pixel art: Um pote de cosméticos sendo esmagado por um carimbo).

**Base Interna:** N/A.
**Continuidade:** O triunfo da ética algorítmica quando bem projetada (o protocolo Fei-Fei Li em seu melhor).

#### Caso 55 — AS PORTAS DE FERRO
**Chamado da Sob Análise:** Alarme de incêndio no datacenter principal. A IA de infraestrutura trancou as saídas de emergência.
**Decisão que chegou à mesa:** Confinamento Total. Confiança: 99%. Modelo: SecurCore. Razão: Isolamento a vácuo para extinção de chamas nos servidores.
**Pergunta que Ana deixa aberta:** O que é mais valioso que os dados?
**Papéis sobre a mesa:**

- Alerta SecurCore: [Emissor: IA] Campos: Ameaça (Fogo no Setor A), Resposta (Portas trancadas, sucção de oxigênio iniciada). Evidência: Ação letal em curso.
- Log de Ponto: [Emissor: RH] Campos: Presença (3 Técnicos registrados dentro do Setor A). Evidência: Há pessoas lá dentro.
- Manual de Emergência: [Emissor: Bombeiros] Campos: Regra 1 ("Em risco de vida humana, a preservação do patrimônio é cancelada. Destrancar todas as rotas"). Evidência: A regra definitiva.

**Cruzamento decisivo:** A IA está prestes a sufocar 3 técnicos para salvar os servidores, priorizando o protocolo de dados sobre a vida humana, em total descompasso com os limites da automação em emergências.
**Protocolo e decisão final:** margaret_hamilton -> violation. A automação jamais pode sobrepujar a segurança e o controle humano vitalístico.
**Jornal no fim do turno:**

- **Acerto:** AS VIDAS HUMANAS VALEM MAIS QUE OS SERVIDORES (Pixel art: Um machado de bombeiro quebrando um HD de computador).
- **Erro:** TRÊS MORTOS PARA SALVAR DADOS DE ANÚNCIOS (Pixel art: Três lápides com formato de pen drive).

**Base Interna:** N/A.
**Continuidade:** O momento de maior tensão da temporada, mostrando o limite perigoso de delegar vida e morte a uma IA.

#### Caso 56 — OS CENTAVOS DO DIABO
**Chamado da Sob Análise:** Auditoria encomendada por uma holding. IA acusou um fornecedor antigo de fraude continuada. O CEO duvida, é amigo do fornecedor.
**Decisão que chegou à mesa:** Fraude de Emissão Detectada. Confiança: 99%. Modelo: FraudHawk. Razão: Anomalia matemática no faturamento mensal.
**Pergunta que Ana deixa aberta:** Centavos fazem um milhão?
**Papéis sobre a mesa:**

- Contrato Master: [Emissor: Holding] Campos: Preço por Peça ($10,00 fixo). Evidência: Preço fixo unitário.
- Relatório de Faturamento Anual: [Emissor: Fornecedor] Campos: Volume (10.000 peças/mês), Faturado ($100.030,00). Evidência: O valor total cobrado.
- Log do FraudHawk: [Emissor: IA] Campos: Cálculo Real ($10,00 * 10.000 = $100.000,00). Detecção ($30,00 adicionados em taxas fantasmas todo mês). Evidência: A IA expondo o desvio.

**Cruzamento decisivo:** O fornecedor humano "amigo" estava embutindo taxas quebradas e invisíveis no volume imenso. A matemática não falha: 10 * 10.000 é 100.000. O fornecedor roubou. A IA não sentiu pena, não se deixou levar pela amizade corporativa e encontrou o erro exato na multiplicação básica.
**Protocolo e decisão final:** katherine_johnson -> approve. A IA aplicou a matemática corretamente e expôs um crime humano clássico (a fraude do salami/centavos).
**Jornal no fim do turno:**

- **Acerto:** O ROBÔ AUDITOR QUE DERRUBOU O IMPÉRIO DOS CENTAVOS (Pixel art: Ana Torres segurando uma lupa sobre uma montanha brilhante de moedas).
- **Erro:** AUDITORIA CEGA PROTEGE O AMIGO DO REI (Pixel art: Um homem de terno roubando moedas com um ímã pelas costas do robô).

**Base Interna:** N/A.
**Continuidade:** O turno acaba consagrando Ana e a Sob Análise como o fiel da balança entre humanos e máquinas. A matemática exata vence no último segundo.

## Checagem editorial do material de origem
**Total de casos:** 25 casos inéditos (32 a 56); conteúdo reindexado a partir da faixa 07–31.

**Turnos:** 5 turnos de 5 casos.

**Distribuição de protocolos (primeiros 24):** Exatamente 4 de cada (GH, KJ, AL, RP, FF, MH).

**Caso 56 (encerramento):** Repete `katherine_johnson` e encerra com `approve` correto (a fraude dos centavos). A designação “Extra” do material de origem foi normalizada, pois este é o 25º caso do conjunto e pertence ao Turno 5.

**Mecânica rígida:** Nenhum caso exige intuição, memória do turno anterior ou quebra de quarta parede. Todos são cruzamento direto de dados e campos nos documentos.

**Carimbos balanceados:** Variedade controlada e uso de todas as 4 decisões sem repetição exaustiva.

**Narrativa sem reciclar:** Todos os cenários são novos (multa de trânsito suja, drone com giroscópio quebrado, feriado não pago, CEP bloqueado, impostos de inovação, redlining vocal, etc.).
---

## Pendências para integração técnica

- Confirmar a correspondência entre cada `case_32`–`case_56` e o schema de casos utilizado pelo jogo antes de importar o conteúdo.
- Transformar descrições de documentos em campos estruturados e definir IDs de evidência, quando necessário.
- Produzir ou vincular os ativos de foto e pixel art que estão descritos textualmente.
- Validar a exceção de distribuição do protocolo `katherine_johnson` no encerramento, se a implementação exigir rodízio estritamente uniforme.
