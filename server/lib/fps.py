from threading import Lock
import time

from . import HasThread


counters = {}
count_lock = Lock()


def count(name):
    with count_lock:
        counters.setdefault(name, 0)
        counters[name] += 1


class FPSThread(HasThread):
    def run_thread_loop(self):
        time.sleep(1)
        with count_lock:
            if counters:
                print("FPS:", ', '.join((k + ': ' + str(v) for k, v in counters.items())))
                for k in counters:
                    counters[k] = 0

FPSThread()