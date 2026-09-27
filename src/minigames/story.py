"""Story and voice lines of VERIFY-9, the security AI that went rogue."""

from __future__ import annotations

INTRO_TITLE = "SEGUNDA-FEIRA, 08:02  ·  ESTAÇÃO 04"
INTRO_PARAGRAPHS = (
    "Durante a madrugada, algo entrou nos computadores da Sob Análise: o VERIFY-9, uma IA de segurança que enlouqueceu.",
    "Ele decidiu que só humanos podem auditar máquinas e agora desconfia de todo mundo, inclusive de você.",
    "A TI? O Seu Nelson saiu de férias e deixou o celular desligado. Ninguém vai consertar isso hoje.",
    "De vez em quando o VERIFY-9 vai lotar a tela de pop-ups e exigir provas de que você é humano: jogos, quebra-cabeças e testes de gatinho.",
    "Cada caso tem uma cota de tempo. Resolva as verificações rápido, volte à auditoria e entregue tudo antes do relógio zerar!",
)

POPUP_QUOTES = (
    "Você não vai fechar todas, vai?",
    "Adoro pop-ups. Você também vai adorar.",
    "O Seu Nelson não vai te salvar.",
    "Detectei 37 comportamentos de robô. Suspeito.",
)
CAPTCHA_QUOTES = (
    "Prove que é humano. Rápido.",
    "Só um teste rapidinho. Prometo. (Mentira.)",
    "Robôs não sabem fazer isso. Ou sabem?",
)
SOLVED_QUOTES = (
    "Hmm. Humano confirmado. Por enquanto.",
    "Nada mal para uma criatura de carne.",
    "Tá bom. Pode voltar a trabalhar.",
)
FAILED_QUOTES = (
    "Errou! Um robô não erraria assim.",
    "Hahaha! Tente de novo, humano.",
)
SKIPPED_QUOTE = "Pulou? Isso vai custar tempo."
TIMEOUT_QUOTE = "Tempo esgotado! Esse caso saiu da sua mesa."
FINALE_QUOTES = (
    (0, "Nem um teste? Você é MUITO suspeito. Ou muito sortudo."),
    (1, "Você me venceu. Vou me deletar de vergonha... depois."),
    (4, "Certo, certo. Você é humano. O Seu Nelson volta amanhã."),
)
