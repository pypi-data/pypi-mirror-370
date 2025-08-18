class Disposable:
    def __init__(self, disposable):
        self._disposable = disposable

    def stop(self):
        self._disposable.Dispose()

    def __enter__(self):
        # Empty method required to be used as a context manager.
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
