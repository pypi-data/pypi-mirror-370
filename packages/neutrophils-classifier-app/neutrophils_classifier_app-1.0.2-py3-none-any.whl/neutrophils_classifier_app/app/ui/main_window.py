"""
Main window class for the Neutrophils Classifier Application.
Refactored to use mixins for better code organization.
"""
import os
import sys
import gc
import json
import time
from io import StringIO

# Import utilities
from ..utils.benchmark import log_benchmark
from ..utils.imports import import_heavy_modules, import_vtk_modules
from ..utils.logging_config import get_logger, log_debug_separator, log_method_entry, log_method_exit, log_state_check, log_error_with_context

# PyQt imports will be handled by the imports utility
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QMessageBox,
                           QProgressDialog, QDialog, QTextBrowser, QVBoxLayout,
                           QProgressBar, QLabel, QToolTip)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

# Import lightweight modules
import numpy as np
import pandas as pd

# Import from app logic
from ..logic.file_io import load_single_image_files_dialog, load_image_directory_dialog, load_image_files, load_image_directory
from ..logic.frontend_cache_manager import get_frontend_cache_manager
from ..logic.geometry_calculator import GeometryCalculator

# Import mixins
from .ui_setup_mixin import UiSetupMixin
from .ui_handlers_mixin import UiHandlersMixin
from .ui_processing_mixin import UiProcessingMixin
from .ui_data_mixin import UiDataMixin
from .ui_rendering_mixin import UiRenderingMixin
from .ui_utils_mixin import UiUtilsMixin

# These will be imported via deferred imports
tf = None
K = None
sns = None
vtk = None
numpy_support = None
QVTKRenderWindowInteractor = None
vtkRenderer = None
vtkRenderWindow = None
FigureCanvas = None
Figure = None
plt = None
tifffile = None
rescale_intensity = None
toml = None
MarkdownIt = None
texmath_plugin = None
Classifier = None
GeometricFeaturesWindow = None
EmbeddedFeaturesWindow = None
ModelLoadingThread = None
ModelInferenceThread = None
HeavyComponentsLoadingThread = None
ImageProcessingThread = None

class MainWindow(QMainWindow, UiSetupMixin, UiHandlersMixin, UiProcessingMixin, 
                 UiDataMixin, UiRenderingMixin, UiUtilsMixin):
    setup_done_signal = pyqtSignal()
    model_loaded_and_ready_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Initialize logger for this class
        self.logger = get_logger('ui.main_window')
        log_debug_separator(self.logger, "MAIN WINDOW INITIALIZATION")
        log_method_entry(self.logger, "__init__")
        
        # Initialize essential variables
        self.img = None
        self.resProb = None
        self.model = None
        self.model_config = None
        self.classifier = None  # neutrophils-core Classifier instance
        self.files = []
        self.geometric_features_window = None
        self.embedded_features_window = None
        self.geometry_calculator = None
        self.processing_thread = None
        
        # CLI arguments for auto-loading
        self._cli_args = None
        self._cli_auto_load_done = False
        
        # Import status tracking
        self._heavy_modules_loaded = False
        self._vtk_modules_loaded = False
        self._heavy_components_loaded = False
        
        # Initialize empty collections
        self.models = list()
        self.configs = list()
        
        # Initialize progress components for status bar
        self.progress_bar = None
        self.progress_label = None
        
        # Thread management for proper cleanup
        self.active_threads = []
        self.heavyLoadingThread = None
        self.imageLoadingThread = None
        
        # Initialize streamlined image manager
        self.streamlined_manager = None  # Will be initialized after UI setup
        
        # Create minimal DataFrame structure (empty, will be populated later)
        self.result_db = pd.DataFrame(columns=[
            "ImageName", "ManualAnnotation", "Model",
            "ClassProb_M", "ClassProb_MM", "ClassProb_BN", "ClassProb_SN", "MaturationScore",
            "Area_1", "Vol_1", "NSI_1", "Sphericity_1", "SA_Vol_Ratio_1", "Solidity_1", "Elongation_1", "Genus_1",
            "Area_2", "Vol_2", "NSI_2", "Sphericity_2", "SA_Vol_Ratio_2", "Solidity_2", "Elongation_2", "Genus_2",
            "Path", "threshold1", "threshold2",
        ])
        
        # Perform immediate minimal UI setup
        self._immediate_setup()
        
        # Dynamically set initial splitter position so right pane is at most 1/4 of screen width
        # but respects actual minimum size constraints from the widgets
        self._setup_splitter_layout()
        
        # Show window immediately
        self.showMaximized()
        
        # Start deferred import process
        QTimer.singleShot(100, self._start_deferred_imports_and_setup)
        
        log_method_exit(self.logger, "__init__")

    def _setup_splitter_layout(self):
        """Set up the splitter layout for optimal screen usage"""
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            screen_width = screen.size().width()
            desired_right_width = int(screen_width / 5)
            
            splitter = self.findChild(QtWidgets.QSplitter, "splitter")
            if splitter:
                # Get the actual minimum size requirements from the right pane widgets
                right_widget = splitter.widget(1) if splitter.count() > 1 else None
                min_right_width = desired_right_width  # Default fallback
                
                if right_widget:
                    # Query the actual minimum size hint from the widget
                    min_size_hint = right_widget.minimumSizeHint()
                    widget_min_width = right_widget.minimumWidth()
                    
                    # Use the larger of the size hint or explicitly set minimum width
                    if min_size_hint.isValid() and min_size_hint.width() > 0:
                        min_right_width = max(min_right_width, min_size_hint.width())
                    if widget_min_width > 0:
                        min_right_width = max(min_right_width, widget_min_width)
                
                # Use the larger of desired width or actual minimum required width
                actual_right_width = max(desired_right_width, min_right_width)
                left_width = screen_width - actual_right_width
                
                # Ensure left width is reasonable (at least 25% of screen width)
                min_left_width = int(screen_width * 0.25)
                if left_width < min_left_width:
                    left_width = min_left_width
                    actual_right_width = screen_width - left_width
                
                splitter.setSizes([left_width, actual_right_width])
                
                self.logger.debug(f"Splitter sizes set: left={left_width}px, right={actual_right_width}px "
                                f"(desired: {desired_right_width}px, min detected: {min_right_width}px, "
                                f"screen: {screen_width}px)")

    # Note: Most methods are now inherited from mixins for better code organization:
    # - UiSetupMixin: UI initialization, deferred loading, component setup
    # - UiHandlersMixin: Event handlers, user interactions, signal connections
    # - UiProcessingMixin: Background image processing and threading
    # - UiDataMixin: Database operations, threshold calculations, data management
    # - UiRenderingMixin: Image rendering, VTK operations, visualization
    # - UiUtilsMixin: Utility methods, progress display, cleanup operations