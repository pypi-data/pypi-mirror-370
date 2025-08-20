"""
Import utilities for managing deferred and critical imports.
"""
import sys
import os

from .benchmark import log_benchmark


def import_critical_pyqt_components():
    """Import essential PyQt components for immediate UI"""
    log_benchmark("CRITICAL_PYQT_IMPORTS")
    
    # Only import essential PyQt components for immediate UI
    from PyQt5 import QtWidgets, uic, QtGui
    from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QFileDialog,
                               QTableWidgetItem, QSplashScreen, QMessageBox,
                               QProgressDialog, QDialog, QTextBrowser, QVBoxLayout,
                               QProgressBar)
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent, QUrl, QThread
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
    except ImportError:
        print("Warning: PyQt5.QtWebEngineWidgets not found. Markdown rendering will be disabled.")
        QWebEngineView, QWebEngineSettings = None, None
    
    log_benchmark("CRITICAL_PYQT_IMPORTS")
    
    return {
        'QtWidgets': QtWidgets,
        'uic': uic,
        'QtGui': QtGui,
        'QApplication': QApplication,
        'QLabel': QLabel,
        'QMainWindow': QMainWindow,
        'QFileDialog': QFileDialog,
        'QTableWidgetItem': QTableWidgetItem,
        'QSplashScreen': QSplashScreen,
        'QMessageBox': QMessageBox,
        'QProgressDialog': QProgressDialog,
        'QDialog': QDialog,
        'QTextBrowser': QTextBrowser,
        'QVBoxLayout': QVBoxLayout,
        'QProgressBar': QProgressBar,
        'QIcon': QIcon,
        'Qt': Qt,
        'QTimer': QTimer,
        'pyqtSignal': pyqtSignal,
        'QEvent': QEvent,
        'QUrl': QUrl,
        'QThread': QThread,
        'QWebEngineView': QWebEngineView,
        'QWebEngineSettings': QWebEngineSettings
    }

    if QWebEngineView is None:
        del components['QWebEngineView']
        del components['QWebEngineSettings']


def import_lightweight_modules():
    """Import only lightweight, thread-safe modules immediately"""
    log_benchmark("LIGHTWEIGHT_IMPORTS")
    
    import numpy as np
    import pandas as pd
    
    log_benchmark("LIGHTWEIGHT_IMPORTS")
    
    return {
        'np': np,
        'pd': pd
    }


def import_heavy_modules():
    """Import heavy modules that can be safely imported on main thread with delay"""
    modules = {}
    
    try:
        print("DEBUG: Importing heavy modules...")
        
        print("DEBUG: Importing TensorFlow...")
        import tensorflow as tf
        print("DEBUG: TensorFlow imported.")
        
        print("DEBUG: Importing Keras backend...")
        from tensorflow.keras import backend as K
        print("DEBUG: Keras backend imported.")
        
        modules['tf'] = tf
        modules['K'] = K
        
        print("DEBUG: Importing tifffile...")
        import tifffile
        print("DEBUG: tifffile imported.")
        
        print("DEBUG: Importing scikit-image...")
        from skimage.exposure import rescale_intensity
        print("DEBUG: scikit-image imported.")
        
        print("DEBUG: Importing toml...")
        import toml
        print("DEBUG: toml imported.")
        
        print("DEBUG: Importing markdown-it...")
        from markdown_it import MarkdownIt
        print("DEBUG: markdown-it imported.")
        
        print("DEBUG: Importing mdit-py-plugins...")
        from mdit_py_plugins.texmath import texmath_plugin
        print("DEBUG: mdit-py-plugins imported.")
        
        print("DEBUG: Importing Classifier from neutrophils-core...")
        
        # Try multiple import paths for both dev and packaging environments
        Classifier = None
        import_error = None
        
        # Try standard package import first (works after proper installation)
        try:
            from neutrophils_core.models.unified_interface import Classifier
            print("DEBUG: Classifier imported via standard package path")
        except ImportError as e1:
            import_error = e1
            print(f"DEBUG: Standard import failed: {e1}")
            
            # Try sys.path manipulation for development environment
            try:
                import sys
                import os
                
                # Get the absolute path to neutrophils-core
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                neutrophils_core_path = os.path.join(current_dir, 'neutrophils-core')
                
                # Add neutrophils-core to sys.path if it exists and isn't already there
                if os.path.exists(neutrophils_core_path) and neutrophils_core_path not in sys.path:
                    sys.path.insert(0, neutrophils_core_path)
                    print(f"DEBUG: Added {neutrophils_core_path} to sys.path")
                
                # Try importing again after path modification
                from neutrophils_core.models.unified_interface import Classifier
                print("DEBUG: Classifier imported via sys.path manipulation")
                
            except ImportError as e2:
                print(f"DEBUG: sys.path import also failed: {e2}")
                
                # Final fallback: try relative import for development
                try:
                    import sys
                    import os
                    
                    # Add the neutrophils-core directory to path
                    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    neutrophils_path = os.path.join(script_dir, 'neutrophils-core')
                    
                    if neutrophils_path not in sys.path:
                        sys.path.append(neutrophils_path)
                    
                    from neutrophils_core.models.unified_interface import Classifier
                    print("DEBUG: Classifier imported via fallback relative path")
                    
                except ImportError as e3:
                    print(f"DEBUG: All import attempts failed. Final error: {e3}")
                    raise ImportError(
                        f"Could not import Classifier from neutrophils_core. "
                        f"Tried standard import ({e1}), sys.path manipulation ({e2}), "
                        f"and relative import ({e3}). "
                        f"Please ensure neutrophils-core is properly installed."
                    )
        
        if Classifier is None:
            raise ImportError("Failed to import Classifier despite no exceptions caught")
            
        print("DEBUG: Classifier imported successfully.")
        
        modules['tifffile'] = tifffile
        modules['rescale_intensity'] = rescale_intensity
        modules['toml'] = toml
        modules['MarkdownIt'] = MarkdownIt
        modules['texmath_plugin'] = texmath_plugin
        modules['Classifier'] = Classifier
        
        print("DEBUG: Importing threading classes...")
        from ..logic.threads.model_threads import (ModelLoadingThread, SingleInferenceThread, BatchInferenceThread)
        from ..logic.threads.utility_threads import HeavyComponentsLoadingThread
        print("DEBUG: Threading classes imported.")
        
        modules['ModelLoadingThread'] = ModelLoadingThread
        modules['InferenceThread'] = SingleInferenceThread
        modules['BatchInferenceThread'] = BatchInferenceThread
        modules['HeavyComponentsLoadingThread'] = HeavyComponentsLoadingThread
        
        print("DEBUG: Importing GeometricFeaturesWindow...")
        from ..ui.geometric_features_window import GeometricFeaturesWindow
        print("DEBUG: GeometricFeaturesWindow imported.")
        modules['GeometricFeaturesWindow'] = GeometricFeaturesWindow
        
        print("DEBUG: Importing EmbeddedFeaturesWindow...")
        from ..ui.embedded_features_window import EmbeddedFeaturesWindow
        print("DEBUG: EmbeddedFeaturesWindow imported.")
        modules['EmbeddedFeaturesWindow'] = EmbeddedFeaturesWindow
        
        print("DEBUG: All heavy modules imported successfully.")
        return True, modules
        
    except Exception as e:
        import traceback
        print(f"ERROR: Failed to import heavy modules: {e}")
        print(traceback.format_exc())
        return False, modules


def import_vtk_modules():
    """Import VTK modules on main thread (required for OpenGL context)"""
    modules = {}
    
    try:
        log_benchmark("DEFERRED_VTK_IMPORTS")
        print("DEBUG: Importing VTK on main thread...")
        import vtk
        import vtk.util.numpy_support as numpy_support
        from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
        from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow
        
        modules['vtk'] = vtk
        modules['numpy_support'] = numpy_support
        modules['QVTKRenderWindowInteractor'] = QVTKRenderWindowInteractor
        modules['vtkRenderer'] = vtkRenderer
        modules['vtkRenderWindow'] = vtkRenderWindow
        log_benchmark("DEFERRED_VTK_IMPORTS")
        
        
        return True, modules
        
    except Exception as e:
        print(f"ERROR: Failed to import VTK modules: {e}")
        return False, modules