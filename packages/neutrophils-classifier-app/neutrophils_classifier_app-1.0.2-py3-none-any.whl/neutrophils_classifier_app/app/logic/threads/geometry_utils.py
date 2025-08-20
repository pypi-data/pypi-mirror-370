"""
Geometry calculation utilities for VTK polydata processing.
"""
import numpy as np


def calculate_metrics_from_polydata(vtk, contour_polydata):
    """
    Calculates geometry metrics from a vtkPolyData object.
    This is a stateless function designed to be run in a thread.
    Includes proper error handling and VTK error suppression.
    """
    metrics = {}
    if not contour_polydata or contour_polydata.GetNumberOfPoints() <= 3 or contour_polydata.GetNumberOfCells() == 0:
        return metrics

    try:
        # Suppress VTK warnings/errors that can cause popup windows
        vtk_error_observer = _VTKErrorObserver()
        vtk.vtkObject.GlobalWarningDisplayOff()
        
        # Basic properties
        print("Calculating geometry metrics...")
        massProp = vtk.vtkMassProperties()
        massProp.SetInputData(contour_polydata)
        massProp.AddObserver("ErrorEvent", vtk_error_observer)
        massProp.Update()
        surface_area = massProp.GetSurfaceArea()
        volume = massProp.GetVolume()
        metrics['area'] = surface_area
        metrics['vol'] = volume
        metrics['nsi'] = massProp.GetNormalizedShapeIndex()

        # Sphericity
        print("Calculating sphericity...")
        if surface_area > 1e-9:
            metrics['sphericity'] = (np.pi**(1/3) * (6 * volume)**(2/3)) / surface_area
        else:
            metrics['sphericity'] = np.nan

        # SA-to-Volume Ratio
        print("Calculating SA-to-Volume ratio...")
        if volume > 1e-9:
            metrics['sa_vol_ratio'] = surface_area / volume
        else:
            metrics['sa_vol_ratio'] = np.nan

        # Solidity - PROTECTED WITH ERROR HANDLING AND TIMEOUT
        print("Calculating solidity...")
        try:
            # Use safer convex hull calculation with error handling
            metrics['solidity'] = _calculate_solidity_safe(vtk, contour_polydata, volume, vtk_error_observer)
        except Exception as e:
            print(f"Warning: Solidity calculation failed: {e}")
            metrics['solidity'] = np.nan

        # Elongation
        print("Calculating elongation...")
        try:
            bounds = contour_polydata.GetBounds()
            dims = [bounds[1]-bounds[0], bounds[3]-bounds[2], bounds[5]-bounds[4]]
            dims_positive = [d for d in dims if d > 1e-9]
            if len(dims_positive) == 3:
                metrics['elongation'] = max(dims_positive) / min(dims_positive)
            else:
                metrics['elongation'] = np.nan
        except Exception as e:
            print(f"Warning: Elongation calculation failed: {e}")
            metrics['elongation'] = np.nan

        # Genus - PROTECTED WITH ERROR HANDLING
        print("Calculating genus...")
        try:
            metrics['genus'] = _calculate_genus_safe(vtk, contour_polydata, vtk_error_observer)
        except Exception as e:
            print(f"Warning: Genus calculation failed: {e}")
            metrics['genus'] = np.nan

        print("Geometry metrics calculation complete.")
        print("Metrics:", metrics)

        return metrics
        
    except Exception as e:
        print(f"Error in geometry metrics calculation: {e}")
        # Return partial metrics if possible
        return metrics
    finally:
        # Re-enable VTK warnings
        vtk.vtkObject.GlobalWarningDisplayOn()


def _calculate_solidity_safe(vtk, contour_polydata, volume, error_observer):
    """
    Safely calculate solidity with timeout and error handling.
    The vtkDelaunay3D operation is known to hang on complex geometry.
    """
    try:
        # Check if geometry is too complex (heuristic check)
        num_points = contour_polydata.GetNumberOfPoints()
        num_cells = contour_polydata.GetNumberOfCells()
        
        # Skip convex hull for very complex geometries to prevent hanging
        if num_points > 10000 or num_cells > 20000:
            print(f"Warning: Skipping solidity for complex geometry (points: {num_points}, cells: {num_cells})")
            return np.nan
        
        # Create Delaunay3D filter with error handling
        delaunay = vtk.vtkDelaunay3D()
        delaunay.SetInputData(contour_polydata)
        delaunay.AddObserver("ErrorEvent", error_observer)
        delaunay.AddObserver("WarningEvent", error_observer)
        
        # Set conservative parameters to prevent hanging
        delaunay.SetTolerance(0.001)
        delaunay.SetAlpha(0.0)  # Use all points
        delaunay.BoundingTriangulationOff()
        
        print("Running Delaunay3D triangulation...")
        delaunay.Update()
        
        # Check if Delaunay failed
        if error_observer.has_errors:
            print("Warning: Delaunay3D triangulation had errors")
            return np.nan
        
        # Get surface of convex hull
        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputConnection(delaunay.GetOutputPort())
        surface_filter.AddObserver("ErrorEvent", error_observer)
        surface_filter.Update()
        
        convex_hull_polydata = surface_filter.GetOutput()
        
        if convex_hull_polydata and convex_hull_polydata.GetNumberOfPoints() > 3:
            massPropHull = vtk.vtkMassProperties()
            massPropHull.SetInputData(convex_hull_polydata)
            massPropHull.AddObserver("ErrorEvent", error_observer)
            massPropHull.Update()
            
            convex_hull_volume = massPropHull.GetVolume()
            if convex_hull_volume > 1e-9:
                solidity = volume / convex_hull_volume
                # Sanity check: solidity should be <= 1.0
                if solidity <= 1.0:
                    return solidity
                else:
                    print(f"Warning: Invalid solidity value {solidity} > 1.0")
                    return np.nan
            else:
                return np.nan
        else:
            return np.nan
            
    except Exception as e:
        print(f"Error in solidity calculation: {e}")
        return np.nan


def _calculate_genus_safe(vtk, contour_polydata, error_observer):
    """
    Safely calculate genus with error handling.
    """
    try:
        V = contour_polydata.GetNumberOfPoints()
        F = contour_polydata.GetNumberOfPolys()
        
        # Boundary edge detection
        boundary_edge_filter = vtk.vtkFeatureEdges()
        boundary_edge_filter.SetInputData(contour_polydata)
        boundary_edge_filter.BoundaryEdgesOn()
        boundary_edge_filter.FeatureEdgesOff()
        boundary_edge_filter.ManifoldEdgesOff()
        boundary_edge_filter.NonManifoldEdgesOff()
        boundary_edge_filter.AddObserver("ErrorEvent", error_observer)
        boundary_edge_filter.Update()
        
        if boundary_edge_filter.GetOutput().GetNumberOfLines() == 0:
            # No boundary edges, proceed with genus calculation
            edge_filter = vtk.vtkFeatureEdges()
            edge_filter.SetInputData(contour_polydata)
            edge_filter.BoundaryEdgesOff()
            edge_filter.FeatureEdgesOff()
            edge_filter.ManifoldEdgesOn()
            edge_filter.NonManifoldEdgesOn()
            edge_filter.AddObserver("ErrorEvent", error_observer)
            edge_filter.Update()
            
            E = edge_filter.GetOutput().GetNumberOfLines()
            
            connectivity = vtk.vtkConnectivityFilter()
            connectivity.SetInputData(contour_polydata)
            connectivity.SetExtractionModeToAllRegions()
            connectivity.AddObserver("ErrorEvent", error_observer)
            connectivity.Update()
            
            C = connectivity.GetNumberOfExtractedRegions()
            
            if V > 0 and C > 0:
                euler_char = V - E + F
                genus_val = C - (euler_char / 2.0)
                return int(round(genus_val))
            else:
                return np.nan
        else:
            return np.nan
            
    except Exception as e:
        print(f"Error in genus calculation: {e}")
        return np.nan


class _VTKErrorObserver:
    """
    VTK error observer to capture and suppress error dialogs.
    Prevents VTK error windows from blocking the thread.
    """
    def __init__(self):
        self.has_errors = False
        self.error_messages = []
    
    def __call__(self, obj, event, message):
        self.has_errors = True
        self.error_messages.append(f"{event}: {message}")
        print(f"VTK {event}: {message}")
        # Return True to suppress the error dialog
        return True

def _format_metric_key(key):
    """Formats the metric key for display in the table."""
    if key == 'nsi':
        return 'NSI'
    elif key == 'sa_vol_ratio':
        return 'SA_Vol_Ratio'
    else:
        return key.capitalize()


# Import processing functions from neutrophils-core
try:
    from neutrophils_core.loader.ImageDataGenerator2D import pad_image_2d as pad_image, crop_center_2d as crop_center
except ImportError:
    print("WARNING: neutrophils-core processing functions not available, using fallback")
    def pad_image(img, padded_size=[96, 96]):
        """Fallback padding function"""
        current_shape = img.shape
        pad_width = []
        for i in range(len(current_shape)):
            if i < 2:  # Only pad height and width
                target_size = padded_size[i] if i < len(padded_size) else current_shape[i]
                if current_shape[i] < target_size:
                    pad_before = (target_size - current_shape[i]) // 2
                    pad_after = target_size - current_shape[i] - pad_before
                    pad_width.append((pad_before, pad_after))
                else:
                    pad_width.append((0, 0))
            else:
                pad_width.append((0, 0))
        return np.pad(img, pad_width, mode='constant', constant_values=0)
    
    def crop_center(img, crop_size=[96, 96]):
        """Fallback center cropping function"""
        shape = img.shape
        start_indices = []
        for i in range(min(len(shape), len(crop_size))):
            start = max((shape[i] - crop_size[i]) // 2, 0)
            start_indices.append(start)
        
        if len(shape) == 2:
            return img[start_indices[0]:start_indices[0] + crop_size[0],
                      start_indices[1]:start_indices[1] + crop_size[1]]
        elif len(shape) == 3:
            return img[start_indices[0]:start_indices[0] + crop_size[0],
                      start_indices[1]:start_indices[1] + crop_size[1], :]
        else:
            return img