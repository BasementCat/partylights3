import threading
import time


class HasThread:
    all_threads = []

    def __init__(self, *args, target_name='run_thread_loop', start_immediately=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_thread = threading.Event()
        self.thread = None

        if not hasattr(self, target_name):
            return
        self.target_loop = getattr(self, target_name)

        self.thread = threading.Thread(target=self.run_thread)
        self.all_threads.append(self)
        if start_immediately:
            self.start()

    def setup_main(self):
        pass

    def setup_thread(self):
        pass

    def teardown_main(self):
        pass

    def teardown_thread(self):
        pass        

    def start(self):
        if self.thread:
            self.setup_main()
            self.thread.start()

    def stop(self, join=True):
        self.stop_thread.set()
        if join:
            self.join()

    def join(self):
        if self.thread:
            self.thread.join()
            self.teardown_main()

    @classmethod
    def stop_all(cls, join=True):
        for t in cls.all_threads:
            t.stop(join=False)
        if join:
            cls.join_all()

    @classmethod
    def join_all(cls):
        for t in cls.all_threads:
            t.join()

    def run_thread_loop(self):
      time.sleep(1)

    def run_thread(self):
        self.setup_thread()
        while not self.stop_thread.is_set():
            self.target_loop()
        self.teardown_thread()


def ListOf(type_):
    def _check(v):
        if not isinstance(v, type_):
            raise ValueError(str(type(v)))
        return v

    class ListOfType(list):
        def __init__(self, *args):
            if len(args) == 1 and isinstance(args[0], (list, tuple, dict, set)):
                args = args[0]
            args = list(map(_check, args))
            super().__init__(args)

        # Some operations aren't supported - they would require re-instantiation
        def __add__(self, other):
            raise RuntimeError("Not supported")

        def __radd__(self, other):
            raise RuntimeError("Not supported")

        def __iadd__(self, other):
            raise RuntimeError("Not supported")

        def copy(self):
            raise RuntimeError("Not supported")

        def append(self, item):
            super().append(_check(item))

        def extend(self, other):
            super().extend(map(_check, other))

        def insert(self, i, item):
            super().insert(i, _check(item))

        def __setitem__(self, i, item):
            super().__setitem__(i, _check(item))

    return ListOfType


class Named:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)


def Collected(key='name', allow_none=False):
    class CollectedBy:
        COLLECTION = {}

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            coll_key = getattr(self, key, None)
            if coll_key is None and not allow_none:
                raise ValueError(f"Collection key {key} is None")

            if coll_key in self.COLLECTION:
                raise ValueError(f"Collection key {key}={repr(coll_key)} is already present in collection")

            self.COLLECTION[coll_key] = self

        @classmethod
        def get(cls, key=False, aslist=False):
            if key is not False:
                return cls.COLLECTION.get(key, None)
            if aslist:
                return list(cls.COLLECTION.values())
            return dict(cls.COLLECTION)

    return CollectedBy


class Grouped:
    def __init__(self, *args, groups=None, **kwargs):
        self.groups = groups or []
        super().__init__(*args, **kwargs)

    @classmethod
    def get_by_groups(cls, *groups, any=False):
        if not issubclass(cls, Collected):
            raise RuntimeError(f'{cls.__name__} is not a subclass of Collected')
        for item in cls.get(aslist=True):
            if any:
                if set(groups) & set(item.groups):
                    yield item
            else:
                if not set(groups) - set(item.groups):
                    yield item
