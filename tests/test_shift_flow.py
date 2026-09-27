import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from src.core.app import Application
from src.gameplay.cases import CASE_BANK, SHIFT_SIZE, TUTORIAL_CASE, pick_shift
from src.scenes.audit import MONITOR_SCREEN_RECT
from src.ui.game_setup import CARD_RECTS, START_RECT, TUTORIAL_RECT
from src.ui.newspaper import MENU_RECT


@pytest.fixture(scope="module")
def app():
    application = Application()
    yield application
    pygame.quit()


def _tick(app, frames=1, dt=0.05):
    for _ in range(frames):
        app.scene_manager.update(dt)


def _login(app):
    app.scene_manager.switch_to("login")
    login = app.scene_manager.current_scene
    login.username, login.password = "admin", "admin"
    login._attempt_login()
    _tick(app, 30)
    audit = app.scene_manager.current_scene
    if not audit.setup.is_open:  # a previous test left a shift running
        audit._restart_turn()
    return audit


def _click(app, scene, monitor_position):
    position = (monitor_position[0] + MONITOR_SCREEN_RECT.x, monitor_position[1] + MONITOR_SCREEN_RECT.y)
    app.input_manager.mouse_position = position
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=position, button=1, clicks=1))


def _finish_case(scene, stamp):
    scene.case_dialog.mode = None
    scene.ai_report_seen = True
    scene._commit_stamp(stamp)
    signature = pygame.Surface((40, 20), pygame.SRCALPHA)
    pygame.draw.line(signature, (0, 0, 0, 255), (2, 2), (38, 18), 3)
    scene._get_document("final").sign(signature)
    scene._advance_case_or_show_newspaper()


def test_login_opens_the_setup_screen_and_clicks_choose_the_shift(app):
    audit = _login(app)
    assert type(audit).__name__ == "AuditScene"
    assert audit.setup.is_open
    _click(app, audit, CARD_RECTS[2].center)
    assert audit.setup.count == 10
    _click(app, audit, CARD_RECTS[0].center)
    assert audit.setup.count == 1
    _click(app, audit, TUTORIAL_RECT.center)
    assert not audit.setup.with_tutorial
    _click(app, audit, START_RECT.center)
    assert not audit.setup.is_open
    assert len(audit.shift_cases) == 1
    assert not audit.tutorial_active and audit.case is audit.shift_cases[0]
    assert audit.case_dialog.mode == "briefing"


def test_setup_keyboard_shortcuts(app):
    audit = _login(app)
    audit.setup.count, audit.setup.with_tutorial = 5, True
    audit.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_0, mod=0, unicode="0"))
    assert audit.setup.count == 10
    audit.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, mod=0, unicode=""))
    assert audit.setup.count == 5
    audit.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode=""))
    assert not audit.setup.is_open and audit.tutorial_active


@pytest.mark.parametrize("count", [1, 5, 10])
def test_full_shift_for_each_length_ends_in_the_newspaper_and_a_fresh_setup(app, count):
    audit = _login(app)
    audit.begin_shift(count, True)
    assert audit.tutorial_active and audit.case is TUTORIAL_CASE
    assert audit.case_dialog.mode == "briefing"
    first_shift = [case.case_id for case in audit.shift_cases]
    assert len(first_shift) == count

    _finish_case(audit, TUTORIAL_CASE.correct_stamp)
    assert not audit.tutorial_active
    for index, case in enumerate(list(audit.shift_cases)):
        assert audit.case is case
        sources = [d for d in audit.documents if d.document_id != "final"]
        assert 2 <= len(sources) <= 4
        assert all(d.visible for d in sources), "every paper starts on the desk"
        assert [d.order_number for d in sources] == list(range(1, len(sources) + 1))
        _finish_case(audit, case.correct_stamp if index % 2 == 0 else "deny")

    _tick(app, 80)
    assert audit.newspaper.is_open
    assert audit.newspaper.page_count == count + 1
    assert len(audit.case_results) == count

    audit.handle_escape()
    assert audit.newspaper.is_open  # Esc never throws the newspaper away

    _click(app, audit, MENU_RECT.center)
    assert type(app.scene_manager.current_scene).__name__ == "MainMenuScene"

    audit = _login(app)
    assert audit.setup.is_open and not audit.case_results and not audit.newspaper.is_open


def test_pause_menu_offers_help_and_main_menu(app):
    audit = _login(app)
    audit.begin_shift(5, True)
    audit.case_dialog.mode = None
    audit.handle_escape()
    assert audit.pause_menu.is_open
    assert audit.pause_menu._activate(1) == "help"
    audit.pause_menu.is_open = True
    assert audit.pause_menu._activate(3) == "menu"


def test_audit_sheet_is_hidden_until_opened_from_the_side_panel(app):
    audit = _login(app)
    audit.begin_shift(1, False)
    audit.case_dialog.mode = None
    final = audit._get_document("final")
    assert not final.visible
    rows = audit.ai_decision_panel._rows()
    assert rows[-1].document_id == "final"
    audit.ai_decision_panel.scroll_to_end()
    row = audit.ai_decision_panel.row_rect_for_document("final")
    assert row is not None
    _click(app, audit, row.center)
    assert final.visible and audit.documents[-1] is final
    assert "final" in audit.read_document_ids


def test_choosing_a_stamp_also_opens_the_sheet(app):
    audit = _login(app)
    audit.begin_shift(1, False)
    audit.case_dialog.mode = None
    final = audit._get_document("final")
    audit._select_stamp(audit.stamp_buttons[0])
    assert final.visible and audit.documents[-1] is final


def test_conclusions_come_before_the_stamp_confirmation(app):
    audit = _login(app)
    audit.begin_shift(1, False)
    audit.case_dialog.mode = None
    audit.ai_report_seen = True
    audit._select_stamp(audit.stamp_buttons[0])
    audit._request_stamp("approve")
    panel = audit.conclusion_panel
    assert panel.is_open and not audit.case_dialog.is_open
    truths = [truth for _, truth in panel.statements]
    for index, truth in enumerate(truths):
        if truth:
            panel.checked.add(index)
    assert panel.score() == (len(truths), len(truths))
    _click(app, audit, panel.tutorial_target().center)  # confirm button once everything true is ticked
    assert audit.conclusion_done and audit.conclusion_answers == (len(truths), len(truths))
    assert audit.case_dialog.mode == "confirm"


def test_shift_plan_for_1_5_and_10_cases():
    import random

    rng = random.Random(3)
    one = pick_shift(set(), rng, 1)
    five = pick_shift(set(), rng, 5)
    ten = pick_shift(set(), rng, 10)
    assert len(one) == 1
    assert [c.turn for c in five] == [1, 2, 3, 4, 5]
    assert [c.turn for c in ten] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    assert len({c.case_id for c in ten}) == 10
    assert SHIFT_SIZE == 5 and all(c in CASE_BANK for c in ten)


def _timed_easy_case(app):
    """A shift of one turn-1 case, so the plan is always two popup waves and two captchas."""
    audit = _login(app)
    audit.begin_shift(1, False, True)
    audit.story_intro.close()
    audit.shift_cases[0] = next(case for case in CASE_BANK if case.turn == 1)
    audit._load_case(0)
    audit.case_dialog.mode = None
    return audit


def _play(audit, seconds, step=0.25):
    for _ in range(int(seconds / step)):
        audit.update(step)


def test_clock_runs_only_while_working_and_pauses_for_the_dossier(app):
    audit = _login(app)
    audit.begin_shift(1, False, True)
    assert audit.story_intro.is_open and not audit._clock_running()
    audit.story_intro.close()
    assert audit.case_dialog.is_open and not audit._clock_running()  # dossier: read in peace
    audit.case_dialog.mode = None
    left = audit.clock_left
    assert audit.clock_limit > 0 and audit._clock_running()
    _play(audit, 5)
    assert audit.clock_left == pytest.approx(left - 5, abs=0.3)
    audit.pause_menu.open()
    frozen = audit.clock_left
    _play(audit, 3)
    assert audit.clock_left == frozen
    audit.pause_menu.close()


def test_training_and_relaxed_mode_have_no_clock(app):
    audit = _login(app)
    audit.begin_shift(1, True, True)
    audit.story_intro.close()
    assert audit.tutorial_active and audit.clock_limit == 0 and not audit._clock_running()
    audit.begin_shift(1, False, False)
    assert audit.clock_limit == 0 and not audit._clock_running()


def test_popups_then_captcha_interrupt_the_work_and_solving_gives_time(app):
    audit = _timed_easy_case(app)
    plan = audit.clock_plan
    assert [event.kind for event in plan][-1] == "captcha"
    first_captcha = next(event for event in plan if event.kind == "captcha")
    _play(audit, plan[0].at + 1)
    assert audit.popups.active > 0
    _play(audit, first_captcha.at - audit.clock_elapsed + 1)
    assert audit.captcha_overlay.is_open and audit.captchas_shown == 1
    assert audit._clock_running()  # the clock keeps ticking during the test
    before = audit.clock_left
    captcha = audit.captcha_overlay.captcha
    captcha.win()
    _play(audit, 2)
    assert not audit.captcha_overlay.is_open and audit.captchas_solved == 1
    assert audit.clock_left > before - 3  # +6s bonus minus the 2s that passed


def test_wrong_answers_and_skipping_cost_time(app):
    audit = _timed_easy_case(app)
    audit._trigger(audit.clock_plan[-1])
    assert audit.captcha_overlay.is_open
    before = audit.clock_left
    audit.captcha_overlay.captcha.fail()
    audit.update(0.01)
    assert audit.clock_left <= before - 2.9
    audit.captcha_overlay.elapsed = 100
    before = audit.clock_left
    from src.ui.captcha_overlay import SKIP_RECT
    _click(app, audit, SKIP_RECT.center)
    audit.update(0.01)
    assert not audit.captcha_overlay.is_open
    assert audit.clock_left <= before - 14


def test_running_out_of_time_sends_the_case_away_without_a_decision(app):
    audit = _login(app)
    audit.begin_shift(2, False, True)
    audit.story_intro.close()
    audit.case_dialog.mode = None
    first = audit.case
    audit.clock_left = 0.4
    _play(audit, 1)
    assert audit.timeout_time > 0 and audit.case_completed
    assert audit.case_results[-1].selected_stamp == "timeout" and not audit.case_results[-1].correct
    _play(audit, 3)
    assert audit.timeout_time == 0 and audit.case is not first  # next case is on the desk
    assert audit.clock_left > 0 and audit.case_dialog.is_open


def test_popups_block_clicks_until_closed_and_stamping_clears_them(app):
    audit = _login(app)
    audit.begin_shift(1, False, True)
    audit.story_intro.close()
    audit.case_dialog.mode = None
    audit.popups.spawn(2, decoys=False)
    popup = audit.popups.popups[-1]
    _click(app, audit, popup.close_rect.center)
    assert audit.popups.active == 1
    audit._commit_stamp("approve")
    assert audit.popups.active == 0 and not audit._clock_running()


def test_setup_screen_clock_toggle(app):
    audit = _login(app)
    from src.ui.game_setup import CLOCK_RECT
    assert audit.setup.with_clock
    _click(app, audit, CLOCK_RECT.center)
    assert not audit.setup.with_clock
    audit.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c, mod=0, unicode="c"))
    assert audit.setup.with_clock
