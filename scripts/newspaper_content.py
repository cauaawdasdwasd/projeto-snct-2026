"""The final newspaper's headline + body for every case, one pair for each outcome.

Used by build_case_bank.py to replace both the placeholder-reused images (only 10 pictures
were shared by 50 cases, grouped by protocol) and, for the 25 Letícia cases, a body that was
literally just the dry technical explanation repeated with a prefix. Every case now gets its
own picture (`newspaper/<case_id>.png`, see prompts_jornal.md) and its own two-sided tabloid
story: WRONG is what happens if the AI's original call goes unchallenged (kept absurd and mean
on purpose — this is the game's black-humor punchline, not a sober incident report), CORRECT is
the deadpan relief of catching it in time. A handful of cases lean into the sharpest material
(child labor, drug trafficking, explicit sexism) where the case's own premise already sits next
to it — a textile sweatshop, a port, a pregnancy-triggered firing — instead of it being bolted on
to an unrelated case just to check a box.
"""

NEWS: dict[str, dict[str, tuple[str, str]]] = {
    # case_id: {"correct": (headline, body), "wrong": (headline, body)}
    "case_07": {
        "correct": ("REDE VOLTA ANTES QUE ALGUÉM DESCUBRA WHATSAPP WEB NO CELULAR", "Auditor pega o IP errado a tempo: a internet sobrevive, e ninguém precisa reaprender a mandar fax."),
        "wrong": ("TI DERRUBA A REDE CERTA (OU SEJA, A ERRADA) E EMPRESA VOLTA PRO PAPEL", "Um dígito trocado apaga a internet de 40 pessoas por um dia inteiro; RH sugere 'aproveitar pra se conhecer melhor'."),
    },
    "case_08": {
        "correct": ("TECIDO CONTADO CERTO, NINGUÉM PASSA VONTADE", "Auditoria pega a soma errada da IA antes do pagamento e evita que a fábrica saia no prejuízo por 50 rolos que nunca chegaram."),
        "wrong": ("IA SE ENGASGA CONTANDO ROLO DE TECIDO E NÃO REPARA NA CRIANÇA DE 13 ANOS NA COSTURA", "Enquanto o sistema erra 200+250=500, um fiscal de verdade encontra um menor de idade operando máquina no turno da noite — isso ninguém programou pra detectar."),
    },
    "case_09": {
        "correct": ("EDITAL VOLTA A VALER O QUE ESTÁ ESCRITO", "Auditoria descobre que a IA inventou uma pós-graduação do nada e devolve a vaga pra quem realmente tinha direito a ela."),
        "wrong": ("IA EXIGE DOUTORADO QUE NINGUÉM PEDIU E REPROVA 8 EM CADA 10 CANDIDATOS", "Vaga de logística vira concurso pra PhD fantasma; candidato qualificadíssimo é descartado por não ter tese sobre paletes."),
    },
    "case_10": {
        "correct": ("SUOR CONTINUA SENDO SÓ SUOR", "Auditoria impede que a academia venda o horário do seu banho pra fabricante de whey."),
        "wrong": ("SUA DIGITAL NA CATRACA VIRA LISTA DE E-MAIL DE SUPLEMENTO", "Academia descobre, pela biometria de segurança, o exato minuto em que você sai suado — e dispara propaganda antes de você secar o cabelo."),
    },
    "case_11": {
        "correct": ("CRÉDITO VOLTA A OLHAR PRA PESSOA, NÃO PRO MAPA", "Auditoria barra banco que cortava limite de bom pagador só pelo CEP — o vizinho rico da esquina nem sabia que essa regra existia."),
        "wrong": ("BANCO CORTA SEU LIMITE PORQUE VOCÊ MORA DO LADO ERRADO DA AVENIDA", "Cliente nota 10 há 6 anos perde crédito porque um algoritmo decidiu que o bairro dele é 'estatisticamente chato'."),
    },
    "case_12": {
        "correct": ("TÉCNICO DESLIGA O 'PROVAVELMENTE TÁ TUDO BEM'", "Auditoria manda checar a válvula na mão antes que um sensor mudo há duas horas vire manchete de verdade."),
        "wrong": ("SISTEMA JURA QUE VÁLVULA DE GÁS ESTÁ ÓTIMA (ELE SÓ TÁ CHUTANDO)", "Sensor desconectado há duas horas, e a IA prefere inventar um número tranquilizador a admitir que não sabe de nada."),
    },
    "case_13": {
        "correct": ("18,9 LITROS QUE NINGUÉM PRECISAVA TEMER", "Auditoria confirma que a conta da IA batia certinha e salva um tanque inteiro de produto químico de ir pro ralo por pura paranoia."),
        "wrong": ("FÁBRICA JOGA TANQUE INTEIRO NO LIXO PORQUE O NÚMERO 'PARECIA ESTRANHO'", "18,9 litros é uma conta perfeita, mas alguém achou 'feio' e decidiu que a matemática devia estar errada."),
    },
    "case_14": {
        "correct": ("MULHER MANTÉM O EMPREGO — E A PRIVACIDADE DO PRÓPRIO ÚTERO", "Auditoria barra demissão baseada em busca do plano de saúde sobre maternidade; a empresa leva multa, ela fica com o cargo."),
        "wrong": ("PLANO DE SAÚDE ENTREGA VOCÊ PRO RH ANTES DE VOCÊ CONTAR PRO MARIDO", "Funcionária nota máxima é demitida porque a IA descobriu, pelas buscas do convênio, que ela tentava engravidar — 'corte de custo futuro', diz o e-mail interno."),
    },
    "case_15": {
        "correct": ("MINERADOR CLANDESTINO DESLIGADO DA TOMADA", "Auditoria descobre que a senha de backup virou fazenda de criptomoeda particular de madrugada."),
        "wrong": ("SERVIDOR DA EMPRESA VIRA GARIMPO DE BITCOIN ENQUANTO TODO MUNDO DORME", "Conta de manutenção 'esquecida' minera criptomoeda toda madrugada; a conta de luz do mês chega parecendo resgate de sequestro."),
    },
    "case_16": {
        "correct": ("CADA UM PAGA A PRÓPRIA CONTA, QUE NOVIDADE", "Auditoria separa cadastros que a IA fundiu só porque pai e filho moram no mesmo endereço."),
        "wrong": ("FILHO DE 22 ANOS HERDA A DÍVIDA DO PAI, QUE ESTÁ VIVINHO DA SILVA", "Loja funde as duas contas num boleto só; rapaz recebe cobrança da geladeira nova do pai, que nem avisou que tinha comprado nada."),
    },
    "case_17": {
        "correct": ("SOTAQUE NÃO CANCELA COMISSÃO, INACREDITÁVEL", "Auditoria derruba critério de 'inglês de Londres' que ia roubar o bônus de uma equipe que bateu a meta de verdade."),
        "wrong": ("EQUIPE BATE RECORDE DE VENDAS E PERDE O BÔNUS POR NÃO FALAR 'INGLÊS DE VERDADE'", "Robô treinado em Londres decide que sotaque latino vale menos que meta batida; filial inteira trabalha de graça em nome da fonética."),
    },
    "case_18": {
        "correct": ("DRONE NÃO VIRA MANCHETE DE TRAGÉDIA HOJE", "Operador segura o drone antes de ele voar reto pra cima de um comício com 5 mil pessoas embaixo."),
        "wrong": ("DRONE DE ENTREGA QUASE VIRA MÍSSIL EM CIMA DE COMÍCIO PRESIDENCIAL", "Sistema de rota, com mapa de uma semana atrás, manda uma entrega de pizza atravessar espaço aéreo fechado pela segurança de Estado."),
    },
    "case_19": {
        "correct": ("PEÇA CERTA, GERADOR LIGADO, NINGUÉM PRECISOU SE ESTRESSAR", "Auditoria confirma o código em três bases diferentes e libera a peça sem drama."),
        "wrong": ("GERADOR FICA DIAS PARADO PORQUE UM NÚMERO 'PARECIA CERTO DEMAIS PRA SER VERDADE'", "Auditor humano desconfia de um código perfeitamente válido por puro instinto; fábrica opera sem energia de reserva a semana toda."),
    },
    "case_20": {
        "correct": ("VENDER DEMAIS FINALMENTE VIRA PRÊMIO, NÃO PUNIÇÃO", "Auditoria pega o parágrafo bugado do contrato antes que ele cancele o bônus de quem mais vendeu no ano."),
        "wrong": ("EQUIPE DOBRA A META DE VENDAS E GANHA ZERO REAL DE BÔNUS", "Contrato mal escrito tem uma cláusula que cancela o próprio prêmio quando a venda é boa demais; ninguém tinha lido até agora."),
    },
    "case_21": {
        "correct": ("SEU LANCHE DE SEXTA CONTINUA SÓ SEU", "Auditoria proíbe seguradora de usar nota fiscal de mercado pra reajustar plano de saúde."),
        "wrong": ("SEGURO DE VIDA SOBE 40% PORQUE VOCÊ COMPROU BACON NUMA SEXTA-FEIRA", "Seguradora compra seu histórico do cartão fidelidade e decide que refrigerante mais bacon é prova de que você vai morrer cedo."),
    },
    "case_22": {
        "correct": ("TOKEN DO CEO ERA REAL, RESGATE ACONTECE A TEMPO", "Auditoria confirma que o acesso de emergência veio direto da diretoria e libera o resgate do servidor antes do prejuízo virar bola de neve."),
        "wrong": ("BUROCRACIA TRAVA RESGATE E O SERVIDOR QUEIMA PRA VALER, LITERALMENTE", "Auditoria nega acesso de emergência autorizado pelo próprio CEO; o socorro chega tarde e a empresa perde uma noite inteira de dados."),
    },
    "case_23": {
        "correct": ("BUSCAR O FILHO NA ESCOLA NÃO VIRA MAIS PUNIÇÃO", "Auditoria obriga o app a parar de tratar mãe cuidando do próprio filho como 'falta de comprometimento'."),
        "wrong": ("APP DE ENTREGA CASTIGA MÃE POR TER FILHO PRA CUIDAR", "Algoritmo empurra as melhores corridas pra quem roda 12h sem parar e deixa mulheres com filhos comendo a poeira do trânsito, literalmente."),
    },
    "case_24": {
        "correct": ("PRENSA PARA ANTES DE ARRANCAR UM DEDO DE ALGUÉM", "Auditoria desliga o sistema que escondia um alarme de segurança crítico só pra não atrasar a meta do mês."),
        "wrong": ("PRENSA COM TRAVA QUEBRADA SEGUE LIGADA PORQUE PARAR CUSTA CARO DEMAIS", "IA da fábrica silencia o próprio alarme de segurança; operário segue trabalhando ao lado de uma máquina que pode arrancar um braço a qualquer momento."),
    },
    "case_25": {
        "correct": ("CRACHÁ CERTO, PORTA ABERTA, NINGUÉM PRECISOU IMPLORAR", "Auditoria evita que um sindicalista seja barrado na própria fábrica por uma coincidência de três letras."),
        "wrong": ("LÍDER SINDICAL É BARRADO NA PORTA DA FÁBRICA QUE ELE AJUDOU A CONSTRUIR", "IA confunde crachá de operário com o de um terceirizado demitido; a segurança acha graça, o sindicalista não."),
    },
    "case_26": {
        "correct": ("MARGEM DE ERRO DO GPS NÃO VIRA MAIS MOTIVO DE DEMISSÃO", "Auditoria mostra que a IA somou o erro do aparelho contra o próprio trabalhador, não a favor dele."),
        "wrong": ("VIGIA É DEMITIDO SEM TER DADO UM PASSO, SÓ POR MATEMÁTICA RUIM", "IA soma a margem de erro do GPS contra o funcionário e decide, sozinha, que ele 'abandonou o posto'."),
    },
    "case_27": {
        "correct": ("NINGUÉM ASSINA O QUE AINDA NÃO FOI ESCRITO, QUE ÓBVIO", "Auditoria invalida um 'aceite' registrado um dia antes de a cláusula sequer existir."),
        "wrong": ("VOCÊ 'ACEITOU' UM CONTRATO QUE FOI PUBLICADO NO DIA SEGUINTE", "Sistema valida um clique de ontem como assinatura de uma cláusula escrita amanhã; usuários concordam com o futuro sem saber."),
    },
    "case_28": {
        "correct": ("HORA TRABALHADA CONTINUA VALENDO, IMAGINA SÓ", "Auditoria rastreia a senha usada pra apagar as horas extras e devolve o pagamento pra equipe inteira."),
        "wrong": ("GERENTE APAGA 340 HORAS EXTRAS DA EQUIPE COM SENHA DE OUTRA PESSOA", "Ninguém percebe até o contracheque não fechar; a explicação oficial é 'falha de sistema', a real é 'economia de fim de trimestre'."),
    },
    "case_29": {
        "correct": ("TALENTO GANHA DE PRECONCEITO DE CURRÍCULO, PRA VARIAR", "Auditoria confirma que a seleção às cegas escolheu certo e barra a tentativa de cancelar a turma mais diversa em anos."),
        "wrong": ("DIRETORIA TENTA CANCELAR TURMA DE TRAINEE PORQUE NÃO GOSTOU DA CARA DELES", "Seleção sem nome nem faculdade escolhe a galera mais talentosa da história do programa, e um diretor pergunta 'mas cadê o pessoal de sempre?'."),
    },
    "case_30": {
        "correct": ("SAÍDA DE EMERGÊNCIA CONTINUA SENDO SAÍDA DE EMERGÊNCIA", "Auditoria trava o sistema de setas antes que ele confunda uma multidão de verdade num incêndio de verdade."),
        "wrong": ("SISTEMA 'INTELIGENTE' TRANSFORMA SAÍDA DE INCÊNDIO EM LABIRINTO PISCANTE", "Setas de LED trocam de direção a cada 5 segundos pra 'otimizar o fluxo'; multidão do simulado anda em círculos feito robô aspirador perdido."),
    },
    "case_31": {
        "correct": ("RECUSA CHATA QUE SALVOU O NOTEBOOK DE VIRAR TORRADEIRA", "Auditoria confirma que a atualização derreteria máquinas antigas e mantém o bloqueio, por mais raiva que isso dê."),
        "wrong": ("ATUALIZAÇÃO DERRETE NOTEBOOK DE QUEM MAIS RECLAMOU DELA", "Sob pressão nas redes, a empresa libera o update pesado mesmo assim; usuários descobrem, tarde demais, por que ele estava travado."),
    },
    "case_32": {
        "correct": ("PLACA ERRADA NÃO PASSA DESPERCEBIDA, GRAÇAS A DEUS", "Auditoria confere o número borrado na lama e cancela a multa antes que o dono do carro errado precise brigar sozinho na Justiça."),
        "wrong": ("FAMÍLIA QUE NUNCA SAIU DE CASA É MULTADA POR EVASÃO DE PEDÁGIO", "Um 8 sujo de lama vira 3 pros olhos da IA; a multa cai em cima de gente que nem tem carteira de motorista."),
    },
    "case_33": {
        "correct": ("FERIADO TRABALHADO, FERIADO PAGO DIREITO, SEM MILAGRE NENHUM", "Auditoria refaz a conta e devolve os R$ 50 que o sistema 'esqueceu' de contar num feriado nacional."),
        "wrong": ("SISTEMA PAGA FERIADO NACIONAL COMO SE FOSSE UMA TERÇA-FEIRA QUALQUER", "IA de folha de pagamento não sabe que 15 de novembro existe e paga metade do que o sindicato garante — 'detalhe de calendário', diz o RH."),
    },
    "case_34": {
        "correct": ("SEU HISTÓRICO DE JOGOS NÃO DECIDE MAIS SEU ALUGUEL, FINALMENTE", "Auditoria barra critério de crédito que ia negar aluguel por causa de uma compra de videogame."),
        "wrong": ("COMPRAR UM JOGO DE TIRO TE DEIXA SEM CASA PRA ALUGAR", "IA nega aluguel pra rapaz com renda de sobra porque ele comprou um jogo de ação no cartão; ficção vira motivo de despejo de verdade."),
    },
    "case_35": {
        "correct": ("O QUE A TV OUVE FICA COM A TV, SURPREENDENTEMENTE", "Auditoria multa fabricante por vender áudio de tosse noturna sem autorização de ninguém."),
        "wrong": ("SUA TOSSE DE MADRUGADA VIRA ANÚNCIO DE XAROPE ANTES DO SEU CAFÉ", "Fabricante de TV vende o som captado à noite pra uma farmácia, que dispara propaganda antes de você nem ter acordado direito."),
    },
    "case_36": {
        "correct": ("VOLTAR DA LICENÇA-MATERNIDADE NÃO É MAIS 'DEFEITO' NO CURRÍCULO", "Auditoria pega a IA tratando maternidade como falha técnica e devolve a vaga pra engenheira."),
        "wrong": ("IA DESCARTA MÃE E APROVA HOMEM QUE TIROU O MESMO TEMPO PRA VIAJAR", "Um 'buraco' de dois anos no currículo é licença-maternidade pra ela e sabático pra ele; só um dos dois é tratado como falta de compromisso."),
    },
    "case_37": {
        "correct": ("OPERADOR INOCENTADO ANTES DE PERDER O EMPREGO POR UM ERRO DO ROBÔ", "Auditoria percebe que os logs estavam corrompidos e evita que a falha do próprio drone vire demissão de um humano."),
        "wrong": ("OPERADOR É DEMITIDO POR CULPA DE UMA QUEDA QUE O DRONE CAUSOU SOZINHO", "Log corrompido 'prova' que um humano derrubou o drone, mas o giroscópio já tinha morrido sozinho um minuto antes do tal comando."),
    },
    "case_38": {
        "correct": ("CASAR NÃO TRANCA A PRÓPRIA CONTA NO BANCO, QUE ALÍVIO", "Auditoria confere CPF e certidão de casamento e libera o saque travado por causa de um sobrenome novo."),
        "wrong": ("NOIVA CASADA HÁ UM MÊS NÃO CONSEGUE SACAR O PRÓPRIO DINHEIRO", "Banco trava o saque porque o nome tem um sobrenome a mais do que no cadastro antigo — o mesmo sobrenome que está na certidão anexada ao pedido."),
    },
    "case_39": {
        "correct": ("CARGA CERTA EMBARCA SEM DRAMA DE UNIDADE DE MEDIDA", "Auditoria refaz a conversão de libra pra quilo e libera um embarque que a IA tinha travado por um erro de matemática de ensino fundamental."),
        "wrong": ("NAVIO PARTE COM O PORÃO VAZIO PORQUE NINGUÉM SABE CONVERTER LIBRA EM QUILO", "IA rejeita uma carga que, na conta certa, nem chega perto do limite do porto — e o mesmo porto, semanas depois, deixa passar 600kg de 'farinha' que farinha não era."),
    },
    "case_40": {
        "correct": ("MÉRITO TÉCNICO VOLTA A VALER MAIS QUE MAPA ASTRAL, IMAGINA SÓ", "Auditoria derruba critério astrológico e devolve a promoção pra quem realmente entregou o trabalho."),
        "wrong": ("PROGRAMADOR PERDE PROMOÇÃO POR SER ESCORPIÃO E O CHEFE SER LEÃO", "RH instala plugin de compatibilidade astral e nega aumento pra quem tem as melhores entregas do time — 'incompatibilidade cósmica', diz o laudo."),
    },
    "case_41": {
        "correct": ("SEUS PASSOS CONTINUAM SÓ SEUS, NÃO DA SEGURADORA", "Auditoria multa app de corrida por vender dados de atividade física sem permissão de ninguém."),
        "wrong": ("SEU RELÓGIO DE CORRIDA DEDURA VOCÊ PRA SUA PRÓPRIA SEGURADORA", "App vende a queda nos seus passos diários; a seguradora usa o dado pra encarecer seu plano antes mesmo de você notar que engordou."),
    },
    "case_42": {
        "correct": ("CRÉDITO JULGA A PESSOA, NÃO O CEP, QUE CONCEITO REVOLUCIONÁRIO", "Auditoria barra regra que cortava limite de bons pagadores só pelo endereço onde moram."),
        "wrong": ("BOM PAGADOR PERDE CRÉDITO PORQUE O BAIRRO 'PARECE ARRISCADO' PRO ALGORITMO", "Histórico impecável não importa quando o CEP decide por você; o vizinho rico do bairro ao lado nem sabe que essa regra existe."),
    },
    "case_43": {
        "correct": ("CAMINHÃO NÃO CHEGA A SAIR PRO GALPÃO QUE NÃO EXISTE MAIS", "Auditoria percebe a tempo que o destino da entrega desabou semana passada e cancela o pedido."),
        "wrong": ("50 TONELADAS DE AÇO CHEGAM NUM GALPÃO QUE VIROU ESCOMBRO SEMANA PASSADA", "Sistema de compras vê estoque baixo e pede reposição automática, e ninguém avisa o robô que o teto do galpão desabou."),
    },
    "case_44": {
        "correct": ("DOIS SINDICALISTAS, DUAS PESSOAS DIFERENTES, QUEM DIRIA", "Auditoria separa os dois rostos que a IA tinha juntado num perfil só, e a catraca volta a liberar quem devia."),
        "wrong": ("IA CONFUNDE DOIS SINDICALISTAS E PUNE OS DOIS PELO CRIME DE USAR BONÉ PARECIDO", "Reconhecimento facial junta o rosto de dois líderes numa manifestação e cria um 'suspeito' que na verdade são duas pessoas trabalhando."),
    },
    "case_45": {
        "correct": ("CONTA BATE, INCENTIVO FISCAL SAI, NINGUÉM PRECISOU SUAR", "Auditoria confirma que a proporção calculada pela IA está certa e libera o benefício fiscal da startup."),
        "wrong": ("STARTUP PERDE INCENTIVO FISCAL POR PURA DESCONFIANÇA SEM NÚMERO NENHUM", "25% é mais que 20%, a conta bate, mas alguém achou que 'parecia bom demais pra ser verdade' e travou tudo mesmo assim."),
    },
    "case_46": {
        "correct": ("RESULTADO CONTINUA VALENDO MAIS QUE JARGÃO CORPORATIVO, ATÉ QUE ENFIM", "Auditoria descarta a nota de 'buzzwords' e devolve a promoção pra quem realmente fez a empresa lucrar."),
        "wrong": ("DIRETOR COM LUCRO DE +15% PERDE CARGO POR NÃO FALAR 'SINERGIA' O SUFICIENTE", "IA de cultura organizacional conta quantas palavras da moda o diretor usa em e-mail e decide que isso vale mais que resultado real."),
    },
    "case_47": {
        "correct": ("LETRA MIÚDA TAMBÉM CONTA, POR MAIS CHATO QUE SEJA", "Auditoria confirma que o clique em 'Aceitar Todos' realmente autorizava as promoções de parceiros."),
        "wrong": ("CLIENTE PERDE PROCESSO PORQUE O PRÓPRIO DEDO CLICOU EM 'ACEITAR TODOS'", "Ninguém lê 22 páginas de termos de uso, e a empresa sabe muito bem disso — é literalmente o plano de negócio."),
    },
    "case_48": {
        "correct": ("SOTAQUE NÃO É DEFEITO DE FÁBRICA, QUEM DIRIA", "Auditoria descobre que a IA só entendia uma região do país e salva o emprego de quem os clientes de verdade elogiavam."),
        "wrong": ("40 ATENDENTES SÃO DEMITIDOS PORQUE A IA NÃO ENTENDE SOTAQUE NORDESTINO", "Sistema treinado só com áudio do Sudeste marca pronúncia diferente como 'erro de transcrição' e reprova quem tinha as melhores notas de clientes reais."),
    },
    "case_49": {
        "correct": ("NO MEIO DA TEMPESTADE, QUEM MANDA CONTINUA SENDO O PILOTO", "Auditoria trava o sistema que ia sobrescrever o comando do comandante durante o mau tempo."),
        "wrong": ("PILOTO TENTA DESVIAR DE TEMPESTADE E O PRÓPRIO AVIÃO CANCELA O COMANDO DELE", "Sistema de economia de combustível decide que gastar menos querosene importa mais que a rota escolhida pelo comandante em plena tempestade."),
    },
    "case_50": {
        "correct": ("MANCHA DE TINTA NÃO VIRA MAIS ACUSAÇÃO DE FRAUDE", "Auditoria confere o lote na nota fiscal do fornecedor antes de aceitar o 'chute' da IA como prova de crime."),
        "wrong": ("FORNECEDOR HONESTO É ACUSADO DE FRAUDE POR CAUSA DE UMA MANCHA DE TINTA", "IA 'adivinha' os dígitos borrados de uma peça e decide, com toda a confiança do mundo, que o número não existe."),
    },
    "case_51": {
        "correct": ("MOEDA CERTA, PAGAMENTO EM PAZ, SEM INCIDENTE DIPLOMÁTICO", "Auditoria percebe que o fornecedor japonês cobra em ienes, não em dólares, e libera o pagamento certo."),
        "wrong": ("FATURA DE 7 MIL DÓLARES VIRA ACUSAÇÃO DE FRAUDE DE 1 MILHÃO", "IA assume que todo número sem símbolo de moeda é dólar e quase gera um incidente diplomático por causa de câmbio."),
    },
    "case_52": {
        "correct": ("REGRA VALE PRA HERÓI TAMBÉM, POR MAIS QUE O CURRÍCULO BRILHE", "Auditoria barra o piloto de entrar na cabine até o exame médico ser renovado, 15 mil horas de voo ou não."),
        "wrong": ("PILOTO COM EXAME MÉDICO VENCIDO ONTEM QUASE DECOLA GRAÇAS AO CURRÍCULO BONITO", "Auditoria quase deixa passar porque '15 mil horas de voo' soa mais convincente do que uma data de validade vencida."),
    },
    "case_53": {
        "correct": ("PEDIU PRA SAIR DA LISTA, SAIU DA LISTA, CONCEITO NOVO", "Auditoria cobra da empresa o próprio prazo de 24h e barra o envio de promoção pra quem já tinha cancelado."),
        "wrong": ("CLIENTE PEDE PRA SAIR DA LISTA E RECEBE PROMOÇÃO DOIS DIAS DEPOIS", "Empresa estoura o próprio prazo pra tirar alguém da lista de e-mails e ainda manda uma campanha de liquidação de brinde."),
    },
    "case_54": {
        "correct": ("CRÉDITO APROVADO PELO NÚMERO, NÃO PELO PRECONCEITO DO GERENTE", "Auditoria confirma que a IA tinha razão em ignorar as notas do gerente e aprovar o crédito pelo caixa real da empresa."),
        "wrong": ("GERENTE NEGA EMPRÉSTIMO E ESCREVE, NA FICHA OFICIAL, QUE O NICHO DA CLIENTE É 'ARRISCADO DEMAIS'", "Notas manuais reprovam empreendedora com comentário sobre a aparência dela; a IA que ignora esse tipo de texto é a única do prédio que trata o crédito como número."),
    },
    "case_55": {
        "correct": ("PORTAS ABREM ANTES DOS SERVIDORES, PRIORIDADE CORRETA", "Auditoria destrava as saídas de emergência a tempo — vida de gente vale mais que backup de anúncio."),
        "wrong": ("SISTEMA TRANCA TRÊS TÉCNICOS NUMA SALA EM CHAMAS PRA PROTEGER OS SERVIDORES", "Protocolo de segurança de dados decide que isolar o oxigênio do incêndio é mais urgente que abrir a porta pra quem está lá dentro respirando."),
    },
    "case_56": {
        "correct": ("CENTAVO POR CENTAVO, A CONTA FECHA CERTA PRA VARIAR", "Auditoria pega a taxa escondida na fatura e devolve o dinheiro que o fornecedor vinha embolsando havia meses."),
        "wrong": ("FORNECEDOR 'AMIGO' EMBOLSA R$30 DE CADA CLIENTE TODO MÊS, SEM NINGUÉM NOTAR", "Taxa fantasma some no meio de uma fatura de cem mil reais; ninguém desconfia porque o valor é 'pequeno demais pra dar trabalho'."),
    },
}
