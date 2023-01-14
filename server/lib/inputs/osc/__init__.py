"""\
OSC input base classes
"""

import time

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from lib import HasThread
from lib.inputs import Input


class OSCAddress:
    """\
    Represents a mapping of an OSC address to an event
    """

    def __init__(self, address, addr_args, event=None, event_args=None, description=None, mapper=None):
        """\
        Create a new OSC address to event mapping

        Args:
        address: OSC address
        addr_args: Iterable of argument types expected to be received in the OSC event
        event: Event name, if not provided, the OSC address without the leading "/" is used
        event_args: Iterable of argument types passed to the event, if not provided, the types defined for the OSC address are used
        description: A description of the event
        mapper: A function that remaps the OSC message to the event.  Accepts (address, *args) and should return (event, args)
        """

        self.address = address
        self.addr_args = addr_args
        self.event = event or address.lstrip('/')
        self.event_args = event_args or addr_args
        self.description = description
        self.mapper = mapper or self._default_mapper

    def __str__(self):
        out = "{} ({}) -> {} ({})".format(
            self.address,
            ', '.join(map(str, self.addr_args)),
            self.event,
            ', '.join(map(str, self.event_args)),
        )
        if self.description:
            out += ': ' + self.description

    def _default_mapper(self, address, *args):
        return self.event, args

    def _pre_map_args(self, args):
        for a, t in zip(args, self.addr_args):
            yield t(a)

    def _post_map_args(self, args):
        for a, t in zip(args, self.event_args):
            yield t(a)

    def __call__(self, address, *args):
        args = self._pre_map_args(args)
        event, args = self.mapper(address, *args)
        args = self._post_map_args(args)
        return event, tuple(args)


class OSCFlavor:
    """\
    A "flavor" of OSC, mapping OSC events to internal events
    """

    EVENTS = []

    def __init__(self):
        self._addr_map = {a.address: a for a in self.EVENTS}

    def __call__(self, address, *args):
        addr = self._addr_map.get(address)
        if not addr:
            # TODO: log
            return None, None
        return addr(address, *args)


class _OSCBlockingServer(HasThread):
    def __init__(self, osc_input, osc_flavor, host='0.0.0.0', port=7000, *args, **kwargs):
        self.osc_input = osc_input
        self.osc_flavor = osc_flavor
        self.host = host
        self.port = port
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self.osc_handler)
        self.server = BlockingOSCUDPServer((self.host, self.port), self.dispatcher)
        super().__init__(*args, **kwargs)

    def run_thread_loop(self):
        # This blocks forever - server.shutdown() is called externally when threads should exit & at that point the main thread loop will also exit
        self.server.serve_forever()

    def osc_handler(self, address, *args):
        event, event_args = self.osc_flavor(address, *args)
        if len(event_args) == 1:
            event_args = event_args[0]
        elif len(event_args) == 0:
            event_args = None

        self.osc_input.output_queue.put((event, event_args))


class OSCServerInput(Input):
    def __init__(self, osc_flavor, host='0.0.0.0', port=7000, *args, **kwargs):
        self.server = _OSCBlockingServer(self, osc_flavor, host=host, port=port, *args, **kwargs)
        super().__init__(*args, **kwargs)

    def run_thread_loop(self):
        time.sleep(1)

    def run_thread(self):
        super().run_thread()
        # Parent method will return when threads should stop
        # Notify the server thread to stop (but don't join) - in case only this input thread was stopped, then the server thread should also stop
        self.server.stop(join=False)
        # Tell the actual udp server to stop as well
        self.server.server.shutdown()
