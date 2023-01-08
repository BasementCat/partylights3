import time
import colorsys
import math

import easing_functions

from . import Named, ListOf


class Transition:
    def __init__(self, property, duration, delay=None, start_value=None, end_value=None, duration_beat=None, easing='LinearInOut', spread=None, light=None):
        self.property = property
        self.duration = duration

        if start_value == end_value:
            raise ValueError("start_value and end_value must differ")

        self.delay = delay or 0
        self.start_value = start_value
        self.end_value = end_value
        self.duration_beat = duration_beat
        self.easing = easing
        self.spread = spread or {}
        self.light = light

        if self.light:
            self.started_at = time.time()
            self.easing_function = getattr(easing_functions, self.easing, easing_functions.LinearInOut)(start=0.0, end=1.0, duration=1.0)

    def _prep_to_copy(self, index, light, data):
        if self.light:
            raise RuntimeError("Can't copy to a light, already assigned")

        kwargs = {
            'property': self.property,
            'duration': self.duration,
            'delay': self.delay,
            'easing': self.easing,
            'light': light,
        }

        def _resolve_start_end(value):
            if value == 'CURRENT' or value is None:
                return light.get_raw_state(property, 0)
            elif value == 'DEFAULT' or value is True:
                # TODO: resolve to default
                return 0
            # TODO: cycle (difficult - requires state somehow)
            # TODO: next/prev (may require start=next/prev & end=same, to immediately transition)
            return value
        kwargs['start_value'] = _resolve_start_end(self.start_value)
        kwargs['end_value'] = _resolve_start_end(self.end_value)
        
        if self.duration_beat and data.get('audio/bpm/bpmconfidence', 0) >= 0.8 and data.get('audio/bpm/bpm'):
            # TODO: use constant for OK bpm confidence
            kwargs['duration'] = (60.0 / data['audio/bpm/bpm']) * self.duration_beat

        return kwargs

    def _apply_spread(self, index, light, data, kwargs):
        for k, m in self.spread.items():
            v = kwargs.get(k, 0)
            v = v + (index * m)
            if k in ('start_value', 'end_value'):
                while v < 0:
                    v += 1
                while v > 1:
                    v -= 1
            kwargs[k] = v
        return kwargs

    def _copy(self, *args, **kwargs):
        return Transition(*args, **kwargs)

    def for_light(self, index, light, data):
        kwargs = self._prep_to_copy(index, light, data)
        kwargs = self._apply_spread(index, light, data, kwargs)
        return self._copy(**kwargs)

    @property
    def is_running(self):
        return hasattr(self, 'started_at') and time.time() - self.started_at <= self.delay + self.duration

    def _calc_percent(self, data):
        return (time.time() - (self.started_at + self.delay)) / self.duration

    def _calc_short_circuit(self, data, percent):
        if percent <= 0:
            return
        # Short circuit - if we've reached the end of the duration, just return the end value
        if percent >= 1:
            return self.end_value
        return True

    def _calc_easing(self, data, percent):
        mul = self.easing_function(percent)
        # TODO: scaling - where does this go & how does it work?
        conv = lambda s, e: s + ((e - s) * mul)
        return mul, conv

    def __call__(self, data):
        percent = self._calc_percent(data)
        res = self._calc_short_circuit(data, percent)
        if res is not True:
            return res

        _, conv = self._calc_easing(data, percent)

        try:
            iter(self.start_value)
            # assume rgb color
            s_hls = colorsys.rgb_to_hls(*self.start_value)
            e_hls = colorsys.rgb_to_hls(*self.end_value)
            o_hls = (conv(s_hls[i], e_hls[i]) for i in range(3))
            return colorsys.hls_to_rgb(*o_hls)
        except:
            pass

        return conv(self.start_value, self.end_value)


class MovementTransition(Transition):
    def __init__(self, duration, delay=None, duration_beat=None, easing='LinearInOut', spread=None, light=None):
        # Pass some default values to satisfy the parent constructor, they won't really be used
        super().__init__('pan', duration, delay=delay, start_value=0, end_value=1, duration_beat=duration_beat, easing=easing, spread=spread, light=light)

    def _prep_to_copy(self, index, light, data):
        kwargs = super()._prep_to_copy(index, light, data)
        for k in ('property', 'start_value', 'end_value'):
            kwargs.pop(k, None)
        return kwargs

    def _copy(self, *args, **kwargs):
        raise NotImplementedError()

    def __call__(self, data):
        # The implementation depends heavily on the type of movement, this exists only to prevent the parent method from being invoked
        raise NotImplementedError()


class CircleMovementTransition(MovementTransition):
    def __init__(self, pan, tilt, radius, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pan = pan
        self.tilt = tilt
        self.radius = radius

    def _prep_to_copy(self, index, light, data):
        kwargs = super()._prep_to_copy(index, light, data)

        kwargs.update({
            'pan': self.pan,
            'tilt': self.tilt,
            'radius': self.radius,
        })

        return kwargs

    def _apply_spread(self, index, light, data, kwargs):
        has_pan = bool(self.light.type.functions.get('pan') and self.light.type.functions.get('pan').meta.get('range_deg'))
        has_tilt = bool(self.light.type.functions.get('tilt') and self.light.type.functions.get('tilt').meta.get('range_deg'))
        if has_pan:
            kwargs['pan'] = kwargs['pan'] % self.light.type.functions.get('pan').meta.get('range_deg')
        if has_tilt:
            kwargs['tilt'] = kwargs['tilt'] % self.light.type.functions.get('tilt').meta.get('range_deg')
        # TODO: ideally would limit radius so it doesn't extend outside of the range given set pan/tilt
        # if has_pan and has_tilt:
        #     kwargs['radius'] = kwargs['radius']
        return kwargs

    def _copy(self, *args, **kwargs):
        return CircleMovementTransition(*args, **kwargs)

    def __call__(self, data):
        if not (self.light.type.functions.get('pan') and self.light.type.functions.get('pan').meta.get('range_deg') and self.light.type.functions.get('tilt') and self.light.type.functions.get('tilt').meta.get('range_deg')):
            return
        percent = min(1, self._calc_percent(data))
        res = self._calc_short_circuit(data, percent)
        if res is None:
            return None
        # In any other case we have to actually do the calculation

        mul, _ =self._calc_easing(data, percent)
        rot = math.radians(mul * 360)

        x = math.sin(rot)
        y = math.cos(rot)

        # x and y are "coordinates" in the range of -1 to 1
        # multiply by radius to determine the difference to be applied to the starting position, producing pan/tilt values in degrees
        # divide by range to determine raw pan/tilt values

        pan_deg = self.pan + (x * self.radius)
        tilt_deg = self.tilt + (y * self.radius)

        return {
            'pan': pan_deg / self.light.type.functions['pan'].meta['range_deg'],
            'tilt': tilt_deg / self.light.type.functions['tilt'].meta['range_deg'],
        }


class Effect(Named, ListOf(Transition)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lights = None

    def for_lights(self, data, lights):
        # TODO: may be isolated to specific lights - whether that's externally determined, or figured out here
        transitions = []
        for t in self:
            for i, l in enumerate(lights):
                transitions.append(t.for_light(i, l, data))
        out = Effect(self.name, *transitions)
        out.lights = lights
        return out

    @property
    def is_running(self):
        return any((t.is_running for t in self))

    def __call__(self, data):
        out = {}
        for t in self:
            val = t(data)
            if val is not None:
                if isinstance(val, dict):
                    out.setdefault(t.light.name, {}).update(val)
                else:
                    out.setdefault(t.light.name, {})[t.property] = val
        return out


class Program(Named, ListOf(Effect)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_effect_idx = 0 if len(self) else None
        self.running_effect = None

    def __call__(self, data, lights):
        if not len(self):
            self.current_effect_idx = self.running_effect = None
            return {}

        if self.current_effect_idx is None:
            self.current_effect_idx = 0

        if self.running_effect is not None and not self.running_effect.is_running:
            self.running_effect = None
            self.current_effect_idx = (self.current_effect_idx + 1) % len(self)

        if self.running_effect is None:
            self.running_effect = self[self.current_effect_idx].for_lights(data, lights)

        return self.running_effect(data)


class Scene(Named, ListOf(Program)):
    def __call__(self, data, lights):
        out = {}
        for program in self:
            for light_name, props in program(data, lights).items():
                out.setdefault(light_name, {}).update(props)
        return out


# class SceneGroup(Named, ListOf(Scene)):
#     pass


class Trigger:
    pass


class Mood:
    pass
