import fnmatch


class NodeIO:
    def __init__(self, name, type, default=0, is_array=False, description=None):
        self.name = name
        self.type = type
        self.default = type(default)
        self.is_array = is_array
        self.description = description

    def __call__(self, value):
        if self.is_array:
            return tuple(map(self.type, value))
        return self.type(value)


class Node:
    NAME = None
    DESCRIPTION = None
    INPUTS = []
    OUTPUTS = []
    all_nodes = {}
    node_links = {}

    def __init__(self, name, *args, **kwargs):
        if name in self.all_nodes:
            raise ValueError(f"A node with name '{name}' is already defined")

        self.name = name
        self.input_io_cache = {io.name: io for io in self.INPUTS}
        self.output_io_cache = {io.name: io for io in self.OUTPUTS}
        self.input_cache = {io.name: io.default for io in self.INPUTS}
        self.output_cache = {io.name: io.default for io in self.OUTPUTS}

        self.all_nodes[self.name] = self

        self.setup()

    def setup(self):
        pass

    @classmethod
    def link(cls, src_node_name, output_name, dest_node_name, input_name):
        if isinstance(src_node_name, Node):
            src_node_name = src_node_name.name
        if isinstance(dest_node_name, Node):
            dest_node_name = dest_node_name.name
        cls.node_links.setdefault(src_node_name, []).append((output_name, dest_node_name, input_name))

    def send_input(self, from_node, output_name, input_name, value):
        if input_name not in self.input_io_cache:
            return
        value = self.input_io_cache[input_name](value)
        outputs, send_outputs = self.process(from_node, output_name, input_name, value, self.input_cache, self.output_cache)
        self.input_cache[input_name] = value
        self.cache_outputs(outputs)
        if send_outputs:
            if send_outputs is True:
                self.send_outputs()
            else:
                self.send_outputs(*send_outputs)

    def cache_outputs(self, outputs):
        self.output_cache.update({k: self.output_io_cache[k](v) for k, v in outputs.items() if k in self.output_io_cache})

    def send_outputs(self, *output_names):
        if not output_names:
            output_names = list(self.output_io_cache.keys())

        for o in output_names:
            if o in self.output_cache:
                for output_name, dest_node_name, input_name in self.node_links.get(self.name, []):
                    if dest_node_name in self.all_nodes and fnmatch.fnmatch(o, output_name):
                        self.all_nodes[dest_node_name].send_input(self, o, input_name, self.output_cache[o])

    def process(self, from_node, output_name, input_name, value, input_cache, output_cache):
        return {io.name: value for io in self.OUTPUTS}, True
