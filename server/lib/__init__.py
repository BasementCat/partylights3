import threading
import time


class HasThread:
    all_threads = []
    stop_threads = threading.Event()


    def __init__(self, *args, target_name='run_thread_loop', start_immediately=True, **kwargs):
        self.stop_this_thread = threading.Event()
        self.thread = None

        if not hasattr(self, target_name):
            return
        self.target_loop = getattr(self, target_name)

        self.thread = threading.Thread(target=self.run_thread)
        self.all_threads.append(self)
        if start_immediately:
            self.start()

    def start(self):
        if self.thread:
            self.thread.start()

    def stop(self, join=True):
        self.stop_this_thread.set()
        if join:
            self.join()

    def join(self):
        if self.thread:
            self.thread.join()

    @classmethod
    def stop_all(cls, join=True):
        cls.stop_threads.set()
        if join:
            cls.join_all()

    @classmethod
    def join_all(cls):
        for t in cls.all_threads:
            t.join()

    # def run_thread_loop(self):
    #   time.sleep(1)

    def run_thread(self):
        while not (self.stop_threads.is_set() or self.stop_this_thread.is_set()):
            self.target_loop()
