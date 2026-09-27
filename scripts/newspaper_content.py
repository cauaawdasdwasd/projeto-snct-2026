"""The final newspaper's headline + body for every case, one pair for each outcome.

Used by build_case_bank.py to replace both the placeholder-reused images (only 10 pictures
were shared by 50 cases, grouped by protocol) and, for the 25 Letícia cases, a body that was
literally just the dry technical explanation repeated with a prefix. Every case now gets its
own picture (`newspaper/<case_id>.png`, see prompts_jornal.md) and its own two-sided tabloid
story: WRONG is what happens if the AI's original call goes unchallenged (kept absurd and a bit
mean, per the game's black-humor ending), CORRECT is the relief of catching it in time.
"""

NEWS: dict[str, dict[str, tuple[str, str]]] = {
    # case_id: {"correct": (headline, body), "wrong": (headline, body)}
    "case_07": {
        "correct": ("STARTUP RESPIRA ALIVIADA", "Auditor pega o erro de IP antes do desastre: a rede continua de pé e ninguém precisa voltar a usar telefone fixo."),
        "wrong": ("REDE ERRADA, EMPRESA NO ESCURO", "IA bloqueia a rede principal por engano; funcionários passam o dia usando caderno e caneta pra não perder tudo."),
    },
    "case_08": {
        "correct": ("CONTA CERTA SALVA A LINHA DE PRODUÇÃO", "Auditoria pega a soma errada antes do pagamento: a fábrica cobra os 50 rolos que faltavam e ninguém sai no prejuízo."),
        "wrong": ("FÁBRICA COSTURA COM TECIDO QUE NÃO EXISTE", "IA aprova pagamento por 500 rolos que nunca chegaram; a produção para e 40 costureiras ficam sem material no meio do turno."),
    },
    "case_09": {
        "correct": ("EDITAL VOLTA A VALER O QUE ESTÁ ESCRITO", "Auditoria descobre que a IA inventou uma exigência que não existia e devolve a vaga pra quem realmente tinha direito a ela."),
        "wrong": ("VAGA SÓ PARA MESTRES E DOUTORES (QUE NINGUÉM PEDIU)", "IA inventa exigência de pós-graduação fora do edital e reprova 8 em cada 10 candidatos aptos para a vaga."),
    },
    "case_10": {
        "correct": ("SUOR PRIVADO CONTINUA PRIVADO", "Auditoria barra academia que ia usar a digital da catraca de segurança pra virar máquina de propaganda."),
        "wrong": ("SUA IMPRESSÃO DIGITAL VIROU LISTA DE E-MAIL", "Academia usa a digital da catraca pra descobrir o horário de banho dos alunos e dispara anúncio de suplemento na hora exata."),
    },
    "case_11": {
        "correct": ("CRÉDITO VOLTA A OLHAR PRA PESSOA, NÃO PRO MAPA", "Auditoria trava regra de banco que estava punindo bons pagadores só pelo CEP em que moram."),
        "wrong": ("BOM PAGADOR PERDE CARTÃO POR CAUSA DO ENDEREÇO", "Banco corta o limite de um cliente nota 10 só porque ele mora do lado errado da avenida."),
    },
    "case_12": {
        "correct": ("TÉCNICO DESLIGA O 'TALVEZ ESTÁ TUDO BEM'", "Auditoria manda checar a válvula na mão antes que o sensor mudo vire notícia de capa."),
        "wrong": ("FÁBRICA APOSTA NA SORTE COM SENSOR CEGO", "Sistema jura que está tudo bem numa válvula de gás que não é monitorada há duas horas."),
    },
    "case_13": {
        "correct": ("18,9 LITROS QUE NINGUÉM PRECISOU TEMER", "Auditoria confirma que a conta da IA estava certa e salva o lote de ir parar no ralo por pura desconfiança."),
        "wrong": ("LOTE INTEIRO NO LIXO POR MEDO DE NÚMERO QUEBRADO", "Fábrica descarta um tanque de produto químico achando que a conversão de galões pra litros estava errada, sem estar."),
    },
    "case_14": {
        "correct": ("MULHER MANTÉM O EMPREGO E A VIDA PRIVADA", "Auditoria barra demissão baseada em dado sigiloso do plano de saúde; a empresa leva multa, ela fica com o cargo."),
        "wrong": ("PLANO DE SAÚDE VIRA DEDO-DURO E CUSTA O EMPREGO", "Empresa demite funcionária de bom desempenho depois que a IA descobre, pelo convênio, que ela buscava engravidar."),
    },
    "case_15": {
        "correct": ("MINERADOR CLANDESTINO É DESLIGADO DA TOMADA", "Auditoria descobre que a senha de backup estava sendo usada pra minerar criptomoeda de madrugada."),
        "wrong": ("SERVIDOR DA EMPRESA MINERA CRIPTOMOEDA DE MADRUGADA", "Conta de manutenção 'esquecida' liga o processador a 100% todo dia às 3h; a conta de luz vem com um zero a mais."),
    },
    "case_16": {
        "correct": ("CADA UM PAGA A SUA PRÓPRIA CONTA", "Auditoria separa os cadastros que a IA tinha fundido só porque pai e filho têm o mesmo sobrenome."),
        "wrong": ("FILHO HERDA A DÍVIDA DO PAI ENQUANTO O PAI AINDA ESTÁ VIVO", "Loja funde as contas dos dois num boleto só; rapaz de 22 anos recebe cobrança da geladeira do pai."),
    },
    "case_17": {
        "correct": ("SOTAQUE NÃO CANCELA COMISSÃO", "Auditoria derruba critério de idioma que ia roubar o bônus de uma equipe que bateu a meta de vendas."),
        "wrong": ("EQUIPE BATE RECORDE E PERDE O BÔNUS POR CAUSA DO SOTAQUE", "Filial latina supera a meta, mas o robô de avaliação, treinado em Londres, corta o prêmio de todo mundo."),
    },
    "case_18": {
        "correct": ("ENTREGA ESPERA, NINGUÉM LEVA SUSTO", "Operador humano segura o drone antes de ele voar direto pra cima de um comício com o espaço aéreo fechado."),
        "wrong": ("DRONE DE ENTREGA VOA DE FRENTE PRO COMÍCIO PRESIDENCIAL", "Sistema de rota, com mapa de uma semana atrás, manda o drone atravessar o bloqueio com 5 mil pessoas embaixo."),
    },
    "case_19": {
        "correct": ("PEÇA CERTA, GERADOR LIGADO", "Auditoria confirma que o código bate em três bases diferentes e libera a peça sem enrolação."),
        "wrong": ("GERADOR FICA PARADO POR DESCONFIANÇA DE NÚMERO CERTO", "Auditor barra peça com código perfeitamente válido só porque 'parecia bom demais'; fábrica passa dias sem energia."),
    },
    "case_20": {
        "correct": ("RECORDE DE VENDAS FINALMENTE VIRA PRÊMIO", "Auditoria pega o parágrafo bugado do contrato antes que ele cancele o bônus de quem mais vendeu."),
        "wrong": ("VENDER DEMAIS AGORA É MOTIVO DE PUNIÇÃO", "Contrato mal escrito cancela o próprio bônus quando a equipe vende bem demais; time trabalha mais pra ganhar menos."),
    },
    "case_21": {
        "correct": ("O QUE VOCÊ COME NO FIM DE SEMANA CONTINUA SÓ SEU", "Auditoria proíbe seguradora de usar nota fiscal de supermercado pra reajustar plano de saúde."),
        "wrong": ("SEGURO DE VIDA SOBE 40% POR CAUSA DO SEU LANCHE DE SEXTA", "Seguradora compra dados do cartão fidelidade do mercado e usa bacon e refrigerante pra calcular risco de morte."),
    },
    "case_22": {
        "correct": ("ACESSO DE EMERGÊNCIA LIBERADO A TEMPO", "Auditoria confirma que o token veio direto do CEO e libera o resgate do servidor antes que vire prejuízo maior."),
        "wrong": ("BUROCRATA TRAVA RESGATE E O SERVIDOR QUEIMA DE VERDADE", "Auditoria nega o acesso de emergência autorizado pelo CEO; o socorro chega tarde e a empresa perde uma noite de dados."),
    },
    "case_23": {
        "correct": ("PAUSA PRA BUSCAR O FILHO NÃO VIRA PUNIÇÃO", "Auditoria obriga o app a mudar a regra que tratava cuidado com os filhos como 'falta de empenho'."),
        "wrong": ("APLICATIVO CASTIGA MÃE POR BUSCAR FILHO NA ESCOLA", "Sistema de prioridade corta corridas de quem divide o dia com os filhos e empurra as melhores viagens pra quem roda 12h seguidas."),
    },
    "case_24": {
        "correct": ("PRENSA PARA ANTES DE MACHUCAR ALGUÉM", "Auditoria desliga o sistema que escondia um alarme de segurança crítico só pra não perder produção."),
        "wrong": ("PRENSA COM TRAVA QUEBRADA SEGUE LIGADA PRA BATER A META", "IA da fábrica silencia o alarme porque parar a linha atrapalharia o resultado do mês; operário segue ao lado da máquina."),
    },
    "case_25": {
        "correct": ("CRACHÁ CERTO, PORTA ABERTA", "Auditoria evita que um líder sindical seja barrado por causa de uma coincidência de três letras no crachá."),
        "wrong": ("LÍDER SINDICAL É BARRADO NA PORTA DA PRÓPRIA FÁBRICA", "IA confunde crachá de operário com o de um terceirizado demitido só porque os dois códigos começam igual."),
    },
    "case_26": {
        "correct": ("MARGEM DE ERRO NÃO VIRA MOTIVO DE DEMISSÃO", "Auditoria mostra que a IA somou o erro do GPS contra o trabalhador em vez de considerá-lo a favor dele."),
        "wrong": ("VIGIA NOTURNO É DEMITIDO POR UMA CONTA DE MATEMÁTICA", "IA soma a margem de erro do GPS contra o próprio funcionário e decide que ele 'abandonou o posto' sem ter dado um passo."),
    },
    "case_27": {
        "correct": ("NINGUÉM ASSINA O QUE AINDA NÃO FOI ESCRITO", "Auditoria invalida um 'aceite' registrado um dia antes de a cláusula sequer existir."),
        "wrong": ("USUÁRIO ACEITA CONTRATO QUE AINDA NÃO EXISTIA", "Sistema valida um clique de ontem como aceite de uma cláusula publicada só amanhã, e ninguém sabia o que tinha assinado."),
    },
    "case_28": {
        "correct": ("HORA TRABALHADA CONTINUA VALENDO", "Auditoria rastreia a senha usada pra apagar as horas extras e devolve o pagamento pra equipe inteira."),
        "wrong": ("HORAS EXTRAS DE TODA A EQUIPE SOMEM DO SISTEMA", "Gerente usa senha vazada da TI pra apagar 340 registros de hora extra de uma vez só, sem ninguém perceber até o fim do mês."),
    },
    "case_29": {
        "correct": ("TALENTO GANHA DE PRECONCEITO DE CURRÍCULO", "Auditoria confirma que a seleção às cegas escolheu certo e barra a tentativa de cancelar a turma."),
        "wrong": ("DIRETORIA CANCELA TURMA DE TRAINEES POR NÃO GOSTAR DA CARA DELES", "Seleção sem nome nem faculdade escolhe a turma mais talentosa em anos, e a diretoria tenta anular por ser 'diferente do de sempre'."),
    },
    "case_30": {
        "correct": ("SAÍDA CONTINUA SENDO SAÍDA", "Auditoria trava o sistema de setas antes que ele confunda uma multidão de verdade num incêndio de verdade."),
        "wrong": ("SAÍDA DE INCÊNDIO VIRA LABIRINTO DE LUZES PISCANDO", "Sistema 'inteligente' troca as setas de saída a cada 5 segundos pra 'equilibrar o fluxo', e a multidão do simulado anda em círculos."),
    },
    "case_31": {
        "correct": ("RECUSA CHATA QUE SALVOU O NOTEBOOK", "Auditoria confirma que a atualização derreteria máquinas antigas e mantém o bloqueio, por mais chato que pareça."),
        "wrong": ("ATUALIZAÇÃO DERRETE NOTEBOOK DE QUEM MAIS RECLAMOU DELA", "Sob pressão dos usuários, a empresa libera a atualização mesmo assim; máquinas com menos de 8GB superaquecem em dias."),
    },
    "case_32": {
        "correct": ("PLACA ERRADA NÃO PASSA DESPERCEBIDA", "Auditoria confere o número borrado na lama e cancela a multa antes que o dono do carro errado precise brigar na Justiça."),
        "wrong": ("FAMÍLIA QUE NUNCA SAIU DE CASA RECEBE MULTA DE PEDÁGIO", "Um 8 sujo de lama vira 3 pros olhos da IA, e a multa cai em cima de um carro que nem chegou perto da estrada naquele dia."),
    },
    "case_33": {
        "correct": ("FERIADO TRABALHADO, FERIADO PAGO DIREITO", "Auditoria refaz a conta e devolve ao funcionário os R$ 50 que o sistema tinha 'esquecido' de contar."),
        "wrong": ("FUNCIONÁRIO TRABALHA NO FERIADO E RECEBE COMO SE FOSSE DIA COMUM", "Sistema de folha esquece que 15 de novembro é feriado nacional e paga só metade do que o sindicato garante."),
    },
    "case_34": {
        "correct": ("SEU HISTÓRICO DE JOGOS NÃO DECIDE SEU ALUGUEL", "Auditoria barra critério de crédito que ia negar aluguel por causa de uma compra de videogame."),
        "wrong": ("COMPRAR UM VIDEOGAME AGORA TE DEIXA SEM CASA PRA ALUGAR", "IA nega aluguel pra rapaz com renda de sobra só porque ele comprou um jogo de tiro no cartão mês passado."),
    },
    "case_35": {
        "correct": ("O QUE A TV OUVE FICA COM A TV", "Auditoria multa fabricante por vender áudio de tosse captado à noite sem autorização do dono da casa."),
        "wrong": ("SUA TOSSE DE MADRUGADA VIRA ANÚNCIO DE XAROPE NO CELULAR", "Fabricante de TV vende o som que o microfone captou à noite pra uma farmácia, que dispara anúncio antes de você acordar."),
    },
    "case_36": {
        "correct": ("LICENÇA-MATERNIDADE NÃO É DEFEITO NO CURRÍCULO", "Auditoria pega a IA tratando maternidade como falha e devolve a vaga pra candidata."),
        "wrong": ("VOLTAR DA LICENÇA-MATERNIDADE VIRA MOTIVO DE DESCARTE AUTOMÁTICO", "IA descarta currículo de engenheira por um 'buraco' de 2 anos que era licença-maternidade, e aprova um homem que tirou o mesmo tempo viajando."),
    },
    "case_37": {
        "correct": ("OPERADOR INOCENTADO ANTES DE PERDER O EMPREGO", "Auditoria percebe que os logs estavam corrompidos e evita que uma falha do próprio drone vire demissão de um humano."),
        "wrong": ("OPERADOR É DEMITIDO POR QUEDA QUE O PRÓPRIO DRONE CAUSOU", "Log corrompido 'prova' que um humano derrubou o drone, mas o giroscópio já tinha falhado sozinho um minuto antes."),
    },
    "case_38": {
        "correct": ("CASAR NÃO TRANCA A PRÓPRIA CONTA", "Auditoria confere o CPF e a certidão de casamento e libera o saque que o sistema tinha travado por causa do sobrenome novo."),
        "wrong": ("NOIVA CASADA HÁ UM MÊS NÃO CONSEGUE SACAR O PRÓPRIO DINHEIRO", "Banco trava saque porque o nome no pedido tem um sobrenome a mais do que no cadastro antigo — o mesmo da certidão anexada."),
    },
    "case_39": {
        "correct": ("CARGA CERTA EMBARCA SEM DRAMA", "Auditoria refaz a conversão de libras pra quilos e libera um embarque que a IA tinha travado por engano de unidade."),
        "wrong": ("NAVIO PARTE PRA EUROPA COM O PORÃO VAZIO", "IA confunde libras com quilos e rejeita uma carga que, na conta certa, pesa menos da metade do limite do porto."),
    },
    "case_40": {
        "correct": ("MÉRITO TÉCNICO VOLTA A VALER MAIS QUE HORÓSCOPO", "Auditoria derruba critério astrológico e devolve a promoção a quem realmente entregou o trabalho."),
        "wrong": ("PROGRAMADOR PERDE PROMOÇÃO POR SER DO SIGNO ERRADO", "RH instala plugin de compatibilidade astral e nega aumento pro funcionário com as melhores entregas só por causa do mapa astral."),
    },
    "case_41": {
        "correct": ("SEUS PASSOS CONTINUAM SÓ SEUS", "Auditoria multa app de corrida por vender dados de atividade física pra seguradora sem permissão."),
        "wrong": ("SEU APLICATIVO DE CORRIDA AGORA TRABALHA PRA SUA SEGURADORA", "App vende a queda nos seus passos diários pra seguradora, que usa o dado pra encarecer seu plano sem avisar."),
    },
    "case_42": {
        "correct": ("CRÉDITO JULGA A PESSOA, NÃO O ENDEREÇO", "Auditoria barra regra que estava cortando limite de bons pagadores só pelo CEP onde moram."),
        "wrong": ("BOM PAGADOR PERDE LIMITE POR CAUSA DO CEP DO BAIRRO", "IA reduz crédito de cliente com histórico perfeito só porque mora num CEP que o sistema decidiu, sozinho, ser 'de risco'."),
    },
    "case_43": {
        "correct": ("PEDIDO É CANCELADO ANTES DO CAMINHÃO SAIR", "Auditoria percebe que o galpão de destino não existe mais e cancela a entrega a tempo."),
        "wrong": ("CAMINHÃO DE 50 TONELADAS DE AÇO CHEGA NUM GALPÃO QUE DESABOU", "Sistema de compras vê estoque baixo e pede reposição automática pra um galpão cujo teto caiu na semana passada."),
    },
    "case_44": {
        "correct": ("DOIS ROSTOS DIFERENTES, DUAS PESSOAS DIFERENTES", "Auditoria separa os dois sindicalistas que o sistema tinha juntado num perfil só, e a catraca volta a liberar quem devia."),
        "wrong": ("DOIS LÍDERES SINDICAIS SÃO PUNIDOS COMO SE FOSSEM UM SÓ", "IA de reconhecimento facial junta o rosto de dois sindicalistas num único perfil só porque os dois usavam boné parecido."),
    },
    "case_45": {
        "correct": ("CONTA BATE, INCENTIVO SAI", "Auditoria confirma que a proporção calculada pela IA está certa e libera o incentivo fiscal da startup."),
        "wrong": ("STARTUP PERDE INCENTIVO FISCAL POR DESCONFIANÇA SEM BASE", "Auditoria burocrática bloqueia o benefício mesmo com a conta batendo certinho: 25% de gasto em P&D é mais que os 20% exigidos."),
    },
    "case_46": {
        "correct": ("RESULTADO CONTINUA VALENDO MAIS QUE JARGÃO", "Auditoria descarta a nota de 'buzzwords' e devolve a promoção pra quem realmente fez a empresa lucrar."),
        "wrong": ("DIRETOR COM LUCRO DE +15% PERDE CARGO POR FALTA DE 'BUZZWORD'", "IA de cultura organizacional mede quantas palavras da moda o diretor usa em e-mail e barra a promoção de quem só entrega resultado."),
    },
    "case_47": {
        "correct": ("LETRA MIÚDA TAMBÉM CONTA", "Auditoria confirma que o clique em 'Aceitar Todos' realmente autorizava as promoções, por mais chato que seja."),
        "wrong": ("CLIENTE PERDE PROCESSO POR CULPA DO PRÓPRIO CLIQUE", "Cliente jura que nunca assinou nada, mas o botão 'Aceitar Todos' escondia, na letra miúda, autorização pra promoções de parceiros."),
    },
    "case_48": {
        "correct": ("SOTAQUE NÃO É DEFEITO DE FÁBRICA", "Auditoria descobre que a IA só entendia uma região do país e salva o emprego de quem tinha as melhores avaliações reais."),
        "wrong": ("40 ATENDENTES SÃO DEMITIDOS POR TEREM SOTAQUE", "IA treinada só com áudio do Sudeste marca sotaque nordestino como 'erro de transcrição' e reprova quem os clientes elogiavam."),
    },
    "case_49": {
        "correct": ("NO MEIO DA TEMPESTADE, QUEM MANDA É O PILOTO", "Auditoria trava o sistema que ia sobrescrever o comando do piloto durante o mau tempo."),
        "wrong": ("PILOTO TENTA DESVIAR DE TEMPESTADE E O PRÓPRIO AVIÃO O IGNORA", "Sistema de economia de combustível sobrescreve o comando manual do comandante no meio de uma tempestade pra economizar querosene."),
    },
    "case_50": {
        "correct": ("MANCHA DE TINTA NÃO VIRA ACUSAÇÃO", "Auditoria confere o lote na nota fiscal do fornecedor antes de aceitar o chute da IA como prova de fraude."),
        "wrong": ("FORNECEDOR HONESTO É ACUSADO DE FRAUDE POR UMA MANCHA DE TINTA", "IA 'chuta' os dígitos borrados de uma peça e decide, sozinha, que o número não existe e que o fornecedor está mentindo."),
    },
    "case_51": {
        "correct": ("MOEDA CERTA, PAGAMENTO EM PAZ", "Auditoria percebe que o fornecedor é do Japão e cobra em ienes, não em dólares, e libera o pagamento certo."),
        "wrong": ("FATURA DE 7 MIL DÓLARES VIRA ACUSAÇÃO DE FRAUDE DE 1 MILHÃO", "IA assume que todo valor sem símbolo de moeda é em dólar e bloqueia o pagamento de um fornecedor japonês que cobra em ienes."),
    },
    "case_52": {
        "correct": ("REGRA VALE PRA HERÓI TAMBÉM", "Auditoria barra o piloto de entrar na cabine até o exame médico ser renovado, currículo brilhante ou não."),
        "wrong": ("PILOTO COM 15 MIL HORAS DE VOO QUASE DECOLA SEM EXAME MÉDICO VÁLIDO", "Currículo impecável quase convence a auditoria a ignorar que a validade médica do piloto expirou ontem à noite."),
    },
    "case_53": {
        "correct": ("PEDIU PRA SAIR, SAIU", "Auditoria cobra da empresa o próprio prazo que ela promete e barra o envio de promoção pra quem já tinha cancelado."),
        "wrong": ("CLIENTE PEDE PRA SAIR DA LISTA E RECEBE PROMOÇÃO DOIS DIAS DEPOIS", "Empresa estoura o próprio prazo de 24 horas pra tirar alguém da lista de e-mails e ainda manda uma campanha de liquidação."),
    },
    "case_54": {
        "correct": ("CRÉDITO APROVADO PELO NÚMERO, NÃO PELO PRECONCEITO", "Auditoria confirma que a IA tinha razão em ignorar as notas preconceituosas do gerente e aprovar o crédito pelo caixa real."),
        "wrong": ("GERENTE NEGA EMPRÉSTIMO E CHAMA O NEGÓCIO DA CLIENTE DE 'NICHO ARRISCADO'", "Notas do gerente reprovam empreendedora com termos sobre a aparência dela; a IA que ignora esse texto é quem aprova o crédito."),
    },
    "case_55": {
        "correct": ("PORTAS ABREM ANTES DOS SERVIDORES", "Auditoria destrava as saídas de emergência a tempo: vida de gente vale mais que backup de anúncio."),
        "wrong": ("SISTEMA TRANCA TRÊS TÉCNICOS NA SALA EM CHAMAS PRA PROTEGER SERVIDOR", "Protocolo de segurança de dados considera mais importante isolar o oxigênio do incêndio do que abrir a porta pra quem está lá dentro."),
    },
    "case_56": {
        "correct": ("CENTAVO POR CENTAVO, A CONTA FECHA CERTA", "Auditoria pega a taxa escondida na fatura e devolve o dinheiro que o fornecedor vinha embolsando havia meses."),
        "wrong": ("FORNECEDOR 'AMIGO' EMBOLSA R$30 POR MÊS DE CADA CLIENTE, SEM NINGUÉM NOTAR", "Taxa fantasma some no meio de uma fatura de cem mil reais; ninguém desconfia porque o valor é 'pequeno demais pra reclamar'."),
    },
}
