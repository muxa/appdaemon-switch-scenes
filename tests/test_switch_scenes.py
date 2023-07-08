import pytest
import pytest_mock
from unittest import mock
from appdaemon_testing.pytest import automation_fixture
from apps.switch_scenes.switch_scenes import SwitchScenes

HASS_LISTEN_STATE = "listen_state"
HASS_RUN_IN = "run_in"
HASS_CANCEL_TIMER = "cancel_timer"
HASS_CALL_SERVICE = "call_service"

MAIN_SWITCH = "light.main_switch"
SCENE_LIGHT_1 = "light.scene_light_1"
SCENE_LIGHT_2 = "light.scene_light_2"

@automation_fixture(
    SwitchScenes,
    args={
        "switch": MAIN_SWITCH,
        "scenes": [
            {
                "name": "First",
                "entities": {
                    SCENE_LIGHT_1: "on",
                    SCENE_LIGHT_2: "off"
                }
            },
            {
                "name": "Second",
                "entities": {
                    SCENE_LIGHT_1: "off",
                    SCENE_LIGHT_2: "on"
                }
            },
            {
                "name": "Both",
                "entities": {
                    SCENE_LIGHT_1: "on",
                    SCENE_LIGHT_2: "on"
                }
            },
            {
                "name": "Off",
                "entities": {
                    SCENE_LIGHT_1: "off",
                    SCENE_LIGHT_2: "off"
                }
            },
        ],
        "log_level": "DEBUG"
    },
)
def switch_scenes_app() -> SwitchScenes:
    pass

def test_listens_to_switch(hass_driver, switch_scenes_app: SwitchScenes):
    listen_state = hass_driver.get_mock(HASS_LISTEN_STATE)
    listen_state.assert_called_once_with(
        switch_scenes_app._on_switch_state, MAIN_SWITCH)

def test_switch_starts_1s_timer_when_changed(hass_driver, switch_scenes_app: SwitchScenes):
    with hass_driver.setup():
        hass_driver.set_state(MAIN_SWITCH, "off")

    hass_driver.set_state(MAIN_SWITCH, "on")
    run_in = hass_driver.get_mock(HASS_RUN_IN)
    run_in.assert_called_once_with(
        switch_scenes_app._on_switch_toggle_timeout, 1)

def test_switch_timout_does_not_change_scenes(hass_driver, switch_scenes_app: SwitchScenes):
    with hass_driver.setup():
        hass_driver.set_state(MAIN_SWITCH, "off")

    hass_driver.set_state(MAIN_SWITCH, "on")
    switch_scenes_app._on_switch_toggle_timeout({})
    call_service = hass_driver.get_mock(HASS_CALL_SERVICE)
    call_service.assert_not_called()

def test_timeout_cancelled_when_switch_toggled_within_timout(hass_driver, switch_scenes_app: SwitchScenes):
    with hass_driver.setup():
        hass_driver.set_state(MAIN_SWITCH, "off")

    hass_driver.set_state(MAIN_SWITCH, "on")
    hass_driver.set_state(MAIN_SWITCH, "off")
    
    cancel_timer = hass_driver.get_mock(HASS_CANCEL_TIMER)
    cancel_timer.assert_called()

def test_scene_applied_when_switch_toggled_within_timeout(hass_driver, switch_scenes_app: SwitchScenes, mocker: pytest_mock.MockerFixture):
    with hass_driver.setup():
        hass_driver.set_state(MAIN_SWITCH, "off")

    apply_scene_spy = mocker.spy(switch_scenes_app, "apply_scene")

    hass_driver.set_state(MAIN_SWITCH, "on")
    hass_driver.set_state(MAIN_SWITCH, "off")

    apply_scene_spy.assert_called_once_with(1)

def test_first_scene_activate_when_switch_toggled_on_last_scene(hass_driver, switch_scenes_app: SwitchScenes, mocker: pytest_mock.MockerFixture):
    with hass_driver.setup():
        hass_driver.set_state(MAIN_SWITCH, "off")

    switch_scenes_app.current_scene_index = 3
    apply_scene_spy = mocker.spy(switch_scenes_app, "apply_scene")

    hass_driver.set_state(MAIN_SWITCH, "on")
    hass_driver.set_state(MAIN_SWITCH, "off")

    apply_scene_spy.assert_called_once_with(0)

def test_calls_service_for_all_entities_in_scene(hass_driver, switch_scenes_app: SwitchScenes):

    switch_scenes_app.apply_scene(0)

    call_service = hass_driver.get_mock(HASS_CALL_SERVICE)

    call_service.assert_has_calls([
        mock.call("homeassistant/turn_on", entity_id=SCENE_LIGHT_1),
        mock.call("homeassistant/turn_off", entity_id=SCENE_LIGHT_2),
    ])