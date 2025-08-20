"""
Geometry Calculator for VTK Contour Analysis
Handles calculation of various geometric metrics from VTK polydata objects.
"""
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
import logging

# Setup logging
logger = logging.getLogger(__name__)

# VTK imports will be handled dynamically
vtk = None

class GeometryCalculator(QObject):
    """
    Calculates various geometry metrics for VTK polydata objects (from marching cubes).
    Emits signals for UI updates and provides dictionary of calculated metrics.
    """
    
    # Signals for communication with UI
    metrics_calculated = pyqtSignal(dict, str)  # metrics_dict, label_suffix
    calculation_error = pyqtSignal(str, str)    # error_message, label_suffix
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.vtk_available = False
        self._init_vtk_components()
        
        # Metric information for tooltips and documentation
        self.metric_info = getattr(main_window, 'metric_info', {})
    
    def _init_vtk_components(self):
        """Initialize VTK components using the main window's existing VTK modules"""
        try:
            global vtk
            
            # Access the VTK modules already imported by main_window
            if hasattr(self.main_window, '__dict__'):
                # Get the module globals from main_window's context
                main_module = self.main_window.__class__.__module__
                import sys
                if main_module in sys.modules:
                    module_globals = sys.modules[main_module].__dict__
                    vtk = module_globals.get('vtk')
            
            # Fallback: try direct import
            if vtk is None:
                try:
                    import vtk as vtk_module
                    vtk = vtk_module
                except ImportError:
                    logger.warning("VTK modules not available for geometry calculations")
                    return
            
            self.vtk_available = (vtk is not None)
            if self.vtk_available:
                logger.info("VTK components ready for geometry calculations")
            
        except Exception as e:
            logger.error(f"Error initializing VTK components for geometry calculator: {e}")
    
    def update_ui_with_metrics(self, metrics, label_suffix):
        """
        Updates the UI labels with pre-calculated geometry metrics.
        """
        label_map = { 
            "area": "label_area", "vol": "label_vol", "nsi": "label_nsi",
            "sphericity": "label_sphericity", "sa_vol_ratio": "label_sa_vol_ratio",
            "solidity": "label_solidity", "elongation": "label_elongation",
            "genus": "label_genus"
        }

        for metric_key, value in metrics.items():
            try:
                label_widget_name = f"{label_map[metric_key]}{label_suffix}"
                label_widget = getattr(self.main_window, label_widget_name)
                
                if np.isnan(value):
                    value_str = "N/A"
                elif isinstance(value, int):
                    value_str = str(value)
                else:
                    value_str = "{:.3f}".format(value)

                label_widget.setText(value_str)

                metric_info_data = self.metric_info.get(metric_key)
                if metric_info_data:
                    label_widget.setToolTip(metric_info_data["tooltip"])
                    label_widget.setProperty("metric_key", metric_key)
                    if not hasattr(label_widget, "_event_filter_installed") or not label_widget._event_filter_installed:
                        label_widget.installEventFilter(self.main_window)
                        label_widget._event_filter_installed = True
                else:
                    label_widget.setToolTip("")
                    label_widget.setProperty("metric_key", None)

            except AttributeError:
                logger.warning(f"QLabel '{label_widget_name}' not found in UI.")
            except KeyError:
                logger.warning(f"Metric key '{metric_key}' not found in label_map for UI update.")
        
        self.metrics_calculated.emit(metrics, label_suffix)

    def calculate_and_set_geometry_metrics(self, contour_polydata, label_suffix):
        """
        Calculates various geometry metrics for a given vtkPolyData object (from marching cubes),
        updates the corresponding QLabels in the UI (with tooltips and event filters for double-click), 
        and returns a dictionary of the metrics.
        """
        metrics = {}
        
        # label_map maps internal metric keys to the base name of the QLabel widgets in the UI
        label_map = { 
            "area": "label_area", "vol": "label_vol", "nsi": "label_nsi",
            "sphericity": "label_sphericity", "sa_vol_ratio": "label_sa_vol_ratio",
            "solidity": "label_solidity", "elongation": "label_elongation",
            "genus": "label_genus"
        }

        def set_label_text(metric_key, value_str, numerical_value=None):
            try:
                label_widget_name = f"{label_map[metric_key]}{label_suffix}"
                label_widget = getattr(self.main_window, label_widget_name)
                label_widget.setText(value_str)
                
                # Set tooltip and prepare for double-click documentation
                metric_info_data = self.metric_info.get(metric_key)
                if metric_info_data:
                    label_widget.setToolTip(metric_info_data["tooltip"])
                    label_widget.setProperty("metric_key", metric_key) 
                    # Check if event filter is already installed to prevent multiple installations
                    if not hasattr(label_widget, "_event_filter_installed") or not label_widget._event_filter_installed:
                        label_widget.installEventFilter(self.main_window)
                        label_widget._event_filter_installed = True # Mark as installed
                else:
                    label_widget.setToolTip("")
                    label_widget.setProperty("metric_key", None)

            except AttributeError:
                logger.warning(f"QLabel '{label_widget_name}' not found in UI. Value was: {value_str}")
            except KeyError:
                logger.warning(f"Metric key '{metric_key}' not found in label_map for UI update.")
            
            metrics[metric_key] = numerical_value if numerical_value is not None else np.nan

        try:
            if not self.vtk_available or vtk is None:
                logger.error("VTK not available for geometry calculations")
                self.calculation_error.emit("VTK not available for geometry calculations", label_suffix)
                return {}
            
            if contour_polydata and contour_polydata.GetNumberOfPoints() > 3 and contour_polydata.GetNumberOfCells() > 0:
                # Calculate basic geometric properties using VTK
                massProp = vtk.vtkMassProperties()
                massProp.SetInputData(contour_polydata)
                massProp.Update()

                surface_area = massProp.GetSurfaceArea()
                volume = massProp.GetVolume()
                nsi = massProp.GetNormalizedShapeIndex()

                set_label_text("area", "{:.2f}".format(surface_area), surface_area)
                set_label_text("vol", "{:.2f}".format(volume), volume)
                set_label_text("nsi", "{:.2f}".format(nsi), nsi)

                # Sphericity: (pi^(1/3) * (6*V)^(2/3)) / A
                if surface_area > 1e-9: # Avoid division by zero for very small/degenerate surfaces
                    sphericity_val = (np.pi**(1/3) * (6 * volume)**(2/3)) / surface_area
                    set_label_text("sphericity", "{:.3f}".format(sphericity_val), sphericity_val)
                else:
                    set_label_text("sphericity", "N/A (SA~0)", np.nan)

                # Surface Area to Volume Ratio
                if volume > 1e-9: # Avoid division by zero
                    sa_vol_ratio_val = surface_area / volume
                    set_label_text("sa_vol_ratio", "{:.2f}".format(sa_vol_ratio_val), sa_vol_ratio_val)
                else:
                    set_label_text("sa_vol_ratio", "N/A (Vol~0)", np.nan)

                # Solidity (Convexity Measure): Volume / ConvexHullVolume
                # The vtkHull filter can sometimes produce a 2D surface with no volume.
                # Using vtkDelaunay3D is more robust for creating a solid 3D hull.
                
                # Use vtkDelaunay3D to create a tetrahedral mesh of the convex hull.
                delaunay = vtk.vtkDelaunay3D()
                delaunay.SetInputData(contour_polydata)
                delaunay.Update()

                # Extract the surface of the Delaunay triangulation (the convex hull).
                surface_filter = vtk.vtkDataSetSurfaceFilter()
                surface_filter.SetInputConnection(delaunay.GetOutputPort())
                surface_filter.Update()
                
                convex_hull_polydata = surface_filter.GetOutput()
                
                if convex_hull_polydata and convex_hull_polydata.GetNumberOfPoints() > 3 and convex_hull_polydata.GetNumberOfPolys() > 0:
                    massPropHull = vtk.vtkMassProperties()
                    massPropHull.SetInputData(convex_hull_polydata)
                    massPropHull.Update()
                    convex_hull_volume = massPropHull.GetVolume()
                    if convex_hull_volume > 1e-9:
                        logger.debug(f"Vol: {volume}")
                        logger.debug(f"CHV: {convex_hull_volume}")
                        solidity_val = volume / convex_hull_volume
                        set_label_text("solidity", "{:.3f}".format(solidity_val), solidity_val)
                    else:
                        set_label_text("solidity", "N/A (CHV~0)", np.nan)
                else:
                    set_label_text("solidity", "N/A (Hull Fail)", np.nan)
                
                # Elongation: max_dim / min_dim of bounding box
                bounds = contour_polydata.GetBounds()
                if bounds: 
                    dims = [bounds[1]-bounds[0], bounds[3]-bounds[2], bounds[5]-bounds[4]]
                    # Filter out non-positive dimensions to avoid errors with flat/degenerate objects
                    dims_positive = [d for d in dims if d > 1e-9] 
                    
                    if len(dims_positive) == 3: # Standard 3D case
                        elongation_val = max(dims_positive) / min(dims_positive)
                        set_label_text("elongation", "{:.2f}".format(elongation_val), elongation_val)
                    elif len(dims_positive) > 0: # Degenerate (e.g., 2D projection, line)
                         set_label_text("elongation", "N/A (Degen.)", np.nan)
                    else: # All dimensions are effectively zero
                        set_label_text("elongation", "N/A (ZeroDim)", np.nan)
                else: 
                    set_label_text("elongation", "N/A (NoBounds)", np.nan)

                # Genus (Topological): G = C - (V - E + F)/2
                V = contour_polydata.GetNumberOfPoints()
                F = contour_polydata.GetNumberOfPolys() # Number of cells/faces

                # Check if the surface is enclosed (no boundary edges)
                boundary_edge_filter = vtk.vtkFeatureEdges()
                boundary_edge_filter.SetInputData(contour_polydata)
                boundary_edge_filter.BoundaryEdgesOn()
                boundary_edge_filter.FeatureEdgesOff()
                boundary_edge_filter.ManifoldEdgesOff()
                boundary_edge_filter.NonManifoldEdgesOff()
                boundary_edge_filter.Update()
                num_boundary_edges = boundary_edge_filter.GetOutput().GetNumberOfLines()

                if num_boundary_edges == 0:
                    # Count edges using vtkFeatureEdges
                    edge_filter = vtk.vtkFeatureEdges()
                    edge_filter.SetInputData(contour_polydata)
                    edge_filter.BoundaryEdgesOff()
                    edge_filter.FeatureEdgesOff()
                    edge_filter.ManifoldEdgesOn()
                    edge_filter.NonManifoldEdgesOn()
                    edge_filter.Update()
                    E = edge_filter.GetOutput().GetNumberOfLines()

                    # Count connected components
                    connectivity = vtk.vtkConnectivityFilter()
                    connectivity.SetInputData(contour_polydata)
                    connectivity.SetExtractionModeToAllRegions()
                    connectivity.Update()
                    C = connectivity.GetNumberOfExtractedRegions()

                    if V > 0 and C > 0 : # Basic check for a valid mesh
                        # Euler characteristic: V - E + F
                        euler_char = V - E + F
                        # Genus: G = C - euler_char / 2.0 for orientable surfaces
                        genus_val = C - (euler_char / 2.0)
                        # Genus should be an integer value
                        genus_val_int = int(round(genus_val))
                        set_label_text("genus", str(genus_val_int), genus_val_int)
                    else:
                        set_label_text("genus", "N/A (Mesh Err)", np.nan)
                else:
                    set_label_text("genus", "N/A (Not Closed)", np.nan)

            else: # contour_polydata is None or invalid
                for metric_key in label_map.keys():
                    set_label_text(metric_key, "N/A", np.nan)
            
            # Emit signal with calculated metrics
            self.metrics_calculated.emit(metrics, label_suffix)
            logger.debug(f"Geometry metrics calculated for suffix '{label_suffix}': {len(metrics)} metrics")
            
        except Exception as e:
            error_msg = f"Error calculating geometry metrics: {str(e)}"
            logger.error(error_msg)
            self.calculation_error.emit(error_msg, label_suffix)
            
            # Set all metrics to N/A on error
            for metric_key in label_map.keys():
                set_label_text(metric_key, "Error", np.nan)
        
        return metrics
    
    def get_contour_polydata_from_renderer(self, threshold_value):
        """
        Fallback method to extract contour polydata using marching cubes.
        This is used when renderer surfaces are not available.
        Note: The main window now directly accesses renderer surfaces for better performance.
        """
        try:
            logger.info(f"Using fallback contour calculation for threshold {threshold_value}")
            
            if not self.vtk_available or vtk is None:
                logger.error("VTK not available for contour extraction")
                return None
            
            # Get current image from main window or image renderer
            current_image = None
            if hasattr(self.main_window, 'image_renderer') and self.main_window.image_renderer:
                current_image = self.main_window.image_renderer.current_image
            elif hasattr(self.main_window, 'img') and self.main_window.img is not None:
                current_image = self.main_window.img
            
            if current_image is None:
                logger.warning("No image available for fallback contour calculation")
                return None
            
            # Create VTK image data from numpy array
            vtk_data = self._create_vtk_image_data(current_image)
            if vtk_data is None:
                return None
            
            # Create marching cubes algorithm
            contour = vtk.vtkMarchingCubes()
            contour.SetInputData(vtk_data)
            contour.SetValue(0, threshold_value)
            contour.Update()
            
            return contour.GetOutput()
            
        except Exception as e:
            logger.error(f"Error in fallback contour calculation: {e}")
            return None
    
    def _create_vtk_image_data(self, img):
        """Create VTK image data from numpy array"""
        try:
            if vtk is None:
                return None
            
            # Access numpy_support from main window's context
            numpy_support = None
            if hasattr(self.main_window, '__dict__'):
                main_module = self.main_window.__class__.__module__
                import sys
                if main_module in sys.modules:
                    module_globals = sys.modules[main_module].__dict__
                    numpy_support = module_globals.get('numpy_support')
            
            if numpy_support is None:
                try:
                    from vtkmodules.util import numpy_support
                except ImportError:
                    logger.error("numpy_support not available for VTK image data creation")
                    return None
            
            # Create vtkImageData from numpy array
            vtk_data = vtk.vtkImageData()
            vtk_data.SetDimensions(img.shape)
            vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
            
            # Copy the numpy array data to vtkImageData
            flat_data = img.flatten()
            if img.dtype == np.uint8:
                vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
            elif img.dtype == np.uint16:
                vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT)
            else:
                logger.error(f"Image data type not supported: {img.dtype}")
                return None
                
            vtk_data.GetPointData().SetScalars(vtk_array)
            return vtk_data
            
        except Exception as e:
            logger.error(f"Error creating VTK image data: {e}")
            return None
def cleanup(self):
        """Clean up resources"""
        try:
            self.main_window = None
            self.metric_info = {}
            logger.info("Geometry calculator cleanup completed")
        except Exception as e:
            logger.error(f"Error during geometry calculator cleanup: {e}")