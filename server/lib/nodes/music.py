import time

from . import Node, NodeIO


# TODO: this almost definitely won't line up with the music
# class Measures(Node):
#     NAME = 'MeasureCount'
#     DESCRIPTION = "Produce clocks corresponding to measures and phrases"
#     INPUTS = [
#         NodeIO('reset', bool, description="Reset all clocks to 0"),
#         NodeIO('beat', float, description="Beat clock"),
#         NodeIO('beat_confidence', float, default=1, description="Beat detection confidence"),
#         NodeIO('beat_confidence_threshold', float, description="If beat detection confidence is below this value, reset & don't emit clocks"),
#         NodeIO('beats_per_measure', int, default=4, description="Beats per measure"),
#         NodeIO('measures_per_phrase', int, default=16, description="Measures per phrase"),
#     ]
#     OUTPUTS = [
#         NodeIO('measure', int, description="Measure clock"),
#         NodeIO('phrase', int, description="Phrase clock"),
#     ]

#     def setup(self):
#         self.beat_count = 0
#         self.measure_count = 0

#     def process(self, from_node, output_name, input_name, value, input_cache, output_cache):
#         if input_name == 'reset' or (input_name == 'beat_confidence' and value < input_cache['beat_confidence_threshold']):
#             return {'measure': 0, 'phrase': 0}, Fales
#         elif input_name == 'beat':
#             if input_cache['beat_confidence'] >= input_cache['beat_confidence_threshold'] and value != input_cache['beat']:
#                 out = dict(output_cache)
#                 self.beat_count += 1
#                 if self.beat_count == input_cache['beats_per_measure']:
#                     out['measure'] += 1
#                     self.measure_count += 1
#                     self.beat_count = 0
#                 if out['measure'] == input_cache['measures_per_phrase']:
#                     out['phrase'] += 1
#                     self.measure_count = 0
#                 if out != output_cache:
#                     return out, True

#         return {}, False


class Drop(Node):
    NAME = 'DropDetect'
    DESCRIPTION = "Detect a drop in the music"
    INPUTS = [
        NodeIO('audio', bool, description="Whether audio is present (use a threshold node to consider a range of audio values)"),
        NodeIO('bpm', float, description="Current BPM"),
        NodeIO('min_silent_beats', int, default=1, description="Only consider a drop if the length of the silence is at least this many beats"),
        NodeIO('max_silent_beats', int, default=4, description="Only consider a drop if the length of the silence is less than this many beats"),
        NodeIO('drop_len', int, default=1, description="Drop length in beats"),
    ]
    OUTPUTS = [
        NodeIO('drop', float, description="Output 1 on a drop, and fall off to 0"),
    ]

    def setup(self):
        self._reset()
        self.min_time = self.max_time = self.drop_time = 0

    def _reset(self):
        self.drop_start = self.drop_end = self.last_audio = 0

    def _calc_times(self, inputs, bpm):
        beat_time = 60.0 / bpm
        self.min_time = beat_time * inputs['min_silent_beats']
        self.max_time = beat_time * inputs['max_silent_beats']
        self.drop_time = beat_time * inputs['drop_len']

    def process(self, from_node, output_name, input_name, value, input_cache, output_cache):
        if input_name == 'bpm':
            self._calc_times(input_cache, value)

        if self.drop_end:
            if time.time() >= self.drop_end:
                self._reset()
            else:
                return {'drop': (time.time() - self.drop_start) / (self.drop_end - self.drop_start)}, True

        if input_name == 'audio':
            if value:
                if self.drop_time and self.last_audio:
                    # Only check if we've gotten a BPM update, and have a last audio time
                    silence = time.time() - self.last_audio
                    if silence >= self.min_time and silence <= self.max_time:
                        self.drop_start = time.time()
                        self.drop_end = self.drop_start + self.drop_time
                        return {'drop': 1}, True
                self._reset()
            else:
                self.last_audio = self.last_audio or time.time()


        return {'drop': 0}, True
