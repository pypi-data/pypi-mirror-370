"""
Background Threads - Simplified background calculation threads
Provides MetricsCalculationThread and InferenceThread with proper cancellation.
"""

import os
import time
import numpy as np
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional, Dict, Any

from ...utils.logging_config import get_logger
from .geometry_utils import calculate_metrics_from_polydata

class MetricsCalculationThread(QThread):
    """
    Simplified thread for background geometric metrics calculation.
    Calculates metrics for two polydata objects (threshold1 and threshold2).
    """
    
    # Signals
    metrics_complete = pyqtSignal(int, dict)  # threshold_id, metrics_dict
    progress_update = pyqtSignal(int, str)  # progress, message
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, polydata1, polydata2, parent=None):
        super().__init__(parent)
        self.polydata1 = polydata1
        self.polydata2 = polydata2
        self._cancelled = False
        self.logger = get_logger('logic.background_threads.metrics')
        
    def run(self):
        """Main execution method for metrics calculation."""
        try:
            print("DEBUG METRICS_THREAD: Starting background metrics calculation")
            self.logger.info("Starting background metrics calculation")
            start_time = time.time()
            
            # Check cancellation before starting
            if self._cancelled:
                print("DEBUG METRICS_THREAD: Metrics calculation cancelled before starting")
                self.logger.info("Metrics calculation cancelled before starting")
                return
            
            print("DEBUG METRICS_THREAD: Emitting progress update for threshold 1")
            self.progress_update.emit(10, "Calculating metrics for threshold 1...")
            
            # Calculate metrics for threshold 1
            if self.polydata1 is not None:
                print("DEBUG METRICS_THREAD: Polydata1 available, starting calculation")
                metrics1 = self._calculate_metrics_safe(self.polydata1, 1)
                if self._cancelled:
                    print("DEBUG METRICS_THREAD: Cancelled during threshold 1 calculation")
                    return
                
                if metrics1:
                    print(f"DEBUG METRICS_THREAD: Threshold 1 metrics calculated: {metrics1}")
                    print("DEBUG METRICS_THREAD: About to emit metrics_complete signal for threshold 1")
                    self.metrics_complete.emit(1, metrics1)
                    print("DEBUG METRICS_THREAD: metrics_complete signal emitted for threshold 1")
                    self.progress_update.emit(50, "Metrics for threshold 1 complete")
                else:
                    print("DEBUG METRICS_THREAD: Failed to calculate metrics for threshold 1")
                    self.error_occurred.emit("Failed to calculate metrics for threshold 1")
            else:
                print("DEBUG METRICS_THREAD: Polydata1 is None, skipping threshold 1")
            
            if self._cancelled:
                print("DEBUG METRICS_THREAD: Cancelled before threshold 2")
                return
            
            print("DEBUG METRICS_THREAD: Emitting progress update for threshold 2")
            self.progress_update.emit(60, "Calculating metrics for threshold 2...")
            
            # Calculate metrics for threshold 2
            if self.polydata2 is not None:
                print("DEBUG METRICS_THREAD: Polydata2 available, starting calculation")
                metrics2 = self._calculate_metrics_safe(self.polydata2, 2)
                if self._cancelled:
                    print("DEBUG METRICS_THREAD: Cancelled during threshold 2 calculation")
                    return
                
                if metrics2:
                    print(f"DEBUG METRICS_THREAD: Threshold 2 metrics calculated: {metrics2}")
                    print("DEBUG METRICS_THREAD: About to emit metrics_complete signal for threshold 2")
                    self.metrics_complete.emit(2, metrics2)
                    print("DEBUG METRICS_THREAD: metrics_complete signal emitted for threshold 2")
                    self.progress_update.emit(100, "All metrics calculation complete")
                else:
                    print("DEBUG METRICS_THREAD: Failed to calculate metrics for threshold 2")
                    self.error_occurred.emit("Failed to calculate metrics for threshold 2")
            else:
                print("DEBUG METRICS_THREAD: Polydata2 is None, skipping threshold 2")
            
            total_time = time.time() - start_time
            print(f"DEBUG METRICS_THREAD: Background metrics calculation completed in {total_time:.3f}s")
            self.logger.info(f"Background metrics calculation completed in {total_time:.3f}s")
            
        except Exception as e:
            print(f"DEBUG METRICS_THREAD: Exception in run(): {str(e)}")
            if not self._cancelled:
                error_msg = f"Error in metrics calculation thread: {str(e)}"
                print(f"DEBUG METRICS_THREAD: Emitting error: {error_msg}")
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
    
    def cancel(self):
        """Cancel the metrics calculation."""
        self.logger.info("Cancelling metrics calculation thread")
        self._cancelled = True
    
    def cleanup(self):
        """Clean up thread resources."""
        if self.isRunning():
            self.cancel()
            self.wait(3000)  # Wait up to 3 seconds
            if self.isRunning():
                self.terminate()
                self.wait(1000)  # Wait 1 more second after terminate
    
    def _calculate_metrics_safe(self, polydata, threshold_id: int) -> Optional[Dict[str, float]]:
        """
        Safely calculate metrics for polydata with cancellation checks.
        
        Args:
            polydata: VTK polydata object
            threshold_id: Threshold identifier (1 or 2)
            
        Returns:
            Dictionary of calculated metrics or None if failed/cancelled
        """
        try:
            print(f"DEBUG METRICS_CALC: Starting _calculate_metrics_safe for threshold {threshold_id}")
            if self._cancelled:
                print(f"DEBUG METRICS_CALC: Cancelled before starting threshold {threshold_id}")
                return None
            
            # Import VTK
            print(f"DEBUG METRICS_CALC: Importing VTK for threshold {threshold_id}")
            import vtk
            
            if self._cancelled:
                print(f"DEBUG METRICS_CALC: Cancelled after VTK import for threshold {threshold_id}")
                self.logger.info(f"Metrics calculation cancelled before processing threshold {threshold_id}")
                return None
            
            # Check polydata validity
            if polydata is None:
                print(f"DEBUG METRICS_CALC: Polydata is None for threshold {threshold_id}")
                return None
            
            print(f"DEBUG METRICS_CALC: Polydata for threshold {threshold_id} - Points: {polydata.GetNumberOfPoints()}, Cells: {polydata.GetNumberOfCells()}")
            
            # Use existing geometry utilities function
            print(f"DEBUG METRICS_CALC: Calling calculate_metrics_from_polydata for threshold {threshold_id}")
            self.logger.info(f"Calculating metrics for threshold {threshold_id} isosurface")
            metrics = calculate_metrics_from_polydata(vtk, polydata)
            
            if self._cancelled:
                print(f"DEBUG METRICS_CALC: Cancelled after calculate_metrics_from_polydata for threshold {threshold_id}")
                return None
            
            print(f"DEBUG METRICS_CALC: Metrics calculated for threshold {threshold_id}: {metrics}")
            print(f"DEBUG METRICS_CALC: Metric keys for threshold {threshold_id}: {list(metrics.keys()) if metrics else 'None'}")
            self.logger.debug(f"Calculated metrics for threshold {threshold_id}: {list(metrics.keys()) if metrics else 'None'}")
            return metrics
            
        except Exception as e:
            print(f"DEBUG METRICS_CALC: Exception in _calculate_metrics_safe for threshold {threshold_id}: {str(e)}")
            import traceback
            print(f"DEBUG METRICS_CALC: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Error calculating metrics for threshold {threshold_id}: {str(e)}")
            return None