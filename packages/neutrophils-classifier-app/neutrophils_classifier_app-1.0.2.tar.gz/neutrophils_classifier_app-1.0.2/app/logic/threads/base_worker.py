import functools
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class ThreadWorker(QObject):
    """
    A generic, reusable worker for running functions in a separate QThread.

    Signals:
        finished: Emitted when the task is completed.
        result(object): Emitted with the return value of the function.
        error(Exception): Emitted if an exception occurs.
        progress(int): Emitted to report progress (0-100).
    """
    finished = pyqtSignal()
    result = pyqtSignal(object)
    error = pyqtSignal(Exception)
    progress = pyqtSignal(int)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

    @pyqtSlot()
    def run(self):
        """Execute the wrapped function."""
        try:
            # Add progress_callback and is_cancelled to kwargs if the target function accepts them
            if 'progress_callback' in self.func.__code__.co_varnames:
                self.kwargs['progress_callback'] = self.progress.emit
            if 'is_cancelled' in self.func.__code__.co_varnames:
                self.kwargs['is_cancelled'] = self.is_cancelled

            res = self.func(*self.args, **self.kwargs)
            self.result.emit(res)
        except Exception as e:
            self.error.emit(e)
        finally:
            self.finished.emit()

    def is_cancelled(self):
        """Check if the task has been cancelled."""
        return self._is_cancelled

    def cancel(self):
        """Signal the worker to cancel the operation."""
        self._is_cancelled = True

def threaded(func):
    """
    A decorator to run a function in a separate QThread, returning a worker and thread.

    This decorator simplifies running functions in the background without blocking the UI.
    It returns a tuple (worker, thread), allowing the caller to connect signals
    before starting the thread.

    Usage:
        @threaded
        def my_long_task(duration):
            # ... task logic ...
            return "Complete"

        worker, thread = my_long_task(10)
        worker.result.connect(handle_result)
        worker.finished.connect(lambda: print("Task finished."))
        thread.started.connect(worker.run)
        thread.start()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = QThread()
        worker = ThreadWorker(func, *args, **kwargs)
        worker.moveToThread(thread)

        # Safe cleanup
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # The caller is responsible for connecting signals and starting the thread.
        # This provides flexibility for different use cases.
        # Example: thread.started.connect(worker.run); thread.start()
        return worker, thread
    return wrapper