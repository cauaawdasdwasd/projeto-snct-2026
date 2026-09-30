"""ARENA VERIFY-9: a self-contained arcade phase, separate from the case/audit flow.

VERIFY-9 finally gets the player alone: no cases, no documents, just a short campaign of
'prove you are human' verifications that gets harder in clear, learnable steps and ends
in a boss fight. See `src/minigames/arcade.py` for the scoring/wave/rank/leaderboard
rules this scene renders.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from src.core.scene import Scene
from src.core.settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from src.minigames.arcade import (
    BOSS_CAPTCHAS,
    CAPTCHAS_PER_WAVE,
    FINAL_WAVE,
    KIND_LABELS,
    MAX_LIVES,
    NAME_MAX_LEN,
    OVERCLOCK_MAX,
    ArcadeRun,
    ArcadeStats,
    Leaderboard,
    captchas_required_for,
)
from src.minigames.captchas import CANVAS
from src.minigames.common import (
    AMBER,
    BORDER,
    BORDER_DARK,
    CYAN,
    GREEN,
    INK,
    INK_BRIGHT,
    INK_MUTED,
    PANEL,
    RED,
    SCREEN_BLACK,
    draw_button,
    draw_text,
    draw_wrapped,
    font,
    wrap_text,
)
from src.minigames.story import CAPTCHA_QUOTES, FAILED_QUOTES, SOLVED_QUOTES
from src.minigames.verify9 import MOOD_COLORS, Verify9

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


ARENA_INTRO = (
    "Chega de auditoria. Só nós dois, humano.",
    "Aqui não tem prazo de caso pra te salvar. Só eu, você, e quantas verificações eu quiser.",
    "Toda vez que você erra, eu ganho. Toda vez que eu erro... isso nunca acontece.",
)
WAVE_TAUNTS = (
    "Vou complicar um pouco mais.",
    "Ainda acha que é humano? Prove de novo.",
    "Novo lote de testes. De nada.",
    "Você está gostando disso, não está? Suspeito.",
)
OVERCLOCK_TAUNTS = (
    "Ok, ISSO foi irritante.",
    "Vida extra. Aproveita enquanto dura.",
    "Você tá jogando limpo demais. Não confio.",
)
GAMEOVER_TAUNTS = (
    "Desconectado. Volte quando for mais... humano.",
    "GG. O Seu Nelson vai adorar essa estatística.",
    "Nada mal. Para um humano.",
)
VICTORY_TAUNTS = (
    "Impossível. Isso é... impossível.",
    "Reiniciando... reiniciando... Erro. Você venceu. Isso não deveria acontecer.",
    "Certo. CERTO. Você é humano. Eu vou... desligar agora. Só isso. Nada demais.",
)
BOSS_INTRO_TAUNTS = (
    "Chega de aquecimento. Isso aqui é o meu teste de verdade.",
    "Última barreira. Tudo o que você aprendeu, tudo ao mesmo tempo.",
    "Vamos ver se 'humano' aguenta o meu melhor.",
)
BOSS_PHASE_TAUNTS = (
    "Uma verificação. Faltam mais.",
    "Não relaxa. Ainda não acabou.",
    "Impressionante. Irrelevante, mas impressionante.",
    "Sente a pressão subindo?",
)
LEADERBOARD_TAUNTS = (
    "Vai por mim, esse ranking não muda sozinho.",
    "Alguém aqui gosta de aparecer no topo.",
)
ARENA_RULES = (
    f"Você tem {MAX_LIVES - 2} vidas para começar. Cada verificação tem um cronômetro: se zerar, perde uma vida.",
    "Resolva rápido e sem erro para empilhar COMBO: quanto mais rápido você resolve, mais pontos vale.",
    "Sequências limpas enchem o medidor OVERCLOCK e te devolvem uma vida quando ele lota.",
    f"A cada {CAPTCHAS_PER_WAVE} verificações a onda sobe: o tempo aperta e novos testes entram em cena.",
    f"A onda {FINAL_WAVE} é o confronto final: {BOSS_CAPTCHAS} verificações seguidas contra o VERIFY-9. Vença e a arena é sua.",
)
NAME_ALLOWED_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÃÉÊÍÓÔÕÚÇÑ0123456789 -_")
PAUSE_LABELS = ("CONTINUAR", "REINICIAR", "MENU PRINCIPAL")
PHASE_BADGES = {
    "celebrate": ("HUMANO CONFIRMADO", GREEN),
    "hit": ("TEMPO ESGOTADO", RED),
}


class ArcadeScene(Scene):
    """ARENA VERIFY-9: name entry -> briefing/leaderboard -> gauntlet -> run summary."""

    PANEL_RECT = pygame.Rect(500, 280, 1380, 640)
    CANVAS_ORIGIN = (PANEL_RECT.centerx - CANVAS[0] // 2, PANEL_RECT.y + 164)
    AVATAR_CENTER = (250, 420)
    TAUNT_RECT = pygame.Rect(50, 560, 420, 190)
    HUD_RECT = pygame.Rect(0, 0, VIRTUAL_WIDTH, 156)

    def __init__(
        self,
        manager: SceneManager,
        assets: AssetManager,
        input_manager: InputManager,
        audio: AudioManager | None = None,
    ) -> None:
        super().__init__(manager, assets, input_manager)
        self.audio = audio
        self.verify9 = Verify9(self.assets.assets_root)
        self.stats = ArcadeStats.load()
        self.leaderboard = Leaderboard.load()
        self.run: ArcadeRun | None = None
        self.summary = None
        self.view = "name_entry"
        self.briefing_view = "main"
        self.achieved_rank: int | None = None
        self._pending_gameover = False
        self.player_name = ""
        self.name_buffer = ""
        self.paused = False
        self.elapsed = 0.0
        self.pointer: tuple[int, int] | None = None
        self.floats: list[dict] = []
        self.banner_queue: list[dict] = []
        self.active_banner: dict | None = None
        self.mood = "suspicious"
        self.mood_timer = 0.0
        self.taunt = random.choice(ARENA_INTRO)

        self.stats_rect = pygame.Rect(0, 0, 540, 150)
        self.stats_rect.center = (640, 626)
        self.board_rect = pygame.Rect(0, 0, 540, 150)
        self.board_rect.center = (1280, 626)
        self.view_leaderboard_rect = pygame.Rect(0, 0, 360, 42)
        self.view_leaderboard_rect.center = (960, 726)
        self.change_player_rect = pygame.Rect(0, 0, 340, 40)
        self.change_player_rect.topright = (1880, 20)
        self.start_rect = pygame.Rect(0, 0, 420, 68)
        self.start_rect.center = (960, 800)
        self.back_rect = pygame.Rect(0, 0, 300, 54)
        self.back_rect.center = (960, 872)

        self.leaderboard_back_rect = pygame.Rect(0, 0, 300, 56)
        self.leaderboard_back_rect.center = (960, 906)

        self.name_input_rect = pygame.Rect(0, 0, 520, 66)
        self.name_input_rect.center = (960, 420)
        self.name_confirm_rect = pygame.Rect(0, 0, 320, 60)
        self.name_confirm_rect.center = (960, 520)

        self.retry_rect = pygame.Rect(0, 0, 380, 68)
        self.retry_rect.center = (760, 900)
        self.menu_rect = pygame.Rect(0, 0, 380, 68)
        self.menu_rect.center = (1160, 900)

        self.PAUSE_PANEL = pygame.Rect(0, 0, 620, 420)
        self.PAUSE_PANEL.center = (960, 540)
        self.pause_rects = tuple(
            pygame.Rect(self.PAUSE_PANEL.x + 60, self.PAUSE_PANEL.y + 130 + index * 90, 500, 64)
            for index in range(3)
        )

        self._rain_columns = [
            {
                "x": index * 26 + 6,
                "y": random.uniform(-1000, 0),
                "speed": random.uniform(90, 220),
                "length": random.uniform(120, 260),
                "glyph": random.choice("01"),
            }
            for index in range(1920 // 26)
        ]

    # -- lifecycle -----------------------------------------------------
    def on_enter(self) -> None:
        self.view = "name_entry"
        self.name_buffer = self.player_name
        self.briefing_view = "main"
        self.run = None
        self.paused = False
        self.elapsed = 0.0
        self.floats = []
        self.banner_queue = []
        self.active_banner = None
        self.mood = "suspicious"
        self.mood_timer = 0.0
        self.taunt = random.choice(ARENA_INTRO)
        if self.audio is not None:
            self.audio.stop_ambience()
            self.audio.play_music_sequence(("audit_1", "audit_2"), fade_ms=700)

    def handle_escape(self) -> bool:
        if self.view == "name_entry":
            self._play_sound("back", 0.65)
            self.manager.switch_to("main_menu")
        elif self.view == "briefing":
            if self.briefing_view == "leaderboard":
                self._play_sound("back", 0.65)
                self.briefing_view = "main"
            else:
                self._play_sound("back", 0.65)
                self.manager.switch_to("main_menu")
        elif self.view == "gameover":
            self._play_sound("back", 0.65)
            self.view = "briefing"
        elif self.view == "playing":
            self.paused = not self.paused
            self._play_sound("click" if self.paused else "back", 0.6)
        return True

    def _start_run(self) -> None:
        self.run = ArcadeRun(self.assets.assets_root, self.stats, random.Random())
        self.paused = False
        self.floats = []
        self.banner_queue = []
        self.active_banner = None
        self._pending_gameover = False
        self.mood = "suspicious"
        self.mood_timer = 0.0
        self.taunt = random.choice(ARENA_INTRO)
        self.view = "playing"

    # -- input -----------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        pointer = self.input_manager.mouse_position
        if event.type == pygame.MOUSEMOTION:
            self.pointer = pointer

        if self.view == "name_entry":
            self._handle_name_entry_event(event, pointer)
            return
        if self.view == "briefing":
            self._handle_briefing_event(event, pointer)
            return
        if self.view == "gameover":
            self._handle_gameover_event(event, pointer)
            return
        if self.paused:
            self._handle_pause_event(event, pointer)
            return
        if self.run is None or self.run.game_over:
            return

        if event.type == pygame.MOUSEMOTION:
            self.run.handle_mouse_move(self._local(pointer))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pointer is not None:
            self.run.handle_mouse_down(self._local(pointer))
        elif event.type == pygame.MOUSEBUTTONUP and pointer is not None:
            self.run.handle_mouse_up(self._local(pointer))
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            self.run.handle_key(event)

    def _local(self, pointer: tuple[int, int] | None) -> tuple[int, int] | None:
        if pointer is None:
            return None
        return pointer[0] - self.CANVAS_ORIGIN[0], pointer[1] - self.CANVAS_ORIGIN[1]

    def _handle_briefing_event(self, event: pygame.event.Event, pointer) -> None:
        if self.briefing_view == "leaderboard":
            wants_back = (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and pointer is not None
                and self.leaderboard_back_rect.collidepoint(pointer)
            ) or (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE))
            if wants_back:
                self._play_sound("back")
                self.briefing_view = "main"
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pointer is not None:
            if self.start_rect.collidepoint(pointer):
                self._play_sound("forward")
                self._start_run()
            elif self.back_rect.collidepoint(pointer):
                self._play_sound("back")
                self.manager.switch_to("main_menu")
            elif self.view_leaderboard_rect.collidepoint(pointer):
                self._play_sound("click")
                self.taunt = random.choice(LEADERBOARD_TAUNTS)
                self.briefing_view = "leaderboard"
            elif self.change_player_rect.collidepoint(pointer):
                self._play_sound("click")
                self.view = "name_entry"
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._play_sound("forward")
            self._start_run()

    def _handle_gameover_event(self, event: pygame.event.Event, pointer) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pointer is not None:
            if self.retry_rect.collidepoint(pointer):
                self._play_sound("forward")
                self._start_run()
            elif self.menu_rect.collidepoint(pointer):
                self._play_sound("back")
                self.manager.switch_to("main_menu")
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._play_sound("forward")
            self._start_run()

    def _handle_name_entry_event(self, event: pygame.event.Event, pointer) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pointer is not None:
            if self.name_confirm_rect.collidepoint(pointer):
                self._confirm_player_name()
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_BACKSPACE:
            self.name_buffer = self.name_buffer[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._confirm_player_name()
        else:
            typed = getattr(event, "unicode", "")
            if typed and typed.upper() in NAME_ALLOWED_CHARS and len(self.name_buffer) < NAME_MAX_LEN:
                self.name_buffer += typed.upper()

    def _confirm_player_name(self) -> None:
        self.player_name = self.name_buffer.strip() or "ANÔNIMO"
        self.name_buffer = self.player_name
        self._play_sound("confirm", 0.7)
        self.view = "briefing"

    def _handle_pause_event(self, event: pygame.event.Event, pointer) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pointer is not None:
            for index, rect in enumerate(self.pause_rects):
                if rect.collidepoint(pointer):
                    self._activate_pause(index)
                    return

    def _activate_pause(self, index: int) -> None:
        self._play_sound("back" if index == 2 else "forward")
        if index == 0:
            self.paused = False
        elif index == 1:
            self._start_run()
        else:
            self.manager.switch_to("main_menu")

    # -- update ------------------------------------------------------------
    def update(self, dt: float) -> None:
        self.elapsed += dt
        for column in self._rain_columns:
            column["y"] += column["speed"] * dt
            if column["y"] - column["length"] > VIRTUAL_HEIGHT:
                column["y"] = random.uniform(-400, -40)
                column["speed"] = random.uniform(90, 220)
                column["length"] = random.uniform(120, 260)
        if self.view == "playing" and not self.paused and self.run is not None:
            self.run.update(dt)
            self._consume_run_events()
            # Never let the next captcha appear while a notice is still on screen: wait
            # for the run's own minimum pause AND for every queued banner to finish.
            if self.run.ready_to_resume and self.active_banner is None and not self.banner_queue:
                self.run.resume()
            if self._pending_gameover and self.active_banner is None and not self.banner_queue:
                self._pending_gameover = False
                self.view = "gameover"
        self._update_floats(dt)
        self._update_banner(dt)
        self.mood_timer = max(0.0, self.mood_timer - dt)

    def _consume_run_events(self) -> None:
        assert self.run is not None
        pending_wave: int | None = None
        pending_unlocks: list[str] = []
        for event in self.run.pop_events():
            if event.kind == "sound":
                self._play_sound(str(event.value), 0.5)
            elif event.kind == "mistake":
                self._flash_mood("angry", 0.6)
                self._spawn_float("-2s", RED, (1150, 300))
            elif event.kind == "solved":
                self._flash_mood("happy", 0.7)
                self._spawn_float(f"+{event.value}", AMBER if self.run.combo > 1 else GREEN, (1780, 60))
                if self.run.combo >= 2:
                    self._spawn_float(f"COMBO x{self.run.combo}", CYAN, (1780, 96))
                self.taunt = random.choice(BOSS_PHASE_TAUNTS if self.run.wave == FINAL_WAVE else SOLVED_QUOTES)
            elif event.kind == "overclock":
                self._queue_banner("OVERCLOCK!", "Sequência limpa recompensada: +1 VIDA", CYAN, 1.8)
                self._flash_mood("angry", 1.0)
                self.taunt = random.choice(OVERCLOCK_TAUNTS)
            elif event.kind == "wave":
                pending_wave = int(event.value)
            elif event.kind == "unlock":
                pending_unlocks.append(str(event.value))
            elif event.kind == "timeout":
                self._play_sound("error", 0.7)
                self._flash_mood("angry", 1.0)
                self._queue_banner("VIDA PERDIDA", "O tempo acabou.", RED, 1.1)
                self.taunt = random.choice(FAILED_QUOTES)
            elif event.kind == "gameover":
                self.summary = event.value
                self.taunt = random.choice(VICTORY_TAUNTS if self.summary.victory else GAMEOVER_TAUNTS)
                self.achieved_rank = self.leaderboard.add(self.player_name, self.summary.score, self.summary.wave)
                try:
                    self.leaderboard.save()
                except OSError:
                    pass
                self._pending_gameover = True  # switch views only once every banner has cleared

        if pending_wave is not None:
            # A wave-up and its unlock(s) fire together: one banner, not a queue of them,
            # so the player never has two notices fighting for the same screen space.
            if pending_wave == FINAL_WAVE:
                self._queue_banner("CONFRONTO FINAL", random.choice(BOSS_INTRO_TAUNTS), RED, 2.2)
                self.taunt = random.choice(BOSS_INTRO_TAUNTS)
            elif pending_unlocks:
                labels = ", ".join(KIND_LABELS.get(kind, kind.upper()) for kind in pending_unlocks)
                self._queue_banner(f"ONDA {pending_wave}", f"Novo teste liberado: {labels}", GREEN, 1.6)
                self.taunt = random.choice(CAPTCHA_QUOTES)
            else:
                self._queue_banner(f"ONDA {pending_wave}", random.choice(WAVE_TAUNTS), AMBER, 1.3)
                self.taunt = random.choice(CAPTCHA_QUOTES)

    def _flash_mood(self, mood: str, duration: float) -> None:
        self.mood = mood
        self.mood_timer = duration

    def _spawn_float(self, text: str, color: tuple[int, int, int], pos: tuple[int, int]) -> None:
        self.floats.append({"text": text, "color": color, "x": pos[0], "y": pos[1], "vy": -46.0, "life": 1.1, "total": 1.1})

    def _update_floats(self, dt: float) -> None:
        for entry in self.floats:
            entry["y"] += entry["vy"] * dt
            entry["life"] -= dt
        self.floats = [entry for entry in self.floats if entry["life"] > 0]

    def _queue_banner(
        self,
        title: str,
        subtitle: str,
        color: tuple[int, int, int],
        duration: float,
    ) -> None:
        self.banner_queue.append({"title": title, "subtitle": subtitle, "color": color, "duration": duration, "timer": 0.0})

    def _update_banner(self, dt: float) -> None:
        if self.active_banner is None and self.banner_queue:
            self.active_banner = self.banner_queue.pop(0)
        if self.active_banner is not None:
            self.active_banner["timer"] += dt
            if self.active_banner["timer"] >= self.active_banner["duration"]:
                self.active_banner = None

    # -- render --------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        surface.fill(SCREEN_BLACK)
        self._render_rain(surface)
        if self.view == "name_entry":
            self._render_name_entry(surface)
        elif self.view == "briefing":
            self._render_briefing(surface)
        elif self.view == "gameover":
            self._render_gameover(surface)
        else:
            self._render_playing(surface)
            if self.paused:
                self._render_pause(surface)

    def _render_rain(self, surface: pygame.Surface) -> None:
        glyph_font = font(21, True)
        for column in self._rain_columns:
            top = pygame.Vector2(column["x"], column["y"] - column["length"])
            bottom = pygame.Vector2(column["x"], column["y"])
            pygame.draw.line(surface, (18, 46, 26), top, bottom, 2)
            glyph = glyph_font.render(column["glyph"], False, (70, 150, 86))
            surface.blit(glyph, glyph.get_rect(center=(column["x"], column["y"])))

    def _render_playing(self, surface: pygame.Surface) -> None:
        self._render_hud(surface)
        self._render_stage(surface)
        self._render_verify_column(surface)
        self._render_floats(surface)
        self._render_banner(surface)

    def _render_hud(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (9, 14, 11), self.HUD_RECT)
        pygame.draw.line(surface, BORDER_DARK, (0, self.HUD_RECT.bottom), (VIRTUAL_WIDTH, self.HUD_RECT.bottom), 2)
        run = self.run

        draw_text(surface, "VIDAS", font(16, True), INK_MUTED, (60, 26))
        for index in range(MAX_LIVES):
            filled = run is not None and index < run.lives
            self._heart(surface, (68 + index * 44, 74), 16, filled)
        draw_text(surface, f"JOGANDO: {self.player_name}", font(14), INK_MUTED, (60, 108))

        wave = run.wave if run is not None else 1
        is_boss = wave == FINAL_WAVE
        wave_label = "CONFRONTO FINAL" if is_boss else f"ONDA {wave:02d}"
        wave_color = RED if is_boss else INK_BRIGHT
        draw_text(surface, wave_label, font(39, True), wave_color, (960, 22), "midtop")
        cleared = run.cleared_in_wave if run is not None else 0
        required = captchas_required_for(wave)
        start_x = 960 - (required * 24) // 2 + 12
        for index in range(required):
            color = (RED if is_boss else AMBER) if index < cleared else BORDER_DARK
            pygame.draw.circle(surface, color, (start_x + index * 24, 86), 6)

        score = run.score if run is not None else 0
        draw_text(surface, "PONTUAÇÃO", font(15, True), INK_MUTED, (1860, 16), "topright")
        draw_text(surface, f"{score:05d}", font(32, True), INK_BRIGHT, (1860, 32), "topright")
        combo = run.combo if run is not None else 0
        combo_color = AMBER if combo >= 3 else (GREEN if combo >= 1 else INK_MUTED)
        draw_text(surface, f"COMBO x{combo}", font(18, True), combo_color, (1860, 72), "topright")
        draw_text(surface, f"recorde: {self.stats.best_score}", font(14), INK_MUTED, (1860, 96), "topright")

        overclock_rect = pygame.Rect(1600, 134, 260, 14)
        ratio = (run.overclock / OVERCLOCK_MAX) if run is not None else 0.0
        draw_text(surface, "OVERCLOCK", font(13, True), CYAN, (overclock_rect.right, overclock_rect.y - 15), "topright")
        self._meter(surface, overclock_rect, ratio, CYAN)

    def _heart(self, surface: pygame.Surface, center: tuple[int, int], size: float, filled: bool) -> None:
        color = RED if filled else BORDER_DARK
        cx, cy = center
        radius = size * 0.55
        pygame.draw.circle(surface, color, (round(cx - radius * 0.6), round(cy - radius * 0.3)), round(radius))
        pygame.draw.circle(surface, color, (round(cx + radius * 0.6), round(cy - radius * 0.3)), round(radius))
        pygame.draw.polygon(
            surface,
            color,
            [
                (cx - radius * 1.15, cy),
                (cx + radius * 1.15, cy),
                (cx, cy + radius * 1.6),
            ],
        )

    def _meter(self, surface: pygame.Surface, rect: pygame.Rect, ratio: float, color: tuple[int, int, int]) -> None:
        pygame.draw.rect(surface, (20, 28, 22), rect, border_radius=6)
        fill = rect.copy()
        fill.width = max(0, round(rect.width * max(0.0, min(1.0, ratio))))
        if fill.width > 0:
            pygame.draw.rect(surface, color, fill, border_radius=6)
        pygame.draw.rect(surface, BORDER_DARK, rect, 2, border_radius=6)

    def _render_stage(self, surface: pygame.Surface) -> None:
        run = self.run
        pygame.draw.rect(surface, (13, 19, 15), self.PANEL_RECT, border_radius=20)
        pygame.draw.rect(surface, BORDER, self.PANEL_RECT, 3, border_radius=20)
        if run is None or run.captcha is None:
            return

        label = KIND_LABELS.get(run.captcha.kind, run.captcha.kind.upper())
        draw_text(surface, f"TESTE: {label}", font(17, True), AMBER, (self.PANEL_RECT.right - 24, self.PANEL_RECT.y + 22), "topright")
        draw_wrapped(
            surface,
            run.captcha.instruction,
            font(22),
            INK,
            pygame.Rect(self.PANEL_RECT.x + 24, self.PANEL_RECT.y + 20, self.PANEL_RECT.width - 280, 60),
            29,
        )

        timer_rect = pygame.Rect(self.PANEL_RECT.x + 24, self.PANEL_RECT.y + 64, self.PANEL_RECT.width - 48, 16)
        ratio = (run.time_left / run.time_limit) if run.time_limit else 0.0
        color = GREEN if ratio > 0.5 else (AMBER if ratio > 0.22 else RED)
        self._meter(surface, timer_rect, ratio, color)
        draw_text(surface, f"{max(0.0, run.time_left):0.1f}s", font(17, True), INK_BRIGHT, (timer_rect.x, timer_rect.y - 20))

        canvas = pygame.Surface(CANVAS)
        canvas.fill((13, 20, 16))
        run.captcha.render(canvas)
        surface.blit(canvas, self.CANVAS_ORIGIN)
        pygame.draw.rect(surface, BORDER_DARK, pygame.Rect(self.CANVAS_ORIGIN, CANVAS), 2)

        badge = PHASE_BADGES.get(run.phase)
        if badge is not None and self.active_banner is None:
            # A banner (wave-up, overclock, life lost...) already covers this same
            # moment on its own, bigger notice — never show both at once.
            title, color = badge
            rect = pygame.Rect(0, 0, 420, 66)
            rect.center = (self.CANVAS_ORIGIN[0] + CANVAS[0] // 2, self.CANVAS_ORIGIN[1] + CANVAS[1] // 2)
            panel = pygame.Surface(rect.size, pygame.SRCALPHA)
            panel.fill((*SCREEN_BLACK, 210))
            pygame.draw.rect(panel, color, panel.get_rect(), 3)
            surface.blit(panel, rect)
            draw_text(surface, title, font(30, True), color, rect.center, "center")

        draw_text(
            surface,
            "Erros custam tempo. Acabou o tempo, custa uma vida.",
            font(16),
            INK_MUTED,
            (self.PANEL_RECT.centerx, self.PANEL_RECT.bottom - 26),
            "center",
        )

    def _render_verify_column(self, surface: pygame.Surface) -> None:
        mood = self.mood if self.mood_timer > 0 else "suspicious"
        self.verify9.draw(surface, self.AVATAR_CENTER, 220, mood, self.elapsed)
        box = self.TAUNT_RECT
        pygame.draw.rect(surface, (10, 16, 13), box, border_radius=14)
        pygame.draw.rect(surface, MOOD_COLORS.get(mood, MOOD_COLORS["neutral"]), box, 3, border_radius=14)
        draw_text(surface, "VERIFY-9", font(16, True), MOOD_COLORS.get(mood, MOOD_COLORS["neutral"]), (box.x + 18, box.y + 14))
        draw_wrapped(surface, self.taunt, font(21), INK_BRIGHT, pygame.Rect(box.x + 18, box.y + 42, box.width - 36, box.height - 56), 26)
        rank, _ = self.stats.rank()
        draw_text(surface, f"RANK: {rank}", font(15), INK_MUTED, (box.x + 2, box.bottom + 22))

    def _render_floats(self, surface: pygame.Surface) -> None:
        for entry in self.floats:
            alpha = max(0, min(255, round(255 * entry["life"] / entry["total"])))
            rendered = font(28, True).render(entry["text"], False, entry["color"])
            rendered.set_alpha(alpha)
            surface.blit(rendered, rendered.get_rect(center=(entry["x"], entry["y"])))

    def _render_banner(self, surface: pygame.Surface) -> None:
        banner = self.active_banner
        if banner is None:
            return
        progress = banner["timer"] / banner["duration"]
        fade = 1.0 if progress < 0.8 else max(0.0, (1.0 - progress) / 0.2)
        rect = pygame.Rect(0, 0, 760, 140)
        rect.center = (960, 540)
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((*SCREEN_BLACK, round(225 * fade)))
        pygame.draw.rect(panel, (*banner["color"], round(255 * fade)), panel.get_rect(), 4, border_radius=18)
        surface.blit(panel, rect)
        title = font(44, True).render(banner["title"], False, banner["color"])
        title.set_alpha(round(255 * fade))
        surface.blit(title, title.get_rect(center=(rect.centerx, rect.y + 48)))
        subtitle = font(21).render(banner["subtitle"], False, INK_BRIGHT)
        subtitle.set_alpha(round(255 * fade))
        surface.blit(subtitle, subtitle.get_rect(center=(rect.centerx, rect.y + 96)))

    def _render_pause(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 3, 2, 190))
        surface.blit(dim, (0, 0))
        pygame.draw.rect(surface, (9, 15, 12), self.PAUSE_PANEL, border_radius=14)
        pygame.draw.rect(surface, BORDER, self.PAUSE_PANEL, 3, border_radius=14)
        draw_text(surface, "ARENA PAUSADA", font(34, True), INK_BRIGHT, (self.PAUSE_PANEL.centerx, self.PAUSE_PANEL.y + 50), "midtop")
        for label, rect in zip(PAUSE_LABELS, self.pause_rects):
            hovered = self.pointer is not None and rect.collidepoint(self.pointer)
            draw_button(surface, rect, label, hovered, size=23)

    def _render_briefing(self, surface: pygame.Surface) -> None:
        if self.briefing_view == "leaderboard":
            self._render_leaderboard_full(surface)
            return

        draw_text(surface, "ARENA VERIFY-9", font(69, True), INK_BRIGHT, (960, 56), "midtop")
        draw_text(surface, "HUMANO  vs.  INTELIGÊNCIA ARTIFICIAL", font(25, True), AMBER, (960, 132), "midtop")
        self.verify9.draw(surface, (960, 244), 150, "suspicious", self.elapsed)

        change_hover = self.pointer is not None and self.change_player_rect.collidepoint(self.pointer)
        draw_button(surface, self.change_player_rect, f"JOGANDO: {self.player_name}  (trocar)", change_hover, CYAN, 15)

        y = 330
        rules_font = font(21)
        rules_rect_width = 1040
        for line in ARENA_RULES:
            draw_wrapped(surface, line, rules_font, INK, pygame.Rect(440, y, rules_rect_width, 44), 26, center=True)
            wrapped_line_count = len(wrap_text(line, rules_font, rules_rect_width))
            y += wrapped_line_count * 26 + 10

        rank, next_at = self.stats.rank()
        next_text = (
            f"PRÓXIMO RANK EM {max(0, next_at - self.stats.total_cleared)} VERIFICAÇÕES"
            if next_at is not None
            else "RANK MÁXIMO ATINGIDO"
        )
        self._render_stats_panel(surface, rank, next_text)
        self._render_leaderboard_preview(surface)

        link_hover = self.pointer is not None and self.view_leaderboard_rect.collidepoint(self.pointer)
        link_label = "VER RANKING COMPLETO" if self.leaderboard.entries else "AINDA SEM RANKING — SEJA O 1º"
        draw_button(surface, self.view_leaderboard_rect, link_label, link_hover, CYAN, 17)

        start_hover = self.pointer is None or self.start_rect.collidepoint(self.pointer)
        back_hover = self.pointer is not None and self.back_rect.collidepoint(self.pointer)
        draw_button(surface, self.start_rect, "ENTRAR NA ARENA", start_hover, GREEN, 28)
        draw_button(surface, self.back_rect, "VOLTAR AO MENU", back_hover, AMBER, 21)

    def _render_stats_panel(self, surface: pygame.Surface, rank: str, next_text: str) -> None:
        rect = self.stats_rect
        pygame.draw.rect(surface, PANEL, rect, border_radius=12)
        pygame.draw.rect(surface, BORDER_DARK, rect, 2, border_radius=12)
        draw_text(surface, "SEU PROGRESSO", font(15, True), INK_MUTED, (rect.centerx, rect.y + 10), "midtop")
        draw_text(surface, f"Recorde: {self.stats.best_score} pts", font(18, True), INK_BRIGHT, (rect.centerx, rect.y + 32), "midtop")
        draw_text(surface, f"Onda máxima: {self.stats.best_wave}", font(15), INK, (rect.centerx, rect.y + 56), "midtop")
        draw_text(surface, f"Rank: {rank}", font(15, True), AMBER, (rect.centerx, rect.y + 76), "midtop")
        draw_text(surface, next_text, font(13), INK_MUTED, (rect.centerx, rect.y + 96), "midtop")
        if self.stats.total_victories > 0:
            draw_text(surface, f"VERIFY-9 derrotado {self.stats.total_victories}x", font(14, True), GREEN, (rect.centerx, rect.y + 118), "midtop")

    def _render_leaderboard_preview(self, surface: pygame.Surface) -> None:
        rect = self.board_rect
        pygame.draw.rect(surface, PANEL, rect, border_radius=12)
        pygame.draw.rect(surface, BORDER_DARK, rect, 2, border_radius=12)
        draw_text(surface, "RANKING — TOP 5", font(15, True), INK_MUTED, (rect.centerx, rect.y + 12), "midtop")
        entries = self.leaderboard.entries[:5]
        if not entries:
            draw_text(surface, "Nenhum recorde ainda.", font(16), INK_MUTED, (rect.centerx, rect.y + 54), "midtop")
            draw_text(surface, "Seja o primeiro da estação!", font(14), INK_MUTED, (rect.centerx, rect.y + 76), "midtop")
            return
        row_y = rect.y + 34
        for index, entry in enumerate(entries):
            color = AMBER if index == 0 else INK
            draw_text(surface, f"{index + 1}.", font(16, True), color, (rect.x + 20, row_y))
            draw_text(surface, entry.name, font(16, True), color, (rect.x + 48, row_y))
            draw_text(surface, str(entry.score), font(16, True), color, (rect.right - 20, row_y), "topright")
            row_y += 19

    def _render_leaderboard_full(self, surface: pygame.Surface) -> None:
        draw_text(surface, "RANKING — ARENA VERIFY-9", font(48, True), AMBER, (960, 60), "midtop")
        draw_text(surface, "Os melhores da estação. Supere quem estiver na frente.", font(19), INK, (960, 118), "midtop")

        panel = pygame.Rect(0, 0, 900, 560)
        panel.center = (960, 560)
        pygame.draw.rect(surface, PANEL, panel, border_radius=16)
        pygame.draw.rect(surface, BORDER, panel, 3, border_radius=16)

        header_y = panel.y + 22
        draw_text(surface, "#", font(16, True), INK_MUTED, (panel.x + 40, header_y))
        draw_text(surface, "NOME", font(16, True), INK_MUTED, (panel.x + 100, header_y))
        draw_text(surface, "ONDA", font(16, True), INK_MUTED, (panel.right - 260, header_y))
        draw_text(surface, "PONTOS", font(16, True), INK_MUTED, (panel.right - 40, header_y), "topright")
        pygame.draw.line(surface, BORDER_DARK, (panel.x + 24, header_y + 26), (panel.right - 24, header_y + 26), 2)

        entries = self.leaderboard.entries
        if not entries:
            draw_text(surface, "Ninguém entrou para o ranking ainda.", font(23), INK_MUTED, panel.center, "center")
            draw_text(surface, "Jogue uma partida e seja o primeiro nome aqui.", font(17), INK_MUTED, (panel.centerx, panel.centery + 34), "midtop")
        else:
            row_y = header_y + 42
            for index, entry in enumerate(entries):
                color = AMBER if index == 0 else (INK_BRIGHT if index < 3 else INK)
                draw_text(surface, f"{index + 1}", font(22, True), color, (panel.x + 40, row_y))
                draw_text(surface, entry.name, font(22, True), color, (panel.x + 100, row_y))
                draw_text(surface, f"{entry.wave}", font(22, True), color, (panel.right - 260, row_y))
                draw_text(surface, f"{entry.score}", font(22, True), color, (panel.right - 40, row_y), "topright")
                row_y += 46

        back_hover = self.pointer is None or self.leaderboard_back_rect.collidepoint(self.pointer)
        draw_button(surface, self.leaderboard_back_rect, "VOLTAR", back_hover, AMBER, 23)

    def _render_gameover(self, surface: pygame.Surface) -> None:
        summary = self.summary
        victory = bool(summary and summary.victory)
        new_record = bool(summary and summary.new_record)
        if victory:
            draw_text(surface, "VOCÊ DERROTOU O VERIFY-9!", font(55, True), GREEN, (960, 60), "midtop")
        else:
            draw_text(surface, "CONEXÃO ENCERRADA", font(60, True), AMBER if new_record else RED, (960, 60), "midtop")
        self.verify9.draw(surface, (960, 210), 150, "angry" if victory else ("suspicious" if new_record else "angry"), self.elapsed)
        draw_wrapped(surface, self.taunt, font(22), INK_BRIGHT, pygame.Rect(540, 306, 840, 56), 28, center=True)

        if summary is not None:
            y = 388
            if victory:
                draw_text(surface, "CONFRONTO FINAL VENCIDO. HUMANIDADE PROVADA.", font(25, True), GREEN, (960, y), "midtop")
                y += 42
            elif self.achieved_rank is not None:
                draw_text(surface, f"#{self.achieved_rank + 1} NO RANKING DA ESTAÇÃO!", font(28, True), AMBER, (960, y), "midtop")
                y += 42
            elif new_record:
                draw_text(surface, "NOVO RECORDE PESSOAL!", font(28, True), AMBER, (960, y), "midtop")
                y += 42
            lines = (
                f"PONTUAÇÃO FINAL: {summary.score}",
                f"ONDA ALCANÇADA: {summary.wave}",
                f"VERIFICAÇÕES RESOLVIDAS: {summary.cleared}",
                f"MELHOR COMBO: x{summary.best_combo}",
                f"RANK: {summary.rank}"
                + (f"  ·  próximo em {max(0, summary.next_rank_at - self.stats.total_cleared)}" if summary.next_rank_at else "  ·  máximo"),
            )
            for line in lines:
                draw_text(surface, line, font(23, True), INK, (960, y), "midtop")
                y += 34

        retry_hover = self.pointer is None or self.retry_rect.collidepoint(self.pointer)
        menu_hover = self.pointer is not None and self.menu_rect.collidepoint(self.pointer)
        draw_button(surface, self.retry_rect, "JOGAR DE NOVO", retry_hover, GREEN, 25)
        draw_button(surface, self.menu_rect, "MENU PRINCIPAL", menu_hover, AMBER, 23)

    def _render_name_entry(self, surface: pygame.Surface) -> None:
        draw_text(surface, "ARENA VERIFY-9", font(64, True), INK_BRIGHT, (960, 56), "midtop")
        draw_text(surface, "QUEM ESTÁ JOGANDO?", font(28, True), AMBER, (960, 128), "midtop")
        self.verify9.draw(surface, (960, 244), 150, "suspicious", self.elapsed)
        draw_text(surface, "Digite seu nome ou apelido para entrar na arena:", font(21), INK, (960, 336), "midtop")

        box = self.name_input_rect
        pygame.draw.rect(surface, (10, 16, 13), box, border_radius=10)
        pygame.draw.rect(surface, AMBER, box, 3, border_radius=10)
        blink = int(self.elapsed * 2) % 2 == 0
        if self.name_buffer:
            shown = self.name_buffer + ("_" if blink else "")
            draw_text(surface, shown, font(32, True), INK_BRIGHT, box.center, "center")
        else:
            draw_text(surface, "_" if blink else "", font(32, True), INK_MUTED, box.center, "center")
        draw_text(surface, f"{len(self.name_buffer)}/{NAME_MAX_LEN}", font(14), INK_MUTED, (box.right, box.bottom + 6), "topright")

        confirm_hover = self.pointer is None or self.name_confirm_rect.collidepoint(self.pointer)
        draw_button(surface, self.name_confirm_rect, "CONTINUAR", confirm_hover, GREEN, 25)
        draw_text(
            surface,
            "Enter também confirma. Em branco entra como ANÔNIMO.",
            font(15),
            INK_MUTED,
            (960, self.name_confirm_rect.bottom + 22),
            "midtop",
        )

    # -- sound -----------------------------------------------------------
    def _play_sound(self, name: str, volume: float = 0.8) -> None:
        if self.audio is not None:
            self.audio.play(name, volume)
