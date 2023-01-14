import itertools
import time
from queue import Queue, Empty
from threading import RLock

from lib import HasThread


def calcdiff(new, old):
    single = False
    try:
        iter(new)
    except:
        single = True
        new = [new]
    try:
        iter(old)
    except:
        single = True
        old = [old or 0]

    out_old = []
    diff = []
    diff_p = []

    for nv, ov in itertools.zip_longest(new, old, fillvalue=0):
        out_old.append(ov)
        diff.append(nv - ov)
        if ov == 0:
            diff_p.append(0)
        else:
            diff_p.append(diff[-1] / ov)

    if single:
        return out_old[0], diff[0], diff_p[0]
    return out_old, diff, diff_p


class Input(HasThread):
    output_queue = Queue()
    event_cache = {}
    event_cache_lock = RLock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def process_events(self, timeout=None):
        start = time.time()
        while True:
            try:
                event, args = self.output_queue.get(block=False)
                last_args = self.event_cache.get(event)
                if last_args:
                    last_args = last_args[0]
                old, diff, diff_p = calcdiff(args, last_args)
                with self.event_cache_lock:
                    self.event_cache[event] = (args, old, diff, diff_p)
                # return event, args, old, diff, diff_p
                if timeout is not None and time.time() - start >= timeout:
                    break
            except Empty:
                break

    @classmethod
    def get_data(self, process=True, timeout=None):
        if process:
            self.process_events(timeout=timeout)
        with self.event_cache_lock:
            return dict(self.event_cache)
