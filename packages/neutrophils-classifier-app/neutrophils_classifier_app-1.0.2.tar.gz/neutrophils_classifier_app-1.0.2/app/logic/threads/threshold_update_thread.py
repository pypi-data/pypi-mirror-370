"""
Threshold Update Thread - Background processing for VTK isosurface updates when thresholds change
"""
import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional, Tuple
from .vtk_computation_utils import VTKComputationUtils


class ThresholdUpdateThread(QThread):
    """
    Background thread for VTK isosurface recomputation when thresholds change.
    Uses shared VTK computation utilities to avoid code duplication.
    """
    
    # Signals for progress updates and results
    progress_update = pyqtSignal(int, str)  # progress percentage, status message
    vtk_polydata_ready = pyqtSignal(object, object)  # polydata1, polydata2 (for main thread rendering)
    error_occurred = pyqtSignal(str)  # error_message
    update_complete = pyqtSignal(int, int)  # threshold1, threshold2
    
    def __init__(self, image_data: np.ndarray, threshold1: int, threshold2: int, vtk_renderer=None):
        super().__init__()
        self.image_data = image_data
        self.threshold1 = threshold1
        self.threshold2 = threshold2
        self.vtk_renderer = vtk_renderer
        self._stop_requested = False
        
    def run(self):
        """Execute the background threshold update workflow"""
        try:
            # Initial validation (10%)
            if self._stop_requested:
                return
            self.progress_update.emit(10, "Starting threshold update...")
            
            if self.image_data is None or self.image_data.size == 0:
                self.error_occurred.emit("Invalid image data for threshold update")
                return
            
            # Use shared VTK computation utility
            def progress_callback(progress, message):
                # Map progress to 10-90% range, leaving 10% for completion
                adjusted_progress = 10 + (progress * 0.8)
                self.progress_update.emit(int(adjusted_progress), message)
            
            success, polydata1, polydata2 = VTKComputationUtils.compute_isosurfaces_background(
                self.image_data, self.threshold1, self.threshold2, self.vtk_renderer, progress_callback
            )
            
            if self._stop_requested:
                return
            
            if success and polydata1 is not None and polydata2 is not None:
                # Emit polydata for main thread rendering
                self.vtk_polydata_ready.emit(polydata1, polydata2)
                self.update_complete.emit(self.threshold1, self.threshold2)
                self.progress_update.emit(100, "Threshold update complete")
            else:
                error_msg = f"Failed to generate isosurfaces for thresholds T1={self.threshold1}, T2={self.threshold2}"
                self.error_occurred.emit(error_msg)
                self.progress_update.emit(100, "Threshold update failed")
            
        except Exception as e:
            if not self._stop_requested:
                error_msg = f"Error updating thresholds T1={self.threshold1}, T2={self.threshold2}: {str(e)}"
                self.error_occurred.emit(error_msg)
                self.progress_update.emit(100, "Threshold update error")
    
    def stop_gracefully(self):
        """Request the thread to stop gracefully"""
        self._stop_requested = True