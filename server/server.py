import time
from lib import HasThread
from lib.inputs.osc import OSCServerInput
from lib.inputs.osc.flavors import SynesthesiaOSCFlavor


try:
    flavor = SynesthesiaOSCFlavor()
    server = OSCServerInput(flavor)

    while True:
        time.sleep(1)
finally:
    HasThread.stop_all()