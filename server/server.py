import time
from lib import HasThread
from lib.inputs.osc import OSCServerInput
from lib.inputs.osc.flavors import SynesthesiaOSCFlavor
from lib.nodes import Node
from lib.nodes.basic import PrintNode


try:
    flavor = SynesthesiaOSCFlavor()
    server = OSCServerInput(flavor)
    printer = PrintNode('printer')
    Node.link(server.server, '*', printer, 'data')

    while True:
        time.sleep(1)
finally:
    HasThread.stop_all()