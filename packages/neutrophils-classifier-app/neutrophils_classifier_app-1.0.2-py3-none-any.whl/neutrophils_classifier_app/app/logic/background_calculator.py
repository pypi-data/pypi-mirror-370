"""
Background Calculator - Manages background metrics calculation and CNN inference
Coordinates background threads with proper cancellation and error handling.
"""

import os
import logging
from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import numpy as np

from ..utils.logging_config import get_logger


class BackgroundCalculator(QObject):
    """
    Manages background calculations including metrics calculation and CNN inference.
    Provides thread coordination, cancellation, and error handling.
    """
    
    # Signals for communication with UI
    metrics_calculation_complete = pyqtSignal(int, dict)  # threshold_id, metrics_dict
    inference_complete = pyqtSignal(dict)  # classification_results
    progress_update = pyqtSignal(int, str)  # progress, message
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.logger = get_logger('logic.background_calculator')
        
        # Thread management
        self.active_threads = []
        self.metrics_thread = None
        self.inference_thread = None
        
        # Model and configuration references
        self.model = None
        self.model_config = None
        self.label_encoder_path = None
        
        self.logger.info("BackgroundCalculator initialized")
    
    def set_model_components(self, model=None, model_config=None, label_encoder_path=None):
        """
        Set model components for CNN inference.
        
        Args:
            model: Trained CNN model
            model_config: Model configuration dictionary
            label_encoder_path: Path to label encoder classes
        """
        self.model = model
        self.model_config = model_config
        self.label_encoder_path = label_encoder_path
        
        self.logger.debug("Model components set in BackgroundCalculator")
    
    def start_metrics_calculation(self, polydata1, polydata2):
        """
        Start background geometric metrics calculation.
        
        Args:
            polydata1: VTK polydata for threshold 1
            polydata2: VTK polydata for threshold 2
        """
        try:
            # Cancel existing metrics calculation if running
            self.cancel_metrics_calculations()
            
            # Import here to avoid circular dependencies
            from .threads.background_threads import MetricsCalculationThread
            
            # Create and configure metrics thread
            self.metrics_thread = MetricsCalculationThread(
                polydata1=polydata1,
                polydata2=polydata2,
                parent=self
            )
            
            # Connect thread signals
            self.metrics_thread.metrics_complete.connect(self._on_metrics_complete)
            self.metrics_thread.progress_update.connect(self._on_progress_update)
            self.metrics_thread.error_occurred.connect(self._on_metrics_error)
            self.metrics_thread.finished.connect(self._on_metrics_thread_finished)
            
            # Add to active threads and start
            self.active_threads.append(self.metrics_thread)
            self.metrics_thread.start()
            
            self.logger.info("Started background metrics calculation")
            
        except Exception as e:
            error_msg = f"Error starting metrics calculation: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def start_inference(self, image_data: np.ndarray):
        """
        Start background CNN inference.
        
        Args:
            image_data: Image data for inference
        """
        try:
            # Check if model components are available
            if not all([self.model, self.model_config, self.label_encoder_path]):
                self.logger.warning("Model components not available for inference")
                return
            
            # Cancel existing inference if running
            self.cancel_inference()
            
            # Import here to avoid circular dependencies
            from .threads.model_threads import SingleInferenceThread
            from neutrophils_core.loader.optimized_image_data_generator_3d import OptimizedImageDataGenerator3D
            import pandas as pd
            import tempfile
            from pathlib import Path
            import tifffile

            # Create temporary image file for OptimizedImageDataGenerator3D
            temp_dir = Path(tempfile.mkdtemp())
            temp_image_path = temp_dir / "temp_inference_image.tif"
            tifffile.imwrite(str(temp_image_path), image_data)

            # Create DataFrame for OptimizedImageDataGenerator3D
            relative_path = temp_image_path.name
            inference_df = pd.DataFrame({'filepath': [relative_path]})

            # Get data config from model_config
            data_config = self.model_config.get("data", {})

            # Create OptimizedImageDataGenerator3D (same parameters as inference_pipeline.py)
            datagen = OptimizedImageDataGenerator3D(
                df=inference_df,
                data_dir=temp_dir,
                batch_size=1,  # Single image
                image_size=data_config.get("image_size", 69),
                mip=data_config.get("use_mip", False),
                classes=None,
                shuffle=False,
                train=False,  # No augmentations for inference
                to_fit=False,
                get_paths=True,
                use_tf_data_optimization=True,
                augmentation_config=None,
                intensity_input_percentiles=(1, 99),  # Same as inference_pipeline.py
                intensity_out_range=(0, 255)  # Same as inference_pipeline.py
            )
            
            # Create and configure inference thread
            self.inference_thread = SingleInferenceThread(
                datagen=datagen,
                model=self.model,
                model_config=self.model_config,
                label_encoder_path=self.label_encoder_path,
                parent=self
            )
            
            # Connect thread signals
            self.inference_thread.inference_complete.connect(self._on_inference_complete)
            self.inference_thread.progress_update.connect(self._on_progress_update)
            self.inference_thread.error_occurred.connect(self._on_inference_error)
            self.inference_thread.finished.connect(self._on_inference_thread_finished)
            self.inference_thread.finished.connect(lambda: self._cleanup_temp_dir(temp_dir))
            
            # Add to active threads and start
            self.active_threads.append(self.inference_thread)
            self.logger.debug("Starting inference thread...")
            self.inference_thread.start()
            
            self.logger.info("Started background CNN inference")
            
        except Exception as e:
            error_msg = f"Error starting CNN inference: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def cancel_metrics_calculations(self):
        """Cancel running metrics calculations."""
        try:
            if self.metrics_thread and self.metrics_thread.isRunning():
                self.logger.info("Cancelling metrics calculation")
                self.metrics_thread.cleanup()
                
                if self.metrics_thread in self.active_threads:
                    self.active_threads.remove(self.metrics_thread)
                
                self.metrics_thread = None
                
        except Exception as e:
            self.logger.error(f"Error cancelling metrics calculation: {str(e)}")
    
    def cancel_inference(self):
        """Cancel running CNN inference."""
        try:
            if self.inference_thread and self.inference_thread.isRunning():
                self.logger.info("Cancelling CNN inference")
                self.inference_thread.cleanup()
                
                if self.inference_thread in self.active_threads:
                    self.active_threads.remove(self.inference_thread)
                
                self.inference_thread = None
                
        except Exception as e:
            self.logger.error(f"Error cancelling CNN inference: {str(e)}")
    
    def cancel_all_calculations(self):
        """Cancel all running background calculations."""
        try:
            self.logger.info("Cancelling all background calculations")
            
            # Cancel specific calculations
            self.cancel_metrics_calculations()
            self.cancel_inference()
            
            # Cancel any remaining active threads
            for thread in self.active_threads[:]:  # Copy list to avoid modification during iteration
                if thread and thread.isRunning():
                    try:
                        if hasattr(thread, 'cleanup'):
                            thread.cleanup()
                        elif hasattr(thread, 'cancel'):
                            thread.cancel()
                            thread.quit()
                            thread.wait(500)  # Wait max 0.5 seconds per thread
                    except Exception as e:
                        self.logger.error(f"Error cancelling thread: {str(e)}")
                    finally:
                        if thread in self.active_threads:
                            self.active_threads.remove(thread)
            
            # Clear active threads list
            self.active_threads.clear()
            
            self.logger.info("All background calculations cancelled")
            
        except Exception as e:
            self.logger.error(f"Error cancelling all calculations: {str(e)}")
    
    def cleanup(self):
        """Clean up resources and cancel all operations."""
        try:
            self.cancel_all_calculations()
            
            # Clear references
            self.model = None
            self.model_config = None
            self.label_encoder_path = None
            
            self.logger.info("BackgroundCalculator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def _on_metrics_complete(self, threshold_id: int, metrics_dict: dict):
        """Handle metrics calculation completion."""
        try:
            self.logger.info(f"Metrics calculation complete for threshold {threshold_id}")
            
            # Emit signal for other components (UI updates handled by StreamlinedImageManager)
            self.metrics_calculation_complete.emit(threshold_id, metrics_dict)
            
        except Exception as e:
            self.logger.error(f"Error handling metrics completion: {str(e)}")
    
    def _on_inference_complete(self, classification_results: dict):
        """Handle CNN inference completion."""
        try:
            self.logger.info("CNN inference complete")
            
            # Emit signal for other components (UI updates handled by StreamlinedImageManager)
            self.inference_complete.emit(classification_results)
            
        except Exception as e:
            self.logger.error(f"Error handling inference completion: {str(e)}")
    
    def _on_progress_update(self, progress: int, message: str):
        """Handle progress updates from background threads."""
        try:
            # Forward progress updates to UI
            self.progress_update.emit(progress, message)
            
        except Exception as e:
            self.logger.error(f"Error handling progress update: {str(e)}")
    
    def _on_metrics_error(self, error_message: str):
        """Handle metrics calculation errors."""
        try:
            self.logger.error(f"Metrics calculation error: {error_message}")
            self.error_occurred.emit(f"Metrics calculation failed: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Error handling metrics error: {str(e)}")
    
    def _on_inference_error(self, error_message: str):
        """Handle CNN inference errors."""
        try:
            self.logger.error(f"CNN inference error: {error_message}")
            self.error_occurred.emit(f"CNN inference failed: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Error handling inference error: {str(e)}")
    
    def _on_metrics_thread_finished(self):
        """Handle metrics thread completion."""
        try:
            if self.metrics_thread and self.metrics_thread in self.active_threads:
                self.active_threads.remove(self.metrics_thread)
            
            if self.metrics_thread:
                # Use the cleanup method for proper thread termination
                self.metrics_thread.cleanup()
                self.metrics_thread.deleteLater()
                self.metrics_thread = None
                
            self.logger.debug("Metrics thread cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error in metrics thread cleanup: {str(e)}")
    
    def _on_inference_thread_finished(self):
        """Handle inference thread completion."""
        try:
            if self.inference_thread and self.inference_thread in self.active_threads:
                self.active_threads.remove(self.inference_thread)
            
            if self.inference_thread:
                # Use the cleanup method for proper thread termination
                self.inference_thread.cleanup()
                self.inference_thread.deleteLater()
                self.inference_thread = None
                
            self.logger.debug("Inference thread cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error in inference thread cleanup: {str(e)}")
    
    def _cleanup_temp_dir(self, temp_dir_path):
        """Clean up the temporary directory."""
        try:
            import shutil
            shutil.rmtree(temp_dir_path)
            self.logger.debug(f"Cleaned up temporary directory: {temp_dir_path}")
        except Exception as e:
            self.logger.error(f"Error cleaning up temporary directory {temp_dir_path}: {e}")

    def _update_ui_metrics(self, threshold_id: int, metrics_dict: dict):
        """Update UI with calculated metrics."""
        try:
            # Get metric labels based on threshold
            suffix = f"_{threshold_id}"
            
            # Map of metric keys to UI label names
            metric_mapping = {
                'area': f'labelArea{suffix}',
                'vol': f'labelVol{suffix}',
                'nsi': f'labelNSI{suffix}',
                'sphericity': f'labelSphericity{suffix}',
                'sa_vol_ratio': f'labelSA_Vol_Ratio{suffix}',
                'solidity': f'labelSolidity{suffix}',
                'elongation': f'labelElongation{suffix}',
                'genus': f'labelGenus{suffix}'
            }
            
            # Update UI labels
            for metric_key, label_name in metric_mapping.items():
                if hasattr(self.main_window, label_name) and metric_key in metrics_dict:
                    value = metrics_dict[metric_key]
                    if value is not None and not np.isnan(value):
                        # Format value appropriately
                        if isinstance(value, float):
                            formatted_value = f"{value:.3f}"
                        else:
                            formatted_value = str(value)
                        
                        getattr(self.main_window, label_name).setText(formatted_value)
                    else:
                        getattr(self.main_window, label_name).setText("N/A")
            
            self.logger.debug(f"Updated UI metrics for threshold {threshold_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating UI metrics: {str(e)}")
    
    def _update_ui_classification(self, classification_results: dict):
        """Update UI with classification results."""
        try:
            # Update classification plot if available
            if hasattr(self.main_window, 'update_classification_plot'):
                self.main_window.update_classification_plot(classification_results)
            
            # Update classification labels if available
            if 'predicted_class' in classification_results:
                if hasattr(self.main_window, 'labelPredictedClass'):
                    self.main_window.labelPredictedClass.setText(classification_results['predicted_class'])
            
            if 'confidence' in classification_results:
                if hasattr(self.main_window, 'labelConfidence'):
                    confidence = classification_results['confidence']
                    self.main_window.labelConfidence.setText(f"{confidence:.3f}")
            
            self.logger.debug("Updated UI classification results")
            
        except Exception as e:
            self.logger.error(f"Error updating UI classification: {str(e)}")