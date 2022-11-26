from . import Node, NodeIO


class PrintNode(Node):
    NAME = 'PrintNode'
    DESCRIPTION = "Prints the data sent to its input"
    INPUTS = [NodeIO('data', str)]

    def process(self, from_node, output_name, input_name, value, input_cache, output_cache):
        print(f"From {from_node.name}: {output_name}: '{value}'")
        return {}, False
