"""
Synchronous VTK Renderer - Fast VTK rendering without threading complexity
Implements synchronous isosurface generation and rendering for the streamlined workflow.
"""
import os
import time
import logging
from typing import Tuple, Optional
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from ..utils.logging_config import get_logger


class SynchronousVTKRenderer(QObject):
    """
    Synchronous VTK renderer for fast isosurface generation and rendering.
    Eliminates threading complexity by performing all operations on the main thread.
    """
    
    # Signals for communication with UI
    rendering_complete = pyqtSignal(str)  # status_message
    error_occurred = pyqtSignal(str)  # error_message
    surfaces_updated = pyqtSignal(object, object)  # polydata1, polydata2
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.logger = get_logger('logic.synchronous_vtk_renderer')
        
        # VTK components (will be set by main window after initialization)
        self.actor1 = None
        self.actor2 = None
        self.mapper1 = None
        self.mapper2 = None
        self.ren = None
        self.widget = None
        self.vtkWidget = None
        self.iren = None
        
        # VTK modules (imported dynamically)
        self.vtk = None
        self.numpy_support = None
        
        # Current state
        self.current_image_data = None
        self.current_polydata1 = None
        self.current_polydata2 = None
        self.current_threshold1 = None
        self.current_threshold2 = None
        
        # Performance tracking
        self.render_times = []
        
        self._init_vtk_modules()
        
        self.logger.info("SynchronousVTKRenderer initialized")
    
    def _init_vtk_modules(self):
        """Initialize VTK modules"""
        try:
            # Try to import VTK modules
            import vtk
            from vtk.util import numpy_support
            
            self.vtk = vtk
            self.numpy_support = numpy_support
            
            self.logger.info("VTK modules imported successfully")
            
        except ImportError as e:
            error_msg = f"Failed to import VTK modules: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def set_vtk_components(self, actor1=None, actor2=None, mapper1=None, mapper2=None, 
                          ren=None, widget=None, vtkWidget=None, iren=None):
        """
        Set VTK components from main window after they are created.
        
        Args:
            actor1: VTK actor for first isosurface (nucleus)
            actor2: VTK actor for second isosurface (membrane)
            mapper1: VTK mapper for first isosurface
            mapper2: VTK mapper for second isosurface
            ren: VTK renderer
            widget: Main widget containing VTK renderer
            vtkWidget: VTK widget for rendering
            iren: VTK render window interactor
        """
        try:
            self.actor1 = actor1
            self.actor2 = actor2
            self.mapper1 = mapper1
            self.mapper2 = mapper2
            self.ren = ren
            self.widget = widget
            self.vtkWidget = vtkWidget
            self.iren = iren
            
            # Set up actor-mapper connections
            if self.actor1 and self.mapper1:
                self.actor1.SetMapper(self.mapper1)
            if self.actor2 and self.mapper2:
                self.actor2.SetMapper(self.mapper2)
            
            # Add actors to renderer
            if self.ren:
                if self.actor1:
                    self.ren.AddActor(self.actor1)
                if self.actor2:
                    self.ren.AddActor(self.actor2)
            
            # Configure actor properties
            self._configure_actor_properties()
            
            self.logger.info("VTK components set and configured")
            
        except Exception as e:
            error_msg = f"Error setting VTK components: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _configure_actor_properties(self):
        """Configure visual properties for VTK actors"""
        try:
            # Configure nucleus actor (actor1)
            if self.actor1:
                self.actor1.GetProperty().SetColor(0, 1, 1)  # Cyan
                self.actor1.GetProperty().SetOpacity(0.6)
                print("DEBUG VTK: Nucleus actor configured with color cyan and opacity 0.6")
            else:
                print("DEBUG VTK: WARNING - Nucleus actor not set, cannot configure properties")
                
            # Configure membrane actor (actor2)
            if self.actor2:
                self.actor2.GetProperty().SetColor(1, 1, 1)  # White
                self.actor2.GetProperty().SetOpacity(0.3)
                print("DEBUG VTK: Membrane actor configured with color white and opacity 0.3")
            else:
                print("DEBUG VTK: WARNING - Membrane actor not set, cannot configure properties")

            self.logger.debug("Actor properties configured")
            
        except Exception as e:
            self.logger.error(f"Error configuring actor properties: {str(e)}")
    
    def render_isosurfaces(self, image_data: np.ndarray, threshold1: int, threshold2: int) -> bool:
        """
        Generate and render isosurfaces synchronously.
        
        Args:
            image_data: Image data as numpy array
            threshold1: First threshold value (nucleus)
            threshold2: Second threshold value (membrane)
            
        Returns:
            True if rendering succeeded, False otherwise
        """
        try:
            start_time = time.time()
            print(f"DEBUG VTK: render_isosurfaces called with shape {image_data.shape}, thresholds {threshold1}, {threshold2}")
            
            if self.vtk is None or self.numpy_support is None:
                error_msg = "VTK modules not available"
                print(f"DEBUG VTK: ERROR - {error_msg}")
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            if image_data is None or image_data.size == 0:
                error_msg = "Invalid image data provided"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            # Store current state
            self.current_image_data = image_data
            self.current_threshold1 = threshold1
            self.current_threshold2 = threshold2
            
            # Convert numpy array to VTK image data
            vtk_image_data = self._numpy_to_vtk_image_data(image_data)
            if vtk_image_data is None:
                return False
            
            # Generate isosurfaces
            polydata1 = self._generate_isosurface(vtk_image_data, threshold1)
            polydata2 = self._generate_isosurface(vtk_image_data, threshold2)
            
            if polydata1 is None or polydata2 is None:
                error_msg = "Failed to generate isosurfaces"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            
            # Update VTK mappers with new surfaces (safe for any thread)
            if self.mapper1:
                self.mapper1.SetInputData(polydata1)
            if self.mapper2:
                self.mapper2.SetInputData(polydata2)
            
            # Store generated polydata
            self.current_polydata1 = polydata1
            self.current_polydata2 = polydata2
            
            # Only trigger UI rendering if called from main thread
            # Background threads should call render_polydata_to_ui() separately
            self._trigger_ui_rendering_if_safe()
            
            # Update camera if this is the first render
            if self.ren and len(self.render_times) == 0:
                self.ren.ResetCamera()
            
            # Performance tracking
            render_time = time.time() - start_time
            self.render_times.append(render_time)
            
            # Emit signals
            self.surfaces_updated.emit(polydata1, polydata2)
            self.rendering_complete.emit(f"Isosurfaces rendered in {render_time:.3f}s")
            
            self.logger.info(f"Successfully rendered isosurfaces - "
                           f"T1={threshold1}, T2={threshold2}, Time={render_time:.3f}s")
            
            return True
            
        except Exception as e:
            error_msg = f"Error rendering isosurfaces: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
    
    def update_thresholds(self, image_data: np.ndarray, threshold1: int, threshold2: int) -> bool:
        """
        DEPRECATED: This method is replaced by background threshold update thread.
        Update existing isosurfaces with new threshold values.
        More efficient than full re-rendering as it reuses VTK image data.
        
        Args:
            image_data: Image data as numpy array
            threshold1: New first threshold value
            threshold2: New second threshold value
            
        Returns:
            True if update succeeded, False otherwise
        """
        print("WARNING: SynchronousVTKRenderer.update_thresholds is deprecated - use ThresholdUpdateThread instead")
        try:
            start_time = time.time()
            
            if self.vtk is None or self.numpy_support is None:
                error_msg = "VTK modules not available"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            # Check if we can reuse existing VTK image data
            if (self.current_image_data is not None and 
                np.array_equal(image_data, self.current_image_data)):
                # Same image, just update thresholds
                vtk_image_data = self._numpy_to_vtk_image_data(image_data)
            else:
                # Different image, need to convert
                vtk_image_data = self._numpy_to_vtk_image_data(image_data)
                self.current_image_data = image_data
            
            if vtk_image_data is None:
                return False
            
            # Generate new isosurfaces with updated thresholds
            polydata1 = self._generate_isosurface(vtk_image_data, threshold1)
            polydata2 = self._generate_isosurface(vtk_image_data, threshold2)
            
            if polydata1 is None or polydata2 is None:
                error_msg = "Failed to generate updated isosurfaces"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            # Update stored state
            self.current_threshold1 = threshold1
            self.current_threshold2 = threshold2
            self.current_polydata1 = polydata1
            self.current_polydata2 = polydata2
            
            # Update VTK mappers
            if self.mapper1:
                self.mapper1.SetInputData(polydata1)
                self.mapper1.Modified()
            if self.mapper2:
                self.mapper2.SetInputData(polydata2)
                self.mapper2.Modified()
            
            # DIAGNOSTIC: Track rendering timing
            render_start_time = time.time()
            print(f"DEBUG VTK: About to trigger VTK rendering - THIS MAY BLOCK UI")
            
            # Trigger rendering
            if self.vtkWidget:
                self.vtkWidget.GetRenderWindow().Render()
            elif self.widget:
                self.widget.update()
            
            render_time = time.time() - render_start_time
            print(f"DEBUG VTK: VTK rendering completed in {render_time:.3f}s")
            
            # Performance tracking
            update_time = time.time() - start_time
            
            # Emit signals
            self.surfaces_updated.emit(polydata1, polydata2)
            self.rendering_complete.emit(f"Thresholds updated in {update_time:.3f}s")
            
            self.logger.debug(f"Successfully updated thresholds - "
                            f"T1={threshold1}, T2={threshold2}, Time={update_time:.3f}s")
            
            return True
            
        except Exception as e:
            error_msg = f"Error updating thresholds: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
    
    def _numpy_to_vtk_image_data(self, image_data: np.ndarray):
        """
        Convert numpy array to VTK image data.
        
        Args:
            image_data: Image data as numpy array
            
        Returns:
            VTK image data object, or None if conversion failed
        """
        try:
            if self.vtk is None or self.numpy_support is None:
                return None
            
            # DIAGNOSTIC: Track conversion timing
            conv_start_time = time.time()
            print(f"DEBUG VTK: Starting numpy to VTK conversion for shape {image_data.shape}, dtype {image_data.dtype}")
            
            # Create VTK image data
            vtk_image_data = self.vtk.vtkImageData()
            vtk_image_data.SetDimensions(image_data.shape)
            
            # Determine VTK data type based on numpy dtype
            if image_data.dtype == np.uint8:
                vtk_type = self.vtk.VTK_UNSIGNED_CHAR
            elif image_data.dtype == np.uint16:
                vtk_type = self.vtk.VTK_UNSIGNED_SHORT
            elif image_data.dtype == np.float32:
                vtk_type = self.vtk.VTK_FLOAT
            elif image_data.dtype == np.float64:
                vtk_type = self.vtk.VTK_DOUBLE
            else:
                # Convert to uint16 as fallback
                image_data = image_data.astype(np.uint16)
                vtk_type = self.vtk.VTK_UNSIGNED_SHORT
            
            vtk_image_data.AllocateScalars(vtk_type, 1)
            
            # DIAGNOSTIC: Track array conversion - this can be slow for large images
            print(f"DEBUG VTK: About to flatten and convert {image_data.size} elements - THIS MAY BLOCK UI")
            flat_data = image_data.flatten()
            vtk_array = self.numpy_support.numpy_to_vtk(
                num_array=flat_data,
                deep=True,
                array_type=vtk_type
            )
            vtk_image_data.GetPointData().SetScalars(vtk_array)
            
            conv_time = time.time() - conv_start_time
            print(f"DEBUG VTK: Numpy to VTK conversion completed in {conv_time:.3f}s")
            
            return vtk_image_data
            
        except Exception as e:
            error_msg = f"Error converting numpy array to VTK image data: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None
    
    def _generate_isosurface(self, vtk_image_data, threshold_value):
        """
        Generate isosurface using VTK marching cubes.
        
        Args:
            vtk_image_data: VTK image data object
            threshold_value: Threshold value for isosurface generation
            
        Returns:
            VTK polydata object, or None if generation failed
        """
        try:
            if self.vtk is None:
                return None
            
            # DIAGNOSTIC: Track marching cubes timing
            mc_start_time = time.time()
            print(f"DEBUG VTK: Starting marching cubes for threshold {threshold_value}")
            
            # Create marching cubes filter
            marching_cubes = self.vtk.vtkMarchingCubes()
            marching_cubes.SetInputData(vtk_image_data)
            marching_cubes.SetValue(0, threshold_value)
            
            # DIAGNOSTIC: This is the potentially blocking operation
            print(f"DEBUG VTK: About to call marching_cubes.Update() - THIS MAY BLOCK UI")
            marching_cubes.Update()
            mc_time = time.time() - mc_start_time
            print(f"DEBUG VTK: Marching cubes completed in {mc_time:.3f}s for threshold {threshold_value}")
            
            # Get the resulting polydata
            polydata = marching_cubes.GetOutput()
            
            # Basic validation
            if polydata.GetNumberOfPoints() == 0:
                self.logger.warning(f"No points generated for threshold {threshold_value}")
                # Return empty polydata instead of None to avoid errors
                return polydata
            
            print(f"DEBUG VTK: Generated {polydata.GetNumberOfPoints()} points, {polydata.GetNumberOfCells()} cells")
            return polydata
            
        except Exception as e:
            error_msg = f"Error generating isosurface for threshold {threshold_value}: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None
    
    def get_current_polydata(self) -> Tuple[Optional[object], Optional[object]]:
        """
        Get current polydata objects for metrics calculation.
        
        Returns:
            Tuple of (polydata1, polydata2), or (None, None) if not available
        """
        return self.current_polydata1, self.current_polydata2
    
    def get_current_thresholds(self) -> Tuple[Optional[int], Optional[int]]:
        """
        Get current threshold values.
        
        Returns:
            Tuple of (threshold1, threshold2), or (None, None) if not set
        """
        return self.current_threshold1, self.current_threshold2
    
    def reset_camera(self):
        """Reset camera to fit all actors in view"""
        try:
            if self.ren:
                self.ren.ResetCamera()
                if self.vtkWidget:
                    self.vtkWidget.GetRenderWindow().Render()
                elif self.widget:
                    self.widget.update()
                self.logger.debug("Camera reset")
        except Exception as e:
            self.logger.error(f"Error resetting camera: {str(e)}")
    
    def set_actor_visibility(self, actor1_visible: bool = True, actor2_visible: bool = True):
        """
        Set visibility of VTK actors.
        
        Args:
            actor1_visible: Visibility of first actor (nucleus)
            actor2_visible: Visibility of second actor (membrane)
        """
        try:
            if self.actor1:
                self.actor1.SetVisibility(actor1_visible)
            if self.actor2:
                self.actor2.SetVisibility(actor2_visible)
            
            # Trigger rendering
            if self.vtkWidget:
                self.vtkWidget.GetRenderWindow().Render()
            elif self.widget:
                self.widget.update()
                
            self.logger.debug(f"Actor visibility set: actor1={actor1_visible}, actor2={actor2_visible}")
            
        except Exception as e:
            self.logger.error(f"Error setting actor visibility: {str(e)}")
    
    def get_performance_stats(self) -> dict:
        """
        Get performance statistics for monitoring.
        
        Returns:
            Dictionary containing performance statistics
        """
        try:
            if not self.render_times:
                return {
                    'total_renders': 0,
                    'avg_render_time': 0,
                    'min_render_time': 0,
                    'max_render_time': 0
                }
            
            return {
                'total_renders': len(self.render_times),
                'avg_render_time': np.mean(self.render_times),
                'min_render_time': np.min(self.render_times),
                'max_render_time': np.max(self.render_times),
                'last_render_time': self.render_times[-1] if self.render_times else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {str(e)}")
            return {}
    
    def cleanup(self):
        """Clean up VTK resources and clear current state"""
        try:
            # Clear current state
            self.current_image_data = None
            self.current_polydata1 = None
            self.current_polydata2 = None
            self.current_threshold1 = None
            self.current_threshold2 = None
            
            # Clear performance tracking
            self.render_times.clear()
            
            # VTK components are managed by the main window, so we don't delete them here
            
            self.logger.info("SynchronousVTKRenderer cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def _trigger_ui_rendering_if_safe(self):
        """
        Trigger UI rendering only if it's safe to do so.
        This method checks if we're in the main thread before calling UI operations.
        """
        try:
            from PyQt5.QtCore import QThread
            
            # Only trigger UI rendering if we're in the main thread
            if QThread.currentThread() == self.main_window.thread():
                # Trigger rendering
                if self.vtkWidget:
                    self.vtkWidget.GetRenderWindow().Render()
                elif self.widget:
                    self.widget.update()
            else:
                # We're in a background thread - don't trigger UI rendering
                print("DEBUG VTK: Skipping UI rendering - called from background thread")
                
        except Exception as e:
            self.logger.error(f"Error checking thread safety for UI rendering: {str(e)}")
    
    def render_polydata_to_ui(self, polydata1, polydata2):
        """
        Render pre-computed polydata to UI. This method is thread-safe and should be
        called from the main thread after receiving polydata from background computation.
        
        Args:
            polydata1: VTK polydata for first isosurface
            polydata2: VTK polydata for second isosurface
        """
        try:
            start_time = time.time()
            
            if polydata1 is None or polydata2 is None:
                error_msg = "Invalid polydata provided for rendering"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            # Store polydata
            self.current_polydata1 = polydata1
            self.current_polydata2 = polydata2
            
            # Update VTK mappers with pre-computed surfaces
            if self.mapper1:
                self.mapper1.SetInputData(polydata1)
            if self.mapper2:
                self.mapper2.SetInputData(polydata2)
            
            # Trigger rendering (safe since this should be called from main thread)
            if self.vtkWidget:
                self.vtkWidget.GetRenderWindow().Render()
            elif self.widget:
                self.widget.update()
            
            # Update camera if this is the first render
            if self.ren and len(self.render_times) == 0:
                self.ren.ResetCamera()
            
            # Performance tracking
            render_time = time.time() - start_time
            self.render_times.append(render_time)
            
            # Emit signals
            self.surfaces_updated.emit(polydata1, polydata2)
            self.rendering_complete.emit(f"Polydata rendered in {render_time:.3f}s")
            
            self.logger.info(f"Successfully rendered pre-computed polydata in {render_time:.3f}s")
            
            return True
            
        except Exception as e:
            error_msg = f"Error rendering polydata to UI: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False