import threading


class DBGatekeeper:
    _locks = {}
    _global_lock = threading.Lock()

    @classmethod
    def get(cls, key: str, max_concurrency: int):
        with cls._global_lock:
            sem = cls._locks.get(key)
            if sem is None:
                sem = threading.BoundedSemaphore(max_concurrency)
                cls._locks[key] = sem
            return sem
