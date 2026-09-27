import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.app import Application
from src.gameplay import cases as C
from src.scenes import audit as A


def _visible_union(scene):
    docs = [d for d in scene.documents if d.visible]
    return docs[0].rect.unionall([d.rect for d in docs[1:]])


def test_right_drag_pans_the_desk_in_every_direction_at_every_zoom(monkeypatch) -> None:
    app = Application()
    app.scene_manager.switch_to("audit")
    scene = app.scene_manager.current_scene
    four = next(c for c in C.CASE_BANK if len(c.documents) == 4)
    monkeypatch.setattr(A, "pick_shift", lambda seen, rng=None, count=5: [four])
    scene.begin_shift(1, False, False)
    scene.story_intro.close()
    for zoom in A.DESK_ZOOM_LEVELS:
        scene._set_desk_zoom(zoom)
        for delta in ((60, 0), (-60, 0), (0, 60), (0, -60)):
            for _ in range(40):
                scene._pan_documents(delta)
        scene._pan_documents((400, 0))
        right_edge = _visible_union(scene).left
        scene._pan_documents((-30, 0))
        assert _visible_union(scene).left < right_edge or right_edge <= A.DOCUMENT_WORKSPACE.right - 220 + 1
        # coming back from the far right must work
        for _ in range(60):
            scene._pan_documents((-40, 0))
        assert _visible_union(scene).right <= A.DOCUMENT_WORKSPACE.left + 220 + 1
        for _ in range(60):
            scene._pan_documents((40, 0))
        assert _visible_union(scene).left >= A.DOCUMENT_WORKSPACE.right - 220 - 1
