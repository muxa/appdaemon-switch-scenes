import appdaemon.plugins.hass.hassapi as hass

DEBUG = "DEBUG"

class SwitchScenes(hass.Hass):
    def initialize(self):

        self.switch = self.args["switch"]
        self.scenes = self.args["scenes"]        
        self.toggle_max_seconds = 1
        self.current_scene_index = 0

        self.listen_state(self._on_switch_state, self.switch)

        # these are used for timeout handlers
        self.switch_tiggle_timeout_handle = None

        self.log(f'Initialised Switch Scenes (switch: {self.switch}, scenes: {self.scenes})', level=DEBUG)

    def _on_switch_state(self, entity, attribute, old, new, kwargs):
        self.log(f'Switch {self.switch} changed from {old} to {new}', level=DEBUG)

        if self.switch_tiggle_timeout_handle == None:
            self.log('Wait for toggle...', level=DEBUG)
            self.switch_tiggle_timeout_handle = self.run_in(self._on_switch_toggle_timeout, self.toggle_max_seconds)
        else:
            self._cancel_switch_toggle_timeout()
            self.log('Toggled. Activate next scene', level=DEBUG)
            self.apply_scene((self.current_scene_index + 1) % len(self.scenes))


    def apply_scene(self, scene_index):
        if scene_index < 0 or scene_index >= len(self.scenes):
            raise ValueError(f'Scene index is out of range: {scene_index}')

        self.current_scene_index = scene_index
        name = self.scenes[scene_index]['name']
        entities = self.scenes[scene_index]['entities']
        self.log(f'Activate scene {name} ({self.current_scene_index}): {entities})', level=DEBUG)
        
        for entity_id, state in entities.items():
            self.call_service(f"homeassistant/turn_{state}", entity_id = entity_id)

    def _cancel_switch_toggle_timeout(self):
        if self.switch_tiggle_timeout_handle != None:
            self.cancel_timer(self.switch_tiggle_timeout_handle)
            self.switch_tiggle_timeout_handle = None

    def _on_switch_toggle_timeout(self, kwargs):
        self.switch_tiggle_timeout_handle = None
        self.log(f"Switch not toggled within {self.toggle_max_seconds}s", level=DEBUG)