"""
VTK Computation Utilities - Shared functions for VTK isosurface generation
"""
import time
import numpy as np
from typing import Optional, Tuple


class VTKComputationUtils:
    """
    Utility class for VTK isosurface computations that can be safely called from background threads.
    Extracts common logic from StreamlinedLoadingThread and SynchronousVTKRenderer.
    """
    
    @staticmethod
    def compute_isosurfaces_background(image_data: np.ndarray, threshold1: int, threshold2: int,
                                     vtk_renderer, progress_callback=None) -> Tuple[bool, Optional[object], Optional[object]]:
        """
        Compute VTK isosurfaces in background thread (safe operations only).
        Returns polydata that can be safely passed to main thread for rendering.
        Includes VTK error suppression to prevent dialog boxes from blocking threads.
        
        Args:
            image_data: Image data as numpy array
            threshold1: First threshold value
            threshold2: Second threshold value
            vtk_renderer: VTK renderer instance with conversion methods
            progress_callback: Optional function to call with progress updates (progress, message)
            
        Returns:
            Tuple of (success, polydata1, polydata2)
        """
        try:
            # Suppress VTK warnings/errors that can cause popup windows
            import vtk
            vtk.vtkObject.GlobalWarningDisplayOff()
            
            if progress_callback:
                progress_callback(10, "Starting VTK isosurface computation...")
            
            if not vtk_renderer:
                if progress_callback:
                    progress_callback(100, "VTK renderer not available")
                return True, None, None
            
            # Convert numpy array to VTK image data
            if progress_callback:
                progress_callback(30, "Converting image data to VTK format...")
            
            vtk_image_data = VTKComputationUtils._numpy_to_vtk_image_data(image_data, vtk_renderer)
            if vtk_image_data is None:
                if progress_callback:
                    progress_callback(100, "VTK image data conversion failed")
                return False, None, None
            
            # Generate first isosurface
            if progress_callback:
                progress_callback(50, f"Computing isosurface 1 (T1={threshold1})...")
            
            polydata1 = VTKComputationUtils._generate_isosurface(vtk_image_data, threshold1, vtk_renderer)
            
            # Generate second isosurface
            if progress_callback:
                progress_callback(75, f"Computing isosurface 2 (T2={threshold2})...")
            
            polydata2 = VTKComputationUtils._generate_isosurface(vtk_image_data, threshold2, vtk_renderer)
            
            if progress_callback:
                progress_callback(100, "VTK isosurface computation complete")
            
            return True, polydata1, polydata2
            
        except Exception as e:
            error_msg = f"VTK isosurface computation failed: {e}"
            print(error_msg)
            if progress_callback:
                progress_callback(100, error_msg)
            return False, None, None
        finally:
            # Re-enable VTK warnings
            try:
                import vtk
                vtk.vtkObject.GlobalWarningDisplayOn()
            except:
                pass
    
    @staticmethod
    def _numpy_to_vtk_image_data(image_data: np.ndarray, vtk_renderer):
        """
        Convert numpy array to VTK image data using the renderer's method.
        Safe to call from background thread.
        """
        try:
            if not vtk_renderer or not hasattr(vtk_renderer, '_numpy_to_vtk_image_data'):
                return None
            
            return vtk_renderer._numpy_to_vtk_image_data(image_data)
            
        except Exception as e:
            print(f"Error converting numpy to VTK image data: {e}")
            return None
    
    @staticmethod
    def _generate_isosurface(vtk_image_data, threshold_value, vtk_renderer):
        """
        Generate isosurface using VTK marching cubes via the renderer's method.
        Safe to call from background thread.
        """
        try:
            if not vtk_renderer or not hasattr(vtk_renderer, '_generate_isosurface'):
                return None
            
            return vtk_renderer._generate_isosurface(vtk_image_data, threshold_value)
            
        except Exception as e:
            print(f"Error generating isosurface for threshold {threshold_value}: {e}")
            return None