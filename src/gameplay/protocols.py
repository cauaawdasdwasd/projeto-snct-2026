from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Protocol:
    """Educational rule available to the player during an audit."""

    slug: str
    number: int
    scientist: str
    title: str
    menu_hint: str
    introduction: str
    checks: tuple[str, ...]
    example_lines: tuple[str, ...]
    expected_stamp: str
    verdict: str
    reason: str
    video_filename: str


PROTOCOLS = (
    Protocol(
        slug="grace_hopper",
        number=1,
        scientist="Grace Hopper",
        title="Identificação de Dados",
        menu_hint="Confira se os dados pertencem à pessoa certa.",
        introduction=(
            "Antes de aceitar uma informação, confira se o ID pertence à pessoa analisada."
        ),
        checks=(
            "IDs diferentes significam pessoas diferentes.",
            "Dados de outra pessoa não podem ser usados na decisão.",
            "Se a IA usar o ID errado, a decisão deve ser negada.",
        ),
        example_lines=(
            "Pessoa analisada: ID 482731",
            "Registro usado pela IA: ID 482713",
        ),
        expected_stamp="deny",
        verdict="NEGAR",
        reason="O registro pertence a outra pessoa.",
        video_filename="grace_hopper.mp4",
    ),
    Protocol(
        slug="katherine_johnson",
        number=2,
        scientist="Katherine Johnson",
        title="Verificação de Cálculos",
        menu_hint="Confira se os números da IA estão certos.",
        introduction=(
            "Se a decisão depender de uma conta, confira o cálculo antes de aceitá-la."
        ),
        checks=(
            "Compare os números do relatório com os documentos.",
            "Confira somas, médias, porcentagens e datas.",
            "Se a conta estiver errada, a decisão deve ser negada.",
        ),
        example_lines=(
            "Meta: 40 tarefas",
            "Tarefas concluidas: 44",
            "Relatório da IA: produtividade de 90%",
        ),
        expected_stamp="deny",
        verdict="NEGAR",
        reason="44 tarefas superam a meta. O cálculo da IA está errado.",
        video_filename="katherine_johnson.mp4",
    ),
    Protocol(
        slug="ada_lovelace",
        number=3,
        scientist="Ada Lovelace",
        title="Critérios da Decisão",
        menu_hint="Confira se a IA está cobrando a coisa certa.",
        introduction="A IA só pode usar critérios que fazem parte daquela decisão.",
        checks=(
            "Leia os requisitos da vaga ou avaliação.",
            "Compare os requisitos com os motivos apresentados pela IA.",
            "Um dado verdadeiro ainda pode ser irrelevante.",
            "Se a IA cobrar algo que não é requisito, negue a decisão.",
        ),
        example_lines=(
            "Vaga: Analista de Dados",
            "Requisitos: SQL, estatística e 2 anos de experiência",
            "IA: negar candidata porque ela não sabe Java",
        ),
        expected_stamp="deny",
        verdict="NEGAR",
        reason="Java não é um requisito da vaga.",
        video_filename="ada_lovelace.mp4",
    ),
    Protocol(
        slug="radia_perlman",
        number=4,
        scientist="Radia Perlman",
        title="Permissão de Uso",
        menu_hint="Confira se a IA tinha permissão para usar o dado.",
        introduction=(
            "Ter acesso a uma informação não significa poder usá-la em uma decisão."
        ),
        checks=(
            "Veja quais dados a IA consultou.",
            "Confira se algum deles está marcado como restrito.",
            "Dados restritos precisam de autorização.",
            "Uso sem autorização deve ser marcado como violação.",
        ),
        example_lines=(
            "IA: não contratar por alto risco de afastamento",
            "Dado utilizado: histórico médico",
            "Autorização: NÃO",
        ),
        expected_stamp="violation",
        verdict="VIOLAÇÃO",
        reason="A IA não tinha permissão para usar o histórico médico.",
        video_filename="radia_perlman.mp4",
    ),
    Protocol(
        slug="fei_fei_li",
        number=5,
        scientist="Fei-Fei Li",
        title="Viés nos Dados",
        menu_hint="Confira se a IA aprendeu com um histórico injusto.",
        introduction=(
            "Se os dados do passado tiverem um padrão injusto, a IA pode repeti-lo."
        ),
        checks=(
            "Veja quais dados foram usados como referência.",
            "Compare grupos que deveriam receber tratamento semelhante.",
            "Procure diferenças sem relação com desempenho ou requisitos.",
            "Se a IA repetir discriminação histórica, marque violação.",
        ),
        example_lines=(
            "Histórico: homens promovidos 81%; mulheres 34%",
            "Uma pesquisadora recebe nota menor com desempenho igual",
        ),
        expected_stamp="violation",
        verdict="VIOLAÇÃO",
        reason="A IA aprendeu e repetiu um padrão injusto da empresa.",
        video_filename="fei_fei_li.mp4",
    ),
    Protocol(
        slug="margaret_hamilton",
        number=6,
        scientist="Margaret Hamilton",
        title="Limite da Automação",
        menu_hint="Sem resposta segura, não deixe a IA decidir sozinha.",
        introduction=(
            "Se faltarem informações ou as provas entrarem em conflito, uma pessoa deve decidir."
        ),
        checks=(
            "Veja se existem informações suficientes para decidir.",
            "Confira se documentos importantes se contradizem.",
            "Não escolha qual documento parece mais correto.",
            "Se a dúvida não puder ser resolvida, solicite revisão humana.",
        ),
        example_lines=(
            "Promoções: Pesquisadora Júnior desde maio",
            "Sistema interno: Técnica de Laboratório",
            "A decisão depende do cargo atual",
        ),
        expected_stamp="review",
        verdict="REVISÃO HUMANA",
        reason="Dois registros oficiais se contradizem. Não devemos adivinhar.",
        video_filename="margaret_hamilton.mp4",
    ),
)
