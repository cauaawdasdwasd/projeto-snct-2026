from __future__ import annotations

import os
from pathlib import Path
import sys


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.assets import AssetManager
from src.core.input_manager import InputManager
from src.core.scene_manager import SceneManager
from src.core.settings import ASSETS_DIR, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from src.scenes.audit import AuditScene
from src.scenes.desktop import DesktopScene


OUTPUT_DIR = ROOT / "site" / "imagens"


def save_scene(scene: object, filename: str, pointer: tuple[int, int] | None = None) -> None:
    input_manager.mouse_position = pointer
    surface.fill((0, 0, 0))
    scene.render(surface)
    pygame.image.save(surface, OUTPUT_DIR / filename)


pygame.init()
pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

assets = AssetManager(ASSETS_DIR)
manager = SceneManager()
input_manager = InputManager((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT)).convert()

audit = AuditScene(manager, assets, input_manager)
desktop = DesktopScene(manager, assets, input_manager, audit_scene=audit)

# The real interactive desktop, before any application is opened.
desktop.on_enter()
save_scene(desktop, "galeria-windows.png", (1010, 515))

# The tutorial desk before the decisive comparison is made.
audit.set_embedded_mode(False)
audit._load_case(-1, tutorial=True)
audit.case_dialog.mode = None
audit.ai_report_seen = True
audit._focus_document("profile")
save_scene(audit, "area-de-auditoria.png", (1010, 515))

# A document opened in the inspector, without collecting any evidence.
audit._load_case(0)
audit.case_dialog.mode = None
audit.ai_report_seen = True
contract = audit._get_document("contract")
audit._focus_document("contract")
audit.document_inspector.open(contract)
save_scene(audit, "galeria-documento.png", (1010, 515))

# A different contract with only its first two source documents visible.
audit._load_case(1)
audit.case_dialog.mode = None
audit.ai_report_seen = True
audit._focus_document("job")
audit._focus_document("candidate")
save_scene(audit, "galeria-outro-caso.png", (1010, 515))

pygame.quit()
