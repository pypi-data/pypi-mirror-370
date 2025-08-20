"""
UI Rendering Mixin for the MainWindow.
Handles image rendering, VTK operations, and visualization methods.
"""
from ..utils.logging_config import log_error_with_context

class UiRenderingMixin:
    """Mixin containing rendering methods for MainWindow."""

    def render_image(self):
        """Render image with isosurfaces using ImageRenderer"""
        try:
            # Get current threshold values from sliders
            value1 = self.horizontalSlider_intensity1.value()
            value2 = self.horizontalSlider_intensity2.value()
            
            if self.img is None:
                return
            
            # Use ImageRenderer if available, otherwise fallback to legacy approach
            if hasattr(self, 'image_renderer') and self.image_renderer:
                self.image_renderer.render_isosurfaces(value1, value2)
            else:
                # Legacy fallback approach
                self._render_image_legacy(value1, value2)
            
            # Render histogram
            if hasattr(self, 'canvasHist') and self.canvasHist:
                self.image_renderer.render_histogram(value1, value2)

        except Exception as e:
            log_error_with_context(self.logger, e, "render_image")
            if hasattr(self, 'progress_label') and self.progress_label:
                self.progress_label.setText(f"Render error: {str(e)}")
                self.progress_label.setVisible(True)

    def _render_image_legacy(self, value1, value2):
        """Legacy rendering approach as fallback"""
        global vtk, numpy_support
        try:
            # Create VTK image data from numpy array (legacy approach)
            vtk_data = vtk.vtkImageData()
            vtk_data.SetDimensions(self.img.shape)
            
            # Copy the numpy array data to vtkImageData
            flat_data = self.img.flatten()
            if self.img.dtype == "uint8" or str(self.img.dtype) == "uint8":
                vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
                vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
            elif self.img.dtype == "uint16" or str(self.img.dtype) == "uint16":
                vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_SHORT, 1)
                vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT)
            else:
                print("Image data type not UINT8 or UINT16:", self.img.dtype)
                return
                
            vtk_data.GetPointData().SetScalars(vtk_array)
            
            # Create marching cubes algorithms (legacy approach)
            contour1 = vtk.vtkMarchingCubes()
            contour1.SetInputData(vtk_data)
            contour1.SetValue(0, value1)
            contour1.Update()
            
            contour2 = vtk.vtkMarchingCubes()
            contour2.SetInputData(vtk_data)
            contour2.SetValue(0, value2)
            contour2.Update()
            
            # Update reusable mappers
            if hasattr(self, 'mapper1') and self.mapper1:
                self.mapper1.SetInputData(contour1.GetOutput())
            if hasattr(self, 'mapper2') and self.mapper2:
                self.mapper2.SetInputData(contour2.GetOutput())
            
            # Render the scene
            if hasattr(self, 'vtkWidget') and self.vtkWidget:
                self.vtkWidget.GetRenderWindow().Render()
                
        except Exception as e:
            log_error_with_context(self.logger, e, "_render_image_legacy")


    def calculate_geometry_metrics(self):
        """Calculate geometry metrics for both isosurfaces after slider value changes"""
        try:
            if not hasattr(self, 'geometry_calculator') or self.geometry_calculator is None:
                self.logger.warning("Geometry calculator not available")
                return
            
            # Get current threshold values from sliders
            value1 = self.horizontalSlider_intensity1.value()
            value2 = self.horizontalSlider_intensity2.value()
            
            if self.img is None:
                self.logger.warning("No image loaded for geometry calculations")
                return
            
            # Get contour surfaces directly from renderer mappers instead of recalculating
            contour1_polydata = None
            contour2_polydata = None
            
            # Try to get contour surfaces from image renderer mappers
            if (hasattr(self, 'image_renderer') and self.image_renderer and
                hasattr(self.image_renderer, 'mapper1') and hasattr(self.image_renderer, 'mapper2')):
                
                # Get polydata from mapper1 (threshold1/nucleus)
                if self.image_renderer.mapper1 and self.image_renderer.mapper1.GetInput():
                    contour1_polydata = self.image_renderer.mapper1.GetInput()
                    self.logger.debug(f"Retrieved contour1 polydata from renderer mapper1 with {contour1_polydata.GetNumberOfPoints()} points")
                
                # Get polydata from mapper2 (threshold2/membrane)
                if self.image_renderer.mapper2 and self.image_renderer.mapper2.GetInput():
                    contour2_polydata = self.image_renderer.mapper2.GetInput()
                    self.logger.debug(f"Retrieved contour2 polydata from renderer mapper2 with {contour2_polydata.GetNumberOfPoints()} points")
            
            # Fallback to legacy approach if renderer surfaces not available
            if contour1_polydata is None:
                self.logger.debug("Falling back to recalculating contour1 polydata")
                contour1_polydata = self.geometry_calculator.get_contour_polydata_from_renderer(value1)
            
            if contour2_polydata is None:
                self.logger.debug("Falling back to recalculating contour2 polydata")
                contour2_polydata = self.geometry_calculator.get_contour_polydata_from_renderer(value2)
            
            # Calculate geometry for both thresholds
            # Threshold 1 (nucleus)
            if contour1_polydata and contour1_polydata.GetNumberOfPoints() > 0:
                self.geometry_calculator.calculate_and_set_geometry_metrics(contour1_polydata, "_1")
            else:
                self.logger.warning("No valid contour1 polydata available for geometry calculations")
            
            # Threshold 2 (membrane)
            if contour2_polydata and contour2_polydata.GetNumberOfPoints() > 0:
                self.geometry_calculator.calculate_and_set_geometry_metrics(contour2_polydata, "_2")
            else:
                self.logger.warning("No valid contour2 polydata available for geometry calculations")
            
            self.logger.debug(f"Geometry calculations completed for thresholds: {value1}, {value2}")
            
        except Exception as e:
            self.logger.error(f"Error in calculate_geometry_metrics: {e}")
            if hasattr(self, 'progress_label') and self.progress_label:
                self.progress_label.setText(f"Geometry error: {str(e)}")
                self.progress_label.setVisible(True)