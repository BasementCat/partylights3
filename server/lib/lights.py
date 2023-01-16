from threading import RLock

from . import Named, Collected, Grouped


class LightTypeFunction(Named):
    def __init__(self, *args, invert=False, reset=None, mapping=None, meta=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.invert = invert
        self.reset = reset
        self.mapping = mapping or {}
        self.meta = dict(meta or {})

    def get_mapping(self, light):
        if isinstance(self.mapping, list):
            mapped_state = light.get_mapped_state()
            for (cond_key, cond_value), mapping in self.mapping:
                if mapped_state.get(cond_key) == cond_value:
                    return mapping
            return {}
        return self.mapping

    def _get_mapping_idx(self, light, value):
        mappings = list(self.get_mapping(light).keys())
        if value in mappings:
            return mappings, mappings.index(value)
        return mappings, None

    def next_mapping_from(self, light, value, wrap=True):
        mappings, idx = self._get_mapping_idx(light, value)
        if idx is not None:
            if idx + 1 >= len(mappings):
                if wrap:
                    return mappings[0]
                return None
            return mappings[idx + 1]
        return None

    def prev_mapping_from(self, light, value, wrap=True):
        mappings, idx = self._get_mapping_idx(light, value)
        if idx is not None:
            if idx < 1:
                if wrap:
                    return mappings[-1]
                return None
            return mappings[idx - 1]
        return None

    def convert_to_raw(self, light, value):
        # Accepts a float/string for mapping
        if isinstance(value, str):
            mapping = self.get_mapping(light)
            if value in mapping:
                out = mapping[value][0]
            else:
                # TODO: log or something? could be noisy
                out = 0
        else:
            out = value
        return out

    def convert_to_mapped(self, light, value):
        # Convert a raw value to a mapping if present, otherwise return raw value
        # mapping is by output value - convert first
        outvalue = self.convert_to_output(light, value)
        mapping = self.get_mapping(light)
        for key, (low, high) in mapping.items():
            if outvalue >= low and outvalue <= high:
                return key
        return value

    def convert_to_output(self, light, value):
        # Convert a raw value to the output value
        if self.invert:
            return 1 - value
        return value


class DMXLightTypeFunction(LightTypeFunction):
    def __init__(self, name, channel, *args, map_highres=None, map_multi=None, range_deg=None, meta=None, **kwargs):
        meta = dict(meta or {})
        if range_deg is not None:
            meta['range_deg'] = range_deg
        super().__init__(name, *args, meta=meta, **kwargs)
        self.channel = channel
        self.map_highres = map_highres
        self.map_multi = map_multi

    def convert_to_output(self, light, value):
        if self.map_highres:
            value = super().convert_to_output(light, value)
            intval = int(((1 << (8 * len(self.map_highres))) - 1) * value)
            out = {}
            # TODO: this should probably get run through the other functions...
            for key in reversed(self.map_highres):
                out[key] = intval & 0xff
                intval = intval >> 8
            return out
        elif self.map_multi:
            value = [super().convert_to_output(light, v) for v in value]
            out = {}
            for i, key in enumerate(self.map_multi):
                fn = light.type.functions.get(key, lambda l, v: int(v * 255))
                out[key] = fn.convert_to_output(value[i])
            return out
        else:
            value = super().convert_to_output(light, value)
            return int(value * 255)


class LightType(Named, Collected()):
    PROTOCOL = None

    def __init__(self, name, functions, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.functions = {f.name: f for f in functions or []}


class DMXLightType(LightType):
    PROTOCOL = 'dmx'

    def __init__(self, name, channels, functions, *args, **kwargs):
        super().__init__(name, functions, *args, **kwargs)
        self.channels = channels


class Light(Named, Grouped, Collected()):
    def __init__(self, name, type, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.name = name
        self.type = LightType.get(type) if isinstance(type, str) else type
        self.state_lock = RLock()
        self.raw_state = {f: 0 for f in self.type.functions}
        self.mapped_state = {f: 0 for f in self.type.functions}
        self.output_state = {f: 0 for f in self.type.functions}

    def update_state(self, new_state):
        with self.state_lock:
            for k, v in new_state.items():
                if k in self.raw_state:
                    self.raw_state[k] = self.type.functions[k].convert_to_raw(self, v)

            for k, v in self.raw_state.items():
                self.mapped_state[k] = self.type.functions[k].convert_to_mapped(self, v)

            for k, v in self.raw_state.items():
                self.output_state[k] = self.type.functions[k].convert_to_output(self, v)

    def get_raw_state(self, key=None, dfl=None):
        with self.state_lock:
            if key:
                return self.raw_state.get(key, dfl)
            return dict(self.raw_state)

    def get_mapped_state(self):
        with self.state_lock:
            return dict(self.mapped_state)

    def get_output_state(self):
        with self.state_lock:
            return dict(self.output_state)


class DMXLight(Light):
    def __init__(self, name, channel, type, *args, **kwargs):
        super().__init__(name, type, *args, **kwargs)
        self.channel = channel

    def get_dmx_state(self, speed_only=False):
        state = self.get_output_state()
        out = {}
        for k, v in state.items():
            if not speed_only or k == 'speed':
                out[self.channel + (self.type.functions[k].channel - 1)] = v
        return out
