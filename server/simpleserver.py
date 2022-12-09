from threading import Thread, Event, Lock
import time
import signal
import random

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


MIN_BPM_CONF = 0.8

stop_event = Event()


class Transition:
    def __init__(self, light, function, from_value, to_value, duration, start=None, cloned_from=None):
        self.function = function
        self.from_value = from_value
        self.to_value = to_value
        self.duration = duration
        self.cloned_from = cloned_from
        self.start = start or time.time()
        self.speed = None
        if light:
            self.set_light(light)

    def set_light(self, light):
        if light.type.functions.get('speed') and light.type.functions.get(self.function, {}).speed:
            high, low = light.type.functions[self.function].speed
            speed = self.duration / (high - low)
            self.speed = max(0, min(1, speed))
        if self.from_value is None:
            self.from_value = light.get_raw_state(self.function, 0)

    def clone(self, light=None, **props):
        kwargs = {
            'function': self.function,
            'from_value': self.from_value,
            'to_value': self.to_value,
            'duration': self.duration,
        }
        kwargs.update(props)
        return Transition(light, start=self.start, cloned_from=self, **kwargs)

    @property
    def expired(self):
        return time.time() >= self.start + self.duration
    
    def __call__(self):
        if self.expired:
            return {self.function: self.to_value}
        elif self.speed is None:
            pc = (time.time() - self.start) / self.duration
            return {self.function: (pc * (self.to_value - self.from_value)) + self.from_value}
        else:
            return {'speed': self.speed, self.function: self.to_value}


class OSCBlockingThread(Thread):
    def __init__(self, host, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self.osc_handler)
        self.server = BlockingOSCUDPServer((self.host, self.port), self.dispatcher)
        self.data = {}
        self.lock = Lock()

    def run(self):
        # This blocks forever - server.shutdown() is called externally when threads should exit & at that point the main thread loop will also exit
        self.server.serve_forever()

    def osc_handler(self, address, *args):
        with self.lock:
            # for synesthesia, all addresses have 1 arg
            self.data[address] = args[0]

    def get_data(self):
        with self.lock:
            return dict(self.data)


class OSCThread(Thread):
    def __init__(self, host='0.0.0.0', port=7000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocking_thread = OSCBlockingThread(host, port)

    def start(self):
        super().start()
        self.blocking_thread.start()

    def run(self):
        stop_event.wait()
        self.blocking_thread.server.shutdown()
        self.blocking_thread.join()

    def get_data(self):
        return self.blocking_thread.get_data()


class ProcessThread(Thread):
    def __init__(self, osc, layers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.osc = osc
        self.layers = layers or []
        self.last_replace_layer = None
        self.data = {}
        self.state = {}
        self.expanded_state = {}
        self.lock = Lock()

    def run(self):
        while not stop_event.is_set():
            with self.lock:
                last_replace_layer = None
                self.data = self.osc.get_data()
                for l in self.layers:
                    lstate = l(self.data, self.state)
                    if lstate is not None:
                        if l.replace:
                            self.state = lstate or {}
                            last_replace_layer = l
                        else:
                            for k, v in (lstate or {}).items():
                                if isinstance(self.state.get(k), Transition) and not self.state[k].expired:
                                    continue
                                self.state[k] = v
                if self.last_replace_layer is not last_replace_layer:
                    self.last_replace_layer = last_replace_layer
                    self.expanded_state = {}

    def get_data(self):
        with self.lock:
            data = dict(self.data)
            state = dict(self.state)
        lights = {l.name: l for l in Light.get()}
        # pass 1 - specific lights
        for k, v in state.items():
            if '.' in k:
                light_name, function = k.split('.')
                light = lights.get(light_name)
                if not light:
                    continue
                if function not in light.type.functions:
                    continue
                current_v = self.expanded_state.get(light_name, {}).get(function)
                if isinstance(current_v, Transition) and not current_v.expired:
                    continue
                if isinstance(v, Transition):
                    v = v.clone(light)
                self.expanded_state.setdefault(light_name, {})[function] = v

        # pass 2 - properties across all lights
        for k, v in state.items():
            if '.' not in k:
                for light_name, light in lights.items():
                    if k not in light.type.functions:
                        continue
                    current_v = self.expanded_state.get(light_name, {}).get(k)
                    if isinstance(current_v, Transition) and not current_v.expired:
                        continue
                    if isinstance(v, Transition):
                        v = v.clone(light)
                    self.expanded_state.setdefault(light_name, {})[k] = v

        # pass 3 - resolve any transitions in the expanded state
        resolved_state = {}
        for light_name, functions in self.expanded_state.items():
            resolved_state.setdefault(light_name, {})
            for function, value in functions.items():
                if isinstance(value, Transition):
                    resolved_state[light_name].update(value())
                else:
                    resolved_state[light_name][function] = value

        return data, resolved_state


class LightTypeFunction:
    def __init__(self, name, speed=None, invert=False, reset=None, mapping=None):
        self.name = name
        self.speed = speed
        self.invert = invert
        self.reset = reset
        self.mapping = mapping or {}

    def resolve_to_raw(self, value):
        # TODO: support mapping based on state
        if isinstance(value, str) and value in self.mapping:
            return self.mapping[value][0]
        return value

    def resolve_to_float(self, value):
        return self.resolve_to_raw(value)


class DMXLightTypeFunction(LightTypeFunction):
    def __init__(self, name, channel, speed=None, invert=False, reset=None, mapping=None, has_fine=False):
        super().__init__(name, speed=speed, invert=invert, reset=reset, mapping=mapping)
        self.channel = channel
        self.has_fine = has_fine

    def resolve_to_raw(self, value):
        # TODO: has_fine
        value = super().resolve_to_raw(value)
        return int(value * 255)

    def resolve_to_float(self, value):
        # TODO: has_fine
        value = super().resolve_to_float(value)
        return value / 255.0


class LightType:
    all_light_types = {}

    def __init__(self, protocol, name, functions):
        self.protocol = protocol
        self.name = name
        self.functions = {f.name: f for f in functions or []}

    @classmethod
    def add(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        cls.all_light_types[obj.name] = obj

    @classmethod
    def get(cls, key):
        return cls.all_light_types[key]


class DMXLightType(LightType):
    def __init__(self, name, channels, functions):
        super().__init__('dmx', name, functions)
        self.channels = channels


DMXLightType.add('UnnamedGobo', 11, [
    DMXLightTypeFunction('pan', 1, speed=(25, 1), has_fine='pan_fine'),
    DMXLightTypeFunction('pan_fine', 2),
    DMXLightTypeFunction('tilt', 3, speed=(10, 0.5), has_fine='tilt_fine'),
    DMXLightTypeFunction('tilt_fine', 4),
    DMXLightTypeFunction('color', 5, mapping={
        'white': [0, 9],
        'yellow': [10, 19],
        'orange': [20, 29],
        'cyan': [30, 39],
        'blue': [40, 49],
        'green': [50, 59],
        'pink': [60, 69],
        'red': [70, 79],
        'pink_red': [80, 89],
        'green_pink': [90, 99],
        'blue_green': [100, 109],
        'cyan_blue': [110, 119],
        'orange_cyan': [120, 129],
        'yellow_orange': [130, 139],
    }),
    DMXLightTypeFunction('gobo', 6, mapping={
        'none': [0, 7],
        'broken_circle': [8, 15],
        'burst': [16, 23],
        '3_spot_circle': [24, 31],
        'square_spots': [32, 39],
        'droplets': [40, 47],
        'swirl': [48, 55],
        'stripes': [56, 63],
        'dither_none': [64, 71],
        'dither_broken_circle': [72, 79],
        'dither_burst': [80, 87],
        'dither_3_spot_circle': [88, 95],
        'dither_square_spots': [96, 103],
        'dither_droplets': [104, 111],
        'dither_swirl': [112, 119],
        'dither_stripes': [120, 127],
    }),
    DMXLightTypeFunction('strobe', 7, invert=True),
    DMXLightTypeFunction('dim', 8),
    DMXLightTypeFunction('speed', 9, invert=True),
    DMXLightTypeFunction('mode', 10, mapping={
        'manual': [0, 59],
        'auto0': [135, 159],
        'auto1': [110, 134],
        'auto2': [85, 109],
        'auto3': [60, 84],
        'sound0': [235, 255],
        'sound1': [210, 234],
        'sound2': [185, 209],
        'sound3': [160, 184],
    }),
    DMXLightTypeFunction('reset', 11, reset=(1, 255)),
])

DMXLightType.add('UKingGobo', 11, [
    DMXLightTypeFunction('pan', 1, speed=(25, 1), has_fine='pan_fine'),
    DMXLightTypeFunction('pan_fine', 2),
    DMXLightTypeFunction('tilt', 3, speed=(10, 0.5), has_fine='tilt_fine'),
    DMXLightTypeFunction('tilt_fine', 4),
    DMXLightTypeFunction('color', 5, mapping={
        'white': [0, 9],
        'red': [10, 19],
        'green': [20, 29],
        'blue': [30, 39],
        'yellow': [40, 49],
        'orange': [50, 59],
        'cyan': [60, 69],
        'pink': [70, 79],
        'pink_cyan': [80, 89],
        'cyan_orange': [90, 99],
        'orange_yellow': [100, 109],
        'yellow_blue': [110, 119],
        'blue_green': [120, 127],
    }),
    DMXLightTypeFunction('gobo', 6, mapping={
        'none': [0, 7],
        'broken_circle': [8, 15],
        'burst': [16, 23],
        '3_spot_circle': [24, 31],
        'square_spots': [32, 39],
        'droplets': [40, 47],
        'swirl': [48, 55],
        'stripes': [56, 63],
        'dither_none': [64, 71],
        'dither_broken_circle': [72, 79],
        'dither_burst': [80, 87],
        'dither_3_spot_circle': [88, 95],
        'dither_square_spots': [96, 103],
        'dither_droplets': [104, 111],
        'dither_swirl': [112, 119],
        'dither_stripes': [120, 127],
    }),
    DMXLightTypeFunction('strobe', 7, invert=True),
    DMXLightTypeFunction('dim', 8),
    DMXLightTypeFunction('speed', 9, invert=True),
    DMXLightTypeFunction('mode', 10),
    DMXLightTypeFunction('dim_mode', 11, reset=(101, 255), mapping={
        'standard': [0, 20],
        'stage': [21, 40],
        'tv': [41, 60],
        'building': [61, 80],
        'theater': [81, 100],
        'reset': [101, 255],
    }),
])

DMXLightType.add('TomshineMovingHead6in1', 18, [
    DMXLightTypeFunction('pan', 1, speed=(25, 1), has_fine='pan_fine'),
    DMXLightTypeFunction('pan_fine', 2),
    DMXLightTypeFunction('tilt', 3, speed=(10, 0.5), has_fine='tilt_fine'),
    DMXLightTypeFunction('tilt_fine', 4),
    DMXLightTypeFunction('speed', 5, invert=True),
    DMXLightTypeFunction('dim', 6),
    DMXLightTypeFunction('strobe', 7),
    DMXLightTypeFunction('red', 8),
    DMXLightTypeFunction('green', 9),
    DMXLightTypeFunction('blue', 10),
    DMXLightTypeFunction('white', 11),
    DMXLightTypeFunction('amber', 12),
    DMXLightTypeFunction('uv', 13),
    DMXLightTypeFunction('mode', 14, mapping={
        'manual': [0, 15],
        'auto0': [105, 128],
        'auto1': [75, 104],
        'auto2': [45, 74],
        'auto3': [16, 44],
        'sound0': [218, 255],
        'sound1': [188, 217],
        'sound2': [158, 187],
        'sound3': [128, 157],
    }),
    DMXLightTypeFunction('motor_sens', 15),
    DMXLightTypeFunction('effect', 16, mapping={
        'manual': [0, 0],
        'gradual': [1, 7],
        'auto1': [8, 39],
        'auto2': [40, 74],
        'auto3': [75, 108],
        'auto4': [109, 140],
        'sound1': [141, 168],
        'sound2': [169, 197],
        'sound3': [198, 226],
        'sound4': [227, 255],
    }),
    DMXLightTypeFunction('led_sens', 17),
    DMXLightTypeFunction('reset', 18, reset=(1, 255)),
])

DMXLightType.add('Generic4ColorLaser', 7, [
    DMXLightTypeFunction('mode', 1, mapping={
        'off': [0, 49],
        'static': [50, 99],
        'dynamic': [100, 149],
        'sound': [150, 199],
        'auto': [200, 255],
    }),
    DMXLightTypeFunction('pattern', 2, mapping={
        # TODO: only when mode=static
        'circle': [0, 4],
        'dot_circle_1': [5, 9],
        'dot_circle_2': [10, 14],
        'scan_circle': [15, 19],
        'horiz_line': [20, 24],
        'horiz_dot_line': [25, 29],
        'vert_line': [30, 34],
        'vert_dot_line': [35, 39],
        '45deg_diag': [40, 44],
        '45deg_dot_diag': [45, 49],
        '135deg_diag': [50, 54],
        '135deg_dot_diag': [55, 59],
        'v_line_1': [60, 64],
        'v_dot_line_1': [65, 69],
        'v_line_2': [70, 74],
        'v_dot_line_2': [75, 79],
        'triangle_1': [80, 84],
        'dot_triangle_1': [85, 89],
        'triangle_2': [90, 94],
        'dot_triangle_2': [95, 99],
        'square': [100, 104],
        'dot_square': [105, 109],
        'rectangle_1': [110, 114],
        'dot_rectangle_1': [115, 119],
        'rectangle_2': [120, 124],
        'dot_rectangle_2': [125, 129],
        'criscross': [130, 134],
        'chiasma_line': [135, 139],
        'horiz_extend_line': [140, 144],
        'horiz_shrink_line': [145, 149],
        'horiz_flex_line': [150, 154],
        'horiz_flex_dot_line': [155, 159],
        'vert_extend_line': [160, 164],
        'vert_shrink_line': [165, 169],
        'vert_flex_line': [170, 174],
        'vert_flex_dot_line': [175, 179],
        'ladder_line_1': [180, 184],
        'ladder_line_2': [185, 189],
        'ladder_line_3': [190, 194],
        'ladder_line_4': [195, 199],
        'tetragon_1': [200, 204],
        'tetragon_2': [205, 209],
        'pentagon_1': [210, 214],
        'pentagon_2': [215, 219],
        'pentagon_3': [220, 224],
        'pentagon_4': [225, 229],
        'wave_line': [230, 234],
        'wave_dot_line': [235, 239],
        'spiral_line': [240, 244],
        'many_dot_1': [245, 249],
        'many_dot_2': [250, 254],
        'square_dot': [255, 255],
        # TODO: only when mode=dynamic
        # 'circle_to_big': [0, 4],
        # 'dot_circle_to_big': [5, 9],
        # 'scan_circle_to_big': [10, 14],
        # 'circle_flash': [15, 19],
        # 'dot_circle_flash': [20, 24],
        # 'circle_roll': [25, 29],
        # 'dot_circle_roll': [30, 34],
        # 'circle_turn': [35, 39],
        # 'dot_circle_turn': [40, 44],
        # 'dot_circle_to_add': [45, 49],
        # 'scan_circle_extend': [50, 54],
        # 'circle_jump': [55, 59],
        # 'dot_circle_jump': [60, 64],
        # 'horiz_line_jump': [65, 69],
        # 'horiz_dot_line_jump': [70, 74],
        # 'vert_line_jump': [75, 79],
        # 'vert_dot_line_jump': [80, 84],
        # 'diag_jump': [85, 89],
        # 'dot_diag_jump': [90, 94],
        # 'short_sector_round_1': [95, 99],
        # 'short_sector_round_2': [100, 104],
        # 'long_sector_round_1': [105, 109],
        # 'long_sector_round_2': [110, 114],
        # 'line_scan': [115, 119],
        # 'dot_line_scan': [120, 124],
        # '45deg_diag_move': [125, 129],
        # 'dot_diag_move': [130, 134],
        # 'horiz_line_flex': [135, 139],
        # 'horiz_dot_line_flex': [140, 144],
        # 'horiz_line_move': [145, 149],
        # 'horiz_dot_line_move': [150, 154],
        # 'vert_line_move': [155, 159],
        # 'vert_dot_line_move': [160, 164],
        # 'rect_extend': [165, 169],
        # 'dot_rect_extend': [170, 174],
        # 'square_extend': [175, 179],
        # 'dot_square_extend': [180, 184],
        # 'rect_turn': [185, 189],
        # 'dot_rect_turn': [190, 194],
        # 'square_turn': [195, 199],
        # 'dot_square_turn': [200, 204],
        # 'pentagon_turn': [205, 209],
        # 'dot_pentagon_turn': [210, 214],
        # 'tetragon_turn': [215, 219],
        # 'pentagon_star_turn': [220, 224],
        # 'bird_fly': [225, 229],
        # 'dot_bird_fly': [230, 234],
        # 'wave_flowing': [235, 239],
        # 'dot_wave_flowing': [240, 244],
        # 'many_dot_jump_1': [245, 249],
        # 'square_dot_jump': [250, 254],
        # 'many_dot_jump_2': [255, 255],
    }),
    DMXLightTypeFunction('x', 3),
    DMXLightTypeFunction('y', 4),
    DMXLightTypeFunction('scan_speed', 5, invert=True),
    DMXLightTypeFunction('pattern_speed', 6, invert=True),
    DMXLightTypeFunction('pattern_size', 7),
])

# TODO: that other light


class Light:
    all_lights = {}

    def __init__(self, name, type):
        self.name = name
        self.type = LightType.get(type) if isinstance(type, str) else type
        self.raw_state = {f: 0 for f in self.type.functions}
        # TODO: set raw state
        # TODO: convert
        self.converted_state = {f: 0 for f in self.type.functions}

    @classmethod
    def add(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        cls.all_lights[obj.name] = obj

    @classmethod
    def get(cls, key=None):
        if key:
            return cls.all_lights[key]
        return list(cls.all_lights.values())

    def get_raw_state(self, key=None, dfl=None):
        if key:
            return self.raw_state.get(key, dfl)
        return dict(self.raw_state)


class DMXLight(Light):
    def __init__(self, name, channel, type):
        super().__init__(name, type)
        self.channel = channel


DMXLight.add('back_1', 1, 'UnnamedGobo')
# DMXLight.add('back_2', 12, 'UnnamedGobo')
# DMXLight.add('mid_1', 23, 'UKingGobo')
# DMXLight.add('mid_2', 34, 'UKingGobo')
# DMXLight.add('mid_3', 45, 'UKingGobo')
# DMXLight.add('mid_4', 56, 'UKingGobo')
# DMXLight.add('front_1', 67, 'TomshineMovingHead6in1')
# DMXLight.add('front_2', 85, 'TomshineMovingHead6in1')
# DMXLight.add('laser', 103, 'Generic4ColorLaser')


class Layer:
    def __init__(self, replace, *callbacks):
        self.replace = bool(replace)
        self.callbacks = callbacks
        self.setup()

    def setup(self):
        pass

    def process(self, data, state):
        out = {}
        for c in self.callbacks:
            res = c(data, state)
            if res:
                out.update(res)
        return out

    def __call__(self, data, state):
        out = self.process(data, state)
        # TODO: transform for lights
        return out


# {
#     '/audio/beat/beattime': 0.0,
#     '/audio/beat/onbeat': 1.0,
#     '/audio/beat/randomonbeat': 1.0,
#     '/audio/bpm/bpm': 193.5784454345703,
#     '/audio/bpm/bpmconfidence': 0.10241653025150299,
#     '/audio/bpm/bpmsin': 0.10148508846759796,
#     '/audio/bpm/bpmsin2': 0.10218312591314316,
#     '/audio/bpm/bpmsin4': 5.838836659677327e-05,
#     '/audio/bpm/bpmtri': 0.00311369844712317,
#     '/audio/bpm/bpmtri2': 0.0015569041715934873,
#     '/audio/bpm/bpmtwitcher': 678.2443237304688,
#     '/audio/energy/intensity': 1.0,
#     '/audio/hits/all': 0.08847624808549881,
#     '/audio/hits/bass': 0.0,
#     '/audio/hits/mid': 0.0,
#     '/audio/hits/midhigh': 0.0,
#     '/audio/hits/high': 0.0,
#     '/audio/level/all': 0.721630334854126,
#     '/audio/level/bass': 0.9228341579437256,
#     '/audio/level/mid': 1.0,
#     '/audio/level/midhigh': 1.0,
#     '/audio/level/high': 1.0,
#     '/audio/level/raw': 0.35350826382637024
#     '/audio/presence/all': 0.06737750768661499,
#     '/audio/presence/bass': 3.526156797306612e-05,
#     '/audio/presence/mid': 0.0,
#     '/audio/presence/midhigh': 1.013699034047022e-06,
#     '/audio/presence/high': 1.7057253387520177e-08,
#     '/audio/time/all': 1952.8458251953125,
#     '/audio/time/curved': 498.9521484375,
#     '/audio/time/bass': 1375.769775390625,
#     '/audio/time/mid': 1955.64111328125,
#     '/audio/time/midhigh': 2104.434326171875,
#     '/audio/time/high': 2104.861572265625,
# }


class DataLayer(Layer):
    def setup(self):
        self.dead_since = None
        self.idle_since = None

        self.last_beat_clock = None
        self.beat_counter = 0
        self.measure = 0
        self.phrase = 0

    def process(self, data, state):
        self._timers(data)
        self._beats(data)

    def _timers(self, data):
        now = time.time()
        audio = data.get('/audio/level/all', 0)

        if audio < 0.05:
            self.dead_since = self.dead_since or time.time()
        else:
            self.dead_since = None

        if audio < 0.2:
            self.idle_since = self.idle_since or time.time()
        else:
            self.idle_since = None

        data.update({
            'dead_for': time.time() - self.dead_since if self.dead_since is not None else 0,
            'idle_for': time.time() - self.idle_since if self.idle_since is not None else 0,
        })

    def _beats(self, data):
        data['exact_beat'] = False
        if data.get('/audio/bpm/bpmconfidence', 0) < MIN_BPM_CONF:
            self.last_beat_clock = None
            self.beat_counter = 0
            self.measure = 0
            self.phrase = 0
        elif data.get('/audio/beat/beattime', 0) != self.last_beat_clock:
            data['exact_beat'] = True
            self.last_beat_clock = data['/audio/beat/beattime']
            self.beat_counter += 1
            if self.beat_counter % 4 == 0:
                self.measure += 1
            if self.beat_counter % 16 == 0:
                self.phrase += 1

        data.update({
            'measure_beat': (((self.beat_counter - 1) % 4) + 1) if self.beat_counter else 0,
            'measure': self.measure,
            'phrase': self.phrase,
        })


class IdleFadeout(Layer):
    def process(self, data, state):
        idle = data.get('idle_for', 0)
        if idle >= 0.75:
            return {'dim': 0}
        elif idle >= 0.25:
            return {'dim': Transition(None, 'dim', None, 0, 0.5)}


class BaseCoastLayer(Layer):
    def __init__(self, property, timeout, fade_transition, dim, speed, intervals, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.property = property
        self.timeout = timeout
        self.fade_transition = fade_transition
        self.dim = dim
        self.speed = speed
        self.intervals = intervals or {}

    def process(self, data, state):
        duration = data.get(self.property + '_for', 0)
        if duration < self.timeout:
            return
        elif duration < self.timeout + self.fade_transition:
            return {'dim': Transition(None, 'dim', None, self.dim, self.fade_transition)}
        else:
            out = {'dim': self.dim, 'speed': self.speed}
            now = time.time()
            for k in self.intervals:
                for l in Light.get():
                    out[l.name + '.' + k] = Transition(None, k, None, random.random(), self.intervals[k])
            return out


class IdleCoast(BaseCoastLayer):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'idle',
            2,
            0.25,
            0.4,
            0.7,
            {
                'pan': 7,
                'tilt': 7,
                'color': 5,
                'gobo': 4,
            },
            *args, **kwargs
        )


class DeadCoast(BaseCoastLayer):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'dead',
            10,
            0.25,
            0.7,
            0.4,
            {
                'pan': 11,
                'tilt': 11,
                'color': 9,
                'gobo': 6,
            },
            *args, **kwargs
        )


class AudioDim(Layer):
    def process(self, data, state):
        if data.get('idle_for', 0):
            return
        return {'dim': 1, 'speed': 1}


class Movement(Layer):
    def _circle(self, data, position, radius, oval_pan=False, oval_tilt=False):
        if oval_pan:
            pan_prop = lambda: data.get('/audio/bpm/bpmsin4', 0)
            tilt_prop = lambda: data.get('/audio/bpm/bpmtri2', 0)
        elif oval_tilt:
            pan_prop = lambda: data.get('/audio/bpm/bpmtri2', 0)
            tilt_prop = lambda: data.get('/audio/bpm/bpmsin4', 0)
        else:
            pan_prop = lambda: data.get('/audio/bpm/bpmtri2', 0)
            tilt_prop = lambda: data.get('/audio/bpm/bpmsin2', 0)

        x, y = map(lambda v: v - radius, position)
        diameter = radius * 2
        pan_deg = x + (diameter * pan_prop())
        tilt_deg = y + (diameter * tilt_prop())

        # TODO: get from light
        return {'pan': pan_deg / 540, 'tilt': tilt_deg / 180}

    def _square(self, data, position, size):
        if data['measure_beat'] == 0:
            return False

        x1, y1 = map(lambda v: v - (size / 2), position)
        x2, y2 = map(lambda v: v + size, (x1, y1))
        positions = (
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y2),
        )

        # TODO: get from light
        pan_deg, tilt_deg = positions[data['measure_beat'] - 1]
        return {'pan': pan_deg / 540, 'tilt': tilt_deg / 180}

    def process(self, data, state):
        # TODO: use MIN_BPM_CONF to determine whether to run movements requiring sane beat detection
        # return self._circle(data, (90, 120), 15)
        res = self._square(data, (90, 120), 15)
        if res:
            return res


def _sighandler(signo, frame):
    stop_event.set()

signal.signal(signal.SIGINT, _sighandler)
signal.signal(signal.SIGTERM, _sighandler)


layers = [
    DataLayer(False),
    IdleFadeout(True),
    IdleCoast(True),
    DeadCoast(True),
    AudioDim(True),
    Movement(False),
]


threads = []

osc = OSCThread()
threads.append(osc)

process = ProcessThread(osc, layers)
threads.append(process)

for t in threads:
    t.start()

while not stop_event.is_set():
    data, state = process.get_data()
    print(state)

for t in threads:
    t.join()