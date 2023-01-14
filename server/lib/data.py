import time
import colorsys
import math
import random

import easing_functions

from . import Named, ListOf


def get_bpm_duration(data, beats):
    conf = data.get('audio/bpm/bpmconfidence')
    bpm = data.get('audio/bpm/bpm')
    if conf and bpm:
        conf = conf[0]
        bpm = bpm[0]
        # TODO: use constant for OK bpm confidence
        if beats and conf >= 0.8:
            return (60.0 / bpm) * beats
    return None


def HasTriggers(*names):
    class HasTriggersImpl:
        def __init__(self, *args, **kwargs):
            self.triggers = {n: kwargs.pop('trigger_' + n, None) or [] for n in names}
            super().__init__(*args, **kwargs)

        def run_triggers(self, data):
            for name, triggers in self.triggers.items():
                if Trigger.run_trigger_group(data, triggers):
                    yield name

    return HasTriggersImpl


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

        bpm_duration = get_bpm_duration(data, self.duration_beat)
        if bpm_duration:
            kwargs['duration'] = bpm_duration

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


class PanTiltSpreadMixin:
    def _apply_spread(self, index, light, data, kwargs):
        kwargs = super()._apply_spread(index, light, data, kwargs)
        has_pan = bool(light.type.functions.get('pan') and light.type.functions.get('pan').meta.get('range_deg'))
        has_tilt = bool(light.type.functions.get('tilt') and light.type.functions.get('tilt').meta.get('range_deg'))
        if has_pan:
            kwargs['pan'] = kwargs['pan'] % light.type.functions.get('pan').meta.get('range_deg')
        if has_tilt:
            kwargs['tilt'] = kwargs['tilt'] % light.type.functions.get('tilt').meta.get('range_deg')
        # TODO: for circle, ideally would limit radius to avoid extending outside of the range
        # TODO: for points, could more easily limit points to range
        return kwargs


class CircleMovementTransition(PanTiltSpreadMixin, MovementTransition):
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


class PointsMovementTransition(MovementTransition):
    def __init__(self, *args, start=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.points = self._calc_points()
        self.start = int(max(0, min(len(self.points), start)))

    def _calc_points(self):
        raise NotImplementedError("return a list of tuples of points, in degrees")

    def _prep_to_copy(self, index, light, data):
        kwargs = super()._prep_to_copy(index, light, data)

        kwargs.update({
            'start': self.start,
        })

        return kwargs

    def _copy(self, *args, **kwargs):
        return PointsMovementTransition(*args, **kwargs)

    def __call__(self, data):
        if not (self.light.type.functions.get('pan') and self.light.type.functions.get('pan').meta.get('range_deg') and self.light.type.functions.get('tilt') and self.light.type.functions.get('tilt').meta.get('range_deg')):
            return
        percent = min(1, self._calc_percent(data))
        res = self._calc_short_circuit(data, percent)
        if res is None:
            return None
        # In any other case we have to actually do the calculation

        offset = min(len(self.points) - 1, int(percent * len(self.points)))
        percent = min(1, (percent * len(self.points)) - offset)
        point_i = (self.start + offset) % len(self.points)

        x1, y1 = self.points[point_i]
        x2, y2 = self.points[(point_i + 1) % len(self.points)]

        mul, _ =self._calc_easing(data, percent)

        pan_deg = ((x2 - x1) * mul) + x1
        tilt_deg = ((y2 - y1) * mul) + y1

        return {
            'pan': pan_deg / self.light.type.functions['pan'].meta['range_deg'],
            'tilt': tilt_deg / self.light.type.functions['tilt'].meta['range_deg'],
        }


class SquareMovementTransition(PanTiltSpreadMixin, PointsMovementTransition):
    def __init__(self, pan, tilt, width, *args, height=None, swap_mid=False, **kwargs):
        self.pan = pan
        self.tilt = tilt
        self.width = width
        self.height = height or width
        self.swap_mid = swap_mid
        super().__init__(*args, **kwargs)

    def _calc_points(self):
        half_x = self.width / 2
        half_y = self.height / 2
        points = [
            (self.pan - half_x, self.tilt - half_y),
            (self.pan + half_x, self.tilt - half_y),
            (self.pan - half_x, self.tilt + half_y),
            (self.pan + half_x, self.tilt + half_y),
        ]
        if self.swap_mid:
            points.append(points.pop[2])
        return points

    def _prep_to_copy(self, index, light, data):
        kwargs = super()._prep_to_copy(index, light, data)

        kwargs.update({
            'pan': self.pan,
            'tilt': self.tilt,
            'width': self.width,
            'height': self.height,
            'swap_mid': self.swap_mid,
        })

        return kwargs

    def _copy(self, *args, **kwargs):
        return SquareMovementTransition(*args, **kwargs)


class SweepMovementTransition(PointsMovementTransition):
    def __init__(self, x1, y1, x2, y2, *args, **kwargs):
        if x2 is None and y2 is None:
            raise ValueError("must provide x2 or y2")
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2 or x1
        self.y2 = y2 or y1
        super().__init__(*args, **kwargs)

    def _calc_points(self):
        points = [
            (self.x1, self.y1),
            (self.x2, self.y2),
        ]
        return points

    def _prep_to_copy(self, index, light, data):
        kwargs = super()._prep_to_copy(index, light, data)

        kwargs.update({
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
        })

        return kwargs

    def _copy(self, *args, **kwargs):
        return SweepMovementTransition(*args, **kwargs)


class Effect(Named, HasTriggers('select', 'run'), ListOf(Transition)):
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


class Program(Named, HasTriggers('run', 'stop', 'select', 'next', 'prev', 'random'), ListOf(Effect)):
    def __init__(self, *args, multiple=False, start=True, autoplay=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.multiple = multiple
        if self.multiple:
            self.pending_effects = {}
            self.running_effects = {}
        else:
            self.current_effect_idx = 0 if len(self) else None
            self.running_effect = None
            self.is_running = start
            self.autoplay = autoplay
            self.play_next = False

    def _run_triggers__single(self, data):
        selected = None
        for idx, effect in enumerate(self):
            for name in effect.run_triggers(data):
                if selected is None and name == 'select':
                    selected = idx

        if selected is not None:
            self.running_effect = None
            self.current_effect_idx = selected

        for name in super().run_triggers(data):
            if name == 'run':
                self.is_running = True
            elif name == 'stop':
                self.is_running = False
            elif name == 'select':
                yield name
            elif name == 'next':
                self.running_effect = None
                self.current_effect_idx = (self.current_effect_idx + 1) % len(self)
                self.play_next = True
            elif name == 'prev':
                self.running_effect = None
                self.current_effect_idx = (self.current_effect_idx - 1) % len(self)
                self.play_next = True
            elif name == 'random':
                self.running_effect = None
                self.current_effect_idx = random.randint(0, len(self) - 1)
                self.play_next = True

    def _run_triggers__multi(self, data):
        for idx, effect in enumerate(self):
            for name in effect.run_triggers(data):
                if name == 'run':
                    if idx not in self.pending_effects and idx not in self.running_effects:
                        self.pending_effects[idx] = effect

        for name in super().run_triggers(data):
            # next/prev do not apply here
            if name == 'run':
                self.is_running = True
            elif name == 'stop':
                self.is_running = False
            elif name == 'select':
                yield name
            elif name == 'random':
                choices = set(range(len(self))) - set(list(self.pending_effects.keys()) + list(self.running_effects.keys()))
                if choices:
                    idx = random.choice(choices)
                    self.pending_effects[idx] = self[idx]


    def run_triggers(self, data):
        if self.multiple:
            yield from self._run_triggers__multi(data)
        else:
            yield from self._run_triggers__single(data)

    def _call__single(self, data, lights):
        if not len(self):
            self.current_effect_idx = self.running_effect = None
            return {}

        if not self.is_running:
            return {}

        if self.current_effect_idx is None:
            self.current_effect_idx = 0

        if self.running_effect is not None and not self.running_effect.is_running:
            self.running_effect = None
            if self.autoplay:
                self.current_effect_idx = (self.current_effect_idx + 1) % len(self)

        if self.running_effect is None:
            if self.autoplay or self.play_next:
                self.play_next = False
                self.running_effect = self[self.current_effect_idx].for_lights(data, lights)
            else:
                return {}

        return self.running_effect(data)

    def _call__multi(self, data, lights):
        for k, v in list(self.running_effects.items()):
            if not v.is_running:
                del self.running_effects[k]

        if not (self.is_running and (self.pending_effects or self.running_effects)):
            return {}

        for k, v in self.pending_effects.items():
            self.running_effects[k] = v.for_lights(data, lights)
        self.pending_effects = {}

        out = {}
        for effect in self.running_effects.values():
            for light, values in effect(data).items():
                out.setdefault(light, {}).update(values)

        return out

    def __call__(self, data, lights):
        if self.multiple:
            return self._call__multi(data, lights)
        else:
            return self._call__single(data, lights)


class Scene(Named, HasTriggers('select'), ListOf(Program)):
    def run_triggers(self, data):
        selected = None
        for idx, prog in enumerate(self):
            for name in prog.run_triggers(data):
                if selected is None and name == 'select':
                    selected = idx

        if selected is not None:
            for idx, prog in enumerate(self):
                if prog.autoplay:
                    prog.is_running = idx == selected

        # can only do select - pass up to controller
        yield from super().run_triggers(data)

    def __call__(self, data, lights):
        out = {}
        for program in self:
            for light_name, props in program(data, lights).items():
                out.setdefault(light_name, {}).update(props)
        return out


class SceneController(HasTriggers('next', 'prev', 'random'), ListOf(Scene)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_scene_idx = 0 if len(self) else None

    def run_triggers(self, data):
        selected = None
        for idx, scene in enumerate(self):
            for name in scene.run_triggers(data):
                if selected is None and name == 'select':
                    selected = idx

        if selected is not None:
            self.current_scene_idx = selected

        for name in super().run_triggers(data):
            if name == 'next':
                self.current_scene_idx = (self.current_scene_idx + 1) % len(self)
            elif name == 'prev':
                self.current_scene_idx = (self.current_scene_idx - 1) % len(self)
            elif name == 'random':
                self.current_scene_idx = random.randint(0, len(self) - 1)

    def __call__(self, data, lights):
        if not len(self):
            self.current_scene_idx = None
            return {}

        if self.current_scene_idx is None:
            self.current_scene_idx = 0

        return self[self.current_scene_idx](data, lights)


class Trigger:
    def __init__(self, event, threshold, value='new', below_threshold=False, cooldown=None, cooldown_beat=None):
        self.event = event
        self.threshold = threshold
        self.value = value
        self.below_threshold = below_threshold
        self.cooldown = cooldown
        self.cooldown_beat = cooldown_beat
        self.next_trigger = None

    def __call__(self, data):
        if self.next_trigger is not None and time.time() < self.next_trigger:
            return None

        res = data.get(self.event)
        if not res:
            return None

        new_v, old_v, diff, diff_p = res

        v = new_v
        if self.value == 'old':
            v = old_v
        elif self.value == 'diff':
            v = diff
        elif self.value == 'percent':
            v = diff_p

        if self.below_threshold:
            out = v < self.threshold
        else:
            out = v >= self.threshold

        if out and self.cooldown:
            cooldown = get_bpm_duration(data, self.cooldown_beat) or self.cooldown
            self.next_trigger = time.time() + cooldown

        return out

    @classmethod
    def run_trigger_group(cls, data, triggers):
        for trigger in triggers:
            try:
                iter(trigger)
            except:
                # Outer list is an OR condition
                if trigger(data):
                    return True
            else:
                # inner lists are an AND condition
                if all((t(data) for t in trigger)):
                    return True

        return False


class Mood:
    pass
