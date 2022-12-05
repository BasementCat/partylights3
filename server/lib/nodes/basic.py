from . import Node, NodeIO


class Print(Node):
    NAME = 'Print'
    DESCRIPTION = "Prints the data sent to its input"
    INPUTS = [NodeIO('data', str)]

    def process(self, from_node, output_name, input_name, value, input_cache, output_cache):
        print(f"From {from_node.name}: {output_name}: '{value}'")
        return {}, False


class Threshold(Node):
    NAME = 'Threshold'
    DESCRIPTION = "Determine whether a value is above/below/within thresholds"
    INPUTS = [
        NodeIO('value', float, description="Raw value to consider"),
        NodeIO('low', float, description="Low end of threshold range"),
        NodeIO('high', float, description="High end of threshold range"),
        NodeIO('invert', bool, description="If true, invert the output"),
    ]
    OUTPUTS = [
        NodeIO('value', int, description="1 if value is >= high threshold, -1 if value is <= low threshold, 0 otherwise"),
        NodeIO('valueb', bool, description="True if value is outside of thresholds, False otherwise"),
    ]

    def process(self, from_node, output_name, input_name, value, input_cache, output_cache):
        if input_name != 'value':
            return {}, False

        out = 0
        if value >= input_cache['high']:
            out = 1
        elif value <= input_cache['low']:
            out = -1

        if input_cache['invert']:
            out = -1 if out == 1 else (1 if out == -1 else 0)

        return {'value': out, 'valueb': not out if input_cache['invert'] else out}, True


class ValueChanged(Node):
    NAME = 'ValueChanged'
    DESCRIPTION = "Output a value only if it has changed"
    INPUTS = [NodeIO('value', float)]
    OUTPUTS = [NodeIO('value', float)]

    def process(self, from_node, output_name, input_name, value, input_cache, output_cache):
        return {'value': value}, input_cache['value'] != value


class Timer(Node):
    NAME = 'Timer'
    DESCRIPTION = "Timer that runs while the input value is true"
    INPUTS = [NodeIO('value', bool)]
    OUTPUTS = [NodeIO('duration', float)]

    def setup(self):
        self.timer_start = None

    def process(self, from_node, output_name, input_name, value, input_cache, output_cache):
        if value:
            self.timer_start = self.timer_start or time.time()
        else:
            self.timer_start = None

        if self.timer_start:
            return {'duration': time.time() - self.timer_start}, True
        return {'duration': 0}, True