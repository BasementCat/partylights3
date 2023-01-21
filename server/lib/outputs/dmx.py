import time
import os
import glob
import subprocess
import re

from dmxpy.DmxPy import DmxPy

from . import Output


class DMXDevice:
    @staticmethod
    def hexint(v):
        return int(v, 16)

    def __init__(self, device='0403:6001', debug=None):
        # device can be a device path (/dev/ttyUSB0) or usb vid:pid (0403:6001)
        # If debug is False, nothing is output, if true, data is always logged, if None, data is logged only if no device is found
        self.device = device
        self.debug = debug
        self.last_find = None
        self.dmx = None
        self.data = {i + 1: 0 for i in range(512)}

        self.find_device()

    def find_device(self):
        if self.dmx or self.last_find is None or time.time() - self.last_find >= 1:
            self.last_find = time.time()
            try:
                devfile = self._find_device_file(self.device)
                if devfile:
                    try:
                        self.dmx = DmxPy(devfile)
                    except:
                        print("Can't open dmx device file:", devfile)
            except:
                pass

    @classmethod
    def _find_device_file__linux(cls, vendor, product):
        if not os.path.exists('/sys') or not os.path.isdir('/sys'):
            return None
        for dev in glob.glob('/sys/bus/usb-serial/devices/*'):
            devname = os.path.basename(dev)
            with open(os.path.join(dev, '../uevent'), 'r') as fp:
                for line in fp:
                    line = line.strip()
                    if line and '=' in line:
                        param, value = line.split('=')
                        if param == 'PRODUCT':
                            testvendor, testproduct = map(cls.hexint, value.split('/')[:2])
                            if testvendor == vendor and testproduct == product:
                                return os.path.join('/dev', devname)

    @classmethod
    def _find_device_file__macos(cls, vendor, product):
        devices = []
        curdevice = {}

        try:
            res = subprocess.check_output(['ioreg', '-p', 'IOUSB', '-l', '-b']).decode('utf-8')
        except FileNotFoundError:
            # No ioreg - not macos
            return

        for line in res.split('\n'):
            line = line.strip()
            if not line:
                continue

            match = re.match(u'^\+-o (.+)\s+<', line)
            if match:
                if curdevice:
                    devices.append(curdevice)
                    curdevice = {}
                continue

            match = re.match(u'^[\|\s]*"([\w\d\s]+)"\s+=\s+(.+)$', line)
            if match:
                k, v = match.groups()
                if v.startswith('"'):
                    v = v[1:-1]
                else:
                    try:
                        v = int(v)
                    except:
                        pass
                curdevice[k] = v

        if curdevice:
            devices.append(curdevice)

        for d in devices:
            if d.get('idVendor') == vendor and d.get('idProduct') == product:
                return '/dev/tty.usbserial-' + d['USB Serial Number']

    @classmethod
    def _find_device_file(cls, name):
        # Name is either a path (/dev/ttyUSB0) which might change, or a device ID (0403:6001) which does not
        if name.startswith('/') or ':' not in name:
            # Assume file
            return name

        if ':' not in name:
            raise ValueError(f"Not a valid device ID: {name}")

        vendor, product = map(cls.hexint, name.split(':'))

        for fn in (cls._find_device_file__linux, cls._find_device_file__macos):
            try:
                file = fn(vendor, product)
                if file:
                    return file
            except Exception as e:
                raise RuntimeError("Failure in find device file") from e

        raise RuntimeError(f"Can't find USB device {name}")

    def update(self, data):
        self.data.update(data)

    def set_channel(self, chan, value):
        self.data[chan] = value

    def render(self):
        if self.data:
            self.find_device()
            if self.debug is True or (self.debug is None and not self.dmx):
                print("DMX OUT:", self.data)
            if self.dmx:
                for k, v in self.data.items():
                    self.dmx.set_channel(k, v)
                self.dmx.render()
                self.data = {}


class DMXOutput(Output):
    def __init__(self, *args, **kwargs):
        # TODO: configurable
        self.dmx = DMXDevice()
        self.last_render = None
        self.render_s = 1 / 60.0  # TODO: configure fps
        super().__init__(*args, **kwargs)

    def process_lights(self, lights):
        for l in lights:
            if l.type.PROTOCOL == 'dmx':
                self.dmx.update(l.get_dmx_state())
        if self.last_render is None or time.time() - self.last_render >= self.render_s:
            self.last_render = time.time()
            self.dmx.render()