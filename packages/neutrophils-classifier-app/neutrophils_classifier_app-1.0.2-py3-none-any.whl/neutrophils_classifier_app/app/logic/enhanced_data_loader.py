#!/usr/bin/env python3
"""
Enhanced Data Loading Workflow
Implements batch operations, caching, and auto-processing for the Neutrophils Classifier App.
"""

import os
import time
import threading
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QObject
from PyQt5.QtWidgets import QMessageBox
import logging

# Import frontend-specific cache manager (no neutrophils-core dependency)
from .frontend_cache_manager import get_frontend_cache_manager


class ProcessingState(Enum):
    """States for the data processing pipeline"""
    IDLE = "idle"
    LOADING = "loading"
    PREPROCESSING = "preprocessing"
    INFERENCE = "inference"
    POSTPROCESSING = "postprocessing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ProcessingTask:
    """A single processing task for an image"""
    file_path: str
    file_name: str
    state: ProcessingState = ProcessingState.IDLE
    progress: float = 0.0
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    results: Optional[Dict[str, Any]] = None


class BatchProcessingConfig:
    """Configuration for batch processing"""
    
    def __init__(self):
        self.auto_processing_enabled = False
        self.auto_load_model = True
        self.auto_inference = True
        self.auto_save_results = False
        self.batch_size = 5  # Number of images to process simultaneously
        self.cache_enabled = True
        self.cache_size_mb = 512
        self.progress_update_interval = 100  # ms
        self.max_concurrent_tasks = 3


class EnhancedDataLoader(QObject):
    """
    Enhanced data loader with batch operations, caching, and auto-processing capabilities.
    Replaces the iterative on_list_changed() processing with efficient batch operations.
    """
    
    # Signals for progress reporting
    progress_updated = pyqtSignal(int, str)  # progress percentage, message
    task_completed = pyqtSignal(str, dict)  # file_path, results
    batch_completed = pyqtSignal(list)  # list of completed tasks
    error_occurred = pyqtSignal(str, str)  # file_path, error_message
    
    def __init__(self, main_window, config: Optional[BatchProcessingConfig] = None):
        super().__init__()
        self.main_window = main_window
        self.config = config or BatchProcessingConfig()
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Task management
        self.tasks: Dict[str, ProcessingTask] = {}
        self.active_tasks: List[ProcessingTask] = []
        self.completed_tasks: List[ProcessingTask] = []
        self.failed_tasks: List[ProcessingTask] = []
        
        # Threading
        self.processing_threads: List[QThread] = []
        self.is_processing = False
        self._stop_processing = threading.Event()
        
        # Initialize caching system
        self._init_cache_system()
        
        # Progress update timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        self.progress_timer.setInterval(self.config.progress_update_interval)
        
        # Connect signals
        self._connect_signals()
    
    def _init_cache_system(self):
        """Initialize the frontend caching system (no smart prefetch)"""
        if self.config.cache_enabled:
            try:
                cache_manager = get_frontend_cache_manager()
                self.image_loader = cache_manager.get_loader()
                self.logger.info(f"Initialized FrontendImageLoader with {self.config.cache_size_mb}MB cache")
            except Exception as e:
                self.logger.warning(f"Failed to initialize cache system: {e}")
                self.image_loader = None
        else:
            self.image_loader = None
            self.logger.info("Cache system disabled")
    
    def _connect_signals(self):
        """Connect internal signals"""
        self.progress_updated.connect(self._report_progress_to_ui)
        self.error_occurred.connect(self._handle_error)
    
    def _report_progress_to_ui(self, progress: int, message: str):
        """Report progress to the main window's progress_label"""
        if hasattr(self.main_window, 'progress_label') and self.main_window.progress_label:
            self.main_window.progress_label.setVisible(True)
            self.main_window.progress_label.setText(message)
        
        if hasattr(self.main_window, 'progress_bar') and self.main_window.progress_bar:
            self.main_window.progress_bar.setVisible(True)
            self.main_window.progress_bar.setValue(progress)
    
    def _handle_error(self, file_path: str, error_message: str):
        """Handle processing errors"""
        self.logger.error(f"Processing error for {file_path}: {error_message}")
        
        # Update task state
        if file_path in self.tasks:
            task = self.tasks[file_path]
            task.state = ProcessingState.ERROR
            task.error_message = error_message
            task.end_time = time.time()
            self.failed_tasks.append(task)
    
    def load_files_batch(self, file_paths: List[str]) -> bool:
        """
        Load multiple files in batch mode with caching.
        Replaces the current iterative file loading approach.
        """
        try:
            self.logger.info(f"Starting batch loading of {len(file_paths)} files")
            
            # Clear previous tasks
            self.tasks.clear()
            self.active_tasks.clear()
            self.completed_tasks.clear()
            self.failed_tasks.clear()
            
            # Create tasks for each file
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                task = ProcessingTask(file_path=file_path, file_name=file_name)
                self.tasks[file_path] = task
            
            # Update main window files list
            self.main_window.files = file_paths
            self.logger.debug(f"Updated main_window.files with {len(file_paths)} files")
            
            # Populate file list and trigger initial rendering
            self._populate_file_list()
            
            # Critical fix: Ensure image rendering is triggered after population
            if hasattr(self.main_window, 'listWidget') and self.main_window.listWidget.count() > 0:
                if hasattr(self.main_window, 'on_list_changed'):
                    self.logger.debug("Enhanced loader: Triggering initial image rendering with on_list_changed")
                    # Use QTimer to ensure the UI has updated before triggering rendering
                    QTimer.singleShot(100, self.main_window.on_list_changed)
                else:
                    self.logger.warning("Enhanced loader: No on_list_changed method found - images may not render")
            
            # Report progress
            self.progress_updated.emit(100, f"Loaded {len(file_paths)} files for processing")
            
            # Start auto-processing if enabled
            if self.config.auto_processing_enabled:
                QTimer.singleShot(500, self.start_auto_processing)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load files in batch: {e}")
            self.error_occurred.emit("batch_load", str(e))
            return False
    
    def _populate_file_list(self):
        """Populate the list widget with loaded files"""
        if hasattr(self.main_window, 'listWidget'):
            files_count = len(self.main_window.files) if hasattr(self.main_window, 'files') else 0
            
            # Store current selection before clearing
            current_selection = None
            current_row = self.main_window.listWidget.currentRow()
            if self.main_window.listWidget.currentItem():
                current_selection = self.main_window.listWidget.currentItem().text()
            
            self.main_window.listWidget.clear()
            
            if hasattr(self.main_window, 'files'):
                for i, file_path in enumerate(self.main_window.files):
                    file_name = os.path.basename(file_path)
                    self.main_window.listWidget.addItem(file_name)
                
                # Select first item if available
                if self.main_window.files and self.main_window.listWidget.count() > 0:
                    selection_row = 0
                    
                    # Try to restore previous selection if it still exists
                    if current_selection:
                        for i in range(self.main_window.listWidget.count()):
                            if self.main_window.listWidget.item(i).text() == current_selection:
                                selection_row = i
                                break
                    
                    self.main_window.listWidget.setCurrentRow(selection_row)
                    
                    # Trigger image rendering if method exists
                    if hasattr(self.main_window, 'on_list_changed'):
                        self.main_window.on_list_changed()
    
    def start_auto_processing(self):
        """Start automatic processing of all loaded files"""
        if not self.tasks or self.is_processing:
            return
        
        self.logger.info("Starting auto-processing pipeline")
        self.is_processing = True
        self._stop_processing.clear()
        
        # Start progress timer
        self.progress_timer.start()
        
        # Start processing tasks in batches
        self._process_next_batch()
    
    def stop_processing(self):
        """Stop the auto-processing pipeline"""
        self.logger.info("Stopping auto-processing pipeline")
        self.is_processing = False
        self._stop_processing.set()
        
        # Stop progress timer
        self.progress_timer.stop()
        
        # Stop all processing threads
        for thread in self.processing_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)  # Wait up to 1 second
        
        self.processing_threads.clear()
        self.progress_updated.emit(0, "Processing stopped")
    
    def _process_next_batch(self):
        """Process the next batch of tasks"""
        if self._stop_processing.is_set() or not self.is_processing:
            return
        
        # Find tasks ready for processing
        pending_tasks = [task for task in self.tasks.values() 
                        if task.state == ProcessingState.IDLE]
        
        if not pending_tasks:
            # All tasks completed or no more tasks
            self._finalize_processing()
            return
        
        # Process up to batch_size tasks simultaneously
        batch = pending_tasks[:self.config.batch_size]
        
        for task in batch:
            if len(self.active_tasks) < self.config.max_concurrent_tasks:
                self._start_task_processing(task)
        
        # Schedule next batch check
        QTimer.singleShot(1000, self._process_next_batch)
    
    def _start_task_processing(self, task: ProcessingTask):
        """Start processing a single task"""
        task.state = ProcessingState.LOADING
        task.start_time = time.time()
        self.active_tasks.append(task)
        
        # Create and start processing thread
        thread = EnhancedProcessingThread(task, self.image_loader, self.main_window)
        thread.task_completed.connect(self._on_task_completed)
        thread.task_failed.connect(self._on_task_failed)
        thread.progress_updated.connect(self._on_task_progress)
        
        self.processing_threads.append(thread)
        thread.start()
    
    def _on_task_completed(self, task: ProcessingTask, results: Dict[str, Any]):
        """Handle task completion"""
        task.state = ProcessingState.COMPLETED
        task.end_time = time.time()
        task.results = results
        
        # Move from active to completed
        if task in self.active_tasks:
            self.active_tasks.remove(task)
        self.completed_tasks.append(task)
        
        # Emit completion signal
        self.task_completed.emit(task.file_path, results)
        
        self.logger.info(f"Completed processing: {task.file_name}")
    
    def _on_task_failed(self, task: ProcessingTask, error_message: str):
        """Handle task failure"""
        task.state = ProcessingState.ERROR
        task.end_time = time.time()
        task.error_message = error_message
        
        # Move from active to failed
        if task in self.active_tasks:
            self.active_tasks.remove(task)
        self.failed_tasks.append(task)
        
        # Emit error signal
        self.error_occurred.emit(task.file_path, error_message)
    
    def _on_task_progress(self, task: ProcessingTask, progress: float, message: str):
        """Handle task progress updates"""
        task.progress = progress
        # Individual task progress updates are aggregated in _update_progress
    
    def _update_progress(self):
        """Update overall progress based on all tasks"""
        if not self.tasks:
            return
        
        total_tasks = len(self.tasks)
        completed_count = len(self.completed_tasks)
        failed_count = len(self.failed_tasks)
        active_count = len(self.active_tasks)
        
        # Calculate overall progress
        overall_progress = 0
        if total_tasks > 0:
            base_progress = ((completed_count + failed_count) / total_tasks) * 100
            
            # Add partial progress from active tasks
            active_progress = sum(task.progress for task in self.active_tasks)
            if active_count > 0:
                active_progress = (active_progress / active_count) / total_tasks * 100
            
            overall_progress = min(100, base_progress + active_progress)
        
        # Create status message
        status_parts = []
        if active_count > 0:
            status_parts.append(f"Processing {active_count} files")
        if completed_count > 0:
            status_parts.append(f"{completed_count} completed")
        if failed_count > 0:
            status_parts.append(f"{failed_count} failed")
        
        status_message = ", ".join(status_parts) if status_parts else "Processing..."
        
        self.progress_updated.emit(int(overall_progress), status_message)
    
    def _finalize_processing(self):
        """Finalize the processing pipeline"""
        self.is_processing = False
        self.progress_timer.stop()
        
        # Generate summary
        total_tasks = len(self.tasks)
        completed_count = len(self.completed_tasks)
        failed_count = len(self.failed_tasks)
        
        summary_message = f"Processing complete: {completed_count}/{total_tasks} successful"
        if failed_count > 0:
            summary_message += f", {failed_count} failed"
        
        self.progress_updated.emit(100, summary_message)
        
        # Emit batch completion signal
        self.batch_completed.emit(self.completed_tasks)
        
        # Hide progress after 3 seconds
        QTimer.singleShot(3000, self._hide_progress)
        
        self.logger.info(f"Processing pipeline completed: {completed_count} successful, {failed_count} failed")
    
    def _hide_progress(self):
        """Hide progress indicators"""
        if hasattr(self.main_window, 'progress_label') and self.main_window.progress_label:
            self.main_window.progress_label.setVisible(False)
        if hasattr(self.main_window, 'progress_bar') and self.main_window.progress_bar:
            self.main_window.progress_bar.setVisible(False)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        total_time = 0
        if self.completed_tasks:
            total_time = sum(
                (task.end_time - task.start_time) for task in self.completed_tasks
                if task.start_time and task.end_time
            )
        
        cache_stats = {}
        if self.image_loader:
            cache_stats = self.image_loader.get_cache_stats()
        
        return {
            'total_tasks': len(self.tasks),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'active': len(self.active_tasks),
            'total_processing_time': total_time,
            'average_time_per_task': total_time / len(self.completed_tasks) if self.completed_tasks else 0,
            'cache_stats': cache_stats,
            'is_processing': self.is_processing
        }


class EnhancedProcessingThread(QThread):
    """Thread for processing individual tasks"""
    
    task_completed = pyqtSignal(object, dict)  # task, results
    task_failed = pyqtSignal(object, str)  # task, error_message
    progress_updated = pyqtSignal(object, float, str)  # task, progress, message
    
    def __init__(self, task: ProcessingTask, image_loader, main_window):
        super().__init__()
        self.task = task
        self.image_loader = image_loader
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run the processing pipeline for a single task"""
        try:
            self.logger.info(f"Starting processing pipeline for {self.task.file_name}")
            
            # Step 1: Load image
            self.progress_updated.emit(self.task, 10, "Loading image...")
            self.task.state = ProcessingState.LOADING
            image_data = self._load_image()
            
            # Step 2: Preprocessing
            self.progress_updated.emit(self.task, 30, "Preprocessing...")
            self.task.state = ProcessingState.PREPROCESSING
            processed_image = self._preprocess_image(image_data)
            
            # Step 3: Model inference (if model is available)
            if hasattr(self.main_window, 'model') and self.main_window.model:
                self.progress_updated.emit(self.task, 60, "Running inference...")
                self.task.state = ProcessingState.INFERENCE
                inference_results = self._run_inference(processed_image)
            else:
                inference_results = None
            
            # Step 4: Post-processing
            self.progress_updated.emit(self.task, 90, "Post-processing...")
            self.task.state = ProcessingState.POSTPROCESSING
            final_results = self._postprocess_results(image_data, processed_image, inference_results)
            
            # Step 5: Complete
            self.progress_updated.emit(self.task, 100, "Complete")
            self.task_completed.emit(self.task, final_results)
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Processing failed for {self.task.file_name}: {error_msg}")
            self.task_failed.emit(self.task, error_msg)
    
    def _load_image(self):
        """Load image using cache if available"""
        if self.image_loader:
            return self.image_loader.load_image(self.task.file_path)
        else:
            # Fallback to direct loading
            import tifffile
            return tifffile.imread(self.task.file_path)
    
    def _preprocess_image(self, image_data):
        """Preprocess the image"""
        # This would contain the actual preprocessing logic
        # For now, return the image as-is
        return image_data
    
    def _run_inference(self, processed_image):
        """Run model inference"""
        # This would contain the actual inference logic
        # For now, return placeholder results
        return {
            'predictions': [0.1, 0.2, 0.3, 0.4],
            'confidence': 0.85
        }
    
    def _postprocess_results(self, original_image, processed_image, inference_results):
        """Post-process the results"""
        results = {
            'file_path': self.task.file_path,
            'file_name': self.task.file_name,
            'image_shape': original_image.shape,
            'processing_timestamp': time.time()
        }
        
        if inference_results:
            results.update(inference_results)
        
        return results