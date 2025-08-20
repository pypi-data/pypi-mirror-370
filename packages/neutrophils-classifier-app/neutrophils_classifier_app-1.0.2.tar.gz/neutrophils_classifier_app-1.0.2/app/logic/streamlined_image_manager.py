"""
Streamlined Image Manager - Central coordinator for the new workflow
Handles image selection, loading, rendering, and UI state management
with prevention of concurrent loading operations.
"""
import os
import logging
from typing import List, Optional, Tuple
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import numpy as np
import pandas as pd
import time

from ..utils.logging_config import get_logger
from ..ui.progress_dialog import LoadingProgressDialog
from .threads.streamlined_loading_thread import StreamlinedLoadingThread
from .threads.threshold_update_thread import ThresholdUpdateThread


class StreamlinedImageManager(QObject):
    """
    Central coordinator for the streamlined image processing workflow.
    Manages image selection, loading, rendering, and UI state with
    concurrent loading prevention.
    """
    
    # Signals for communication with UI
    image_loaded = pyqtSignal(str, np.ndarray, tuple)  # file_path, image_data, thresholds
    rendering_completed = pyqtSignal(str)  # status_message
    error_occurred = pyqtSignal(str)  # error_message 
    ui_state_changed = pyqtSignal(bool)  # is_loading
    list_widget_updated = pyqtSignal(list)  # file_paths
    database_updated = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.logger = get_logger('logic.streamlined_image_manager')
        
        # Current state
        self.current_image_path = None
        self.current_image_data = None
        self.is_loading = False
        
        # Background thread management
        self.background_threads = []
        self.loading_thread = None
        self.threshold_update_thread = None
        self.progress_dialog = None
        
        # Components (will be set by main window)
        self.fast_image_loader = None
        self.vtk_renderer = None
        self.secondary_renderers = None
        self.ui_state_manager = None
        self.background_calculator = None
        
        self.logger.info("StreamlinedImageManager initialized")
    
    def set_components(self, fast_image_loader=None, vtk_renderer=None, 
                      secondary_renderers=None, ui_state_manager=None,
                      background_calculator=None):
        """Set component references after they are created"""
        self.fast_image_loader = fast_image_loader
        self.vtk_renderer = vtk_renderer
        self.secondary_renderers = secondary_renderers
        self.ui_state_manager = ui_state_manager
        self.background_calculator = background_calculator
        
        # Connect background calculator signals if available
        if self.background_calculator:
            self._connect_background_calculator_signals()
        
        self.logger.debug("Components set in StreamlinedImageManager")
    
    def select_images(self) -> List[str]:
        """
        Handle image selection via file dialog.
        Returns list of selected image paths.
        """
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self.main_window,
                caption="Select Image Files",
                filter="TIFF (*.tif *.tiff)"
            )
            
            if files:
                self.logger.info(f"Selected {len(files)} image files")
                return files
            else:
                self.logger.debug("No files selected")
                return []
                
        except Exception as e:
            error_msg = f"Error selecting images: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []
    
    def update_list_widget(self, image_paths: List[str]):
        """
        Update main window list widget with new image paths.
        Appends to existing files to maintain loaded images.
        """
        try:
            if not image_paths:
                return
            
            # Get existing files to avoid duplicates
            existing_files = getattr(self.main_window, 'files', [])
            was_list_empty = len(existing_files) == 0
            existing_files_set = set(existing_files)
            
            # Filter out duplicates
            new_files = [f for f in image_paths if f not in existing_files_set]
            
            if not new_files:
                self.logger.debug("No new files to add to list widget")
                return
            
            # Update main window files list
            if not hasattr(self.main_window, 'files'):
                self.main_window.files = []
            self.main_window.files.extend(new_files)
            
            # Update list widget
            if hasattr(self.main_window, 'listWidget'):
                for file_path in new_files:
                    file_name = os.path.basename(file_path)
                    self.main_window.listWidget.addItem(file_name)
            
            # Update database
            self._update_database_with_new_files(new_files)
            
            # Emit signal for UI updates
            self.list_widget_updated.emit(self.main_window.files)
            self.database_updated.emit()
            
            self.logger.info(f"Added {len(new_files)} new files to list widget")
            
            # If the list was empty and we added new files, select the first one
            if was_list_empty and new_files and hasattr(self.main_window, 'listWidget'):
                self.main_window.listWidget.setCurrentRow(0)
                self.logger.info("Auto-selecting first image to trigger loading.")
            
        except Exception as e:
            error_msg = f"Error updating list widget: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def can_load_image(self) -> bool:
        """
        Check if image loading is allowed (not currently loading).
        This prevents concurrent loading operations.
        """
        return not self.is_loading
    
    def load_and_render_image(self, image_path: str):
        """
        Main workflow: load image and render in background thread with progress dialog.
        This method now runs the loading and rendering process in a background thread
        to prevent UI blocking, with a progress dialog for user feedback.
        """
        try:
            # Check if loading is allowed
            if not self.can_load_image():
                self.logger.warning(f"Cannot load image {image_path} - already loading")
                return False
            
            # Validate file path
            if not os.path.exists(image_path):
                error_msg = f"Image file not found: {image_path}"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            # Set loading state
            self.set_ui_loading_state(True)
            
            # Clear previous measurements immediately
            self._clear_measurements()
            
            self.logger.info(f"Starting background loading for: {os.path.basename(image_path)}")
            
            # Create and show progress dialog
            self.progress_dialog = LoadingProgressDialog(
                parent=self.main_window,
                title="Loading Image",
                message=f"Loading {os.path.basename(image_path)}..."
            )
            
            # Connect progress dialog cancel to stop loading
            self.progress_dialog.canceled.connect(self._on_loading_canceled)
            
            # Create and configure loading thread
            self.loading_thread = StreamlinedLoadingThread(
                image_path=image_path,
                fast_image_loader=self.fast_image_loader,
                vtk_renderer=self.vtk_renderer
            )
            
            # Connect thread signals
            self.loading_thread.progress_update.connect(self._on_progress_update)
            self.loading_thread.loading_complete.connect(self._on_loading_complete)
            self.loading_thread.vtk_polydata_ready.connect(self._on_vtk_polydata_ready)
            self.loading_thread.error_occurred.connect(self._on_loading_error)
            self.loading_thread.finished.connect(self._on_thread_finished)
            
            # Show progress dialog and start thread
            self.progress_dialog.show()
            self.loading_thread.start()
            
            return True
            
        except Exception as e:
            # Reset loading state on error
            self.set_ui_loading_state(False)
            error_msg = f"Error starting image load {os.path.basename(image_path)}: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def update_thresholds(self, threshold1: int, threshold2: int):
        """
        Handle threshold slider changes with OPTIMIZED approach.
        SINGLE SURFACE COMPUTATION: Surfaces are computed once during initial loading.
        Only UI controls, secondary renderers, and metrics are updated - NO surface recomputation.
        """
        try:
            if self.current_image_data is None:
                self.logger.warning("No image loaded for threshold update")
                return
            
            # DIAGNOSTIC: Track total threshold update timing
            threshold_start_time = time.time()
            print(f"DEBUG STREAMLINED: Starting OPTIMIZED threshold update T1={threshold1}, T2={threshold2}")
            print(f"DEBUG STREAMLINED: SINGLE SURFACE COMPUTATION - No isosurface recomputation, surfaces computed once during load")
            
            # Start VTK isosurface update in background thread
            self._start_threshold_update_thread(threshold1, threshold2)
            
            # OPTIMIZATION 2: Update only UI threshold displays (lightweight)
            self._update_ui_threshold_displays(threshold1, threshold2)
            
            # OPTIMIZATION 3: Update secondary renderers only (2D slice and histogram) - lightweight operations
            if self.secondary_renderers:
                print(f"DEBUG STREAMLINED: Updating secondary renderers (2D slice/histogram only)")
                secondary_start_time = time.time()
                self.secondary_renderers.update_thresholds(self.current_image_data, threshold1, threshold2)
                secondary_time = time.time() - secondary_start_time
                print(f"DEBUG STREAMLINED: Secondary renderers updated in {secondary_time:.3f}s")
            
            # OPTIMIZATION 4: Cancel existing background calculations and start new metrics calculation only
            # CNN inference is NOT restarted as it doesn't depend on thresholds
            if self.background_calculator:
                self.background_calculator.cancel_metrics_calculations()
                # Start new metrics calculation with new thresholds (no surface recomputation needed)
                QTimer.singleShot(100, lambda: self._start_background_metrics_only(threshold1, threshold2))
            
            # OPTIMIZATION 5: Update database with new thresholds (lightweight)
            self._update_thresholds_in_database(threshold1, threshold2)
            
            total_time = time.time() - threshold_start_time
            print(f"DEBUG STREAMLINED: OPTIMIZED threshold update completed in {total_time:.3f}s (eliminated surface recomputation)")
            self.logger.debug(f"Updated thresholds (optimized): T1={threshold1}, T2={threshold2}")
            
        except Exception as e:
            error_msg = f"Error updating thresholds: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _update_ui_threshold_displays(self, threshold1: int, threshold2: int):
        """Update UI threshold displays without VTK recomputation"""
        try:
            # Update threshold sliders and spinboxes
            if hasattr(self.main_window, 'horizontalSlider_intensity1'):
                self.main_window.horizontalSlider_intensity1.setValue(threshold1)
            
            if hasattr(self.main_window, 'spinBox_intensity1'):
                self.main_window.spinBox_intensity1.setValue(threshold1)
            
            if hasattr(self.main_window, 'horizontalSlider_intensity2'):
                self.main_window.horizontalSlider_intensity2.setValue(threshold2)
            
            if hasattr(self.main_window, 'spinBox_intensity2'):
                self.main_window.spinBox_intensity2.setValue(threshold2)
            
            print(f"DEBUG STREAMLINED: Updated UI threshold displays: T1={threshold1}, T2={threshold2}")
            
        except Exception as e:
            self.logger.error(f"Error updating UI threshold displays: {str(e)}")
    
    def set_ui_loading_state(self, loading: bool):
        """
        Enable/disable UI elements during loading to prevent concurrent operations.
        """
        try:
            self.is_loading = loading
            
            if self.ui_state_manager:
                self.ui_state_manager.set_loading_state(loading)
            else:
                # Fallback direct UI management
                self._set_ui_elements_enabled(not loading)
            
            # Emit signal for other components
            self.ui_state_changed.emit(loading)
            
            self.logger.debug(f"UI loading state set to: {loading}")
            
        except Exception as e:
            self.logger.error(f"Error setting UI loading state: {str(e)}")
    
    def start_background_calculations(self, image_data: np.ndarray, threshold1: int, threshold2: int):
        """
        Start background metrics and inference calculations.
        """
        try:
            if self.background_calculator:
                # Generate polydata for metrics calculation
                polydata1, polydata2 = self._generate_polydata_for_metrics(image_data, threshold1, threshold2)
                
                # Set model components if available
                if hasattr(self.main_window, 'model') and hasattr(self.main_window, 'model_config'):
                    self.background_calculator.set_model_components(
                        model=getattr(self.main_window, 'model', None),
                        model_config=getattr(self.main_window, 'model_config', None),
                        label_encoder_path=getattr(self.main_window, 'label_encoder_path', None)
                    )
                
                # Start background calculations
                self.background_calculator.start_metrics_calculation(polydata1, polydata2)
                self.background_calculator.start_inference(image_data)
                
                self.logger.debug("Started background calculations")
            else:
                self.logger.warning("BackgroundCalculator not available")
                
        except Exception as e:
            self.logger.error(f"Error starting background calculations: {str(e)}")
    
    def _clear_measurements(self):
        """Clear all measurements and show 'calculating...' placeholders"""
        try:
            # Clear geometric metrics in UI using correct label names from mainWindow.ui
            metric_labels = [
                'label_area_1', 'label_vol_1', 'label_nsi_1', 'label_sphericity_1', 'label_sa_vol_ratio_1', 'label_solidity_1', 'label_elongation_1', 'label_genus_1',
                'label_area_2', 'label_vol_2', 'label_nsi_2', 'label_sphericity_2', 'label_sa_vol_ratio_2', 'label_solidity_2', 'label_elongation_2', 'label_genus_2'
            ]
            
            for label_name in metric_labels:
                if hasattr(self.main_window, label_name):
                    getattr(self.main_window, label_name).setText("calculating...")
                    self.logger.debug(f"Set {label_name} to 'calculating...'")
                else:
                    self.logger.warning(f"UI label {label_name} not found during clear")
            
            # Clear classification plot if available
            if hasattr(self.main_window, 'clear_classification_plot'):
                self.main_window.clear_classification_plot()
            
            self.logger.debug("Cleared measurements and set calculating placeholders")
            
        except Exception as e:
            self.logger.error(f"Error clearing measurements: {str(e)}")
    
    def _update_database_with_new_files(self, new_files: List[str]):
        """Update database with new file entries"""
        try:
            if not hasattr(self.main_window, 'result_db'):
                return
            
            records_to_add = []
            for file_path in new_files:
                filename = os.path.basename(file_path)
                new_record = {
                    'ImageName': filename,
                    'Path': file_path,
                    'ManualAnnotation': '', 'Predicted_Class': '', 'Model': '',
                    'ClassProb_M': np.nan, 'ClassProb_MM': np.nan, 'ClassProb_BN': np.nan, 'ClassProb_SN': np.nan, 'MaturationScore': np.nan,
                    'Area_1': np.nan, 'Vol_1': np.nan, 'NSI_1': np.nan, 'Sphericity_1': np.nan, 'SA_Vol_Ratio_1': np.nan, 'Solidity_1': np.nan, 'Elongation_1': np.nan, 'Genus_1': np.nan,
                    'Area_2': np.nan, 'Vol_2': np.nan, 'NSI_2': np.nan, 'Sphericity_2': np.nan, 'SA_Vol_Ratio_2': np.nan, 'Solidity_2': np.nan, 'Elongation_2': np.nan, 'Genus_2': np.nan,
                    'threshold1': np.nan, 'threshold2': np.nan,
                }
                records_to_add.append(new_record)
            
            if records_to_add:
                self.main_window.result_db = pd.concat([self.main_window.result_db, pd.DataFrame(records_to_add)], ignore_index=True)
                self.logger.debug(f"Added {len(records_to_add)} records to database")
                
        except Exception as e:
            self.logger.error(f"Error updating database: {str(e)}")
    
    def _update_ui_controls(self, image_data: np.ndarray, threshold1: int, threshold2: int):
        """Update UI controls with image data and thresholds"""
        try:
            # Get data type maximum
            if image_data.dtype == np.uint8:
                data_max = 255
            elif image_data.dtype == np.uint16:
                data_max = 65535
            else:
                data_max = int(np.max(image_data))
            
            # Update threshold sliders
            if hasattr(self.main_window, 'horizontalSlider_intensity1'):
                self.main_window.horizontalSlider_intensity1.blockSignals(True)
                self.main_window.horizontalSlider_intensity1.setRange(1, data_max)
                self.main_window.horizontalSlider_intensity1.setValue(threshold1)
                self.main_window.horizontalSlider_intensity1.blockSignals(False)

            if hasattr(self.main_window, 'spinBox_intensity1'):
                self.main_window.spinBox_intensity1.blockSignals(True)
                self.main_window.spinBox_intensity1.setRange(1, data_max)
                self.main_window.spinBox_intensity1.setValue(threshold1)
                self.main_window.spinBox_intensity1.blockSignals(False)

            if hasattr(self.main_window, 'horizontalSlider_intensity2'):
                self.main_window.horizontalSlider_intensity2.blockSignals(True)
                self.main_window.horizontalSlider_intensity2.setRange(1, data_max)
                self.main_window.horizontalSlider_intensity2.setValue(threshold2)
                self.main_window.horizontalSlider_intensity2.blockSignals(False)

            if hasattr(self.main_window, 'spinBox_intensity2'):
                self.main_window.spinBox_intensity2.blockSignals(True)
                self.main_window.spinBox_intensity2.setRange(1, data_max)
                self.main_window.spinBox_intensity2.setValue(threshold2)
                self.main_window.spinBox_intensity2.blockSignals(False)
            
            # Update slice slider
            if image_data.ndim >= 3 and hasattr(self.main_window, 'verticalScrollBarSlide'):
                z_max = image_data.shape[0] - 1
                mid_slice = z_max // 2
                self.main_window.verticalScrollBarSlide.setRange(0, z_max)
                self.main_window.verticalScrollBarSlide.setValue(mid_slice)
            
            self.logger.debug(f"Updated UI controls: range 1-{data_max}, T1={threshold1}, T2={threshold2}")
            
        except Exception as e:
            self.logger.error(f"Error updating UI controls: {str(e)}")
    
    def _start_secondary_rendering(self, image_data: np.ndarray, threshold1: int, threshold2: int):
        """Start secondary rendering (2D slice and histogram)"""
        try:
            if self.secondary_renderers:
                # Get current slice
                z_slice = 0
                if image_data.ndim >= 3:
                    z_slice = image_data.shape[0] // 2
                    if hasattr(self.main_window, 'verticalScrollBarSlide'):
                        z_slice = self.main_window.verticalScrollBarSlide.value()
                
                self.secondary_renderers.render_2d_slice(image_data, z_slice, (threshold1, threshold2))
                self.secondary_renderers.render_histogram(image_data, (threshold1, threshold2))
                
                self.logger.debug("Secondary rendering completed")
            
        except Exception as e:
            self.logger.error(f"Error in secondary rendering: {str(e)}")
    
    def _start_background_metrics_only(self, threshold1: int, threshold2: int):
        """Start background metrics calculation only (for threshold updates)"""
        try:
            if self.background_calculator and self.current_image_data is not None:
                polydata1, polydata2 = self._generate_polydata_for_metrics(self.current_image_data, threshold1, threshold2)
                self.background_calculator.start_metrics_calculation(polydata1, polydata2)
                self.logger.debug("Started background metrics calculation for threshold update")
                
        except Exception as e:
            self.logger.error(f"Error starting background metrics: {str(e)}")
    
    def _generate_polydata_for_metrics(self, image_data: np.ndarray, threshold1: int, threshold2: int):
        """Generate VTK polydata for metrics calculation"""
        try:
            # Try to get polydata from VTK renderer if available
            if self.vtk_renderer and hasattr(self.vtk_renderer, 'get_polydata_for_thresholds'):
                return self.vtk_renderer.get_polydata_for_thresholds(threshold1, threshold2)
            
            # If VTK renderer doesn't provide polydata, try to generate using VTK directly
            try:
                import vtk
                from vtkmodules.util import numpy_support
                
                # Create VTK image data
                vtk_data = vtk.vtkImageData()
                vtk_data.SetDimensions(image_data.shape)
                vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_SHORT, 1)
                flat_data = image_data.flatten()
                vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT)
                vtk_data.GetPointData().SetScalars(vtk_array)
                
                # Generate polydata for threshold 1
                contour1 = vtk.vtkMarchingCubes()
                contour1.SetInputData(vtk_data)
                contour1.SetValue(0, threshold1)
                contour1.Update()
                polydata1 = contour1.GetOutput()
                
                # Generate polydata for threshold 2
                contour2 = vtk.vtkMarchingCubes()
                contour2.SetInputData(vtk_data)
                contour2.SetValue(0, threshold2)
                contour2.Update()
                polydata2 = contour2.GetOutput()
                
                return polydata1, polydata2
                
            except ImportError:
                self.logger.warning("VTK not available for polydata generation")
                return None, None
            
        except Exception as e:
            self.logger.error(f"Error generating polydata: {str(e)}")
            return None, None
    
    def _update_thresholds_in_database(self, threshold1: int, threshold2: int):
        """Update threshold values in database for current image"""
        try:
            if (self.current_image_path and hasattr(self.main_window, 'result_db') and 
                not self.main_window.result_db.empty):
                
                mask = self.main_window.result_db['Path'] == self.current_image_path
                if mask.any():
                    self.main_window.result_db.loc[mask, 'threshold1'] = threshold1
                    self.main_window.result_db.loc[mask, 'threshold2'] = threshold2
                    self.logger.debug(f"Updated thresholds in database: T1={threshold1}, T2={threshold2}")
                    
        except Exception as e:
            self.logger.error(f"Error updating thresholds in database: {str(e)}")
    
    def _set_ui_elements_enabled(self, enabled: bool):
        """Fallback method to enable/disable UI elements directly"""
        try:
            # Disable/enable list widget
            if hasattr(self.main_window, 'listWidget'):
                self.main_window.listWidget.setEnabled(enabled)
            
            # Disable/enable image selection buttons
            if hasattr(self.main_window, 'pushButton_Images'):
                self.main_window.pushButton_Images.setEnabled(enabled)
            
            if hasattr(self.main_window, 'pushButton_ImageFolder'):
                self.main_window.pushButton_ImageFolder.setEnabled(enabled)
            
            # Show/hide loading indicator
            if hasattr(self.main_window, 'progress_label'):
                if not enabled:
                    self.main_window.progress_label.setText("Loading image...")
                    self.main_window.progress_label.setVisible(True)
                else:
                    self.main_window.progress_label.setText("Ready")
                    
        except Exception as e:
            self.logger.error(f"Error setting UI elements enabled state: {str(e)}")
    
    def cleanup(self):
        """Clean up resources and cancel background operations"""
        try:
            # Cancel background calculations
            if self.background_calculator:
                self.background_calculator.cancel_all_calculations()
            
            # Clear current state
            self.current_image_path = None
            self.current_image_data = None
            self.is_loading = False
            
            # Clear background threads
            self.background_threads.clear()
            
            self.logger.info("StreamlinedImageManager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def _fallback_load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Fallback image loading method when FastImageLoader is not available.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image data as numpy array, or None if loading failed
        """
        try:
            print(f"DEBUG STREAMLINED: Using fallback image loading for {image_path}")
            
            # Try tifffile first (most common format)
            if image_path.lower().endswith(('.tif', '.tiff')):
                try:
                    import tifffile
                    image_data = tifffile.imread(image_path)
                    print(f"DEBUG STREAMLINED: Fallback loaded via tifffile: shape {image_data.shape}")
                    return image_data
                except ImportError:
                    print("DEBUG STREAMLINED: tifffile not available")
                except Exception as e:
                    print(f"DEBUG STREAMLINED: tifffile loading failed: {e}")
            
            # Try imageio as fallback
            try:
                import imageio
                image_data = imageio.imread(image_path)
                print(f"DEBUG STREAMLINED: Fallback loaded via imageio: shape {image_data.shape}")
                return image_data
            except ImportError:
                print("DEBUG STREAMLINED: imageio not available")
            except Exception as e:
                print(f"DEBUG STREAMLINED: imageio loading failed: {e}")
            
            # Try PIL as last resort
            try:
                from PIL import Image
                import numpy as np
                pil_image = Image.open(image_path)
                image_data = np.array(pil_image)
                print(f"DEBUG STREAMLINED: Fallback loaded via PIL: shape {image_data.shape}")
                return image_data
            except ImportError:
                print("DEBUG STREAMLINED: PIL not available")
            except Exception as e:
                print(f"DEBUG STREAMLINED: PIL loading failed: {e}")
            
            print("DEBUG STREAMLINED: All fallback image loading methods failed")
            return None
            
        except Exception as e:
            self.logger.error(f"Error in fallback image loading: {str(e)}")
            return None
    
    def _fallback_calculate_thresholds(self, image_data: np.ndarray) -> Tuple[int, int]:
        """
        Fallback threshold calculation when FastImageLoader is not available.
        
        Args:
            image_data: Image data as numpy array
            
        Returns:
            Tuple of (threshold1, threshold2)
        """
        try:
            print(f"DEBUG STREAMLINED: Using fallback threshold calculation")
            print(f"DEBUG STREAMLINED: Image range: [{np.min(image_data)}, {np.max(image_data)}]")
            
            # Threshold1: Mean intensity (primary threshold for nucleus)
            mean_val = np.mean(image_data)
            threshold1 = int(np.round(mean_val))
            
            # Threshold2: 2nd percentile (secondary threshold for membrane/background)
            percentile_2_val = np.percentile(image_data, 2)
            threshold2 = int(np.round(percentile_2_val))
            
            # Ensure thresholds are within valid range
            data_min = int(np.min(image_data))
            data_max = int(np.max(image_data))
            
            threshold1 = max(1, min(threshold1, data_max))
            threshold2 = max(1, min(threshold2, data_max))
            
            # Ensure threshold1 >= threshold2 (logical ordering)
            if threshold1 < threshold2:
                threshold1, threshold2 = threshold2, threshold1
            
            print(f"DEBUG STREAMLINED: Fallback calculated thresholds - T1: {threshold1} (mean), T2: {threshold2} (2nd percentile)")
            print(f"DEBUG STREAMLINED: Image stats - mean: {mean_val:.1f}, 2nd percentile: {percentile_2_val:.1f}")
            
            return threshold1, threshold2
            
        except Exception as e:
            self.logger.error(f"Error in fallback threshold calculation: {str(e)}")
            # Return safe default values
            return 100, 50
        
    def _on_progress_update(self, progress: int, message: str):
        """Handle progress updates from loading thread"""
        try:
            if self.progress_dialog and not self.progress_dialog.was_canceled:
                self.progress_dialog.update_progress(progress, message)
        except Exception as e:
            self.logger.error(f"DEBUG STREAMLINED: Error updating progress: {str(e)}")
    
    def _on_loading_complete(self, image_path: str, image_data: np.ndarray, 
                           threshold1: int, threshold2: int, vtk_success: bool):
        """Handle successful completion of background loading"""
        try:
            # Store current state
            self.current_image_path = image_path
            self.current_image_data = image_data
            
            # Update main window compatibility
            self.main_window.img = image_data
            
            # Update UI controls
            self._update_ui_controls(image_data, threshold1, threshold2)
            
            # Start secondary rendering (non-blocking)
            if self.secondary_renderers:
                QTimer.singleShot(50, lambda: self._start_secondary_rendering(image_data, threshold1, threshold2))
            
            # Start background calculations
            QTimer.singleShot(100, lambda: self.start_background_calculations(image_data, threshold1, threshold2))
            
            # Emit signals with thresholds
            self.image_loaded.emit(image_path, image_data, (threshold1, threshold2))
            self.rendering_completed.emit(f"Image loaded: {os.path.basename(image_path)}")
            
            self.logger.info(f"DEBUG STREAMLINED: Successfully loaded and rendered: {os.path.basename(image_path)}")
            
        except Exception as e:
            error_msg = f"DEBUG STREAMLINED: Error in loading completion: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _on_loading_error(self, error_message: str):
        """Handle errors from loading thread"""
        try:
            self.logger.error(f"DEBUG STREAMLINED: Loading thread error: {error_message}")
            self.error_occurred.emit(error_message)
        except Exception as e:
            self.logger.error(f"DEBUG STREAMLINED: Error handling loading error: {str(e)}")
    
    def _on_thread_finished(self):
        """
        Handle loading thread completion (success or failure).
        This method ensures the progress dialog is closed and resources are cleaned up.
        """
        try:
            # Close progress dialog - this is where the dialog gets closed!
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
            
            # Reset loading state
            self.set_ui_loading_state(False)
            
            # Clean up thread reference
            if self.loading_thread:
                self.loading_thread.deleteLater()
                self.loading_thread = None
                
        except Exception as e:
            self.logger.error(f"DEBUG STREAMLINED: Error in thread cleanup: {str(e)}")
    
    def _on_loading_canceled(self):
        """Handle progress dialog cancellation"""
        try:
            self.logger.info("DEBUG STREAMLINED: Loading canceled by user")
            
            # Stop the loading thread gracefully
            if self.loading_thread:
                self.loading_thread.stop_gracefully()
            
            # Reset loading state
            self.set_ui_loading_state(False)
            
        except Exception as e:
            self.logger.error(f"DEBUG STREAMLINED: Error handling loading cancellation: {str(e)}")
    
    def _on_vtk_polydata_ready(self, polydata1, polydata2):
        """
        Handle VTK polydata ready signal from background thread.
        This method runs in the main thread and safely performs UI rendering.
        """
        try:
            self.logger.debug("DEBUG STREAMLINED: Received VTK polydata from background thread")
            
            if self.vtk_renderer and hasattr(self.vtk_renderer, 'render_polydata_to_ui'):
                # Use the thread-safe rendering method
                success = self.vtk_renderer.render_polydata_to_ui(polydata1, polydata2)
                if success:
                    self.logger.info("DEBUG STREAMLINED: VTK polydata rendered successfully in main thread")
                else:
                    self.logger.error("DEBUG STREAMLINED: VTK polydata rendering failed")
            else:
                self.logger.warning("DEBUG STREAMLINED: VTK renderer not available or missing render_polydata_to_ui method")
                
        except Exception as e:
            error_msg = f"DEBUG STREAMLINED: Error rendering VTK polydata in main thread: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _start_threshold_update_thread(self, threshold1: int, threshold2: int):
        """
        Start the threshold update thread for VTK isosurface recomputation.
        Connects progress and polydata ready signals to main window.
        """
        try:
            # Cancel any existing threshold update thread
            if self.threshold_update_thread is not None:
                self.threshold_update_thread.stop_gracefully()
                self.threshold_update_thread.quit()
                self.threshold_update_thread.wait()
                self.threshold_update_thread = None

            # Create and start new thread
            if self.current_image_data is None:
                self.logger.warning("Cannot start threshold update thread: no image data.")
                return

            self.threshold_update_thread = ThresholdUpdateThread(
                self.current_image_data, threshold1, threshold2, self.vtk_renderer
            )
            
            # Connect thread signals
            self.threshold_update_thread.progress_update.connect(self._on_threshold_progress_update)
            self.threshold_update_thread.vtk_polydata_ready.connect(self._on_vtk_polydata_ready)
            self.threshold_update_thread.error_occurred.connect(self._on_threshold_error)
            self.threshold_update_thread.update_complete.connect(self._on_threshold_update_complete)
            self.threshold_update_thread.finished.connect(self._on_threshold_thread_finished)
            
            # Start the thread
            self.threshold_update_thread.start()
            
            # Update main window status
            if hasattr(self.main_window, 'progress_label'):
                self.main_window.progress_label.setText("Updating isosurfaces...")
                self.main_window.progress_label.setVisible(True)
                
            self.logger.debug(f"Started threshold update thread for T1={threshold1}, T2={threshold2}")

        except Exception as e:
            error_msg = f"Error starting threshold update thread: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _on_threshold_progress_update(self, progress: int, message: str):
        """Handle progress updates from threshold update thread"""
        try:
            # Update main window progress bar and status label
            if hasattr(self.main_window, 'progressBar'):
                self.main_window.progressBar.setValue(progress)
            if hasattr(self.main_window, 'progress_label'):
                self.main_window.progress_label.setText(message)
            
        except Exception as e:
            self.logger.error(f"Error updating threshold progress: {str(e)}")
    
    def _on_threshold_error(self, error_message: str):
        """Handle errors from threshold update thread"""
        try:
            self.logger.error(f"Threshold update thread error: {error_message}")
            self.error_occurred.emit(error_message)
            
            # Reset progress UI
            if hasattr(self.main_window, 'progress_label'):
                self.main_window.progress_label.setText("Threshold update failed")
                
        except Exception as e:
            self.logger.error(f"Error handling threshold update error: {str(e)}")
    
    def _on_threshold_update_complete(self, threshold1: int, threshold2: int):
        """Handle successful completion of threshold update"""
        try:
            self.logger.info(f"Threshold update completed: T1={threshold1}, T2={threshold2}")
            
            # Reset progress UI
            if hasattr(self.main_window, 'progress_label'):
                self.main_window.progress_label.setText("Ready")
                
        except Exception as e:
            self.logger.error(f"Error handling threshold update completion: {str(e)}")
    
    def _on_threshold_thread_finished(self):
        """Handle threshold update thread completion (success or failure)"""
        try:
            # Clean up thread reference
            if self.threshold_update_thread:
                self.threshold_update_thread.deleteLater()
                self.threshold_update_thread = None
                
            # Hide progress indicators
            if hasattr(self.main_window, 'progressBar'):
                self.main_window.progressBar.setValue(0)
            if hasattr(self.main_window, 'progress_label'):
                self.main_window.progress_label.setVisible(False)
                
        except Exception as e:
            self.logger.error(f"Error in threshold thread cleanup: {str(e)}")
    
    def _connect_background_calculator_signals(self):
        """Connect background calculator signals to handle results"""
        try:
            if self.background_calculator:
                # Connect signals for metrics completion
                self.background_calculator.metrics_calculation_complete.connect(self._on_background_metrics_complete)
                
                # Connect signals for inference completion
                self.background_calculator.inference_complete.connect(self._on_background_inference_complete)
                
                # Connect progress and error signals
                self.background_calculator.progress_update.connect(self._on_background_progress_update)
                self.background_calculator.error_occurred.connect(self._on_background_error)
                
                self.logger.debug("Connected background calculator signals")
            
        except Exception as e:
            self.logger.error(f"Error connecting background calculator signals: {str(e)}")
    
    def _on_background_metrics_complete(self, threshold_id: int, metrics_dict: dict):
        """Handle background metrics calculation completion"""
        try:
            print(f"DEBUG STREAMLINED_MGR: _on_background_metrics_complete called for threshold {threshold_id}")
            print(f"DEBUG STREAMLINED_MGR: Received metrics: {metrics_dict}")
            self.logger.info(f"Background metrics complete for threshold {threshold_id}")
            
            # Update UI metrics display
            print("DEBUG STREAMLINED_MGR: About to update metrics display")
            self._update_metrics_display(threshold_id, metrics_dict)
            print("DEBUG STREAMLINED_MGR: Metrics display update completed")
            
            # Update database with calculated metrics
            print("DEBUG STREAMLINED_MGR: About to update metrics in database")
            self._update_metrics_in_database(threshold_id, metrics_dict)
            print("DEBUG STREAMLINED_MGR: Database update completed")
            
            # Update feature windows if available
            print("DEBUG STREAMLINED_MGR: Checking for update_feature_windows method")
            if hasattr(self.main_window, 'update_feature_windows'):
                print("DEBUG STREAMLINED_MGR: Calling update_feature_windows")
                self.main_window.update_feature_windows()
                print("DEBUG STREAMLINED_MGR: update_feature_windows completed")
            else:
                print("DEBUG STREAMLINED_MGR: update_feature_windows method not found")
            
            print(f"DEBUG STREAMLINED_MGR: _on_background_metrics_complete finished for threshold {threshold_id}")
            
        except Exception as e:
            print(f"DEBUG STREAMLINED_MGR: Exception in _on_background_metrics_complete: {str(e)}")
            import traceback
            print(f"DEBUG STREAMLINED_MGR: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Error handling background metrics completion: {str(e)}")
    
    def _on_background_inference_complete(self, classification_results: dict):
        """Handle background CNN inference completion"""
        try:
            self.logger.info("Background inference complete")
            
            # Update classification plot display
            self._update_classification_plot(classification_results)
            
            # Update database with classification results
            self._update_classification_in_database(classification_results)
            
            # Update feature windows if available
            if hasattr(self.main_window, 'update_feature_windows'):
                self.main_window.update_feature_windows()
            
        except Exception as e:
            self.logger.error(f"Error handling background inference completion: {str(e)}")
    
    def _on_background_progress_update(self, progress: int, message: str):
        """Handle background calculation progress updates"""
        try:
            # Update status in main window if available
            if hasattr(self.main_window, 'statusbar'):
                self.main_window.statusbar.showMessage(f"Background: {message}")
                
        except Exception as e:
            self.logger.error(f"Error handling background progress update: {str(e)}")
    
    def _on_background_error(self, error_message: str):
        """Handle background calculation errors"""
        try:
            self.logger.error(f"Background calculation error: {error_message}")
            
            # Display error in UI elements
            self._display_calculation_error(error_message)
            
            # Show error in status bar if available
            if hasattr(self.main_window, 'statusbar'):
                self.main_window.statusbar.showMessage(f"Background error: {error_message}")
                
            # Emit error signal for other components
            self.error_occurred.emit(f"Background calculation: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Error handling background error: {str(e)}")
    
    def _update_metrics_in_database(self, threshold_id: int, metrics_dict: dict):
        """Update database with calculated metrics"""
        try:
            print(f"DEBUG STREAMLINED_MGR: _update_metrics_in_database called for threshold {threshold_id}")
            print(f"DEBUG STREAMLINED_MGR: Database update metrics: {metrics_dict}")
            
            if (self.current_image_path and hasattr(self.main_window, 'result_db') and
                not self.main_window.result_db.empty):
                
                print(f"DEBUG STREAMLINED_MGR: Current image path: {self.current_image_path}")
                print(f"DEBUG STREAMLINED_MGR: Database has {len(self.main_window.result_db)} rows")
                
                mask = self.main_window.result_db['Path'] == self.current_image_path
                print(f"DEBUG STREAMLINED_MGR: Found {mask.sum()} matching rows in database")
                
                if mask.any():
                    # Update metrics in database with correct column mapping
                    suffix = f"_{threshold_id}"
                    print(f"DEBUG STREAMLINED_MGR: Using database column suffix: {suffix}")
                    
                    # Proper mapping from metric keys to database column names
                    metric_to_column_mapping = {
                        'area': 'Area',
                        'vol': 'Vol',
                        'nsi': 'NSI',
                        'sphericity': 'Sphericity',
                        'sa_vol_ratio': 'SA_Vol_Ratio',
                        'solidity': 'Solidity',
                        'elongation': 'Elongation',
                        'genus': 'Genus'
                    }
                    
                    print(f"DEBUG STREAMLINED_MGR: Database column mapping: {metric_to_column_mapping}")
                    print(f"DEBUG STREAMLINED_MGR: Available database columns: {list(self.main_window.result_db.columns)}")
                    
                    for metric_key, value in metrics_dict.items():
                        print(f"DEBUG STREAMLINED_MGR: Processing database update for {metric_key} = {value}")
                        if metric_key in metric_to_column_mapping:
                            db_column = f"{metric_to_column_mapping[metric_key]}{suffix}"
                            print(f"DEBUG STREAMLINED_MGR: Looking for database column: {db_column}")
                            if db_column in self.main_window.result_db.columns:
                                self.main_window.result_db.loc[mask, db_column] = value
                                print(f"DEBUG STREAMLINED_MGR: Updated database column {db_column} = {value}")
                                self.logger.debug(f"Updated database column {db_column} = {value}")
                            else:
                                print(f"DEBUG STREAMLINED_MGR: Database column {db_column} not found")
                                self.logger.warning(f"Database column {db_column} not found")
                        else:
                            print(f"DEBUG STREAMLINED_MGR: Unknown metric key: {metric_key}")
                            self.logger.warning(f"Unknown metric key: {metric_key}")
                    
                    print(f"DEBUG STREAMLINED_MGR: Database update completed for threshold {threshold_id}")
                    self.logger.debug(f"Updated metrics in database for threshold {threshold_id}")
                    
                    # Emit database updated signal for UI refresh
                    print("DEBUG STREAMLINED_MGR: About to emit database_updated signal")
                    self.database_updated.emit()
                    print("DEBUG STREAMLINED_MGR: database_updated signal emitted")
                else:
                    print(f"DEBUG STREAMLINED_MGR: No matching rows found in database for path: {self.current_image_path}")
            else:
                print("DEBUG STREAMLINED_MGR: Database update conditions not met")
                print(f"DEBUG STREAMLINED_MGR: current_image_path: {self.current_image_path}")
                print(f"DEBUG STREAMLINED_MGR: has result_db: {hasattr(self.main_window, 'result_db')}")
                if hasattr(self.main_window, 'result_db'):
                    print(f"DEBUG STREAMLINED_MGR: result_db empty: {self.main_window.result_db.empty}")
                    
        except Exception as e:
            print(f"DEBUG STREAMLINED_MGR: Exception in _update_metrics_in_database: {str(e)}")
            import traceback
            print(f"DEBUG STREAMLINED_MGR: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Error updating metrics in database: {str(e)}")
    
    def _update_classification_in_database(self, classification_results: dict):
        """Update database with classification results"""
        try:
            if (self.current_image_path and hasattr(self.main_window, 'result_db') and
                not self.main_window.result_db.empty):
                
                mask = self.main_window.result_db['Path'] == self.current_image_path
                if mask.any():
                    # Ensure Predicted_Class column exists
                    if 'Predicted_Class' not in self.main_window.result_db.columns:
                        self.main_window.result_db['Predicted_Class'] = ''
                    
                    # Update classification results in database
                    if 'predicted_class' in classification_results:
                        self.main_window.result_db.loc[mask, 'Predicted_Class'] = classification_results['predicted_class']
                        # Also update Model column for backward compatibility
                        self.main_window.result_db.loc[mask, 'Model'] = classification_results['predicted_class']
                    
                    if 'confidence' in classification_results:
                        self.main_window.result_db.loc[mask, 'MaturationScore'] = classification_results['confidence']
                    
                    if 'probabilities' in classification_results:
                        probabilities = classification_results['probabilities']
                        if len(probabilities) >= 4:
                            self.main_window.result_db.loc[mask, 'ClassProb_M'] = probabilities[0]
                            self.main_window.result_db.loc[mask, 'ClassProb_MM'] = probabilities[1]
                            self.main_window.result_db.loc[mask, 'ClassProb_BN'] = probabilities[2]
                            self.main_window.result_db.loc[mask, 'ClassProb_SN'] = probabilities[3]
                    
                    self.logger.debug("Updated classification results in database")
                    
        except Exception as e:
            self.logger.error(f"Error updating classification in database: {str(e)}")
    
    def _update_metrics_display(self, threshold_id: int, metrics_dict: dict):
        """Update UI metrics display when background calculations complete"""
        try:
            print(f"DEBUG STREAMLINED_MGR: _update_metrics_display called for threshold {threshold_id}")
            print(f"DEBUG STREAMLINED_MGR: Metrics to display: {metrics_dict}")
            
            # Use geometry calculator to update UI if available
            if hasattr(self.main_window, 'geometry_calculator') and self.main_window.geometry_calculator:
                print("DEBUG STREAMLINED_MGR: Using geometry_calculator for UI update")
                suffix = f"_{threshold_id}"
                self.main_window.geometry_calculator.update_ui_with_metrics(metrics_dict, suffix)
                print(f"DEBUG STREAMLINED_MGR: geometry_calculator.update_ui_with_metrics completed for threshold {threshold_id}")
                self.logger.debug(f"Updated metrics display for threshold {threshold_id}")
            else:
                print("DEBUG STREAMLINED_MGR: geometry_calculator not available, using direct label update")
                # Fallback: Update metric labels directly
                self._update_metric_labels_directly(threshold_id, metrics_dict)
                print("DEBUG STREAMLINED_MGR: Direct label update completed")
                
        except Exception as e:
            print(f"DEBUG STREAMLINED_MGR: Exception in _update_metrics_display: {str(e)}")
            import traceback
            print(f"DEBUG STREAMLINED_MGR: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Error updating metrics display: {str(e)}")
    
    def _update_metric_labels_directly(self, threshold_id: int, metrics_dict: dict):
        """Fallback method to update metric labels directly using correct UI label names"""
        try:
            print(f"DEBUG STREAMLINED_MGR: _update_metric_labels_directly called for threshold {threshold_id}")
            print(f"DEBUG STREAMLINED_MGR: Metrics dict keys: {list(metrics_dict.keys())}")
            
            # Proper mapping from metric keys to exact UI label names from mainWindow.ui
            metric_to_label_mapping = {
                'area': f'label_area_{threshold_id}',
                'vol': f'label_vol_{threshold_id}',
                'nsi': f'label_nsi_{threshold_id}',
                'sphericity': f'label_sphericity_{threshold_id}',
                'sa_vol_ratio': f'label_sa_vol_ratio_{threshold_id}',
                'solidity': f'label_solidity_{threshold_id}',
                'elongation': f'label_elongation_{threshold_id}',
                'genus': f'label_genus_{threshold_id}'
            }
            
            print(f"DEBUG STREAMLINED_MGR: Label mapping: {metric_to_label_mapping}")
            
            for metric_key, value in metrics_dict.items():
                print(f"DEBUG STREAMLINED_MGR: Processing metric {metric_key} = {value}")
                if metric_key in metric_to_label_mapping:
                    label_name = metric_to_label_mapping[metric_key]
                    print(f"DEBUG STREAMLINED_MGR: Looking for UI label: {label_name}")
                    if hasattr(self.main_window, label_name):
                        label = getattr(self.main_window, label_name)
                        if value is not None and not np.isnan(value):
                            formatted_value = f"{value:.4f}"
                            label.setText(formatted_value)
                            print(f"DEBUG STREAMLINED_MGR: Updated UI label {label_name} = {formatted_value}")
                            self.logger.debug(f"Updated UI label {label_name} = {value:.4f}")
                        else:
                            label.setText("N/A")
                            print(f"DEBUG STREAMLINED_MGR: Updated UI label {label_name} = N/A")
                            self.logger.debug(f"Updated UI label {label_name} = N/A")
                    else:
                        print(f"DEBUG STREAMLINED_MGR: UI label {label_name} not found on main_window")
                        self.logger.warning(f"UI label {label_name} not found")
                else:
                    print(f"DEBUG STREAMLINED_MGR: Unknown metric key: {metric_key}")
                    self.logger.warning(f"Unknown metric key for UI update: {metric_key}")
                        
            print(f"DEBUG STREAMLINED_MGR: Direct label update completed for threshold {threshold_id}")
            self.logger.debug(f"Updated metric labels directly for threshold {threshold_id}")
            
        except Exception as e:
            print(f"DEBUG STREAMLINED_MGR: Exception in _update_metric_labels_directly: {str(e)}")
            import traceback
            print(f"DEBUG STREAMLINED_MGR: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Error updating metric labels directly: {str(e)}")
    
    def _update_classification_plot(self, classification_results: dict):
        """Update classification plot when background inference completes"""
        try:
            # Use the existing _update_inference_plot method from UI processing mixin
            if hasattr(self.main_window, '_update_inference_plot'):
                self.main_window._update_inference_plot(classification_results)
                self.logger.debug("Updated classification plot via UI processing mixin")
            else:
                # Fallback: Update plot directly
                self._update_classification_plot_directly(classification_results)
                
        except Exception as e:
            self.logger.error(f"Error updating classification plot: {str(e)}")
    
    def _update_classification_plot_directly(self, classification_results: dict):
        """Fallback method to update classification plot directly using PyQtGraph"""
        try:
            if not hasattr(self.main_window, 'canvasProb'):
                self.logger.warning("Classification plot components not available")
                return
            
            self.logger.debug("Updating classification plot directly using PyQtGraph")
            probabilities = classification_results.get('probabilities', [])
            predicted_class = classification_results.get('predicted_class', 'Unknown')
            confidence = classification_results.get('confidence', 0.0)
            
            if len(probabilities) == 0:
                self.logger.warning("No probabilities to display in classification plot")
                return
            
            # Clear the existing plot
            self.main_window.canvasProb.clear()
            
            # Always use 4-stage maturation labels (M, MM, BN, SN)
            class_labels = ['M', 'MM', 'BN', 'SN']
            
            # Calculate maturation score - linear weighted value from 0 to 1
            # M=0, MM=0.33, BN=0.67, SN=1.0
            maturation_weights = [0.0, 0.33, 0.67, 1.0]
            maturation_score = sum(prob * weight for prob, weight in zip(probabilities, maturation_weights))
            
            # Find the predicted class index for highlighting
            max_idx = probabilities.argmax() if hasattr(probabilities, 'argmax') else max(range(len(probabilities)), key=probabilities.__getitem__)
            
            # Import pyqtgraph for BarGraphItem
            try:
                import pyqtgraph as pg
                
                # Create bars with highlighting using BarGraphItem
                for i, prob in enumerate(probabilities):
                    color = 'red' if i == max_idx else 'lightblue'
                    bar = pg.BarGraphItem(x=[i], height=[prob], width=0.6, brush=color)
                    self.main_window.canvasProb.addItem(bar)
                
                # Set labels and title with maturation score
                self.main_window.canvasProb.setLabel('left', 'Probability')
                self.main_window.canvasProb.setLabel('bottom', 'Classes')
                self.main_window.canvasProb.setTitle(
                    f'<div style="text-align:left; white-space:pre-line; font-size:10pt; color:#333333;">'
                    f'Classification Results<br>'
                    f'Predicted: {predicted_class}<br>'
                    f'Confidence: {confidence:.3f}<br>'
                    f'Maturation Score: {maturation_score:.3f}'
                    f'</div>'
                )
                
                # Set x-axis labels
                ax = self.main_window.canvasProb.getPlotItem().getAxis('bottom')
                ax.setTicks([[(i, label) for i, label in enumerate(class_labels)]])
                
                # Set axis ranges
                self.main_window.canvasProb.setYRange(0, 1)
                self.main_window.canvasProb.setXRange(-0.5, len(class_labels) - 0.5)
                
                self.logger.debug("Updated classification plot directly using PyQtGraph with maturation score")
                
            except ImportError:
                self.logger.error("PyQtGraph not available for classification plot update")
            
        except Exception as e:
            self.logger.error(f"Error updating classification plot directly: {str(e)}")
    
    def _display_calculation_error(self, error_message: str):
        """Display calculation errors in UI components"""
        try:
            # Update metric labels to show error using correct UI label names
            metric_labels = [
                'label_area_1', 'label_vol_1', 'label_nsi_1', 'label_sphericity_1', 'label_sa_vol_ratio_1', 'label_solidity_1', 'label_elongation_1', 'label_genus_1',
                'label_area_2', 'label_vol_2', 'label_nsi_2', 'label_sphericity_2', 'label_sa_vol_ratio_2', 'label_solidity_2', 'label_elongation_2', 'label_genus_2'
            ]
            
            for label_name in metric_labels:
                if hasattr(self.main_window, label_name):
                    getattr(self.main_window, label_name).setText("error")
            
            # Update classification plot to show error
            if hasattr(self.main_window, 'canvasProb'):
                self.main_window.canvasProb.clear()
                
                # Add error text using PyQtGraph TextItem
                try:
                    import pyqtgraph as pg
                    error_text = pg.TextItem("Calculation Error", color=(255, 0, 0), anchor=(0.5, 0.5))
                    error_text.setPos(1.5, 0.5)  # Center position for 4 classes (0-3)
                    self.main_window.canvasProb.addItem(error_text)
                except ImportError:
                    # Fallback if pyqtgraph not available
                    pass
                
                self.main_window.canvasProb.setTitle("Classification Results")
                self.main_window.canvasProb.setXRange(0, 3)
                self.main_window.canvasProb.setYRange(0, 1)
            
            # Show error in progress label if available
            if hasattr(self.main_window, 'progress_label'):
                self.main_window.progress_label.setText(f"Calculation error: {error_message}")
                self.main_window.progress_label.setVisible(True)
                
            self.logger.debug("Displayed calculation error in UI components")
            
        except Exception as e:
            self.logger.error(f"Error displaying calculation error: {str(e)}")