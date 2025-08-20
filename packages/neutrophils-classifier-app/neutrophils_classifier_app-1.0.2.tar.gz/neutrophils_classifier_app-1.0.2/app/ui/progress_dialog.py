import time
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt


class LoadingProgressDialog(QProgressDialog):
    """
    Progress dialog for file loading operations.
    Extends QProgressDialog with specific styling for file loading.
    """
    
    def __init__(self, parent=None, title="Loading Files", message="Loading images..."):
        super().__init__(message, "Cancel", 0, 100, parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModal)
        self.setAutoClose(True)
        self.setAutoReset(True)
        self.setMinimumDuration(0)  # Show immediately
        
        # Track if dialog was canceled
        self.was_canceled = False
        self.canceled.connect(self._on_canceled)
    
    def _on_canceled(self):
        """Handle cancel signal."""
        self.was_canceled = True
    
    def update_progress(self, value, message=None):
        """Update progress bar value and optionally the status message."""
        self.setValue(value)
        if message:
            self.setLabelText(message)


class BatchProgressDialog(QProgressDialog):
    """
    Progress dialog for batch processing operations.
    Shows progress with ratio of completed tasks to total tasks.
    """
    
    def __init__(self, parent=None, title="Batch Processing", total_tasks=0):
        super().__init__("Batch processing...", "Cancel", 0, 100, parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.NonModal)
        self.setAutoClose(True)
        self.setAutoReset(True)
        self.setMinimumDuration(0)  # Show immediately
        
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        self.start_time = time.time()
        
        # Track if dialog was canceled
        self.was_canceled = False
        self.canceled.connect(self._on_canceled)
        
        # Update initial label
        self._update_label()
    
    def _on_canceled(self):
        """Handle cancel signal."""
        self.was_canceled = True
    
    def _format_time(self, seconds):
        """Format seconds into MM:SS."""
        if seconds is None or seconds < 0:
            return "--:--"
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _update_label(self, current_task=None, progress_percent=None):
        """Update the label text with task ratio, percentage, and current task."""
        time_str = ""
        if progress_percent is not None and progress_percent > 0:
            elapsed_time = time.time() - self.start_time
            estimated_total_time = (elapsed_time / progress_percent) * 100
            remaining_time = estimated_total_time - elapsed_time
            time_str = f" | ETA: {self._format_time(remaining_time)}"

        if progress_percent is not None:
            base_text = f"Batch processing... ({self.completed_tasks} / {self.total_tasks} images processed - {progress_percent}%){time_str}"
        else:
            base_text = f"Batch processing... ({self.completed_tasks} / {self.total_tasks} images processed)"
        
        if current_task:
            base_text += f"\nProcessing: {current_task}"
        self.setLabelText(base_text)
    
    def update_progress(self, progress_value, completed_count=None, current_task=None):
        """
        Update progress bar and task information.
        
        Args:
            progress_value: Progress percentage (0-100)
            completed_count: Number of completed tasks
            current_task: Name of current task being processed
        """
        self.setValue(progress_value)
        
        if completed_count is not None:
            self.completed_tasks = completed_count
        elif self.total_tasks > 0:
            # Estimate completed tasks from progress value
            estimated_tasks = int(((progress_value / 100.0) * self.total_tasks) + 0.5)
            self.completed_tasks = min(estimated_tasks, self.total_tasks)
        
        self._update_label(current_task, progress_value)
    
    def set_total_tasks(self, total):
        """Update the total number of tasks."""
        self.total_tasks = total
        current_progress = self.value()
        self._update_label(progress_percent=current_progress)