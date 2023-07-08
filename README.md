# Switch Scenes for AppDaemon

Extend a light switch to be able to control other switches.

## Arguments

- `switch`: entity id of the main switch which will control other switches. This can be anything that has a state of `on` or `off`
- `scenes`: list of scenes; each scene has a `name` attribute and a `entities` attribute, which is a dictionary of entity id as a key and the state as a value for when this scene is on

At least one on scene is required. 

## Example

```yaml
bedroom_light:
  module: switch_scenes
  class: SwitchScenes
  switch: light.bedroom_main_light
  scenes:
    - name: Night Light On
      entities:
        light.night_light: "on"
    - name: Night Light Off
      entities:
        light.night_light: "off"
```