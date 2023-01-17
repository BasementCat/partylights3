import time
import signal

from lib import HasThread
from lib.inputs import Input
from lib.inputs.osc import OSCServerInput
from lib.inputs.osc.flavors import SynesthesiaOSCFlavor
from lib.lights import Light
from lib.outputs import Output

from tempconfig import controller


do_terminate = False
def signal_handler(signo, frame):
    global do_terminate
    do_terminate = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    flavor = SynesthesiaOSCFlavor()
    server = OSCServerInput(flavor)

    while not do_terminate:
        lights = Light.get(aslist=True)
        data = Input.get_data(timeout=0.01)
        controller.run_triggers(data)
        Output.run_all(controller(data, lights), lights)
finally:
    HasThread.stop_all()
