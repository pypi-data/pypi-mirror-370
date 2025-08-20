"""
Streamlined Image Loading Thread - Background processing for image loading and rendering
"""
import os
import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional, Tuple
from .vtk_computation_utils import VTKComputationUtils


class StreamlinedLoadingThread(QThread):
    """
    Background thread for streamlined image loading and rendering operations.
    Handles image loading, threshold calculation, and VTK rendering without blocking the UI.
    """
    
    # Signals for progress updates and results
    progress_update = pyqtSignal(int, str)  # progress percentage, status message
    image_loaded = pyqtSignal(str, np.ndarray, tuple)  # file_path, image_data, thresholds
    vtk_polydata_ready = pyqtSignal(object, object)  # polydata1, polydata2 (for main thread rendering)
    error_occurred = pyqtSignal(str)  # error_message
    loading_complete = pyqtSignal(str, np.ndarray, int, int, bool)  # path, data, t1, t2, vtk_success
    
    def __init__(self, image_path: str, fast_image_loader=None, vtk_renderer=None):
        super().__init__()
        self.image_path = image_path
        self.fast_image_loader = fast_image_loader
        self.vtk_renderer = vtk_renderer
        self._stop_requested = False
        
    def run(self):
        """Execute the background loading workflow"""
        try:
            # Step 1: Validate file path (5%)
            if self._stop_requested:
                return
            self.progress_update.emit(5, "Validating image file...")
            
            if not os.path.exists(self.image_path):
                self.error_occurred.emit(f"Image file not found: {self.image_path}")
                return
            
            # Step 2: Load image data (30%)
            if self._stop_requested:
                return
            self.progress_update.emit(15, "Loading image data...")
            
            image_data = self._load_image_data()
            if image_data is None:
                self.error_occurred.emit("Failed to load image data")
                return
                
            self.progress_update.emit(30, f"Image loaded: {image_data.shape}")
            
            # Step 3: Calculate thresholds (50%)
            if self._stop_requested:
                return
            self.progress_update.emit(40, "Calculating thresholds...")
            
            threshold1, threshold2 = self._calculate_thresholds(image_data)
            self.progress_update.emit(50, f"Thresholds: T1={threshold1}, T2={threshold2}")
            
            # Step 4: VTK isosurface computation (80%) - Safe to do in background thread
            if self._stop_requested:
                return
            self.progress_update.emit(60, "Computing 3D isosurfaces...")
            
            vtk_success, polydata1, polydata2 = self._compute_vtk_isosurfaces(image_data, threshold1, threshold2)
            if vtk_success and polydata1 is not None and polydata2 is not None:
                # Emit polydata for main thread rendering
                self.vtk_polydata_ready.emit(polydata1, polydata2)
                self.progress_update.emit(80, "3D isosurfaces computed")
            else:
                self.progress_update.emit(80, "3D computation failed")
            
            # Step 5: Finalize (100%)
            if self._stop_requested:
                return
            self.progress_update.emit(95, "Finalizing...")
            
            # Emit completion signals
            self.image_loaded.emit(self.image_path, image_data, (threshold1, threshold2))
            self.loading_complete.emit(self.image_path, image_data, threshold1, threshold2, vtk_success)
            
            self.progress_update.emit(100, "Loading complete")
            
        except Exception as e:
            if not self._stop_requested:
                error_msg = f"Error loading image {os.path.basename(self.image_path)}: {str(e)}"
                self.error_occurred.emit(error_msg)
    
    def stop_gracefully(self):
        """Request the thread to stop gracefully"""
        self._stop_requested = True
    
    def _load_image_data(self) -> Optional[np.ndarray]:
        """Load image data using FastImageLoader or fallback methods"""
        try:
            # Try FastImageLoader first
            if self.fast_image_loader:
                try:
                    image_data = self.fast_image_loader.load_image(self.image_path)
                    if image_data is not None:
                        return image_data
                except Exception as e:
                    print(f"FastImageLoader failed: {e}, using fallback")
            
            # Fallback loading methods
            return self._fallback_load_image()
            
        except Exception as e:
            print(f"Error in _load_image_data: {e}")
            return None
    
    def _fallback_load_image(self) -> Optional[np.ndarray]:
        """Fallback image loading when FastImageLoader is not available"""
        try:
            # Try tifffile first (most common format)
            if self.image_path.lower().endswith(('.tif', '.tiff')):
                try:
                    import tifffile
                    return tifffile.imread(self.image_path)
                except ImportError:
                    pass
                except Exception:
                    pass
            
            # Try imageio as fallback
            try:
                import imageio
                return imageio.imread(self.image_path)
            except ImportError:
                pass
            except Exception:
                pass
            
            # Try PIL as last resort
            try:
                from PIL import Image
                import numpy as np
                pil_image = Image.open(self.image_path)
                return np.array(pil_image)
            except ImportError:
                pass
            except Exception:
                pass
            
            return None
            
        except Exception:
            return None
    
    def _calculate_thresholds(self, image_data: np.ndarray) -> Tuple[int, int]:
        """Calculate thresholds using FastImageLoader or fallback method"""
        try:
            # Try FastImageLoader first
            if self.fast_image_loader:
                try:
                    return self.fast_image_loader.calculate_thresholds(image_data)
                except Exception as e:
                    print(f"FastImageLoader threshold calculation failed: {e}, using fallback")
            
            # Fallback threshold calculation
            return self._fallback_calculate_thresholds(image_data)
            
        except Exception:
            # Return safe default values
            return 100, 50
    
    def _fallback_calculate_thresholds(self, image_data: np.ndarray) -> Tuple[int, int]:
        """Fallback threshold calculation method"""
        try:
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
            
            return threshold1, threshold2
            
        except Exception:
            return 100, 50
    
    def _compute_vtk_isosurfaces(self, image_data: np.ndarray, threshold1: int, threshold2: int) -> Tuple[bool, Optional[object], Optional[object]]:
        """
        Compute VTK isosurfaces in background thread (safe operations only).
        Returns polydata that can be safely passed to main thread for rendering.
        
        Returns:
            Tuple of (success, polydata1, polydata2)
        """
        try:
            if not self.vtk_renderer:
                return True, None, None  # Don't fail if VTK renderer not available
            
            if hasattr(self.vtk_renderer, 'render_isosurfaces'):
                # Check if this is SynchronousVTKRenderer (preferred)
                if 'SynchronousVTK' in str(type(self.vtk_renderer)):
                    # Use shared VTK computation utility
                    def progress_callback(progress, message):
                        # Convert to loading thread progress (60-80% range)
                        adjusted_progress = 60 + (progress * 0.2)
                        self.progress_update.emit(int(adjusted_progress), message)
                    
                    return VTKComputationUtils.compute_isosurfaces_background(
                        image_data, threshold1, threshold2, self.vtk_renderer, progress_callback
                    )
                else:
                    # For ImageRenderer, we can't safely compute in background thread
                    print("ImageRenderer detected - skipping VTK computation in background thread")
                    return True, None, None
            else:
                print("VTK renderer has no render_isosurfaces method")
                return False, None, None
                
        except Exception as e:
            print(f"VTK isosurface computation failed: {e}")
            return False, None, None
    
    def _render_vtk_isosurfaces(self, image_data: np.ndarray, threshold1: int, threshold2: int) -> bool:
        """
        DEPRECATED: Use _compute_vtk_isosurfaces instead.
        This method is kept for compatibility.
        """
        print("WARNING: _render_vtk_isosurfaces is deprecated - use _compute_vtk_isosurfaces")
        success, _, _ = self._compute_vtk_isosurfaces(image_data, threshold1, threshold2)
        return success