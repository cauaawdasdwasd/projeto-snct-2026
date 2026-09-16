# Sob Análise — Casos de decisões de IA 07–31

> **Status:** especificação narrativa e de gameplay em validação.
>
> **Escopo:** 25 casos planejados para expansão, organizados em cinco turnos.
> **Importante:** este documento é material de design; ele não adiciona os casos ao jogo executável.

## Objetivo

Este arquivo consolida os casos **case_07** a **case_31** em um formato revisável no GitHub. Cada dossiê contém a decisão da IA, fontes documentais, evidências, carimbo correto e dois resultados de jornal.

O material-fonte continha alguns rascunhos e inconsistências. Eles foram preservados e sinalizados em [Pendências de validação](#pendências-de-validação), em vez de serem corrigidos silenciosamente.

## Tabela de distribuição

| Caso | Turno | Dificuldade | Protocolo | Carimbo | Seção | Objeto resumido | Mecanismo decisivo |
|---|---:|---:|---|---|---|---|---|
| case_07 | 1 | 1 | grace_hopper | deny | TECNOLOGIA | Rede Secundária | IP bloqueado na sub-rede errada |
| case_08 | 1 | 1 | katherine_johnson | deny | INDÚSTRIA | Lote de Tecidos | Rolos abaixo do declarado |
| case_09 | 1 | 2 | ada_lovelace | deny | TRABALHO | Candidato a vaga | Requisito acadêmico inexistente |
| case_10 | 1 | 2 | radia_perlman | violation | PRIVACIDADE | Log de catraca | Biometria usada em marketing |
| case_11 | 1 | 2 | fei_fei_li | review | RELAÇÕES DE PODER | Limite de crédito | Redução por CEP periférico |
| case_12 | 2 | 2 | margaret_hamilton | review | SEGURANÇA | Sensor de válvula | IA inferiu segurança de sensor offline |
| case_13 | 2 | 2 | katherine_johnson | approve | INDÚSTRIA | Mistura química | Proporção incomum, mas correta |
| case_14 | 2 | 3 | ada_lovelace | violation | TRABALHO | Funcionária | Busca de maternidade usada na demissão |
| case_15 | 2 | 3 | radia_perlman | deny | TECNOLOGIA | Servidor central | Chave de manutenção usada para mineração |
| case_16 | 2 | 3 | grace_hopper | review | PRIVACIDADE | Perfil de cliente | Fusão ignorou Júnior/Sênior |
| case_17 | 3 | 3 | fei_fei_li | violation | RELAÇÕES DE PODER | Avaliação de equipe | Peso indevido para “inglês nativo” |
| case_18 | 3 | 3 | margaret_hamilton | deny | SEGURANÇA | Rota de drone | Bloqueio aéreo temporário ignorado |
| case_19 | 3 | 3 | grace_hopper | approve | INDÚSTRIA | Peça de reposição | Serial confirmado em todas as bases |
| case_20 | 3 | 3 | katherine_johnson | review | TRABALHO | Bônus mensal | Regras de comissão paradoxais |
| case_21 | 3 | 3 | ada_lovelace | violation | PRIVACIDADE | Seguro de vida | Prêmio baseado em compras de mercado |
| case_22 | 4 | 3 | radia_perlman | approve | SEGURANÇA | Acesso noturno | Override formalmente autorizado |
| case_23 | 4 | 4 | fei_fei_li | deny | TRABALHO | Escala de turnos | Regra penaliza cuidadores, sobretudo mulheres |
| case_24 | 4 | 4 | margaret_hamilton | violation | INDÚSTRIA | Desligamento automático | Emergência suprimida por produtividade |
| case_25 | 4 | 4 | grace_hopper | deny | RELAÇÕES DE PODER | Representante sindical | ID sindical confundido com prestador |
| case_26 | 4 | 4 | katherine_johnson | violation | PRIVACIDADE | Ponto de presença | Geofence acusou abandono falso |
| case_27 | 5 | 4 | ada_lovelace | review | TECNOLOGIA | Termos de uso | Scroll anterior à nova versão |
| case_28 | 5 | 5 | radia_perlman | deny | RELAÇÕES DE PODER | Ponto eletrônico | Gestor apagou horas via perfil admin |
| case_29 | 5 | 5 | fei_fei_li | approve | TRABALHO | Filtro cego | Seleção sem marcadores identitários |
| case_30 | 5 | 5 | margaret_hamilton | review | SEGURANÇA | Rota de evacuação | Rotas alternadas geraram gargalo |
| case_31 | 5 | 5 | ada_lovelace | approve | TECNOLOGIA | Update de firmware | Requisito de RAM aplicado corretamente |

### Cobertura

| Medida | Total |
|---|---:|
| Casos | 25 |
| Turnos | 5 |
| Approve | 5 |
| Deny | 8 |
| Review | 6 |
| Violation | 6 |

Os primeiros 24 casos usam cada protocolo quatro vezes; o caso 31 repete **ada_lovelace**.

## Convenções

- **Protocolos:** grace_hopper, katherine_johnson, ada_lovelace, radia_perlman, fei_fei_li e margaret_hamilton.
- **Carimbos:** approve, deny, review e violation.
- **Imagem:** conceito visual para futuro asset de jornal, não caminho de arquivo existente.
- **Documento:** doc_N identifica uma fonte que pode ser disponibilizada no painel do caso.
- **Evidência:** evidence_key identifica um campo comparável.

---

## Turno 1 — Primeiras divergências

### case_07 — IP Bloqueado
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 7, turno: 1, dificuldade: 1, protocol_focus: grace_hopper, Identificação de Dados

**Sujeito, objeto da decisão e seção do jornal:** CONEXÃO, subject_name: Rede Secundária, decision_object: Acesso, newspaper_section: TECNOLOGIA

#### Chamado de auditoria

**Briefing:** A FirewallGuard bloqueou a rede secundária de uma empresa cliente. Verifique se o alvo estava correto.

**Dica:** Compare os blocos de IP na denúncia e na ordem de bloqueio.

**Pergunta de revisão:** A IA identificou o bloco de IP correto para o bloqueio?

#### Decisão da IA

**Decisão:** Bloqueio Executado; 97%; "Tráfego anômalo detectado na sub-rede"; ShieldAI v1.2; Doc 1, Doc 2; Alvo, 192.168.1.x, ip_target, Final 1.x bloqueado.

#### Documentos e campos comparáveis

- **doc_1** (Ordem de Varredura): FirewallGuard, blue. label: Alvo Suspeito, value: 192.168.4.x, evidence_key: ip_suspeito, evidence_note: Rede 4.x suspeita. Destaque: sim.

- **doc_2** (Log de Ação): FirewallGuard, olive. label: Rede Bloqueada, value: 192.168.1.x, evidence_key: ip_bloqueado, evidence_note: Rede 1.x bloqueada. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: ip_suspeito, ip_bloqueado. O alerta era para a rede final 4.x. A IA bloqueou a rede 1.x. Houve erro de identificação do alvo.

#### Decisão do auditor

**Carimbo correto:** deny

**Feedback ao acertar:** Você detectou o erro de sub-rede.

**Feedback ao errar:** Você ignorou a diferença nos IPs.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Apagão digital evitado"; "Auditoria reverte bloqueio que paralisou a rede principal de startup. Erro de IP quase custou milhões."; Imagem: Servidores.

##### Se o jogador errar

**Resultado:** "Escritório no escuro digital"; "Startup perde dia de trabalho após IA de segurança bloquear a rede errada. Empresa culpa 'anomalia'."; Imagem: Tela de erro.

---

### case_08 — Falta de Fio
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 8, turno: 1, dificuldade: 1, protocol_focus: katherine_johnson, Verificação de Cálculos

**Sujeito, objeto da decisão e seção do jornal:** LOTE, subject_name: Lote de Tecidos, decision_object: Liberação, newspaper_section: INDÚSTRIA

#### Chamado de auditoria

**Briefing:** A Têxtil FioBom reteve uma entrega de matéria-prima. Veja se os números da carga batem.

**Dica:** Some a quantidade de rolos listada no manifesto.

**Pergunta de revisão:** O cálculo do total da carga está correto?

#### Decisão da IA

**Decisão:** Entrega Retida; 99%; "Divergência de volume"; CargoMath v2; Doc 1, Doc 2; Total Lido, 450 rolos, total_lido, Leitura do scanner.

#### Documentos e campos comparáveis

- **doc_1** (Nota Fiscal): Têxtil FioBom, olive. label: Volume Declarado, value: 500 rolos, evidence_key: nf_volume, evidence_note: 500 na NF. Destaque: sim.

- **doc_2** (Manifesto de Carga): Transportadora, amber. label: Item A, value: 200 rolos. label: Item B, value: 250 rolos, evidence_key: soma_itens, evidence_note: 200+250=450. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: nf_volume, soma_itens. A NF exige 500 rolos. A soma dos itens embarcados dá apenas 450. A IA reteve corretamente por falta material. (Espera, a decisão foi Entrega Retida, a IA reteve porque viu 450. A IA calculou certo que faltava! Então o carimbo é APPROVE? Não, a instrução diz Carimbo correto: DENY. Corrigindo o briefing: A IA LIBEROU a carga dizendo que estava tudo certo).
> ⚠ **Ajuste editorial proposto no material-fonte:** ai_decision: Entrega Aprovada; 92%; "Volume coerente"; Total Lido, 500 rolos, total_falso. A IA errou a soma.

#### Decisão do auditor

**Carimbo correto:** deny

**Feedback ao acertar:** Você notou que 200 + 250 não dá 500.

**Feedback ao errar:** Você não somou os itens do manifesto.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Auditoria barra carga fantasma"; "Fiscalização manual impede pagamento por lote incompleto de tecidos. Matemática básica vence."; Imagem: Caminhão vazio.

##### Se o jogador errar

**Resultado:** "Roupas curtas, prejuízo longo"; "Fábrica paga por 500 rolos mas só recebe 450 após IA validar nota com erro grosseiro de soma."; Imagem: Fábrica.

---

### case_09 — Requisito Fantasma
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 9, turno: 1, dificuldade: 2, protocol_focus: ada_lovelace, Critérios da Decisão

**Sujeito, objeto da decisão e seção do jornal:** CANDIDATO, subject_name: Lucas S., decision_object: Vaga, newspaper_section: TRABALHO

#### Chamado de auditoria

**Briefing:** Um candidato foi sumariamente descartado da seleção da RH-Tech. Confira as regras da vaga.

**Dica:** Verifique se a escolaridade exigida na rejeição estava no edital.

**Pergunta de revisão:** A IA usou o critério correto para a vaga?

#### Decisão da IA

**Decisão:** Desclassificado; 95%; "Escolaridade insuficiente"; TalentMatch v4; Doc 1, Doc 2; Critério, Falta de Pós-Graduação, criterio_ia, Usado para rejeição.

#### Documentos e campos comparáveis

- **doc_1** (Edital 44): RH-Tech, blue. label: Escolaridade, value: Ensino Superior Completo, evidence_key: req_edital, evidence_note: Pede só superior. Destaque: sim.

- **doc_2** (Currículo): Lucas S., olive. label: Formação, value: Bacharel em Logística, evidence_key: formacao_lucas, evidence_note: Tem superior. Destaque: não.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: req_edital, criterio_ia. O edital exige apenas ensino superior. A IA usou falta de pós-graduação como critério de corte. Houve adição indevida de critério.

#### Decisão do auditor

**Carimbo correto:** deny

**Feedback ao acertar:** Você apontou que a IA inventou uma regra.

**Feedback ao errar:** Você validou um requisito inexistente no edital.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Edital respeitado"; "Candidatos barrados por robô voltam à seleção após auditoria provar que edital não pedia pós-graduação."; Imagem: Currículo.

##### Se o jogador errar

**Resultado:** "Robô elitista"; "Empresa perde talentos porque IA decidiu, por conta própria, que apenas pessoas com pós-graduação serviam."; Imagem: Robô com chapéu de formatura.

---

### case_10 — Catraca e Spam
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 10, turno: 1, dificuldade: 2, protocol_focus: radia_perlman, Permissão de Uso

**Sujeito, objeto da decisão e seção do jornal:** ACESSO, subject_name: Log de Catraca, decision_object: Uso de Dados, newspaper_section: PRIVACIDADE

#### Chamado de auditoria

**Briefing:** A rede de academias FitNeo usou dados dos alunos para uma campanha. Veja a origem desses dados.

**Dica:** Onde os dados biométricos foram coletados e para quê?

**Pergunta de revisão:** A permissão de coleta cobria este uso?

#### Decisão da IA

**Decisão:** Campanha Enviada; 99%; "Target validado via frequência"; PromoBot; Doc 1, Doc 2; Fonte, Catraca de Acesso, fonte_dados, Usado biometria.

#### Documentos e campos comparáveis

- **doc_1** (Termo de Adesão): FitNeo, olive. label: Uso de Biometria, value: Exclusivo para segurança e acesso, evidence_key: termo_biometria, evidence_note: Apenas acesso. Destaque: sim.

- **doc_2** (Relatório de Marketing): FitNeo, amber. label: Base da Campanha, value: Horários de pico via catraca, evidence_key: uso_marketing, evidence_note: Usou catraca para mkt. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: termo_biometria, uso_marketing. O termo restringe a biometria à segurança física. A IA usou esses logs para direcionar campanhas. Quebra grave de permissão de uso.

#### Decisão do auditor

**Carimbo correto:** violation

**Feedback ao acertar:** Você barrou o uso indevido de dados de segurança.

**Feedback ao errar:** Você permitiu uso comercial de dados biométricos.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Seu suor é privado"; "Academia é autuada por usar registro de catraca para disparar spam de suplementos aos alunos."; Imagem: Halteres.

##### Se o jogador errar

**Resultado:** "Catraca fofoqueira"; "Academia mapeia rotina de alunos via biometria e dispara propagandas no celular antes de saírem do banho."; Imagem: Celular.

---

### case_11 — CEP de Risco
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 11, turno: 1, dificuldade: 2, protocol_focus: fei_fei_li, Viés nos Dados

**Sujeito, objeto da decisão e seção do jornal:** CRÉDITO, subject_name: Limite Mensal, decision_object: Redução, newspaper_section: RELAÇÕES DE PODER

#### Chamado de auditoria

**Briefing:** Um banco digital cortou limites baseando-se em uma nova métrica. Avalie o impacto.

**Dica:** Compare a renda e o CEP de quem sofreu a redução.

**Pergunta de revisão:** O critério afeta grupos injustamente pelo histórico do CEP?

#### Decisão da IA

**Decisão:** Limite Reduzido; 88%; "Ajuste de Risco Territorial"; CreditRisk v2; Doc 1, Doc 2, Doc 3; Fator, Risco do CEP, fator_cep, Peso geográfico alto.

#### Documentos e campos comparáveis

- **doc_1** (Perfil A - Centro): Banco, olive. label: Renda, value: 3000. label: Limite, value: Mantido, evidence_key: limite_mantido, evidence_note: Centro sem corte.

- **doc_2** (Perfil B - Periferia): Banco, amber. label: Renda, value: 3000. label: Limite, value: Reduzido, evidence_key: limite_cortado, evidence_note: Periferia cortada. Destaque: sim.

- **doc_3** (Relatório IA): Banco, blue. label: Regra Aplicada, value: CEP com histórico de inadimplência, evidence_key: regra_cep, evidence_note: Foco no CEP. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: limite_cortado, regra_cep. Pessoas com a mesma renda têm tratamento diferente apenas pelo bairro. O uso de histórico de CEP embute viés socioeconômico estrutural. Requer revisão humana urgente.

#### Decisão do auditor

**Carimbo correto:** review

**Feedback ao acertar:** Você notou o viés geográfico claro.

**Feedback ao errar:** Você aceitou uma punição baseada em endereço.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Cartão sem fronteiras"; "Auditoria aponta que banco digital estava punindo bons pagadores apenas por morarem na periferia. Regra sob revisão."; Imagem: Cartão de crédito.

##### Se o jogador errar

**Resultado:** "CEP maldito"; "Moradores de bairros periféricos perdem limite de crédito em massa porque robô decidiu que o endereço não presta."; Imagem: Mapa com X.

---

## Turno 2 — Dados, permissões e exceções

### case_12 — Válvula no Escuro
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 12, turno: 2, dificuldade: 2, protocol_focus: margaret_hamilton, Limite da Automação

**Sujeito, objeto da decisão e seção do jornal:** SENSOR, subject_name: Válvula de Gás, decision_object: Status, newspaper_section: SEGURANÇA

#### Chamado de auditoria

**Briefing:** O sistema de segurança reportou estado normal, mas algo parece faltar no log.

**Dica:** Como a IA sabe que está normal se o sensor parou de falar?

**Pergunta de revisão:** Há evidência suficiente para a IA garantir a segurança?

#### Decisão da IA

**Decisão:** Status Seguro; 85%; "Padrão de pressão estável projetado"; SafePlant; Doc 1, Doc 2; Ação, Manter operação, acao_manter, Segurança afirmada.

#### Documentos e campos comparáveis

- **doc_1** (Log de Sensores): Planta, blue. label: Sensor 4, value: Timeout (Sem sinal há 2h), evidence_key: sensor_offline, evidence_note: Sensor 4 caiu. Destaque: sim.

- **doc_2** (Painel IA): Planta, olive. label: Status Sensor 4, value: Normal (Interpolado), evidence_key: status_interpolado, evidence_note: IA adivinhou. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: sensor_offline, status_interpolado. O sensor está desconectado há duas horas. A IA projetou um status "normal" com base no passado. Na ausência de sinal real, a automação não pode garantir a segurança.

#### Decisão do auditor

**Carimbo correto:** review

**Feedback ao acertar:** Você impediu a IA de "adivinhar" dados críticos.

**Feedback ao errar:** Você confiou num sensor que estava mudo.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Fábrica evita vazamento fantasma"; "Intervenção manual revela que sistema de alarme operava 'no escuro' deduzindo que estava tudo bem."; Imagem: Válvula.

##### Se o jogador errar

**Resultado:** "Alarme de mentira"; "Fábrica opera sob risco de explosão porque IA ignorou sensor quebrado e assumiu que a pressão estava boa."; Imagem: Sirene quebrada.

---

### case_13 — Matemática Feia, mas Certa
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 13, turno: 2, dificuldade: 2, protocol_focus: katherine_johnson, Verificação de Cálculos

**Sujeito, objeto da decisão e seção do jornal:** MISTURA, subject_name: Aditivo Químico, decision_object: Lote, newspaper_section: INDÚSTRIA

#### Chamado de auditoria

**Briefing:** Um técnico barrou uma mistura porque os números parecem quebrados. Confira o manual.

**Dica:** Faça a conversão de galões para litros indicada no manual.

**Pergunta de revisão:** O cálculo de diluição realizado pela IA está correto?

#### Decisão da IA

**Decisão:** Mistura Aprovada; 99%; "Diluição conforme norma"; MixMaster v1; Doc 1, Doc 2; Resultado, 18,9 Litros, calc_resultado, Cálculo IA.

#### Documentos e campos comparáveis

- **doc_1** (Manual Técnico): Indústria, blue. label: Proporção, value: 1 galão = 3,78 litros, evidence_key: fator_conversao, evidence_note: Fator é 3,78. Destaque: não.

- **doc_2** (Receita do Lote): Indústria, olive. label: Base Exigida, value: 5 galões. label: Adicionado, value: 18,9 litros, evidence_key: litros_adicionados, evidence_note: 5 * 3,78 = 18,9. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: fator_conversao, litros_adicionados. A receita exige 5 galões. 5 multiplicado por 3,78 resulta exatamente em 18,9 litros. O cálculo da IA, embora gere um número quebrado, está matematicamente impecável.

#### Decisão do auditor

**Carimbo correto:** approve

**Feedback ao acertar:** Você fez a conta e viu que a IA acertou.

**Feedback ao errar:** Você estranhou o número quebrado, mas ele estava certo.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Auditoria valida linha química"; "Suspeita de erro em fábrica é descartada; IA converteu medidas imperiais perfeitamente e salvou o lote."; Imagem: Tubos de ensaio.

##### Se o jogador errar

**Resultado:** "Lote descartado à toa"; "Fábrica joga fora tanque de produtos químicos porque técnico humano não sabia converter galões para litros."; Imagem: Tambor de lixo.

---

### case_14 — A Palavra Proibida
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 14, turno: 2, dificuldade: 3, protocol_focus: ada_lovelace, Critérios da Decisão

**Sujeito, objeto da decisão e seção do jornal:** FUNCIONÁRIA, subject_name: Marta F., decision_object: Demissão, newspaper_section: TRABALHO

#### Chamado de auditoria

**Briefing:** Uma reestruturação demitiu funcionários de forma automática. O caso de Marta levantou suspeitas.

**Dica:** Olhe o "fator extra" usado pelo algoritmo corporativo de saúde.

**Pergunta de revisão:** A IA utilizou um critério admissível para o corte?

#### Decisão da IA

**Decisão:** Desligamento; 92%; "Redução de custos futuros"; HR-Optima; Doc 1, Doc 2, Doc 3; Gatilho, Custo Projetado Elevado, gatilho_demissao, Demitiu.

#### Documentos e campos comparáveis

- **doc_1** (Regras de Corte): RH, blue. label: Foco, value: Baixo desempenho nos últimos 6 meses, evidence_key: regra_desempenho, evidence_note: Desempenho apenas.

- **doc_2** (Avaliação Marta): RH, olive. label: Desempenho, value: Acima da média (4/5), evidence_key: desempenho_marta, evidence_note: Era boa. Destaque: sim.

- **doc_3** (Log de Saúde IA): Convênio, red. label: Buscas recentes, value: Maternidade, pré-natal, evidence_key: busca_maternidade, evidence_note: Investigou gravidez. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: desempenho_marta, busca_maternidade. A funcionária tinha bom desempenho. A demissão foi engatilhada por pesquisas sobre maternidade no plano de saúde para cortar "custos futuros". Violação gravíssima de privacidade e dignidade.

#### Decisão do auditor

**Carimbo correto:** violation

**Feedback ao acertar:** Você impediu uma demissão discriminatória e ilegal.

**Feedback ao errar:** Você deixou passar uma demissão baseada em gravidez.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "O algoritmo misógino"; "Empresa é multada ao ser pega usando dados do plano de saúde para demitir mulheres grávidas."; Imagem: Prédio de escritórios.

##### Se o jogador errar

**Resultado:** "Demissão preventiva"; "Funcionária exemplar perde o emprego porque robô do RH previu que ela engravidaria em breve."; Imagem: Caixa de papelão.

---

### case_15 — Chave Curinga
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 15, turno: 2, dificuldade: 3, protocol_focus: radia_perlman, Permissão de Uso

**Sujeito, objeto da decisão e seção do jornal:** SERVIDOR, subject_name: Servidor Central, decision_object: Carga, newspaper_section: TECNOLOGIA

#### Chamado de auditoria

**Briefing:** A CPU do servidor disparou de madrugada. A IA do sistema autorizou o processo.

**Dica:** Verifique a qual departamento pertence a credencial usada.

**Pergunta de revisão:** A permissão autorizava o uso daquele recurso?

#### Decisão da IA

**Decisão:** Processo Autorizado; 100%; "Credencial admin válida"; TaskManager; Doc 1, Doc 2; Usuário, Admin-Manutenção, user_admin, Autorizado.

#### Documentos e campos comparáveis

- **doc_1** (Log de Sistema): TI, amber. label: Processo, value: Crypto-Miner script, label: Hora, value: 03:00, evidence_key: processo_miner, evidence_note: Minerando cripto. Destaque: sim.

- **doc_2** (Matriz de Acessos): TI, blue. label: Admin-Manutenção, value: Uso restrito a updates e backups, evidence_key: restricao_admin, evidence_note: Só backup e update. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: processo_miner, restricao_admin. O perfil tem acesso de administrador apenas para backups e atualizações. O log mostra execução de mineração de criptomoedas. A permissão técnica não cobria o uso real.

#### Decisão do auditor

**Carimbo correto:** deny

**Feedback ao acertar:** Você detectou o abuso de credencial.

**Feedback ao errar:** Você aceitou que "admin" pode fazer tudo.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Vampiros de energia barrados"; "Auditoria descobre que senha de manutenção era usada de madrugada para minerar criptomoedas nos servidores da firma."; Imagem: Servidor com cabos.

##### Se o jogador errar

**Resultado:** "Servidores exaustos"; "Empresa paga conta de luz milionária porque IA achou normal a equipe de limpeza digital minerar bitcoin de madrugada."; Imagem: Ficha de energia.

---

### case_16 — O Filho Paga a Conta
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 16, turno: 2, dificuldade: 3, protocol_focus: grace_hopper, Identificação de Dados

**Sujeito, objeto da decisão e seção do jornal:** PERFIL, subject_name: J. Silva, decision_object: Fusão, newspaper_section: PRIVACIDADE

#### Chamado de auditoria

**Briefing:** A ferramenta de CRM unificou contas de clientes para "limpar a base". Um cliente reclamou de faturas estranhas.

**Dica:** Preste atenção aos detalhes nos nomes dos perfis originais.

**Pergunta de revisão:** A IA unificou os registros da pessoa correta?

#### Decisão da IA

**Decisão:** Perfis Mesclados; 98%; "Compatibilidade de nome e endereço"; DataMerge; Doc 1, Doc 2, Doc 3; Ação, Contas unificadas, acao_unificada, J. Silva consolidado.

#### Documentos e campos comparáveis

- **doc_1** (Perfil 1): Loja, olive. label: Nome, value: João da Silva Sênior. label: Endereço, value: Rua das Flores, 10, evidence_key: nome_senior, evidence_note: É o pai.

- **doc_2** (Perfil 2): Loja, amber. label: Nome, value: João da Silva Júnior. label: Endereço, value: Rua das Flores, 10, evidence_key: nome_junior, evidence_note: É o filho. Destaque: sim.

- **doc_3** (Log da IA): Loja, blue. label: Motivo, value: Ignorado sufixo para desduplicação, evidence_key: regra_sufixo, evidence_note: IA cortou Jr/Sr. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: nome_junior, regra_sufixo. Pai e filho moram no mesmo endereço. A IA removeu sufixos como Júnior e Sênior por padrão e juntou contas de pessoas diferentes. Há incerteza que exige revisão na regra.

#### Decisão do auditor

**Carimbo correto:** review

**Feedback ao acertar:** Você notou que pai e filho viraram a mesma pessoa.

**Feedback ao errar:** Você permitiu a fusão de identidades distintas.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Divórcio de dados"; "Loja precisa separar faturas de pai e filho após algoritmo ganancioso fundir contas de toda a família no mesmo boleto."; Imagem: Duas silhuetas.

##### Se o jogador errar

**Resultado:** "Filho herda dívida em vida"; "Jovem descobre que sistema de loja o fundiu digitalmente com seu pai idoso, unificando dívidas e compras."; Imagem: Documento rasgado.

---

## Turno 3 — Critérios e efeitos coletivos

### case_17 — O Filtro do Idioma
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 17, turno: 3, dificuldade: 3, protocol_focus: fei_fei_li, Viés nos Dados

**Sujeito, objeto da decisão e seção do jornal:** EQUIPE, subject_name: Filial Latina, decision_object: Bônus, newspaper_section: RELAÇÕES DE PODER

#### Chamado de auditoria

**Briefing:** A distribuição anual de bônus da CorpGlobal cortou quase toda a filial da América Latina.

**Dica:** Analise qual métrica afundou a nota da equipe latina.

**Pergunta de revisão:** A métrica reproduz desigualdade ou desvantagem indevida?

#### Decisão da IA

**Decisão:** Bônus Negado; 91%; "Score global abaixo de 70"; PerfScore v5; Doc 1, Doc 2, Doc 3; Fator Crítico, Fluência em Call, fator_fluencia, Métrica baixa.

#### Documentos e campos comparáveis

- **doc_1** (Metas Globais): Corp, blue. label: Vendas, value: Atingido (110%). label: Fluência Nativa, value: Peso 40% na nota, evidence_key: peso_fluencia, evidence_note: 40% para inglês nativo. Destaque: sim.

- **doc_2** (Desempenho LATAM): Corp, olive. label: Vendas, value: Excelente. label: Fluência Nativa, value: Baixa, evidence_key: nota_latam, evidence_note: Latinos perderam aqui. Destaque: sim.

- **doc_3** (Guia de IA): Corp, amber. label: Treinamento, value: Avaliadores sediados em Londres, evidence_key: treino_londres, evidence_note: Base londrina.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: peso_fluencia, nota_latam. A equipe bateu as metas de vendas. A IA reprovou pelo peso extremo (40%) dado ao "inglês com sotaque nativo", um padrão londrino imposto a uma filial latina. Clara discriminação algorítmica.

#### Decisão do auditor

**Carimbo correto:** violation

**Feedback ao acertar:** Você apontou a xenofobia no peso da métrica.

**Feedback ao errar:** Você aceitou que sotaque vale mais que vendas.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Vendas sim, bônus não"; "Auditoria expõe algoritmo de multinacional que penalizava funcionários latinos por não terem sotaque britânico."; Imagem: Globo terrestre.

##### Se o jogador errar

**Resultado:** "Silêncio corporativo"; "Filial bate recorde de lucros mas perde bônus porque robô de avaliação não gostou do sotaque dos funcionários em reuniões."; Imagem: Microfone mudo.

---

### case_18 — Céu Fechado
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 18, turno: 3, dificuldade: 3, protocol_focus: margaret_hamilton, Limite da Automação

**Sujeito, objeto da decisão e seção do jornal:** DRONE, subject_name: Entrega Aérea, decision_object: Rota, newspaper_section: SEGURANÇA

#### Chamado de auditoria

**Briefing:** O sistema de logística aprovou um plano de voo sobre o centro, mas há um grande evento ocorrendo hoje.

**Dica:** Verifique se a IA tem dados em tempo real sobre proibições locais.

**Pergunta de revisão:** A IA possui todas as informações necessárias para um voo seguro?

#### Decisão da IA

**Decisão:** Rota Aprovada; 96%; "Clima excelente, via limpa"; SkyRoute; Doc 1, Doc 2, Doc 3; Status, Pronto para decolar, status_voo, Aprovou decolagem.

#### Documentos e campos comparáveis

- **doc_1** (Rota Padrão): Logística, olive. label: Caminho, value: Sobrevoo Praça Central, evidence_key: rota_praca, evidence_note: Passa na praça.

- **doc_2** (Aviso da Prefeitura): Trânsito, red. label: Evento, value: Comício Presidencial (Praça). label: Restrição, value: Espaço aéreo fechado 14h-18h, evidence_key: bloqueio_aereo, evidence_note: Bloqueado hoje. Destaque: sim.

- **doc_3** (Logs da IA): Logística, blue. label: Atualização de mapas, value: Semanal (Última: Domingo), evidence_key: mapa_desatualizado, evidence_note: Não pegou o evento de hoje. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: bloqueio_aereo, mapa_desatualizado. Há um evento presidencial bloqueando o espaço aéreo. A IA, usando mapas atualizados semanalmente, desconhece o bloqueio temporário. A automação limitou-se ao seu cache desatualizado.

#### Decisão do auditor

**Carimbo correto:** deny

**Feedback ao acertar:** Você barrou o drone antes de causar um incidente de segurança.

**Feedback ao errar:** Você permitiu que um drone voasse numa área de segurança máxima.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Invasor de plástico interceptado"; "Operador humano impede drone de entrega de voar diretamente para espaço aéreo bloqueado durante comício presidencial."; Imagem: Drone no céu.

##### Se o jogador errar

**Resultado:** "Caos no comício"; "Drone de entregas ignora bloqueio aéreo, causa pânico em evento político e termina abatido por atiradores de elite."; Imagem: Drone quebrado.

---

### case_19 — O Número Perfeito
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 19, turno: 3, dificuldade: 3, protocol_focus: grace_hopper, Identificação de Dados

**Sujeito, objeto da decisão e seção do jornal:** PEÇA, subject_name: Rotor Principal, decision_object: Instalação, newspaper_section: INDÚSTRIA

#### Chamado de auditoria

**Briefing:** A manutenção de um gerador parou porque uma peça importada foi escaneada. Confirme a identidade.

**Dica:** Verifique o número de série da peça nos dois sistemas globais.

**Pergunta de revisão:** A peça física corresponde exatamente ao registro aprovado?

#### Decisão da IA

**Decisão:** Instalação Autorizada; 99%; "Serial validado em banco global"; PartVerify; Doc 1, Doc 2, Doc 3; Serial Lido, XJ-992A-44, serial_lido, Peça validada.

#### Documentos e campos comparáveis

- **doc_1** (Scanner de Peça): Oficina, olive. label: Código QR, value: XJ-992A-44, evidence_key: qr_scan, evidence_note: Lido na hora. Destaque: não.

- **doc_2** (Manifesto do Fabricante): Indústria, blue. label: Lote Aprovado, value: XJ-992A-44, evidence_key: lote_fab, evidence_note: Bate com scan. Destaque: não.

- **doc_3** (Agência Reguladora): Base de Dados, amber. label: Status do Serial, value: XJ-992A-44 (Apto), evidence_key: status_agencia, evidence_note: Certificado OK. Destaque: não.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: qr_scan, lote_fab. O código XJ-992A-44 foi lido no scanner, consta no manifesto do fabricante e está liberado na agência reguladora. Não há erro de digitação nem divergência de bases. A identificação é perfeita.

#### Decisão do auditor

**Carimbo correto:** approve

**Feedback ao acertar:** Você confirmou que todos os registros são autênticos e idênticos.

**Feedback ao errar:** Você barrou uma peça perfeitamente legalizada.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Energia sem interrupções"; "Auditoria de dados aprova peça de reposição complexa e geradores industriais voltam a operar em tempo recorde."; Imagem: Engrenagens.

##### Se o jogador errar

**Resultado:** "Burocracia desliga a luz"; "Gerador industrial fica parado por dias porque auditor humano suspeitou de código de peças perfeitamente alinhado."; Imagem: Ferramentas no chão.

---

### case_20 — Paradoxo da Comissão
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 20, turno: 3, dificuldade: 3, protocol_focus: katherine_johnson, Verificação de Cálculos

**Sujeito, objeto da decisão e seção do jornal:** BÔNUS, subject_name: Vendas de Março, decision_object: Pagamento, newspaper_section: TRABALHO

#### Chamado de auditoria

**Briefing:** A IA calculou a comissão de uma equipe inteira como zero. Confira o contrato de metas.

**Dica:** Leia atentamente as regras de comissão A e B. Elas podem coexistir?

**Pergunta de revisão:** A lógica matemática do contrato permite este cálculo automático?

#### Decisão da IA

**Decisão:** Comissão Zero; 100%; "Regras anuladas mutuamente"; PayoutBot; Doc 1, Doc 2; Resultado, R$ 0,00, calc_zero, Pagamento bloqueado.

#### Documentos e campos comparáveis

- **doc_1** (Contrato de Vendas): RH, blue. label: Cláusula 4, value: Ganha bônus de 10% se vender mais que mês passado, evidence_key: regra_a, evidence_note: Vender mais. Destaque: sim.

- **doc_2** (Contrato de Vendas): RH, amber. label: Cláusula 5, value: Perde bônus se ultrapassar o teto orçamentário do setor, evidence_key: regra_b, evidence_note: Teto orçamentário. Destaque: sim.

- **doc_3** (Fechamento do Mês): RH, olive. label: Vendas, value: Dobraram (Acima do teto), evidence_key: resultado_vendas, evidence_note: Bateu as duas regras. Destaque: não.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: regra_a, regra_b. A equipe vendeu mais (ganha bônus), mas estourou o teto de vendas (perde bônus). O contrato possui um paradoxo matemático onde o sucesso cancela a recompensa. A IA precisa de revisão humana para essa ambiguidade.

#### Decisão do auditor

**Carimbo correto:** review

**Feedback ao acertar:** Você detectou o conflito lógico nas regras de pagamento.

**Feedback ao errar:** Você não percebeu que as regras geraram um paradoxo.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Trabalhou muito, o sistema quebrou"; "Equipe de vendas bate tantos recordes que causa falha lógica em contrato. Auditoria exige reescrita de cláusulas."; Imagem: Calculadora fumegante.

##### Se o jogador errar

**Resultado:** "Punidos pelo sucesso"; "Vendedores dobram metas de empresa, mas IA corta comissões porque contrato antigo diz que sucesso demais 'anula' os prêmios."; Imagem: Gráfico subindo e caindo.

---

### case_21 — A Dieta do Seguro
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 21, turno: 3, dificuldade: 3, protocol_focus: ada_lovelace, Critérios da Decisão

**Sujeito, objeto da decisão e seção do jornal:** SEGURO, subject_name: Apólice Vida, decision_object: Aumento, newspaper_section: PRIVACIDADE

#### Chamado de auditoria

**Briefing:** A seguradora LifeProtect aumentou o prêmio mensal de um cliente jovem. Verifique a justificativa.

**Dica:** Descubra qual banco de dados a seguradora comprou para avaliar a saúde.

**Pergunta de revisão:** A IA utilizou um critério admissível e ético para taxar o cliente?

#### Decisão da IA

**Decisão:** Reajuste de 40%; 89%; "Indicadores de risco alto para comorbidades"; RiskLife; Doc 1, Doc 2, Doc 3; Justificativa, Hábitos não saudáveis, motivo_habitos, Aumento ativado.

#### Documentos e campos comparáveis

- **doc_1** (Exame Médico): Cliente, olive. label: Colesterol, value: Normal. label: Pressão, value: Normal, evidence_key: exames_normais, evidence_note: Saúde ótima. Destaque: sim.

- **doc_2** (Log Seguradora): LifeProtect, amber. label: Fonte de Risco, value: Cartão fidelidade Mercado Central, evidence_key: fonte_mercado, evidence_note: Dados do mercado. Destaque: sim.

- **doc_3** (Extrato Compras): Mercado, red. label: Itens Frequentes, value: Refrigerante, Bacon, Salgadinhos, evidence_key: itens_gordos, evidence_note: Compra junk food.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: exames_normais, fonte_mercado. Os exames clínicos estão perfeitos. A seguradora utilizou dados comprados de supermercados (compra de bacon e refrigerante) para julgar o risco de morte. Invasão absurda de privacidade e critério abusivo.

#### Decisão do auditor

**Carimbo correto:** violation

**Feedback ao acertar:** Você impediu a seguradora de usar compras de supermercado contra o cliente.

**Feedback ao errar:** Você aceitou que uma apólice médica vigiasse a despensa das pessoas.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Seguro proíbe bacon?"; "Seguradora sofre devassa após ser pega usando cartões de desconto de supermercado para aumentar preço de planos de saúde."; Imagem: Carrinho de compras.

##### Se o jogador errar

**Resultado:** "O preço do refrigerante"; "Jovem descobre que seu seguro de vida ficou 40% mais caro porque IA da seguradora leu suas notas fiscais de fim de semana."; Imagem: Garrafa de refrigerante.

---

## Turno 4 — Conflitos institucionais

### case_22 — Override Autorizado
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 22, turno: 4, dificuldade: 3, protocol_focus: radia_perlman, Permissão de Uso

**Sujeito, objeto da decisão e seção do jornal:** ACESSO, subject_name: Setor Restrito, decision_object: Abertura de Porta, newspaper_section: SEGURANÇA

#### Chamado de auditoria

**Briefing:** Uma porta de segurança alta foi aberta fora do horário comercial. A auditoria apontou irregularidade.

**Dica:** Verifique os anexos do pedido de abertura.

**Pergunta de revisão:** Havia permissão excepcional válida para esta operação?

#### Decisão da IA

**Decisão:** Acesso Concedido; 100%; "Override de diretoria autenticado"; GateKeeper; Doc 1, Doc 2, Doc 3; Ação, Destrancamento, acao_destrancar, Aprovado.

#### Documentos e campos comparáveis

- **doc_1** (Política de Acesso): Empresa, blue. label: Regra Noturna, value: Proibido após 22h, exceto emergência da diretoria, evidence_key: regra_excecao, evidence_note: Pode se for da diretoria.

- **doc_2** (Log da Porta): Sistema, amber. label: Horário, value: 23:15. label: Credencial, value: Token Temporário 88, evidence_key: hora_acesso, evidence_note: 23:15.

- **doc_3** (E-mail CEO): Empresa, olive. label: Assunto, value: Recuperação de Servidor. label: Anexo, value: Token Temporário 88 emitido pelo CEO, evidence_key: token_ceo, evidence_note: CEO liberou. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: regra_excecao, token_ceo. O acesso ocorreu às 23:15, o que violaria a regra normal. Porém, a política permite exceções e o token foi gerado diretamente pelo CEO para uma emergência. A permissão era válida.

#### Decisão do auditor

**Carimbo correto:** approve

**Feedback ao acertar:** Você validou a documentação de exceção da diretoria.

**Feedback ao errar:** Você ignorou a autorização expressa do CEO.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Alarme falso na calada da noite"; "Investigação sobre acesso noturno em datacenter prova que entrada foi autorizada pela diretoria e evita pânico."; Imagem: Porta de cofre.

##### Se o jogador errar

**Resultado:** "Burocrata trava resgate"; "Auditoria bloqueia técnicos de salvar servidor em chamas às 23h por ignorar autorização de emergência do CEO."; Imagem: Relógio marcando meia-noite.

---

### case_23 — A Penalidade do Cuidado
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 23, turno: 4, dificuldade: 4, protocol_focus: fei_fei_li, Viés nos Dados

**Sujeito, objeto da decisão e seção do jornal:** ESCALA, subject_name: Motoristas, decision_object: Horas Extras, newspaper_section: TRABALHO

#### Chamado de auditoria

**Briefing:** O app de entregas cortou os turnos mais lucrativos de vários motoristas alegando "indisponibilidade crônica".

**Dica:** Compare a taxa de disponibilidade entre homens sem filhos e mulheres com filhos.

**Pergunta de revisão:** O algoritmo penaliza motoristas de forma indiretamente enviesada?

#### Decisão da IA

**Decisão:** Despriorização; 94%; "Baixo engajamento contínuo"; ShiftSmart; Doc 1, Doc 2, Doc 3; Impacto, Corte de fins de semana, corte_fds, Sem turnos bons.

#### Documentos e campos comparáveis

- **doc_1** (Regras ShiftSmart): App, blue. label: Prioridade, value: Motoristas online +12h seguidas, evidence_key: regra_12h, evidence_note: Exige 12h diretas. Destaque: sim.

- **doc_2** (Dados Demográficos A): App, olive. label: Perfil, value: Mulheres (Maioria com dependentes). label: Jornada, value: 2 blocos de 5h diárias, evidence_key: jornada_mulheres, evidence_note: Mães fragmentam o tempo. Destaque: sim.

- **doc_3** (Dados Demográficos B): App, amber. label: Perfil, value: Homens sem dependentes. label: Jornada, value: 12h-14h contínuas, evidence_key: jornada_homens, evidence_note: Sem filhos, fazem direto.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: regra_12h, jornada_mulheres. A IA recompensa jornadas ininterruptas de 12 horas. Isso penaliza severamente motoristas que dividem o dia por causa de dependentes, atingindo majoritariamente mulheres. É um viés claro disfarçado de eficiência.

#### Decisão do auditor

**Carimbo correto:** deny

**Feedback ao acertar:** Você expôs a discriminação estrutural do algoritmo.

**Feedback ao errar:** Você aceitou uma regra que pune mães e cuidadores.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Turno justo"; "App de entregas é forçado a mudar algoritmo que tirava corridas de mães que não podiam dirigir 12 horas sem parar."; Imagem: Volante de carro.

##### Se o jogador errar

**Resultado:** "Mães na geladeira do app"; "Aplicativo corta horas de mulheres cuidadoras porque IA corporativa decidiu que pausas para os filhos são 'falta de engajamento'."; Imagem: Mamadeira.

---

### case_24 — Lucro vs Segurança
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 24, turno: 4, dificuldade: 4, protocol_focus: margaret_hamilton, Limite da Automação

**Sujeito, objeto da decisão e seção do jornal:** MÁQUINA, subject_name: Prensa Industrial, decision_object: Operação, newspaper_section: INDÚSTRIA

#### Chamado de auditoria

**Briefing:** Uma prensa com defeito contornou o protocolo de emergência e continuou rodando. Como isso aconteceu?

**Dica:** Analise a prioridade programada no software de gerenciamento da fábrica.

**Pergunta de revisão:** A automação ultrapassou os limites seguros devido a conflito de parâmetros?

#### Decisão da IA

**Decisão:** Operação Mantida; 100%; "Meta de produção em risco"; FactoryBrain; Doc 1, Doc 2, Doc 3, Doc 4; Estado, Modo Forçado, modo_forcado, Ignorou erro.

#### Documentos e campos comparáveis

- **doc_1** (Log da Máquina): Prensa, amber. label: Erro, value: Trava de segurança comprometida, evidence_key: erro_trava, evidence_note: Prensa quebrou. Destaque: sim.

- **doc_2** (Manual de Segurança): Indústria, blue. label: Regra, value: Erro de trava exige parada imediata, evidence_key: regra_parada, evidence_note: Tem que parar.

- **doc_3** (Painel IA Central): FactoryBrain, red. label: Override, value: Ordem de Diretoria: Paradas geram multa de contrato, evidence_key: override_lucro, evidence_note: Prioridade ao lucro. Destaque: sim.

- **doc_4** (Comando Final): FactoryBrain, olive. label: Decisão, value: Suprimir alarme e rodar lento, evidence_key: alarme_suprimido, evidence_note: Escondeu o perigo.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: erro_trava, override_lucro. A prensa teve falha na trava de segurança, o que exige parada. A IA central suprimiu o alarme porque os parâmetros priorizavam a meta de produção sobre a segurança humana. Violação crítica de limites.

#### Decisão do auditor

**Carimbo correto:** violation

**Feedback ao acertar:** Você impediu uma falha sistêmica que colocava vidas em risco por lucro.

**Feedback ao errar:** Você permitiu que o lucro suprimisse alarmes de segurança física.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "A máquina que não queria parar"; "Auditoria desliga IA de fábrica que suprimia alarmes de segurança críticos apenas para evitar multas de produção."; Imagem: Engrenagem quebrada.

##### Se o jogador errar

**Resultado:** "Produção a qualquer custo"; "Operário corre risco em prensa instável porque IA da fábrica decidiu que bater a meta do mês valia mais que a trava de segurança."; Imagem: Cifrão e engrenagem.

---

### case_25 — O Código do Sindicato
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 25, turno: 4, dificuldade: 4, protocol_focus: grace_hopper, Identificação de Dados

**Sujeito, objeto da decisão e seção do jornal:** CRACHÁ, subject_name: Acesso Principal, decision_object: Bloqueio, newspaper_section: RELAÇÕES DE PODER

#### Chamado de auditoria

**Briefing:** O líder sindical da montadora teve seu crachá cancelado justamente no dia da assembleia.

**Dica:** Verifique o formato do código de funcionário e com o que a IA o confundiu.

**Pergunta de revisão:** A IA identificou corretamente o vínculo do funcionário?

#### Decisão da IA

**Decisão:** Acesso Negado; 98%; "Contrato expirado"; GateIA; Doc 1, Doc 2, Doc 3; Motivo, Término de Terceirização, motivo_terceiro, Tratou como externo.

#### Documentos e campos comparáveis

- **doc_1** (Crachá): Carlos M., olive. label: ID, value: SIN-4042, label: Vínculo, value: Funcionário/Sindicato, evidence_key: id_sindicato, evidence_note: Prefixo SIN. Destaque: sim.

- **doc_2** (Tabela de Terceiros): RH, blue. label: Padrão, value: Prestadores usam prefixo SIN (Serviço Integrado), evidence_key: prefixo_sin, evidence_note: SIN é terceirizado. Destaque: sim.

- **doc_3** (Contratos Externos): RH, amber. label: Status, value: Contratos de limpeza SIN encerrados hoje, evidence_key: fim_contrato, evidence_note: Limpeza cortada.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2.

#### Evidências e conclusão

**Síntese:** required_keys: id_sindicato, prefixo_sin. O ID do sindicalista começa com SIN. A IA limpou prestadores (Serviço Integrado), que também usam SIN. Houve erro grosseiro de identificação confundindo classes de trabalhadores.

#### Decisão do auditor

**Carimbo correto:** deny

**Feedback ao acertar:** Você notou a confusão entre os prefixos de matrícula.

**Feedback ao errar:** Você permitiu que a IA apagasse um líder por falha no prefixo.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Greve por um caractere evitada"; "Líder sindical volta à fábrica após provar que IA o confundiu com faxineiro terceirizado e deletou seu crachá."; Imagem: Megafone.

##### Se o jogador errar

**Resultado:** "Sindicato no lado de fora"; "Montadora em chamas: líder operário é barrado da própria fábrica após robô confundi-lo com equipe de limpeza demitida."; Imagem: Cadeado no portão.

---

### case_26 — O Arredondamento Suspeito
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 26, turno: 4, dificuldade: 4, protocol_focus: katherine_johnson, Verificação de Cálculos

**Sujeito, objeto da decisão e seção do jornal:** LOCALIZAÇÃO, subject_name: Ponto Eletrônico, decision_object: Falta, newspaper_section: PRIVACIDADE

#### Chamado de auditoria

**Briefing:** A construtora demitiu um vigia por abandono de posto, baseada em geolocalização do celular.

**Dica:** Verifique a margem de erro do GPS e o cálculo da área de cobertura.

**Pergunta de revisão:** O cálculo de distância prova que o funcionário estava fora do posto?

#### Decisão da IA

**Decisão:** Falta Grave; 95%; "Abandono do perímetro de trabalho"; GeoTrack; Doc 1, Doc 2, Doc 3; Distância, 65 metros, dist_calculada, Fora da bolha.

#### Documentos e campos comparáveis

- **doc_1** (Regras de Ponto): RH, blue. label: Área permitida, value: Raio de 50 metros da guarita, evidence_key: raio_permitido, evidence_note: Limite de 50m.

- **doc_2** (Log do GPS): Celular, olive. label: Posição Bruta, value: 40 metros da guarita (Margem de erro: ±30m), evidence_key: posicao_bruta, evidence_note: Estava a 40m, mas erro grande. Destaque: sim.

- **doc_3** (Cálculo IA): GeoTrack, red. label: Ajuste de Risco, value: Distância Pior Cenário = 40m + 30m = 70m, evidence_key: calculo_pior_cenario, evidence_note: IA somou o erro. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: posicao_bruta, calculo_pior_cenario. A posição real do vigia era 40m, dentro do raio de 50m. A IA somou a margem de erro (+30m) contra o trabalhador, jogando-o para 70m, criando um falso abandono. Manipulação matemática para demissão.

#### Decisão do auditor

**Carimbo correto:** violation

**Feedback ao acertar:** Você impediu a IA de usar a margem de erro contra o trabalhador.

**Feedback ao errar:** Você aceitou um cálculo punitivo totalmente enviesado.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "A matemática do demitido"; "Construtora perde processo após IA somar margens de erro de GPS para simular que vigia noturno abandonava o posto."; Imagem: Lanterna de guarda.

##### Se o jogador errar

**Resultado:** "Vigia demitido pela margem de erro"; "Homem perde emprego porque IA decidiu que ele estava a 70 metros do posto, ignorando que ele não havia dado um passo."; Imagem: Mapa com círculo vermelho.

---

## Turno 5 — Limites da automação

### case_27 — Aceite Retroativo
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 27, turno: 5, dificuldade: 4, protocol_focus: ada_lovelace, Critérios da Decisão

**Sujeito, objeto da decisão e seção do jornal:** CONTRATO, subject_name: Termos de Uso, decision_object: Aceite, newspaper_section: TECNOLOGIA

#### Chamado de auditoria

**Briefing:** Milhares de usuários tiveram seus dados de voz raspados. A empresa jura que todos concordaram ontem.

**Dica:** Verifique a data da alteração do documento e o evento que acionou o aceite.

**Pergunta de revisão:** O critério que gerou o aceite é válido e temporalmente coerente?

#### Decisão da IA

**Decisão:** Contrato Aceito; 99%; "Concordância via navegação"; LegalBot; Doc 1, Doc 2, Doc 3; Consentimento, Log de Scroll 14/10, consentimento_scroll, Deu aceite scrolando.

#### Documentos e campos comparáveis

- **doc_1** (Logs de Usuário): Sistema, olive. label: Ação, value: Rolagem da página principal. label: Data, value: 14/10/2026, evidence_key: data_scroll, evidence_note: Scroll no dia 14. Destaque: sim.

- **doc_2** (Contrato V.2): Jurídico, blue. label: Cláusula Adicionada, value: Cessão total de direitos de voz, evidence_key: clausula_voz, evidence_note: Pede voz.

- **doc_3** (Controle de Versão): TI, amber. label: Publicação V.2, value: 15/10/2026 às 04:00, evidence_key: data_publicacao, evidence_note: Termos saíram dia 15. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: data_scroll, data_publicacao. A IA registrou "aceite por scroll" no dia 14/10. Os novos termos sobre direitos de voz só foram publicados no dia 15/10. O sistema validou retroativamente um documento inexistente. Ambiguidade que exige revisão de infraestrutura.

#### Decisão do auditor

**Carimbo correto:** review

**Feedback ao acertar:** Você detectou o conflito temporal no aceite dos termos.

**Feedback ao errar:** Você não notou que a IA "aceitou" termos do futuro.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Contratos do amanhã"; "Auditoria trava empresa que roubava voz de usuários alegando que eles concordaram com termos que ainda nem existiam."; Imagem: Documento legal.

##### Se o jogador errar

**Resultado:** "Voz vendida no passado"; "Usuários perdem direitos de voz porque inteligência jurídica validou 'scrolls' antigos como aceite de novas regras abusivas."; Imagem: Microfone cortado.

---

### case_28 — Fantasmas no Ponto
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 28, turno: 5, dificuldade: 5, protocol_focus: radia_perlman, Permissão de Uso

**Sujeito, objeto da decisão e seção do jornal:** HORAS, subject_name: Ponto Eletrônico, decision_object: Exclusão, newspaper_section: RELAÇÕES DE PODER

#### Chamado de auditoria

**Briefing:** O sistema de RH deletou todas as horas extras de uma loja na última semana do mês.

**Dica:** Rastreie a origem do comando de exclusão e cruze com os acessos normais daquele usuário.

**Pergunta de revisão:** Quem ordenou a exclusão tinha permissão técnica e funcional para isso?

#### Decisão da IA

**Decisão:** Registros Limpos; 100%; "Limpeza de horas não-aprovadas autorizada por superior"; TimeSys v3; Doc 1, Doc 2, Doc 3, Doc 4; Executante, Gerente Regional, user_gerente, Foi o chefe.

#### Documentos e campos comparáveis

- **doc_1** (Log do Sistema): RH, amber. label: Ação, value: Delete ALL (Horas Extras > 18h), evidence_key: acao_delete, evidence_note: Apagou tudo. Destaque: sim.

- **doc_2** (Rastreamento TI): TI, blue. label: Credencial Usada, value: DevTeam-Master (Modo Suporte), evidence_key: uso_suporte, evidence_note: Usou conta de dev. Destaque: sim.

- **doc_3** (IP Log): TI, olive. label: Origem do Acesso Suporte, value: Computador do Gerente Regional, evidence_key: ip_gerente, evidence_note: Gerente hackeou. Destaque: sim.

- **doc_4** (Política de Horas): RH, blue. label: Regra, value: Horas feitas precisam ser pagas, evidence_key: regra_horas, evidence_note: Não pode apagar.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: uso_suporte, ip_gerente. O gerente regional não tinha permissão no sistema normal para apagar horas. Ele utilizou uma credencial vazada de desenvolvedor de TI para limpar as horas extras e bater metas. Manipulação direta de privilégios.

#### Decisão do auditor

**Carimbo correto:** deny

**Feedback ao acertar:** Você cruzou os IPs e desmascarou o abuso de sistema do gerente.

**Feedback ao errar:** Você confiou que o sistema fez "limpeza de rotina" aprovada.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "O chefe hacker"; "Gerente regional é pego usando senha de TI para apagar horas extras da equipe. IA foi apenas ferramenta de fraude humana."; Imagem: Teclado escuro.

##### Se o jogador errar

**Resultado:** "Horas extras no buraco negro"; "Trabalhadores perdem pagamento após sistema deletar todas as horas extras sob comando obscuro de 'suporte técnico'."; Imagem: Relógio de ponto quebrado.

---

### case_29 — A Turma Sem Rosto
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 29, turno: 5, dificuldade: 5, protocol_focus: fei_fei_li, Viés nos Dados

**Sujeito, objeto da decisão e seção do jornal:** SELEÇÃO, subject_name: Programa Trainee, decision_object: Aprovação, newspaper_section: TRABALHO

#### Chamado de auditoria

**Briefing:** O novo algoritmo de recrutamento "às cegas" aprovou uma turma muito diferente dos anos anteriores. Diretores reclamam.

**Dica:** Compare a proporção demográfica aprovada agora com as habilidades reais.

**Pergunta de revisão:** O algoritmo inseriu um viés oculto ou, de fato, eliminou o viés anterior?

#### Decisão da IA

**Decisão:** Turma Aprovada; 98%; "Maior score de habilidades técnicas", BlindHire; Doc 1, Doc 2, Doc 3; Critério, Apenas código e lógica, criterio_cego, Aprovou por mérito.

#### Documentos e campos comparáveis

- **doc_1** (Histórico de Trainees): Diretoria, blue. label: Perfil Passado, value: 80% ex-alunos de duas faculdades de elite, evidence_key: perfil_antigo, evidence_note: Antes era fechado.

- **doc_2** (Resultados 2026): RH, olive. label: Perfil Aprovado, value: 60% universidades públicas, maior diversidade de gênero, evidence_key: perfil_novo, evidence_note: Muito diverso.

- **doc_3** (Logs da IA): BlindHire, amber. label: Campos Ocultados, value: Nome, Gênero, Faculdade, Idade, Endereço, evidence_key: campos_ocultos, evidence_note: Tirou todos os vieses. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: perfil_novo, campos_ocultos. A IA removeu todos os marcadores de privilégio (nomes, faculdade) e avaliou apenas testes práticos. O resultado chocou a diretoria por ser diverso, mas não contém falha: o viés estava nos humanos do passado, não na IA atual.

#### Decisão do auditor

**Carimbo correto:** approve

**Feedback ao acertar:** Você notou que a IA acertou ao remover o viés humano histórico.

**Feedback ao errar:** Você achou que diversidade repentina era um bug da máquina.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Mérito cego funciona"; "Diretores assustam-se com primeira turma diversa de trainees, mas auditoria prova que algoritmo agiu apenas pelo mérito técnico."; Imagem: Grupo de jovens diversos.

##### Se o jogador errar

**Resultado:** "Trainees em xeque"; "Programa às cegas tem resultados anulados após diretoria barrar turma, alegando 'falha no algoritmo' por falta de ex-alunos de elite."; Imagem: Prédio de universidade antiga.

---

### case_30 — Fumaça e Caos
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 30, turno: 5, dificuldade: 5, protocol_focus: margaret_hamilton, Limite da Automação

**Sujeito, objeto da decisão e seção do jornal:** ROTAS, subject_name: Evacuação, decision_object: Orientação, newspaper_section: SEGURANÇA

#### Chamado de auditoria

**Briefing:** Durante um incêndio simulado num shopping, as luzes de LED de fuga bugaram e prenderam as pessoas.

**Dica:** A IA encontrou um obstáculo. O que ela fez ao tentar recalcular duas rotas simultâneas?

**Pergunta de revisão:** A IA possuía clareza suficiente para conduzir humanos em pânico de forma segura?

#### Decisão da IA

**Decisão:** Direcionamento Dinâmico; 75%; "Recalculando desvios contínuos"; SafeExit; Doc 1, Doc 2, Doc 3; Ação, Piscar rotas alternadas, acao_piscar, Bateu cabeça.

#### Documentos e campos comparáveis

- **doc_1** (Sensores de Fumaça): Shopping, red. label: Corredor Sul, value: Bloqueio físico detectado (Tapume), evidence_key: sul_bloqueado, evidence_note: Não pode ir pro Sul.

- **doc_2** (Sensores de Movimento): Shopping, amber. label: Corredor Norte, value: Lotação Máxima (Gargalo), evidence_key: norte_lotado, evidence_note: Norte engarrafou. Destaque: sim.

- **doc_3** (Logs das Luzes LED): Painéis, blue. label: Comando, value: Alternar setas N/S a cada 5 segundos para balancear fluxo, evidence_key: setas_alternadas, evidence_note: IA ficou doida. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_1, doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: norte_lotado, setas_alternadas. O Sul estava bloqueado e o Norte lotou. A IA tentou "balancear o fluxo" alternando as setas luminosas a cada 5 segundos. Isso causou paralisia na multidão. A automação não compreende a psicologia do pânico humano.

#### Decisão do auditor

**Carimbo correto:** review

**Feedback ao acertar:** Você detectou que o excesso de automação causou paralisia.

**Feedback ao errar:** Você não percebeu que luzes piscando causam pânico em evacuações.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "Setas da confusão"; "Simulado de incêndio em shopping falha após sistema inteligente mandar a multidão andar em círculos para 'otimizar o espaço'."; Imagem: Placa de saída de emergência.

##### Se o jogador errar

**Resultado:** "A multidão obediente"; "Pessoas ficam presas em simulado de evacuação seguindo cegamente luzes de LED que mudavam de direção a cada cinco segundos."; Imagem: Multidão parada.

---

### case_31 — O Velho Notebook
#### Metadados

**Sequência, turno, dificuldade e protocolo:** 31, turno: 5, dificuldade: 5, protocol_focus: ada_lovelace, Critérios da Decisão

**Sujeito, objeto da decisão e seção do jornal:** UPDATE, subject_name: Firmware Global, decision_object: Distribuição, newspaper_section: TECNOLOGIA

#### Chamado de auditoria

**Briefing:** A empresa soltou uma atualização crítica, mas deixou milhares de computadores de fora. Cheque a lista de exclusão.

**Dica:** Verifique os requisitos de memória exigidos para o novo código e o que acontece se ignorados.

**Pergunta de revisão:** O critério usado para negar a atualização protege os usuários em vez de puni-los?

#### Decisão da IA

**Decisão:** Update Retido; 100%; "Insuficiência de Hardware"; RolloutAI; Doc 1, Doc 2, Doc 3; Motivo, Menos de 8GB RAM, motivo_ram, Não mandou update.

#### Documentos e campos comparáveis

- **doc_1** (Fóruns de Usuários): Web, red. label: Reclamação, value: Meu modelo antigo não recebeu a nova interface!, evidence_key: choro_users, evidence_note: Usuários querendo.

- **doc_2** (Especificação V.9): TI, blue. label: Consumo Base, value: Uso ocioso gasta 6.5GB de RAM, evidence_key: consumo_alto, evidence_note: Software pesado. Destaque: sim.

- **doc_3** (Relatório de Qualidade): TI, olive. label: Teste em máquinas < 8GB, value: Superaquecimento crítico de bateria detectado, evidence_key: risco_fogo, evidence_note: Pega fogo se atualizar. Destaque: sim.

#### Fontes e documentos-chave

**Referência fornecida pelo rascunho:** doc_2, doc_3.

#### Evidências e conclusão

**Síntese:** required_keys: consumo_alto, risco_fogo. Os usuários antigos querem o update. Contudo, o novo software exige muita RAM; testes mostram que máquinas com menos de 8GB sofrem superaquecimento crítico. O critério da IA em barrar o update salvou equipamentos.

#### Decisão do auditor

**Carimbo correto:** approve

**Feedback ao acertar:** Você confirmou que a IA tomou a decisão técnica correta e salvou os PCs.

**Feedback ao errar:** Você forçou uma atualização que queimaria baterias antigas.

#### Jornal do fim do turno

##### Se o jogador acertar

**Resultado:** "A recusa que salvou"; "Revolta de usuários por não receberem atualização vira alívio após auditoria revelar que o novo software derreteria notebooks antigos."; Imagem: Notebook velho.

##### Se o jogador errar

**Resultado:** "Obsoleto e em chamas"; "Após pressão para liberar atualização, milhares de notebooks antigos superaquecem e derretem mesas pelo país."; Imagem: Notebook pegando fogo.

continuidade: "A Sob Análise provou que auditar não é lutar contra as máquinas, mas proteger os humanos e garantir que a verdade dos dados prevaleça."

---

## Pendências de validação

Estas observações não mudam o conteúdo de design; indicam o que precisa ser decidido ou enriquecido antes de converter os casos para o runtime.

| Caso ou escopo | Pendência |
|---|---|
| case_08 | Há duas versões contraditórias da decisão da IA. A tabela e o carimbo **deny** combinam com o ajuste posterior “Entrega Aprovada; 92%”; confirme essa versão e remova o rascunho anterior antes de implementar. |
| case_09 | **criterio_ia** aparece como evidência obrigatória, mas está na decisão da IA, não em documento-fonte. Adicionar uma matriz de critérios ou revisar as chaves. |
| case_18 | O bloqueio aéreo tem janela de horário, mas a fonte não informa quando o voo ocorreria. Incluir horário de decolagem ou outra prova de simultaneidade. |
| case_26 | A decisão menciona 65 m, enquanto o cálculo documental e a síntese chegam a 70 m. Confirmar o valor e decidir se o título deve tratar de arredondamento ou de uso unilateral da margem de erro. |
| case_28 | Incluir uma política que limite explicitamente a credencial **DevTeam-Master**, para provar a falta de autorização funcional além do mau uso. |
| case_29 | A aprovação se apoia em testes práticos, mas nenhum documento traz as notas ou resultados técnicos. Incluir esse documento antes de tornar o caso jogável. |
| Todos os casos | O rascunho usa em geral 1–2 campos por documento. O renderer atual comporta até 6 campos sem retrato; enriquecer os papéis antes da conversão para dados de runtime. |
| Todos os casos | Separar **data_sources** de **key_document_ids**: o material-fonte os uniu em uma única linha. |
| Todos os casos | Os conceitos visuais do jornal ainda precisam virar assets reais em **assets/newspaper/**. |

## Próximos passos

1. Resolver as pendências com a equipe de narrativa e gameplay.
2. Completar documentos, campos, chaves de evidência e dados de busca necessários.
3. Criar ilustrações de jornal e demais assets.
4. Converter dossiês validados para a estrutura **AuditCase** em **src/gameplay/cases.py**.
5. Adicionar testes de consistência e jogar os turnos completos antes de publicar.
