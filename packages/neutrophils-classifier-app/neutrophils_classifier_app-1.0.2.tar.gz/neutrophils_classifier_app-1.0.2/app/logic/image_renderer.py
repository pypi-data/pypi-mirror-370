"""
Image Rendering Logic for VTK Visualization
Handles efficient loading and isosurface rendering with reusable VTK actors.
Adopts streamlined approach from legacy code for optimal performance.
"""
import os
import numpy as np
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import QMessageBox
import logging
import pyqtgraph as pg

# Setup logging for debugging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

# VTK imports will be handled dynamically
vtk = None
numpy_support = None
tifffile = None

class ImageRenderer(QObject):
    """
    Handles VTK isosurface rendering with reusable actors for two surfaces.
    Streamlined for efficient rendering based on legacy implementation.
    """
    
    # Signals for communication with UI
    image_loaded = pyqtSignal(np.ndarray)  # image_data
    rendering_completed = pyqtSignal(str)  # status_message
    error_occurred = pyqtSignal(str)  # error_message
    slider_ranges_updated = pyqtSignal(int, int, int, int)  # min1, max1, value1, value2
    ui_controls_setup = pyqtSignal(int, int, int, int)  # data_max, threshold1, threshold2, path_hash
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_image = None
        self.vtk_components_ready = False
        
        # VTK component references (will be set by main window)
        self.actor1 = None
        self.actor2 = None
        self.mapper1 = None
        self.mapper2 = None
        self.widget = None
        self.vtkWidget = None
        self.ren = None
        self.iren = None
        
        self._init_vtk_components()
    
    def _init_vtk_components(self):
        """Initialize VTK components using the main window's existing VTK modules"""
        try:
            # Use the global VTK modules from main_window imports
            global vtk, numpy_support, tifffile
            
            # Access the VTK modules already imported by main_window
            if hasattr(self.main_window, '__dict__'):
                # Get the module globals from main_window's context
                main_module = self.main_window.__class__.__module__
                import sys
                if main_module in sys.modules:
                    module_globals = sys.modules[main_module].__dict__
                    vtk = module_globals.get('vtk')
                    numpy_support = module_globals.get('numpy_support')
                    tifffile = module_globals.get('tifffile')
            
            # Fallback: try direct import
            if vtk is None or numpy_support is None:
                try:
                    import vtk as vtk_module
                    from vtkmodules.util import numpy_support as numpy_support_module
                    vtk = vtk_module
                    numpy_support = numpy_support_module
                except ImportError:
                    print("VTK modules not available for image rendering")
                    return
            
            # Try to import tifffile if not available
            if tifffile is None:
                try:
                    import tifffile as tifffile_module
                    tifffile = tifffile_module
                except ImportError:
                    print("tifffile not available for direct loading")
            
            self.vtk_components_ready = (vtk is not None and numpy_support is not None)
            if self.vtk_components_ready:
                print("VTK components ready for isosurface rendering")
            
        except Exception as e:
            print(f"Error initializing VTK components: {e}")
    
    def set_vtk_components(self, actor1, actor2, mapper1, mapper2, widget, vtkWidget, ren, iren):
        """Set VTK components from main window after they are created"""
        self.actor1 = actor1
        self.actor2 = actor2
        self.mapper1 = mapper1
        self.mapper2 = mapper2
        self.widget = widget
        self.vtkWidget = vtkWidget
        self.ren = ren
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

        # Change actor property, allow dynamic setup later
        # nucleus
        self.actor1.GetProperty().SetColor(0,204/255,1)
        self.actor1.GetProperty().SetOpacity(0.6)

        # membrane
        self.actor2.GetProperty().SetColor(1,1,1)
        self.actor2.GetProperty().SetOpacity(0.3)
        
        print("VTK components set and configured in ImageRenderer")

    def set_image_and_surfaces(self, image_data, polydata1, polydata2, threshold1=None, threshold2=None):
        """
        Sets the current image and pre-computed surfaces for rendering.
        Bypasses internal marching cubes calculation.
        """
        if image_data is None:
            print("ERROR: image_data is None in set_image_and_surfaces")
            return
            
        self.current_image = image_data
        self.main_window.img = image_data  # Maintain compatibility
        print(f"Set current_image with shape: {image_data.shape}, dtype: {image_data.dtype}")

        # Set up both surfaces with proper error checking
        surfaces_set = 0
        
        if self.mapper1 and polydata1 and polydata1.GetNumberOfPoints() > 0:
            self.mapper1.SetInputData(polydata1)
            self.mapper1.ScalarVisibilityOff()
            surfaces_set += 1
            print(f"Surface 1 set with {polydata1.GetNumberOfPoints()} points")
        else:
            print(f"Surface 1 not set - mapper1: {self.mapper1 is not None}, polydata1: {polydata1 is not None}, points: {polydata1.GetNumberOfPoints() if polydata1 else 0}")

        if self.mapper2 and polydata2 and polydata2.GetNumberOfPoints() > 0:
            self.mapper2.SetInputData(polydata2)
            self.mapper2.ScalarVisibilityOff()
            surfaces_set += 1
            print(f"Surface 2 set with {polydata2.GetNumberOfPoints()} points")
        else:
            print(f"Surface 2 not set - mapper2: {self.mapper2 is not None}, polydata2: {polydata2 is not None}, points: {polydata2.GetNumberOfPoints() if polydata2 else 0}")

        # Ensure actors are visible and properly configured
        if self.actor1:
            self.actor1.SetVisibility(True)
            self.actor1.GetProperty().SetColor(0, 204/255, 1)  # Cyan for nucleus
            self.actor1.GetProperty().SetOpacity(0.6)
            
        if self.actor2:
            self.actor2.SetVisibility(True)
            self.actor2.GetProperty().SetColor(1, 1, 1)  # White for membrane
            self.actor2.GetProperty().SetOpacity(0.3)

        # Set up UI controls with threshold values if provided
        if threshold1 is not None and threshold2 is not None:
            data_max = self._get_data_type_max(image_data)
            self.ui_controls_setup.emit(data_max, threshold1, threshold2, hash(str(image_data.shape)))
            print(f"Emitted ui_controls_setup signal with thresholds: T1={threshold1}, T2={threshold2}")

        # Defer rendering to main thread using signal
        print(f"Set {surfaces_set} surfaces, deferring render to main thread")
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, self._do_render)  # Render on next event loop iteration (main thread)
        
        self.rendering_completed.emit(f"Pre-computed surfaces ready ({surfaces_set} surfaces).")
        self.image_loaded.emit(image_data)
    
    def _do_render(self):
        """Perform actual rendering on main thread"""
        try:
            if self.vtkWidget:
                self.vtkWidget.GetRenderWindow().Render()
            elif self.widget:
                self.widget.GetRenderWindow().Render()
            print("Scene rendered successfully on main thread")
        except Exception as e:
            print(f"Render error: {e}")
    
    def load_and_setup_image(self, file_path):
        """
        Load image and set up UI controls using signals for clean separation.
        This is the single point for all image operations.
        """
        try:
            # Check if heavy components are loaded
            if not hasattr(self.main_window, '_heavy_components_loaded') or not self.main_window._heavy_components_loaded:
                self.error_occurred.emit("Application components not ready. Please wait for initialization to complete.")
                return False
            
            # Load image using most efficient method
            image_data = self._load_image_efficiently(file_path)
            if image_data is None:
                return False
            
            # Store the loaded image
            self.current_image = image_data
            self.main_window.img = image_data  # Maintain compatibility
            
            # Get data type maximum and calculate thresholds
            data_max = self._get_data_type_max(image_data)
            threshold1, threshold2 = self._get_or_calculate_thresholds(file_path, image_data)

            # Reset camera
            if self.ren:
                self.ren.ResetCamera()
            
            # Emit signals for UI updates instead of direct manipulation
            self.ui_controls_setup.emit(data_max, threshold1, threshold2, hash(file_path))
            self.image_loaded.emit(image_data)
            self.rendering_completed.emit("Image loaded and ready for analysis")
            
            return True
                
        except Exception as e:
            error_msg = f"Error loading image: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def _load_image_efficiently(self, file_path):
        """Load image using the most efficient method available"""
        try:
            # Strategy 1: Use enhanced data loader if available (leverages existing cache)
            if self._has_enhanced_data_loader():
                return self.main_window.enhanced_data_loader.image_loader.load_image(file_path)
            
            # Strategy 2: Use tifffile directly if available
            if tifffile is not None:
                return tifffile.imread(file_path)
            
            # Strategy 3: Use ImageLoadingThread (fallback)
            ImageLoadingThread = self._import_image_loading_thread()
            if ImageLoadingThread is not None:
                # For synchronous loading, we'll fall back to direct import
                import tifffile as tf_module
                return tf_module.imread(file_path)
            
            raise Exception("No suitable image loading method available")
                
        except Exception as e:
            print(f"Error in efficient image loading: {e}")
            return None
    
    def _has_enhanced_data_loader(self):
        """Check if enhanced data loader with cache is available"""
        return (hasattr(self.main_window, 'enhanced_data_loader') and
                self.main_window.enhanced_data_loader and
                hasattr(self.main_window.enhanced_data_loader, 'image_loader') and
                self.main_window.enhanced_data_loader.image_loader)
    
    def _import_image_loading_thread(self):
        """Import ImageLoadingThread on-demand when needed for image loading"""
        try:
            from .threads.utility_threads import ImageLoadingThread
            return ImageLoadingThread
        except ImportError:
            try:
                from app.logic.threads.utility_threads import ImageLoadingThread
                return ImageLoadingThread
            except ImportError:
                return None
    
    def _get_data_type_max(self, image_data):
        """Get maximum value for the image data type"""
        try:
            if image_data.dtype == np.uint8:
                return 255
            elif image_data.dtype == np.uint16:
                return 65535
            else:
                return int(np.iinfo(image_data.dtype).max) if hasattr(np.iinfo(image_data.dtype), 'max') else int(np.max(image_data))
        except Exception as e:
            print(f"Error getting data type max: {e}")
            return 65535  # Safe fallback
    
    def _get_or_calculate_thresholds(self, file_path, image_data):
        """Get or calculate threshold values for the image, checking measurement DB first"""
        try:
            filename = os.path.basename(file_path)
            
            # Check if thresholds exist in measurement database
            if (hasattr(self.main_window, 'result_db') and
                not self.main_window.result_db.empty):
                existing_record = self.main_window.result_db[self.main_window.result_db['Path'] == file_path]
                if not existing_record.empty:
                    # Extract existing threshold values
                    if ('threshold1' in self.main_window.result_db.columns and
                        'threshold2' in self.main_window.result_db.columns):
                        threshold1 = int(existing_record.iloc[0]['threshold1'])
                        threshold2 = int(existing_record.iloc[0]['threshold2'])
                        print(f"Using cached thresholds for {filename}: T1={threshold1}, T2={threshold2}")
                        return threshold1, threshold2
            
            # Calculate new thresholds
            threshold1 = int(np.mean(image_data))
            threshold2 = int(np.percentile(image_data, 2))
            
            # Store thresholds in measurement database for future use
            self._store_thresholds_in_db(file_path, threshold1, threshold2)
            
            print(f"Calculated new thresholds for {filename}: T1={threshold1}, T2={threshold2}")
            return threshold1, threshold2
            
        except Exception as e:
            print(f"Error getting/calculating thresholds for {file_path}: {e}")
            # Fallback to simple calculations
            threshold1 = int(np.mean(image_data)) if image_data is not None else 1000
            threshold2 = int(np.percentile(image_data, 2)) if image_data is not None else 100
            return threshold1, threshold2
    
    def _store_thresholds_in_db(self, file_path, threshold1, threshold2):
        """Store calculated thresholds in measurement database"""
        try:
            filename = os.path.basename(file_path)
            
            # Create or update record in result_db
            new_record = {
                'ImageName': filename,
                'Path': file_path,
                'threshold1': threshold1,
                'threshold2': threshold2,
                # Add other default values as needed
                'ManualAnnotation': '',
                'Model': '',
                'ClassProb_M': 0, 'ClassProb_MM': 0, 'ClassProb_BN': 0, 'ClassProb_SN': 0,
                'MaturationScore': 0,
                'Area_1': 0, 'Vol_1': 0, 'NSI_1': 0, 'Sphericity_1': 0, 'SA_Vol_Ratio_1': 0, 'Solidity_1': 0, 'Elongation_1': 0, 'Genus_1': 0,
                'Area_2': 0, 'Vol_2': 0, 'NSI_2': 0, 'Sphericity_2': 0, 'SA_Vol_Ratio_2': 0, 'Solidity_2': 0, 'Elongation_2': 0, 'Genus_2': 0
            }
            
            # Check if record already exists
            existing_idx = self.main_window.result_db[self.main_window.result_db['Path'] == file_path].index
            if not existing_idx.empty:
                # Update existing record
                for key, value in new_record.items():
                    if key in ['threshold1', 'threshold2']:  # Only update threshold values
                        self.main_window.result_db.loc[existing_idx[0], key] = value
            else:
                # Add new record
                import pandas as pd
                self.main_window.result_db = pd.concat([self.main_window.result_db, pd.DataFrame([new_record])], ignore_index=True)
                
            print(f"Stored thresholds in database for {filename}")
            
        except Exception as e:
            print(f"Failed to store thresholds in database: {e}")
    
    def render_isosurfaces(self, threshold1, threshold2):
        """
        Render isosurfaces using legacy approach with reusable actors.
        Uses VTK marching cubes for efficient surface generation.
        """
        try:
            if not self.vtk_components_ready or vtk is None or numpy_support is None:
                print("VTK components not available for isosurface rendering")
                return False
            
            if self.current_image is None:
                print("No image loaded for isosurface rendering")
                return False
            
            if not self.ren:
                print("VTK renderer not available - ensure VTK components are set")
                return False
            
            # Create VTK image data from numpy array (legacy approach)
            vtk_data = self._create_vtk_image_data(self.current_image)
            if vtk_data is None:
                return False
            
            # Create marching cubes algorithms (legacy approach)
            contour1 = vtk.vtkMarchingCubes()
            contour1.SetInputData(vtk_data)
            contour1.SetValue(0, threshold1)
            contour1.Update()
            
            contour2 = vtk.vtkMarchingCubes()
            contour2.SetInputData(vtk_data)
            contour2.SetValue(0, threshold2)
            contour2.Update()
            
            # Update reusable mappers
            if self.mapper1:
                self.mapper1.SetInputData(contour1.GetOutput())
                self.mapper1.ScalarVisibilityOff()
            
            if self.mapper2:
                self.mapper2.SetInputData(contour2.GetOutput())
                self.mapper2.ScalarVisibilityOff()
            
            # Set actor properties (legacy colors and opacity)
            if self.actor1:
                # Nucleus - cyan with transparency
                logger.debug("Setting actor1 properties for nucleus")
                self.actor1.GetProperty().SetColor(0, 204/255, 1)
                self.actor1.GetProperty().SetOpacity(0.6)
            
            if self.actor2:
                # Membrane - white with transparency
                logger.debug("Setting actor2 properties for membrane")
                self.actor2.GetProperty().SetColor(1, 1, 1)
                self.actor2.GetProperty().SetOpacity(0.3)
            
            # Render the scene
            if self.vtkWidget:
                self.vtkWidget.GetRenderWindow().Render()
            elif self.widget:
                self.widget.GetRenderWindow().Render()
            
            print(f"Rendered isosurfaces with thresholds: {threshold1}, {threshold2}")
            self.rendering_completed.emit("Isosurface rendering completed")
            return True
            
        except Exception as e:
            error_msg = f"Error rendering isosurfaces: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def _create_vtk_image_data(self, img):
        """Create VTK image data from numpy array (legacy approach)"""
        try:
            if vtk is None or numpy_support is None:
                return None
            
            # Create vtkImageData from numpy array
            vtk_data = vtk.vtkImageData()
            vtk_data.SetDimensions(img.shape)
            
            # Copy the numpy array data to vtkImageData
            flat_data = img.flatten()
            if img.dtype == np.uint8:
                vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
                vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
            elif img.dtype == np.uint16:
                vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_SHORT, 1)
                vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT)
            else:
                print("Image data type not UINT8 or UINT16:", img.dtype)
                return None
                
            vtk_data.GetPointData().SetScalars(vtk_array)
            return vtk_data
            
        except Exception as e:
            print(f"Error creating VTK image data: {e}")
            return None
    
    def get_current_intensity_values(self):
        """Get current intensity threshold values from UI sliders"""
        try:
            value1 = 0
            value2 = 0
            
            if hasattr(self.main_window, 'horizontalSlider_intensity1'):
                value1 = self.main_window.horizontalSlider_intensity1.value()
            
            if hasattr(self.main_window, 'horizontalSlider_intensity2'):
                value2 = self.main_window.horizontalSlider_intensity2.value()
            
            return value1, value2
            
        except Exception as e:
            print(f"Error getting intensity values: {e}")
            return 0, 0
    
    def get_current_image_info(self):
        """Get information about the currently loaded image"""
        if self.current_image is not None:
            return {
                'shape': self.current_image.shape,
                'dtype': str(self.current_image.dtype),
                'min_value': float(np.min(self.current_image)),
                'max_value': float(np.max(self.current_image)),
                'mean_value': float(np.mean(self.current_image))
            }
        return None
    
    def render_histogram(self, value1, value2):
        """Render histogram with threshold lines in matplotlib canvas"""
        try:
            # Check if histogram canvas components are available through main window
            if not (hasattr(self.main_window, 'canvasHist') and self.main_window.canvasHist is not None and
                    hasattr(self.main_window, 'axHist') and self.main_window.axHist is not None):
                logger.warning("Histogram canvas not available for histogram rendering")
                return
            
            if self.current_image is None:
                logger.warning("No image loaded for histogram rendering")
                return
            
            # Matplotlib is now imported directly at the top of the file.
            
            # Clear previous histogram
            self.main_window.axHist.clear()
            
            # Create histogram
            count, _, _ = self.main_window.axHist.hist(self.current_image.ravel(), bins=256,
                                                      range=(0, int(np.iinfo(self.current_image.dtype).max-1)),
                                                      density=True, color='gray', alpha=0.7)
            
            # Set histogram properties
            self.main_window.axHist.set_title('Histogram')
            self.main_window.axHist.set_xlabel('Pixel Intensity')
            self.main_window.axHist.set_ylabel('Frequency')
            self.main_window.axHist.set_yscale("log")
            
            # Add threshold lines
            self.main_window.axHist.vlines(x=[value1, value2], ymin=0, ymax=np.max(count)*1.05,
                                          colors=[(0, 204/255, 1), (0.8, 0.8, 0.8)])
            
            # Apply tight layout with minimal padding and draw
            self.main_window.canvasHist.figure.tight_layout(pad=0.1)
            self.main_window.canvasHist.draw()
            
            logger.debug(f"Rendered histogram with threshold lines: {value1}, {value2}")
            
        except Exception as e:
            error_msg = f"Error rendering histogram: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.current_image = None
            print("Image renderer cleanup completed")
        except Exception as e:
            print(f"Error during image renderer cleanup: {e}")