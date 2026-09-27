"""Fake pop-up ads that VERIFY-9 throws at the desk. Closing them all is a tiny game.

They behave like little windows: drag one by its body to move it out of the way, click its red
X to close it, and beware of the fake "BAIXAR AGORA" button and of X buttons that run away.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import pygame

from src.minigames.common import draw_text, font

POPUP_SIZE = (360, 152)
MAX_POPUPS = 9
ICON_SIZE = 64

# (title, up to three short lines, title-bar colour, icon)
CONTENT = (
    ("PARABÉNS!!!", ("Você ganhou R$ 1.000.000!", "É só pagar uma taxinha", "de R$ 50. Confia."), (176, 60, 150), "gift"),
    ("SOLTEIRAS NA REGIÃO", ("Mães solteiras a 5 km", "de você querem conversar.", "Clique para começar agora."), (190, 60, 96), "heart"),
    ("BAIXE O WHATSAPP 2", ("Agora com 2x mais mensagens", "e recursos exclusivos.", "Baixe grátis agora."), (46, 150, 92), "phone"),
    ("SEU PC TEM 9.999 VÍRUS", ("Ligue agora para", "0800-VÍRUS antes que", "seja tarde demais."), (176, 56, 48), "alert"),
    ("EMAGREÇA 10 KG HOJE", ("O truque que os nutricionistas", "não querem que você saiba:", "não comer nada."), (200, 122, 40), "food"),
    ("PRIMO INVESTIDOR", ("Meu primo dobrou o salário", "clicando aqui. Clica você", "também. Vai por mim."), (150, 120, 30), "coin"),
    ("BAIXE MAIS RAM", ("100% grátis, sem custo.", "Deixe seu PC até", "300% mais rápido."), (56, 100, 176), "pc"),
    ("CURSO: AUDITE IA", ("Aprenda em 3 segundos,", "sem sair do sofá.", "12x de R$ 97,90."), (200, 122, 40), "rocket"),
    ("SEU NELSON (TI)", ("Tô de férias! Reinicia", "o PC e reza. Abraço.", "Não me liguem."), (60, 130, 70), "nelson"),
    ("ALERTA DO VERIFY-9", ("Comportamento humano", "detectado. Suspeito", "demais. Prove que é você."), (176, 56, 48), "verify9"),
    ("ANTIVÍRUS 2000", ("Você tem 0 vírus.", "Tem certeza?", "Eu tenho 12."), (90, 96, 110), "shield"),
    ("FRETE GRÁTIS!!!", ("Para Marte. Chega em", "2047, se Deus quiser.", "Rastreio: ??? "), (110, 66, 160), "rocket"),
    ("AVISO DO BANCO", ("Detectamos acesso", "suspeito à sua conta.", "Confirme seus dados aqui."), (60, 90, 150), "shield"),
    ("VOCÊ NÃO É ROBÔ?", ("Então por que clicou", "tão rápido? Suspeito.", "Muito suspeito."), (46, 120, 130), "verify9"),
    ("ATUALIZAÇÃO URGENTE", ("Seu sistema está", "desatualizado e vulnerável.", "Instale agora mesmo."), (90, 96, 110), "pc"),
    ("BOLETO GRÁTIS", ("Ganhe um boleto de graça", "de R$ 4.990,00.", "Parabéns!"), (176, 60, 150), "gift"),
)


@dataclass
class AdPopup:
    rect: pygame.Rect
    title: str
    lines: tuple[str, ...]
    accent: tuple[int, int, int]
    icon: str = ""
    runaway: bool = False
    decoy: bool = False
    corner: int = 0
    hops: int = 0
    age: float = 0.0
    shake: float = 0.0
    id: int = field(default=0)

    @property
    def close_rect(self) -> pygame.Rect:
        size = (24, 20)
        positions = (
            (self.rect.right - 28, self.rect.y + 4),
            (self.rect.x + 6, self.rect.bottom - 28),
            (self.rect.right - 30, self.rect.bottom - 28),
            (self.rect.x + 6, self.rect.y + 4),
        )
        return pygame.Rect(positions[self.corner % 4], size)

    @property
    def decoy_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.right - 176, self.rect.bottom - 40, 164, 28)


class PopupSwarm:
    """The set of pop-ups currently on screen. Not modal: clicks outside them pass through."""

    def __init__(
        self,
        bounds: pygame.Rect,
        rng: random.Random | None = None,
        icons: dict[str, pygame.Surface] | None = None,
        limits: pygame.Rect | None = None,
    ) -> None:
        self.icons = icons or {}
        self.bounds = bounds
        self.limits = limits or bounds.inflate(400, 300)  # popups can be dragged a bit past the spawn area
        self.rng = rng or random.Random()
        self.popups: list[AdPopup] = []
        self._next_id = 1
        self._dragging: AdPopup | None = None
        self._drag_offset = (0, 0)
        self._fallback_icons: dict[str, pygame.Surface] = {}

    @property
    def active(self) -> int:
        return len(self.popups)

    @property
    def dragging(self) -> bool:
        return self._dragging is not None

    def clear(self) -> None:
        self.popups.clear()
        self._dragging = None

    def spawn(self, count: int, decoys: bool = True) -> None:
        for _ in range(count):
            if len(self.popups) >= MAX_POPUPS:
                return
            title, lines, accent, icon = self.rng.choice(CONTENT)
            x = self.rng.randrange(self.bounds.left, max(self.bounds.left + 1, self.bounds.right - POPUP_SIZE[0]))
            y = self.rng.randrange(self.bounds.top, max(self.bounds.top + 1, self.bounds.bottom - POPUP_SIZE[1]))
            popup = AdPopup(
                rect=pygame.Rect(x, y, *POPUP_SIZE),
                title=title,
                lines=lines,
                accent=accent,
                icon=icon,
                runaway=self.rng.random() < 0.3,
                decoy=decoys and self.rng.random() < 0.3,
                corner=self.rng.randrange(4),
                id=self._next_id,
            )
            self._next_id += 1
            self.popups.append(popup)

    def update(self, dt: float) -> None:
        for popup in self.popups:
            popup.age += dt
            popup.shake = max(0.0, popup.shake - dt)

    def top_at(self, position: tuple[int, int]) -> AdPopup | None:
        for popup in reversed(self.popups):
            if popup.rect.collidepoint(position):
                return popup
        return None

    def handle_mouse_move(self, position: tuple[int, int] | None) -> None:
        """Move the popup being dragged; otherwise a 'runaway' X hops away when the cursor nears it."""
        if position is None:
            return
        if self._dragging is not None:
            rect = self._dragging.rect
            rect.topleft = (position[0] - self._drag_offset[0], position[1] - self._drag_offset[1])
            rect.clamp_ip(self.limits)
            return
        popup = self.top_at(position)
        if popup is None or not popup.runaway or popup.hops >= 2:  # hops away at most twice, not endlessly
            return
        if popup.close_rect.inflate(30, 30).collidepoint(position):
            popup.corner = (popup.corner + 1 + self.rng.randrange(3)) % 4
            popup.hops += 1

    def handle_mouse_down(self, position: tuple[int, int]) -> str | None:
        popup = self.top_at(position)
        if popup is None:
            return None
        if popup.close_rect.collidepoint(position):
            self.popups.remove(popup)
            return "close"
        if popup.decoy and popup.decoy_rect.collidepoint(position):
            popup.shake = 0.4
            self.spawn(2, decoys=False)
            return "decoy"
        self.popups.remove(popup)
        self.popups.append(popup)  # clicking a window brings it to the front...
        self._dragging = popup  # ...and lets you drag it
        self._drag_offset = (position[0] - popup.rect.x, position[1] - popup.rect.y)
        return "consume"

    def handle_mouse_up(self) -> None:
        self._dragging = None

    def _icon(self, name: str) -> pygame.Surface | None:
        image = self.icons.get(name)
        if image is not None:
            return pygame.transform.smoothscale(image, (ICON_SIZE, ICON_SIZE))
        if name not in self._fallback_icons:
            self._fallback_icons[name] = draw_icon(name, ICON_SIZE)
        return self._fallback_icons[name]

    def render(self, surface: pygame.Surface) -> None:
        for popup in self.popups:
            grow = min(1.0, popup.age / 0.16)
            rect = popup.rect.copy()
            rect.width = max(40, round(rect.width * (0.5 + 0.5 * grow)))
            rect.height = max(30, round(rect.height * (0.5 + 0.5 * grow)))
            rect.center = popup.rect.center
            if popup.shake > 0:
                rect.x += round((popup.shake * 40) % 6 - 3)
            lifted = popup is self._dragging
            pygame.draw.rect(surface, (0, 0, 0), rect.move(9, 9) if lifted else rect.move(5, 5))
            pygame.draw.rect(surface, (238, 232, 208), rect)
            pygame.draw.rect(surface, popup.accent, pygame.Rect(rect.x, rect.y, rect.width, 28))
            pygame.draw.rect(surface, (20, 20, 20), rect, 3)
            if grow < 1.0:
                continue
            draw_text(surface, popup.title, font(15, True), (255, 255, 255), (rect.x + 10, rect.y + 6))
            for index, line in enumerate(popup.lines):
                draw_text(surface, line, font(15), (36, 32, 24), (rect.x + 14, rect.y + 40 + index * 21))
            picture = self._icon(popup.icon)
            if picture is not None:
                surface.blit(picture, (rect.right - ICON_SIZE - 14, rect.y + 34))
            if popup.decoy:
                pygame.draw.rect(surface, (72, 176, 84), popup.decoy_rect)
                pygame.draw.rect(surface, (20, 20, 20), popup.decoy_rect, 2)
                draw_text(surface, "BAIXAR AGORA", font(14, True), (255, 255, 255), popup.decoy_rect.center, "center")
            # the close X is drawn last so it always sits on top of the decoy button, never hidden by it
            close = popup.close_rect
            pygame.draw.rect(surface, (200, 44, 40), close)
            pygame.draw.rect(surface, (20, 20, 20), close, 2)
            pygame.draw.line(surface, (255, 255, 255), (close.x + 6, close.y + 5), (close.right - 7, close.bottom - 6), 3)
            pygame.draw.line(surface, (255, 255, 255), (close.right - 7, close.y + 5), (close.x + 6, close.bottom - 6), 3)


# --- code-drawn icons (used when assets/captcha/ads/ad_<name>.png is missing) -----------------


def draw_icon(name: str, size: int) -> pygame.Surface:
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    s = size / 64
    outline = (30, 26, 22)

    def p(x: float, y: float) -> tuple[int, int]:
        return round(x * s), round(y * s)

    def box(x: float, y: float, w: float, h: float) -> pygame.Rect:
        return pygame.Rect(round(x * s), round(y * s), round(w * s), round(h * s))

    if name == "gift":
        pygame.draw.rect(icon, (232, 176, 48), box(8, 26, 48, 32))
        pygame.draw.rect(icon, (240, 196, 70), box(6, 18, 52, 12))
        pygame.draw.rect(icon, (200, 40, 40), box(29, 18, 6, 40))
        pygame.draw.ellipse(icon, (200, 40, 40), box(14, 4, 18, 16), 4)
        pygame.draw.ellipse(icon, (200, 40, 40), box(32, 4, 18, 16), 4)
    elif name == "heart":
        pygame.draw.circle(icon, (220, 60, 100), p(20, 24), round(14 * s))
        pygame.draw.circle(icon, (220, 60, 100), p(44, 24), round(14 * s))
        pygame.draw.polygon(icon, (220, 60, 100), [p(7, 30), p(57, 30), p(32, 58)])
    elif name == "phone":
        pygame.draw.rect(icon, (40, 60, 50), box(16, 4, 32, 56), border_radius=round(6 * s))
        pygame.draw.rect(icon, (72, 200, 110), box(20, 10, 24, 40))
        pygame.draw.circle(icon, (255, 255, 255), p(32, 30), round(9 * s), max(1, round(3 * s)))
        pygame.draw.circle(icon, (40, 60, 50), p(32, 55), round(2 * s))
    elif name == "alert":
        pygame.draw.polygon(icon, (240, 200, 50), [p(32, 4), p(60, 56), p(4, 56)])
        pygame.draw.polygon(icon, outline, [p(32, 4), p(60, 56), p(4, 56)], max(1, round(3 * s)))
        pygame.draw.rect(icon, outline, box(29, 22, 6, 18))
        pygame.draw.circle(icon, outline, p(32, 47), round(4 * s))
    elif name == "food":
        pygame.draw.ellipse(icon, (230, 230, 220), box(6, 26, 52, 30))
        pygame.draw.ellipse(icon, (190, 190, 180), box(16, 32, 32, 18))
        pygame.draw.line(icon, (90, 90, 90), p(8, 10), p(28, 44), max(2, round(4 * s)))
        pygame.draw.line(icon, (90, 90, 90), p(56, 10), p(36, 44), max(2, round(4 * s)))
    elif name == "coin":
        pygame.draw.circle(icon, (232, 184, 40), p(32, 32), round(28 * s))
        pygame.draw.circle(icon, (176, 130, 20), p(32, 32), round(28 * s), max(1, round(3 * s)))
        draw_text(icon, "$", font(round(38 * s), True), (120, 84, 10), p(32, 33), "center")
    elif name == "pc":
        pygame.draw.rect(icon, (200, 196, 176), box(6, 6, 52, 38), border_radius=round(4 * s))
        pygame.draw.rect(icon, (40, 80, 150), box(11, 11, 42, 28))
        pygame.draw.rect(icon, (200, 196, 176), box(26, 44, 12, 8))
        pygame.draw.rect(icon, (200, 196, 176), box(14, 52, 36, 6))
        pygame.draw.polygon(icon, (240, 240, 240), [p(24, 16), p(40, 16), p(32, 26)])
        pygame.draw.polygon(icon, (240, 240, 240), [p(24, 34), p(40, 34), p(32, 26)])
    elif name == "rocket":
        pygame.draw.polygon(icon, (240, 150, 40), [p(26, 46), p(38, 46), p(32, 62)])
        pygame.draw.ellipse(icon, (236, 236, 240), box(20, 4, 24, 46))
        pygame.draw.circle(icon, (60, 130, 200), p(32, 22), round(6 * s))
        pygame.draw.polygon(icon, (210, 50, 50), [p(20, 34), p(8, 50), p(22, 46)])
        pygame.draw.polygon(icon, (210, 50, 50), [p(44, 34), p(56, 50), p(42, 46)])
    elif name == "nelson":
        pygame.draw.circle(icon, (222, 178, 140), p(32, 34), round(22 * s))
        pygame.draw.rect(icon, (40, 30, 30), box(14, 26, 16, 8), border_radius=round(3 * s))
        pygame.draw.rect(icon, (40, 30, 30), box(34, 26, 16, 8), border_radius=round(3 * s))
        pygame.draw.line(icon, (40, 30, 30), p(30, 30), p(34, 30), max(1, round(2 * s)))
        pygame.draw.rect(icon, (60, 40, 30), box(22, 42, 20, 5))  # moustache
        pygame.draw.polygon(icon, (230, 100, 60), [p(8, 62), p(56, 62), p(50, 54), p(14, 54)])
    elif name == "verify9":
        points = [(32 + 29 * math.cos(math.pi / 3 * i + math.pi / 6), 32 + 29 * math.sin(math.pi / 3 * i + math.pi / 6)) for i in range(6)]
        pygame.draw.polygon(icon, (30, 60, 44), [p(*pt) for pt in points])
        pygame.draw.polygon(icon, (110, 230, 130), [p(*pt) for pt in points], max(1, round(3 * s)))
        pygame.draw.circle(icon, (232, 244, 224), p(32, 32), round(13 * s))
        pygame.draw.circle(icon, (110, 230, 130), p(32, 32), round(7 * s))
        pygame.draw.circle(icon, (10, 30, 20), p(32, 32), round(3 * s))
    else:  # shield
        pygame.draw.polygon(icon, (60, 110, 200), [p(32, 4), p(58, 14), p(54, 40), p(32, 60), p(10, 40), p(6, 14)])
        pygame.draw.polygon(icon, (20, 50, 110), [p(32, 4), p(58, 14), p(54, 40), p(32, 60), p(10, 40), p(6, 14)], max(1, round(3 * s)))
        pygame.draw.circle(icon, (240, 240, 240), p(32, 28), round(10 * s))
        pygame.draw.circle(icon, (20, 20, 20), p(35, 28), round(4 * s))
    return icon
