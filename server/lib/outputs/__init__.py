from queue import Queue, Empty

from lib import HasThread, Named, Collected


class Output(Named, Collected(), HasThread):
    all_outputs = []

    def __init__(self, *args, **kwargs):
        self.queue = Queue()
        super().__init__(*args, **kwargs)
        self.all_outputs.append(self)

    def run_thread_loop(self):
        try:
            self.process_lights(self.queue.get(timeout=1))
        except Empty:
            pass

    def process_lights(self, lights):
        pass

    @classmethod
    def run_all(cls, output, lights):
        modified = []
        for l in lights:
            if l.name in output:
                l.update_state(output[l.name])
                modified.append(l)

        if modified:
            for o in cls.all_outputs:
                o.queue.put(modified)
