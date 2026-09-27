p = "src/minigames/captchas.py"
s = open(p, encoding="utf-8").read()

i = s.index("class RotateCaptcha(Captcha):")
j = s.index("    def upright(self) -> bool:", i)
new_head = '''def _sky_and_ground(size: int, ground_top: int) -> pygame.Surface:
    scene = pygame.Surface((size, size), pygame.SRCALPHA)
    for y in range(size):
        shade = y / size
        pygame.draw.line(scene, (70 + int(90 * shade), 150 + int(70 * shade), 230), (0, y), (size, y))
    pygame.draw.circle(scene, (255, 226, 90), (size - 56, 52), 26)  # the sun is always up
    for cx, cy in ((54, 60), (150, 34)):
        for dx, dy, r in ((0, 0, 16), (16, 4, 13), (-16, 5, 12)):
            pygame.draw.circle(scene, (250, 250, 255), (cx + dx, cy + dy), r)
    pygame.draw.rect(scene, (74, 168, 84), (0, ground_top, size, size - ground_top))
    pygame.draw.rect(scene, (52, 130, 62), (0, ground_top, size, 6))
    return scene


def _scene_person(size: int) -> pygame.Surface:
    scene = _sky_and_ground(size, 176)
    cx = size // 2
    pygame.draw.line(scene, (40, 40, 60), (cx - 8, 138), (cx - 12, 186), 8)  # legs
    pygame.draw.line(scene, (40, 40, 60), (cx + 8, 138), (cx + 12, 186), 8)
    pygame.draw.ellipse(scene, (30, 30, 30), (cx - 26, 182, 20, 10))  # shoes
    pygame.draw.ellipse(scene, (30, 30, 30), (cx + 6, 182, 20, 10))
    pygame.draw.rect(scene, (220, 70, 60), (cx - 20, 88, 40, 56), border_radius=8)  # shirt
    pygame.draw.line(scene, (220, 70, 60), (cx - 20, 96), (cx - 42, 128), 8)  # arms
    pygame.draw.line(scene, (220, 70, 60), (cx + 20, 96), (cx + 42, 128), 8)
    pygame.draw.circle(scene, (238, 200, 160), (cx, 66), 22)  # head
    pygame.draw.circle(scene, (250, 250, 250), (cx - 8, 62), 5)
    pygame.draw.circle(scene, (250, 250, 250), (cx + 8, 62), 5)
    pygame.draw.circle(scene, (20, 20, 20), (cx - 8, 63), 2)
    pygame.draw.circle(scene, (20, 20, 20), (cx + 8, 63), 2)
    pygame.draw.arc(scene, (150, 60, 50), (cx - 10, 68, 20, 14), math.pi * 1.1, math.pi * 1.9, 3)
    pygame.draw.rect(scene, (60, 40, 30), (cx - 22, 42, 44, 12), border_top_left_radius=12, border_top_right_radius=12)  # hair
    pygame.draw.rect(scene, (120, 84, 50), (28, 150, 10, 30))  # tree
    pygame.draw.circle(scene, (40, 130, 60), (33, 140), 22)
    return scene


def _scene_house(size: int) -> pygame.Surface:
    scene = _sky_and_ground(size, 170)
    pygame.draw.rect(scene, (236, 210, 150), (66, 104, 108, 76))
    pygame.draw.polygon(scene, (190, 70, 60), [(54, 108), (120, 52), (186, 108)])
    pygame.draw.rect(scene, (150, 60, 50), (150, 56, 14, 30))  # chimney
    for k in range(3):  # smoke rises
        pygame.draw.circle(scene, (235, 235, 240), (160 + k * 5, 44 - k * 14), 7 + k * 2)
    pygame.draw.rect(scene, (110, 70, 44), (108, 134, 26, 46))  # door
    pygame.draw.circle(scene, (240, 200, 60), (128, 158), 2)
    for x in (76, 146):
        pygame.draw.rect(scene, (120, 190, 240), (x, 118, 22, 20))
        pygame.draw.rect(scene, (80, 60, 40), (x, 118, 22, 20), 2)
    pygame.draw.polygon(scene, (200, 180, 140), [(108, 180), (134, 180), (150, 236), (90, 236)])  # path
    return scene


def _scene_rocket(size: int) -> pygame.Surface:
    scene = _sky_and_ground(size, 190)
    cx = size // 2
    pygame.draw.polygon(scene, (255, 170, 40), [(cx - 12, 168), (cx + 12, 168), (cx, 206)])  # flame is below
    pygame.draw.ellipse(scene, (236, 236, 244), (cx - 20, 50, 40, 124))
    pygame.draw.polygon(scene, (210, 50, 50), [(cx - 20, 82), (cx + 20, 82), (cx, 42)])  # red nose on top
    pygame.draw.circle(scene, (70, 140, 210), (cx, 104), 11)
    pygame.draw.circle(scene, (30, 60, 100), (cx, 104), 11, 3)
    pygame.draw.polygon(scene, (210, 50, 50), [(cx - 20, 140), (cx - 42, 176), (cx - 20, 164)])
    pygame.draw.polygon(scene, (210, 50, 50), [(cx + 20, 140), (cx + 42, 176), (cx + 20, 164)])
    return scene


def _scene_robot(size: int) -> pygame.Surface:
    scene = _sky_and_ground(size, 184)
    cx = size // 2
    pygame.draw.rect(scene, (110, 120, 140), (cx - 30, 118, 60, 58), border_radius=6)  # body
    pygame.draw.rect(scene, (80, 90, 110), (cx - 30, 176, 22, 14))  # feet
    pygame.draw.rect(scene, (80, 90, 110), (cx + 8, 176, 22, 14))
    pygame.draw.rect(scene, (150, 160, 180), (cx - 36, 58, 72, 56), border_radius=10)  # head
    pygame.draw.circle(scene, (110, 230, 130), (cx - 14, 84), 8)
    pygame.draw.circle(scene, (110, 230, 130), (cx + 14, 84), 8)
    pygame.draw.line(scene, (80, 90, 110), (cx, 58), (cx, 38), 4)  # antenna on top
    pygame.draw.circle(scene, (230, 80, 70), (cx, 34), 6)
    pygame.draw.line(scene, (80, 90, 110), (cx - 30, 130), (cx - 50, 156), 7)
    pygame.draw.line(scene, (80, 90, 110), (cx + 30, 130), (cx + 50, 156), 7)
    return scene


ROTATE_SCENES = (
    (_scene_person, "Gire a imagem até a pessoa ficar em pé."),
    (_scene_house, "Gire a imagem até a casa ficar em pé."),
    (_scene_rocket, "Gire a imagem até o foguete apontar para cima."),
    (_scene_robot, "Gire a imagem até o robô ficar em pé."),
)


class RotateCaptcha(Captcha):
    kind = "rotate"
    instruction = "Gire a imagem até a pessoa ficar em pé."
    LEFT = pygame.Rect(180, 304, 90, 44)
    RIGHT = pygame.Rect(450, 304, 90, 44)
    VERIFY = pygame.Rect(280, 304, 160, 44)
    CENTER = (360, 150)
    SIZE = 240
    TOLERANCE = 12

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        drawer, self.instruction = rng.choice(ROTATE_SCENES)
        self.image = drawer(self.SIZE)
        self.angle = rng.choice([-1, 1]) * rng.randrange(45, 166, 15)
        self.dragging = False
        self._last_x = 0
        self._mask = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self._mask, (255, 255, 255, 255), (self.SIZE // 2, self.SIZE // 2), self.SIZE // 2)

'''
s = s[:i] + new_head + s[j:]

old_render = """        rotated = pygame.transform.rotate(self.image, -self.angle)
        surface.blit(rotated, rotated.get_rect(center=self.CENTER))
"""
new_render = """        frame = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        rotated = pygame.transform.rotate(self.image, -self.angle)
        frame.blit(rotated, rotated.get_rect(center=(self.SIZE // 2, self.SIZE // 2)))
        frame.blit(self._mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)  # keep the picture inside the circle
        surface.blit(frame, frame.get_rect(center=self.CENTER))
"""
assert old_render in s
s = s.replace(old_render, new_render)
if "\nimport math" not in s:
    s = s.replace("from __future__ import annotations\n", "from __future__ import annotations\n\nimport math", 1)
open(p, "w", encoding="utf-8").write(s)
