"""
UI Setup Mixin for the MainWindow.
Handles the initialization and setup of UI components, including deferred loading.
"""
import os
from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg

from ..utils.benchmark import log_benchmark
from ..utils.resource_loader import get_ui_file_path, get_asset_path
from .status_lamp import StatusLamp

class UiSetupMixin:
    """Mixin containing UI setup methods for MainWindow."""

    def _immediate_setup(self):
        """Minimal UI setup to show window immediately"""
        # Load basic UI files using packaging utilities
        ui_path = get_ui_file_path('mainWindow.ui')
        log_benchmark("MAIN_UI_LOADING")
        self.ui_main = uic.loadUi(str(ui_path), self)
        log_benchmark("MAIN_UI_LOADING")

        ui_preferences_path = get_ui_file_path('preferences.ui')
        self.ui_preferences = uic.loadUi(str(ui_preferences_path), QtWidgets.QDialog())
        if hasattr(Qt, 'WindowContextHelpButtonHint'):
            self.ui_preferences.setWindowFlags(self.ui_preferences.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Initialize preferences manager
        self._init_preferences_manager()

        # Set basic window properties
        from PyQt5.QtGui import QIcon
        # Use packaging utilities for icon loading
        icon_path = get_asset_path('icon.png')
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            self.ui_preferences.setWindowIcon(QIcon(str(icon_path)))
        else:
            print(f"WARNING: Icon not found at {icon_path}")
        
        # Initialize status bar with progress bar
        self._setup_status_bar()

        # Set up essential signal connections that don't require heavy components
        self._setup_basic_connections()

        # Initially disable all image loading and processing controls
        self._set_image_controls_enabled(False)

    def _setup_status_bar(self):
        """Set up status bar with model status on the left and progress on the right"""
        # Create progress label for status messages
        self.progress_label = QtWidgets.QLabel("Starting application...")
        self.progress_label.setVisible(False)
        self.progress_label.setMinimumWidth(350)
        
        # Create progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setRange(0, 100)

        # Add both widgets to the right side of status bar (label first, then progress bar)
        self.statusBar().addPermanentWidget(self.progress_label)
        self.statusBar().addPermanentWidget(self.progress_bar)

        # Add a separator after the model status lamp
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.statusBar().addPermanentWidget(separator)

        # Create and add the status lamp and its label to the right side (persistent)
        self.status_lamp_label = QtWidgets.QLabel("Model Status:")
        self.status_lamp = StatusLamp()
        self.statusBar().addPermanentWidget(self.status_lamp_label)
        self.statusBar().addPermanentWidget(self.status_lamp)

    def _start_deferred_imports_and_setup(self):
        """Start the deferred import and setup process"""
        self._show_progress(0, "Initializing application...")
        
        # Import heavy modules first
        self._show_progress(10, "Loading TensorFlow and core ML modules...")
        
        from ..utils.imports import import_heavy_modules
        success, modules = import_heavy_modules()
        if success:
            self._heavy_modules_loaded = True
            self._update_global_modules(modules)
            self._show_progress(30, "Core ML modules loaded successfully")
        else:
            self._show_progress(30, "Warning: Some heavy modules failed to load")
        
        # Import VTK modules on main thread
        self._show_progress(40, "Loading VTK visualization modules...")
        
        from ..utils.imports import import_vtk_modules
        success, vtk_modules = import_vtk_modules()
        if success:
            self._vtk_modules_loaded = True
            self._update_global_vtk_modules(vtk_modules)
            self._show_progress(60, "VTK visualization modules loaded successfully")
        else:
            self._show_progress(60, "Warning: VTK modules failed to load")
        
        # Start component initialization
        self._show_progress(70, "Initializing application components...")
        
        # Start deferred setup after imports are complete
        QTimer.singleShot(100, self._deferred_setup)

    def _deferred_setup(self):
        """Load heavy components in background"""
        try:
            if not hasattr(self, 'HeavyComponentsLoadingThread') or self.HeavyComponentsLoadingThread is None:
                self.logger.warning("HeavyComponentsLoadingThread not available, falling back to main thread setup")
                self._create_components_on_main_thread()
                return
            
            self.logger.debug("Starting HeavyComponentsLoadingThread")
            self.heavyLoadingThread = self.HeavyComponentsLoadingThread()
            self.active_threads.append(self.heavyLoadingThread)
            
            self.heavyLoadingThread.progress_signal.connect(self._update_loading_progress)
            self.heavyLoadingThread.components_loaded_signal.connect(self._on_heavy_components_loaded)
            self.heavyLoadingThread.finished.connect(lambda: self._on_thread_finished(self.heavyLoadingThread))
            
            self.heavyLoadingThread.start()
            
        except Exception as e:
            self.logger.error(f"Exception in _deferred_setup: {e}")
            self._create_components_on_main_thread()

    def _create_components_on_main_thread(self):
        """Fallback method to create all components on main thread when threading fails"""
        try:
            self._show_progress(80, "Initializing fallback mode")
            
            self.metric_info = {}
            self.models = []
            self.configs = []
            
            self._show_progress(85, "Discovering available models")
            discovered_models = self._discover_models_sync()
            self.models, self.configs = discovered_models
            
            for model_path in self.models:
                model_name = os.path.splitext(os.path.basename(model_path))[0]
                self.comboBoxModel.addItem(model_name)
            
            if len(self.models) > 0:
                self.comboBoxModel.setCurrentIndex(0)
            
            self._show_progress(90, "Creating VTK visualization components")
            vtk_components = self._setup_vtk_components_main_thread()
            
            self._show_progress(95, "Creating plotting components")
            plotting_components = self._setup_plotting_components_main_thread()
            
            self._on_heavy_components_loaded(((self.metric_info, (self.models, self.configs))), vtk_components, plotting_components)
            
            # Trigger model loading after components are set up
            if len(self.models) > 0:
                self.model_changed()
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to create components on main thread: {e}")
            self._hide_progress()
            self.progress_label.setText("Error: Failed to initialize components")
            self.progress_label.setVisible(True)

    def _on_heavy_components_loaded(self, components, vtk_components=None, plotting_components=None):
        """Handle completion of heavy component loading"""
        log_benchmark("HEAVY_COMPONENTS_LOADING")
        
        (self.metric_info, discovered_models) = components
        
        if vtk_components is None:
            vtk_components = self._setup_vtk_components_main_thread()
        if plotting_components is None:
            plotting_components = self._setup_plotting_components_main_thread()
        
        (self.actor1, self.actor2, self.mapper1, self.mapper2,
         self.widget, self.vtkWidget, self.ren, self.iren) = vtk_components
        
        (self.imageView, self.hist_plot_widget, self.canvasProb, self.axProb) = plotting_components
        
        layout_vtk, layout_slides, layout_hist, layoutProb = self._setup_canvas_layouts_main_thread(vtk_components, plotting_components)
        self.frame_vtk.setLayout(layout_vtk)
        self.frameSlide.setLayout(layout_slides)
        self.framePlotHist.setLayout(layout_hist)
        self.framePlot.setLayout(layoutProb)
        
        self.models, self.configs = discovered_models
        for model_path in self.models:
            model_name = os.path.splitext(os.path.basename(model_path))[0]
            self.comboBoxModel.addItem(model_name)
        
        if len(self.models) > 0:
            self.comboBoxModel.setCurrentIndex(0)
        
        self._setup_heavy_component_connections()
        
        # Manually trigger model loading for the first model, if available
        if len(self.models) > 0:
            self.model_changed()
        
        self._heavy_components_loaded = True
        
        self._init_enhanced_data_loader()
        self._init_image_renderer()
        self._init_geometry_calculator()
        self._init_feature_windows()

        # Pass VTK components to the image renderer
        if self.image_renderer and vtk_components:
            self.image_renderer.set_vtk_components(*vtk_components)
            
        # Connect image renderer signals to UI handlers
        self._connect_image_renderer_signals()
        
        # Initialize streamlined image manager after all components are ready
        self._init_streamlined_manager()
        
        self.progress_label.setText("Application ready")
        self.progress_label.setVisible(True)
        
    def _init_streamlined_manager(self):
        """Initialize the streamlined image manager with all required components"""
        try:
            print("DEBUG INIT: Starting _init_streamlined_manager")
            
            # DIAGNOSTIC: Check if components initialization was successful
            print(f"DEBUG INIT: Checking component availability before StreamlinedImageManager creation...")
            
            # Initialize all streamlined workflow components
            self._init_streamlined_components()
            
            # DIAGNOSTIC: Verify components were created successfully
            print(f"DEBUG INIT: fast_image_loader: {getattr(self, 'fast_image_loader', 'NOT_SET')}")
            print(f"DEBUG INIT: synchronous_vtk_renderer: {getattr(self, 'synchronous_vtk_renderer', 'NOT_SET')}")
            print(f"DEBUG INIT: secondary_renderers: {getattr(self, 'secondary_renderers', 'NOT_SET')}")
            print(f"DEBUG INIT: ui_state_manager: {getattr(self, 'ui_state_manager', 'NOT_SET')}")
            
            # Create StreamlinedImageManager even if some components failed
            print("DEBUG INIT: Creating StreamlinedImageManager")
            try:
                from ..logic.streamlined_image_manager import StreamlinedImageManager
                self.streamlined_manager = StreamlinedImageManager(main_window=self)
                print(f"DEBUG INIT: StreamlinedImageManager created: {self.streamlined_manager}")
                
                # Set components after initialization (None values are acceptable)
                print("DEBUG INIT: Setting components on StreamlinedImageManager")
                self.streamlined_manager.set_components(
                    fast_image_loader=getattr(self, 'fast_image_loader', None),
                    vtk_renderer=getattr(self, 'synchronous_vtk_renderer', None),  # Use the new synchronous renderer
                    secondary_renderers=getattr(self, 'secondary_renderers', None),
                    ui_state_manager=getattr(self, 'ui_state_manager', None),
                    background_calculator=getattr(self, 'background_calculator', None)
                )
                print("DEBUG INIT: Components set successfully")
                
                # DIAGNOSTIC: Verify components were set
                print(f"DEBUG INIT: StreamlinedManager components after setting:")
                print(f"  - fast_image_loader: {self.streamlined_manager.fast_image_loader}")
                print(f"  - vtk_renderer: {self.streamlined_manager.vtk_renderer}")
                print(f"  - secondary_renderers: {self.streamlined_manager.secondary_renderers}")
                print(f"  - ui_state_manager: {self.streamlined_manager.ui_state_manager}")
                print(f"  - background_calculator: {self.streamlined_manager.background_calculator}")
                
                # Connect streamlined manager signals
                print("DEBUG INIT: Connecting streamlined manager signals")
                self.streamlined_manager.image_loaded.connect(self._on_streamlined_image_loaded)
                self.streamlined_manager.rendering_completed.connect(self._on_streamlined_rendering_complete)
                self.streamlined_manager.error_occurred.connect(self._on_streamlined_error)
                
                # Connect database_updated signal to refresh embedded features window
                self.streamlined_manager.database_updated.connect(self._on_database_updated)
                
                # Connect UI state manager signals for loading indicators (if available)
                if hasattr(self, 'ui_state_manager') and self.ui_state_manager:
                    print("DEBUG INIT: Connecting UI state manager signals")
                    self.ui_state_manager.loading_state_changed.connect(self._on_loading_state_changed)
                    self.ui_state_manager.ui_elements_updated.connect(self._on_ui_elements_updated)
                else:
                    print("DEBUG INIT: WARNING - UI state manager not available for signal connections")
                
                print("DEBUG INIT: StreamlinedImageManager initialized successfully!")
                print(f"DEBUG INIT: Final streamlined_manager: {self.streamlined_manager}")
                self.logger.info("StreamlinedImageManager initialized successfully")
                
            except ImportError as e:
                print(f"DEBUG INIT: ImportError creating StreamlinedImageManager: {e}")
                print("DEBUG INIT: StreamlinedImageManager import failed - setting to None")
                self.streamlined_manager = None
            except Exception as e:
                print(f"DEBUG INIT: ERROR creating StreamlinedImageManager: {e}")
                import traceback
                print(f"DEBUG INIT: StreamlinedImageManager creation traceback: {traceback.format_exc()}")
                self.streamlined_manager = None
            
            # Final diagnostic
            if self.streamlined_manager is not None:
                print("DEBUG INIT: StreamlinedImageManager initialization SUCCESSFUL")
            else:
                print("DEBUG INIT: StreamlinedImageManager initialization FAILED - will use legacy workflow")
            
        except Exception as e:
            print(f"DEBUG INIT: CRITICAL ERROR - Failed to initialize StreamlinedImageManager: {e}")
            import traceback
            print(f"DEBUG INIT: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Failed to initialize StreamlinedImageManager: {e}")
            self.streamlined_manager = None
            print(f"DEBUG INIT: streamlined_manager set to None due to critical error")

    def _init_streamlined_components(self):
        """Initialize all components required for the streamlined workflow"""
        try:
            print("DEBUG INIT: Initializing streamlined workflow components")
            
            # Initialize FastImageLoader with error handling for missing dependencies
            print("DEBUG INIT: Creating FastImageLoader")
            try:
                from ..logic.fast_image_loader import FastImageLoader
                self.fast_image_loader = FastImageLoader()
                print(f"DEBUG INIT: FastImageLoader created successfully: {self.fast_image_loader}")
            except ImportError as e:
                print(f"DEBUG INIT: ImportError creating FastImageLoader: {e}")
                print("DEBUG INIT: FastImageLoader dependencies missing - creating fallback")
                self.fast_image_loader = None
            except Exception as e:
                print(f"DEBUG INIT: ERROR creating FastImageLoader: {e}")
                self.fast_image_loader = None
            
            # Initialize SynchronousVTKRenderer with VTK import protection
            print("DEBUG INIT: Creating SynchronousVTKRenderer")
            try:
                # Check if VTK is available before importing
                try:
                    import vtk
                    vtk_available = True
                    print("DEBUG INIT: VTK modules are available")
                except ImportError:
                    vtk_available = False
                    print("DEBUG INIT: VTK modules not available - creating fallback renderer")
                
                from ..logic.synchronous_vtk_renderer import SynchronousVTKRenderer
                
                # Create SynchronousVTKRenderer with main_window parameter
                self.synchronous_vtk_renderer = SynchronousVTKRenderer(main_window=self)
                print(f"DEBUG INIT: SynchronousVTKRenderer created: {self.synchronous_vtk_renderer}")
                
                # Set VTK components after initialization only if VTK is available
                if vtk_available:
                    vtk_components = (
                        getattr(self, 'actor1', None),
                        getattr(self, 'actor2', None),
                        getattr(self, 'mapper1', None),
                        getattr(self, 'mapper2', None),
                        getattr(self, 'ren', None),
                        getattr(self, 'widget', None),
                        getattr(self, 'vtkWidget', None),
                        getattr(self, 'iren', None)
                    )
                    
                    print(f"DEBUG INIT: VTK components available: {[type(comp).__name__ if comp is not None else 'None' for comp in vtk_components]}")
                    for idx, comp in enumerate(vtk_components):
                        print(f"DEBUG INIT: VTK component {idx}: {repr(comp)}")

                    if any(vtk_components):
                        self.synchronous_vtk_renderer.set_vtk_components(*vtk_components)
                        print("DEBUG INIT: SynchronousVTKRenderer created and VTK components set")
                    else:
                        print("DEBUG INIT: WARNING - VTK components not available, using SynchronousVTKRenderer without components")
                else:
                    print("DEBUG INIT: VTK not available - SynchronousVTKRenderer will work in fallback mode")
                    
            except ImportError as e:
                print(f"DEBUG INIT: ImportError creating SynchronousVTKRenderer: {e}")
                print("DEBUG INIT: SynchronousVTKRenderer dependencies missing - creating fallback")
                self.synchronous_vtk_renderer = None
            except Exception as e:
                print(f"DEBUG INIT: ERROR creating SynchronousVTKRenderer: {e}")
                import traceback
                print(f"DEBUG INIT: SynchronousVTKRenderer traceback: {traceback.format_exc()}")
                self.synchronous_vtk_renderer = None
            
            # Initialize SecondaryRenderers (matplotlib deprecated - using pyqtgraph only)
            print("DEBUG INIT: Creating SecondaryRenderers")
            try:
                print("DEBUG INIT: Using pyqtgraph-only rendering (matplotlib deprecated)")
                
                from ..logic.secondary_renderers import SecondaryRenderers
                self.secondary_renderers = SecondaryRenderers(main_window=self)
                print(f"DEBUG INIT: SecondaryRenderers created: {self.secondary_renderers}")
                
                # Pass the pyqtgraph imageView as the 'canvas' for 2D slices
                canvas = getattr(self, 'imageView', None)
                ax = None # Not needed for pyqtgraph
                
                # Pass the pyqtgraph PlotWidget for the histogram
                canvasHist = getattr(self, 'hist_plot_widget', None)
                axHist = None # Not needed for pyqtgraph
                
                print(f"DEBUG INIT: UI components for SecondaryRenderers - canvas (slice): {canvas}, canvasHist: {canvasHist}, axHist: {axHist}")
                
                self.secondary_renderers.set_ui_components(
                    canvas=canvas, ax=ax, canvasHist=canvasHist, axHist=axHist
                )
                print("DEBUG INIT: SecondaryRenderers created and UI components set")
                
            except ImportError as e:
                print(f"DEBUG INIT: ImportError creating SecondaryRenderers: {e}")
                print("DEBUG INIT: SecondaryRenderers dependencies missing - creating fallback")
                self.secondary_renderers = None
            except Exception as e:
                print(f"DEBUG INIT: ERROR creating SecondaryRenderers: {e}")
                import traceback
                print(f"DEBUG INIT: SecondaryRenderers traceback: {traceback.format_exc()}")
                self.secondary_renderers = None
            
            # Initialize UIStateManager (should always work as it only uses PyQt5)
            print("DEBUG INIT: Creating UIStateManager")
            try:
                from ..logic.ui_state_manager import UIStateManager
                self.ui_state_manager = UIStateManager(main_window=self)
                print(f"DEBUG INIT: UIStateManager created successfully: {self.ui_state_manager}")
            except Exception as e:
                print(f"DEBUG INIT: ERROR creating UIStateManager: {e}")
                import traceback
                print(f"DEBUG INIT: UIStateManager traceback: {traceback.format_exc()}")
                self.ui_state_manager = None
            
            # Initialize BackgroundCalculator for background processing
            print("DEBUG INIT: Creating BackgroundCalculator")
            try:
                from ..logic.background_calculator import BackgroundCalculator
                self.background_calculator = BackgroundCalculator(main_window=self)
                print(f"DEBUG INIT: BackgroundCalculator created successfully: {self.background_calculator}")
            except Exception as e:
                print(f"DEBUG INIT: ERROR creating BackgroundCalculator: {e}")
                import traceback
                print(f"DEBUG INIT: BackgroundCalculator traceback: {traceback.format_exc()}")
                self.background_calculator = None
            
            # Summary of component initialization
            print("DEBUG INIT: Component initialization summary:")
            print(f"  - fast_image_loader: {'SUCCESS' if self.fast_image_loader else 'FAILED'}")
            print(f"  - synchronous_vtk_renderer: {'SUCCESS' if self.synchronous_vtk_renderer else 'FAILED'}")
            print(f"  - secondary_renderers: {'SUCCESS' if self.secondary_renderers else 'FAILED'}")
            print(f"  - ui_state_manager: {'SUCCESS' if self.ui_state_manager else 'FAILED'}")
            print(f"  - background_calculator: {'SUCCESS' if self.background_calculator else 'FAILED'}")
            
            # Allow partial initialization - at least UIStateManager should work
            successful_components = sum(1 for comp in [
                self.fast_image_loader, self.synchronous_vtk_renderer,
                self.secondary_renderers, self.ui_state_manager, self.background_calculator
            ] if comp is not None)
            
            if successful_components >= 1:
                self.logger.info(f"Streamlined workflow components initialized: {successful_components}/5 successful")
            else:
                self.logger.error("All streamlined workflow components failed to initialize")
            
        except Exception as e:
            print(f"DEBUG INIT: CRITICAL ERROR - Failed to initialize streamlined components: {e}")
            import traceback
            print(f"DEBUG INIT: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Failed to initialize streamlined components: {e}")
            # Set components to None to prevent issues
            self.fast_image_loader = None
            self.synchronous_vtk_renderer = None
            self.secondary_renderers = None
            self.ui_state_manager = None
            self.background_calculator = None
        
        QTimer.singleShot(3000, lambda: self.progress_label.setVisible(False))
        
        self.setup_done()
        log_benchmark("HEAVY_COMPONENTS_LOADING")

    def _setup_vtk_components_main_thread(self):
        """Set up VTK components on main thread"""
        try:
            if not hasattr(self, 'vtk') or self.vtk is None or not hasattr(self, 'QVTKRenderWindowInteractor') or self.QVTKRenderWindowInteractor is None:
                return (None, None, None, None, None, None, None, None)
            
            actor1 = self.vtk.vtkActor()
            actor2 = self.vtk.vtkActor()
            mapper1 = self.vtk.vtkPolyDataMapper()
            mapper2 = self.vtk.vtkPolyDataMapper()
            mapper1.SetScalarVisibility(False) # Disable scalar visibility for nucleus
            mapper2.SetScalarVisibility(False) # Disable scalar visibility for membrane
            widget = self.QVTKRenderWindowInteractor()
            vtkWidget = widget
            ren = self.vtkRenderer()
            iren = widget.GetRenderWindow().GetInteractor()
            iren.SetInteractorStyle(self.vtk.vtkInteractorStyleTrackballCamera())
            widget.GetRenderWindow().AddRenderer(ren)
            
            return (actor1, actor2, mapper1, mapper2, widget, vtkWidget, ren, iren)
        except Exception as e:
            self.logger.error(f"Error setting up VTK components: {e}")
            return (None, None, None, None, None, None, None, None)

    def _setup_plotting_components_main_thread(self):
        """Set up pyqtgraph and matplotlib components on main thread"""
        try:
            # Setup pyqtgraph ImageView for 2D slice rendering
            imageView = pg.ImageView()
            imageView.ui.roiBtn.hide()
            imageView.ui.menuBtn.hide()
            imageView.ui.histogram.hide() # Hide the LUT
            
            # Add initial centered text
            font = QtGui.QFont()
            font.setPointSize(18)
            text = pg.TextItem("Slice Viewer", color=(128, 128, 128), anchor=(0.5, 0.5))
            text.setFont(font)
            # Position text at the center of the view
            text.setPos(0, 0)
            imageView.view.addItem(text)
            # Center the view on the text
            imageView.view.setRange(xRange=[-50, 50], yRange=[-50, 50], padding=0)
            # Disable pan/zoom function and right-click
            imageView.getView().setMouseEnabled(x=False, y=False)
            imageView.getView().setMenuEnabled(False)
            imageView.getView().disableAutoRange()
            
            # PyQtGraph components are created regardless of matplotlib availability

            # Create pyqtgraph PlotWidget for histogram with disabled interactions
            hist_plot_widget = pg.PlotWidget()
            hist_plot_widget.setBackground('w')
            hist_plot_widget.setLabel('left', 'Frequency')
            hist_plot_widget.setLabel('bottom', 'Intensity')
            hist_plot_widget.setTitle('Intensity Histogram')
            hist_plot_widget.showGrid(x=True, y=True, alpha=0.3)
            
            # Disable zoom, pan, and right-click functionality
            hist_plot_widget.setMouseEnabled(x=False, y=False)
            hist_plot_widget.setMenuEnabled(False)
            
            # Create inference plot with PyQtGraph PlotWidget
            prob_plot_widget = pg.PlotWidget()
            prob_plot_widget.setBackground('w')  # White background
            prob_plot_widget.setLabel('left', 'Probability')
            prob_plot_widget.setLabel('bottom', 'Class')
            prob_plot_widget.setTitle('Classsification Results')
            prob_plot_widget.showGrid(x=True, y=True, alpha=0.3)
            
            # Disable zoom, pan, and right-click functionality
            prob_plot_widget.setMouseEnabled(x=False, y=False)
            prob_plot_widget.setMenuEnabled(False)
            
            # Add placeholder text
            prob_plot_widget.setRange(xRange=[-0.1, 3.1], yRange=[0, 1.05], padding=0)
            # Set custom x-axis ticks for class probabilities
            axis = prob_plot_widget.getAxis('bottom')
            axis.setTicks([[(0, 'M'), (1, 'MM'), (2, 'BN'), (3, 'SN')]])
            prob_plot_widget.showGrid(x=False, y=False)
            
            canvasProb = prob_plot_widget
            axProb = None  # Not needed for PyQtGraph

            return (imageView, hist_plot_widget, canvasProb, axProb)
        except Exception as e:
            self.logger.error(f"Error setting up Plotting components: {e}")
            return (None, None, None, None)

    def _setup_canvas_layouts_main_thread(self, vtk_components, plotting_components):
        """Set up canvas layouts on main thread"""
        try:
            (actor1, actor2, mapper1, mapper2, widget, vtkWidget, ren, iren) = vtk_components
            (imageView, hist_plot_widget, canvasProb, axProb) = plotting_components
            
            layout_vtk = QtWidgets.QVBoxLayout()
            if widget is not None:
                layout_vtk.addWidget(widget)
            
            layout_slides = QtWidgets.QVBoxLayout()
            layout_slides.setContentsMargins(0, 0, 0, 0)
            layout_slides.setSpacing(0)
            if imageView is not None:
                layout_slides.addWidget(imageView)
            
            layout_hist = QtWidgets.QVBoxLayout()
            layout_hist.setContentsMargins(0, 0, 0, 0)
            layout_hist.setSpacing(0)
            if hist_plot_widget is not None:
                layout_hist.addWidget(hist_plot_widget)
                
            layoutProb = QtWidgets.QVBoxLayout()
            layoutProb.setContentsMargins(0, 0, 0, 0)
            layoutProb.setSpacing(0)
            if canvasProb is not None:
                layoutProb.addWidget(canvasProb)
            
            return (layout_vtk, layout_slides, layout_hist, layoutProb)
        except Exception as e:
            self.logger.error(f"Error setting up canvas layouts: {e}")
            return (QtWidgets.QVBoxLayout(), QtWidgets.QVBoxLayout(), QtWidgets.QVBoxLayout(), QtWidgets.QVBoxLayout())

    def _init_feature_windows(self):
        """Initialize the geometric and embedded features windows."""
        if hasattr(self, 'GeometricFeaturesWindow') and self.GeometricFeaturesWindow:
            self.geometric_features_window = self.GeometricFeaturesWindow(self)
            self.logger.debug("GeometricFeaturesWindow initialized.")
        else:
            self.logger.error("GeometricFeaturesWindow not available.")
            
        if hasattr(self, 'EmbeddedFeaturesWindow') and self.EmbeddedFeaturesWindow:
            self.embedded_features_window = self.EmbeddedFeaturesWindow(
                parent=self
            )
            self.logger.debug("EmbeddedFeaturesWindow initialized.")
        else:
            self.logger.error("EmbeddedFeaturesWindow not available.")
            
    def _connect_image_renderer_signals(self):
        """Connect image renderer signals to UI handlers"""
        try:
            if hasattr(self, 'image_renderer') and self.image_renderer:
                # Connect signals to handlers
                self.image_renderer.image_loaded.connect(self._on_image_loaded)
                self.image_renderer.rendering_completed.connect(self._on_image_rendered)
                self.image_renderer.error_occurred.connect(self._on_image_render_error)
                self.image_renderer.ui_controls_setup.connect(self._on_ui_controls_setup)
                
                self.logger.debug("Image renderer signals connected successfully")
            else:
                self.logger.warning("Image renderer not available for signal connections")
                
        except Exception as e:
            self.logger.error(f"Error connecting image renderer signals: {e}")