# TODO

## misc

  * main/separate thread for running node stack - keep it out of OSC thread

## Node combos:
    threshold on audio level -> drop, pretty much required
    threshold on audio level -> timer for idle/dead
        pass through threshold again for idle/dead bool

## Nodes

### Common/basic

### Music


movement - circle, pan, sine, etc
cycle (colors, scenes, etc)
rgb?
strobes
that one light
lasers
idle/dead behavior

light outputs - dmx

----------

effect: animation of one or more parameters over a time period or # of beats, w/ easing functions
program: sequence of effects running sequentially
scene: collections of programs running simultaneously

mood: collections of property values, optionally grouped by band, can be used in effects

triggers: based on input data, do things like change effects/programs/scenes

effects, programs, scenes may apply to 0 or more lights or groups, those applied to lights are highest priority, then groups, then all
they may also specify a priority: default is order, but this allows temporary triggered effects to take precedence