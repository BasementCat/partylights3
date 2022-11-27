# TODO

## misc

  * main/separate thread for running node stack - keep it out of OSC thread

## Nodes

### Common/basic

* Threshold
    - inputs:
        + value(float) - value to consider
        + low(float) - low end of range
        + high(float) - high end of range
        + bool(bool) - whether to consider above/below or just in
        + invert(bool) - invert bool output
    - outputs:
        + threshold(float) - 1 if >= high, -1 if <= low, 0 otherwise - unless bool, then just cast to bool, and invert as appropriate
* changed:
    - inputs:
        + value(float) - value to consider
    - outputs:
        + value(float) - emit same value, but only if changed

### Music

* measures
    - inputs:
        + reset(bool): reset clocks
        + TODO: beat input,consider confidence(reset on low confidence & don't emit)
        + beats/measure(int): dfl 4, # of beats per measure
        + beats/phrase(int): dfl 16, # of beats per phrase
    - outputs:
        + measure: every n beats, emit measure clock
        + phrase: every n beats, emit phrase clock
* drop:
    - inputs:
        + audio(float): Audio value to check for presence
        + beat clock(float): beat counter
        + #TODO: consider confidence
        + beat duration(int): # of silent beats (dfl 3)
        + low threshold(float): below this, consider no audio
        + high threshold(float): above this, consider audio
    - outputs:
        + drop(bool): if audio remains below low threshold for no more than n beats, then jumps to above high threshold, emit drop

movement - circle, pan, sine, etc
cycle (colors, scenes, etc)
rgb?
strobes
that one light
lasers
idle/dead behavior

light outputs - dmx