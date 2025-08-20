import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import Mock, MagicMock, patch
import time

# Mock PyQt5 dependencies to avoid GUI requirements in tests
mock_qobject = MagicMock()
mock_qthread = MagicMock()
mock_pyqtsignal = MagicMock()

# In a real QThread, started and finished are signals. We'll mock them.
mock_qthread.started = MagicMock()
mock_qthread.finished = MagicMock()


# Import the modules that will be tested
from app.logic.threads.base_worker import ThreadWorker, threaded

# --- Test Functions ---

def simple_task(duration):
    """A simple function that runs for a given duration."""
    time.sleep(duration)
    return "Success"

def task_with_args(x, y, factor=2):
    """A function with positional and keyword arguments."""
    return (x + y) * factor

def failing_task():
    """A function that raises an exception."""
    raise ValueError("Task Failed")

def progress_task(progress_callback, is_cancelled):
    """A function that reports progress and can be cancelled."""
    for i in range(11):
        if is_cancelled():
            return "Cancelled"
        progress_callback(i * 10)
        time.sleep(0.01)
    return "Complete"

# --- Test Cases ---

@patch('app.logic.threads.base_worker.QObject')
class TestThreadWorker(unittest.TestCase):
    """Unit tests for the ThreadWorker class."""

    def test_run_success(self, MockQObject):
        """Test successful execution of a function."""
        mock_result_slot = Mock()
        mock_finished_slot = Mock()

        worker = ThreadWorker(simple_task, 0.01)
        worker.result.connect(mock_result_slot)
        worker.finished.connect(mock_finished_slot)

        worker.run()

        mock_result_slot.assert_called_once_with("Success")
        mock_finished_slot.assert_called_once()

    def test_run_with_args_and_kwargs(self, MockQObject):
        """Test execution with various arguments."""
        mock_result_slot = Mock()
        worker = ThreadWorker(task_with_args, 5, 5, factor=3)
        worker.result.connect(mock_result_slot)
        worker.run()
        mock_result_slot.assert_called_once_with(30)

    def test_run_error(self, MockQObject):
        """Test that the error signal is emitted on exception."""
        mock_error_slot = Mock()
        mock_finished_slot = Mock()

        worker = ThreadWorker(failing_task)
        worker.error.connect(mock_error_slot)
        worker.finished.connect(mock_finished_slot)

        worker.run()

        mock_error_slot.assert_called_once()
        self.assertIsInstance(mock_error_slot.call_args[0][0], ValueError)
        mock_finished_slot.assert_called_once()

    def test_progress_and_cancellation_injection(self, MockQObject):
        """Test that progress and cancellation callbacks are passed correctly."""
        mock_progress_slot = Mock()
        mock_result_slot = Mock()

        # Mock the function's code object to simulate its signature
        mock_func = MagicMock()
        mock_func.__code__ = MagicMock()
        mock_func.__code__.co_varnames = ('progress_callback', 'is_cancelled')

        worker = ThreadWorker(mock_func)
        worker.progress.connect(mock_progress_slot)
        worker.result.connect(mock_result_slot)

        worker.run()

        # Check that the function was called with the injected kwargs
        self.assertIn('progress_callback', worker.kwargs)
        self.assertIn('is_cancelled', worker.kwargs)
        # Check that the mock function was called (which means the injected args were passed)
        mock_func.assert_called_once()
        self.assertEqual(worker.kwargs['is_cancelled'], worker.is_cancelled)

    def test_cancellation_logic(self, MockQObject):
        """Test the cancellation mechanism."""
        worker = ThreadWorker(simple_task, 0)
        self.assertFalse(worker.is_cancelled())
        worker.cancel()
        self.assertTrue(worker.is_cancelled())


class TestThreadedDecorator(unittest.TestCase):
    """Unit tests for the @threaded decorator."""

    @patch('app.logic.threads.base_worker.QThread')
    @patch('app.logic.threads.base_worker.ThreadWorker')
    def test_decorator_returns_worker_and_thread(self, MockThreadWorker, MockQThread):
        """Test that the decorator returns a worker and a thread instance."""
        mock_worker_instance = MagicMock()
        mock_thread_instance = MagicMock()
        MockThreadWorker.return_value = mock_worker_instance
        MockQThread.return_value = mock_thread_instance

        @threaded
        def decorated_func(arg1, kwarg1=None):
            return "done"

        # Call the decorated function
        worker, thread = decorated_func("test_arg", kwarg1="test_kwarg")

        # Assert that the decorator returned the mocked instances
        self.assertIs(worker, mock_worker_instance)
        self.assertIs(thread, mock_thread_instance)

        # Assert that ThreadWorker was instantiated correctly
        MockThreadWorker.assert_called_once()
        # The first argument to ThreadWorker is the original function
        self.assertEqual(MockThreadWorker.call_args[0][0].__name__, 'decorated_func')
        # Check other args and kwargs
        self.assertEqual(MockThreadWorker.call_args[0][1], "test_arg")
        self.assertEqual(MockThreadWorker.call_args[1], {'kwarg1': 'test_kwarg'})

        # Assert that the worker was moved to the thread
        mock_worker_instance.moveToThread.assert_called_once_with(mock_thread_instance)

        # Assert that cleanup signals were connected
        self.assertEqual(mock_worker_instance.finished.connect.call_count, 2)
        mock_worker_instance.finished.connect.assert_any_call(mock_thread_instance.quit)
        mock_worker_instance.finished.connect.assert_any_call(mock_worker_instance.deleteLater)
        mock_thread_instance.finished.connect.assert_called_once_with(mock_thread_instance.deleteLater)

    @patch('app.logic.threads.base_worker.QThread')
    @patch('app.logic.threads.base_worker.ThreadWorker.moveToThread')
    def test_worker_and_thread_integration(self, mock_move_to_thread, MockQThread):
        """Test the full lifecycle of a decorated function by only mocking QThread."""
        # We need the mock to look like a QThread instance for type checking
        from PyQt5.QtCore import QThread
        mock_thread_instance = MagicMock(spec=QThread)
        MockQThread.return_value = mock_thread_instance

        mock_result_slot = Mock()
        mock_finished_slot = Mock()

        # Use the real decorator and worker, but a mocked thread
        decorated_task = threaded(simple_task)
        worker, thread = decorated_task(0.01)

        # Check that the returned thread is our mock
        self.assertIs(thread, mock_thread_instance)

        # Check that moveToThread was called
        mock_move_to_thread.assert_called_once_with(mock_thread_instance)

        worker.result.connect(mock_result_slot)
        worker.finished.connect(mock_finished_slot)

        # The decorator should not connect the `started` signal
        mock_thread_instance.started.connect.assert_not_called()

        # Manually trigger run to simulate what `thread.start()` would do
        worker.run()

        mock_result_slot.assert_called_once_with("Success")
        mock_finished_slot.assert_called_once()


if __name__ == '__main__':
    unittest.main()