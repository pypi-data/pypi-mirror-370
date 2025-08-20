"""
UI Utils Mixin for the MainWindow.
Handles utility methods, progress display, initialization helpers, and cleanup.
"""
import os
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

class UiUtilsMixin:
    """Mixin containing utility methods for MainWindow."""

    def _set_image_controls_enabled(self, enabled):
        """Enable or disable all image loading and processing controls."""
        # Controls for loading images
        self.pushButton_Images.setEnabled(enabled)
        self.pushButton_ImageFolder.setEnabled(enabled)
        self.actionSelect_Images.setEnabled(enabled)
        self.actionSelect_Image_Folder.setEnabled(enabled)
        self.pushButtonImportCSV.setEnabled(enabled)
        self.actionImport_CSV.setEnabled(enabled)
        
        # Controls for processing and features that depend on a loaded image
        self.pushButton_GeometricFeatures.setEnabled(enabled)
        self.pushButton_EmbeddedFeatures.setEnabled(enabled)
        self.actionGeometric_Features.setEnabled(enabled)
        self.actionEmbedded_Features.setEnabled(enabled)
        
        # Intensity sliders
        self.horizontalSlider_intensity1.setEnabled(enabled)
        self.horizontalSlider_intensity2.setEnabled(enabled)
        self.spinBox_intensity1.setEnabled(enabled)
        self.spinBox_intensity2.setEnabled(enabled)
        
        # File list interaction
        self.listWidget.setEnabled(enabled)

    def _show_progress(self, value, message):
        """Show progress in status bar with label and progress bar"""
        if self.progress_label:
            self.progress_label.setVisible(True)
            self.progress_label.setText(message)
        if self.progress_bar:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(value)
        QApplication.processEvents()

    def _hide_progress(self):
        """Hide progress label and bar"""
        if self.progress_label:
            self.progress_label.setVisible(False)
        if self.progress_bar:
            self.progress_bar.setVisible(False)
        QApplication.processEvents()

    def _show_progress_briefly(self, message, duration=1500):
        """Show progress message briefly then hide it"""
        if hasattr(self, 'progress_label') and self.progress_label:
            self.progress_label.setText(message)
            self.progress_label.setVisible(True)
            QTimer.singleShot(duration, lambda: self.progress_label.setVisible(False))

    def _update_loading_progress(self, progress, message):
        """Update loading progress in status bar"""
        self._show_progress(progress, message)

    def _update_global_modules(self, modules):
        """Update instance attributes with imported modules"""
        self.tf = modules.get('tf')
        self.K = modules.get('K')
        self.sns = modules.get('sns')
        self.tifffile = modules.get('tifffile')
        self.rescale_intensity = modules.get('rescale_intensity')
        self.toml = modules.get('toml')
        self.MarkdownIt = modules.get('MarkdownIt')
        self.texmath_plugin = modules.get('texmath_plugin')
        self.Classifier = modules.get('Classifier')
        print(f"DEBUG: _update_global_modules - Classifier from modules: {self.Classifier}")
        print(f"DEBUG: _update_global_modules - Classifier type: {type(self.Classifier)}")
        print(f"DEBUG: _update_global_modules - Classifier is None: {self.Classifier is None}")
        
        self.GeometricFeaturesWindow = modules.get('GeometricFeaturesWindow')
        self.EmbeddedFeaturesWindow = modules.get('EmbeddedFeaturesWindow')
        self.ModelLoadingThread = modules.get('ModelLoadingThread')
        self.ModelInferenceThread = modules.get('ModelInferenceThread')
        self.HeavyComponentsLoadingThread = modules.get('HeavyComponentsLoadingThread')
        self.ImageProcessingThread = modules.get('ImageProcessingThread')

        # Log status of threading classes
        self.logger.debug(f"Updated instance modules - HeavyComponentsLoadingThread: {self.HeavyComponentsLoadingThread is not None}")
        self.logger.debug(f"Updated instance modules - Classifier: {self.Classifier is not None}")
        print(f"DEBUG: _update_global_modules - Logged Classifier status: {self.Classifier is not None}")

    def _update_global_vtk_modules(self, modules):
        """Update instance attributes with imported VTK modules"""
        self.vtk = modules.get('vtk')
        self.numpy_support = modules.get('numpy_support')
        self.QVTKRenderWindowInteractor = modules.get('QVTKRenderWindowInteractor')
        self.vtkRenderer = modules.get('vtkRenderer')
        self.vtkRenderWindow = modules.get('vtkRenderWindow')
        self.FigureCanvas = modules.get('FigureCanvas')
        self.Figure = modules.get('Figure')
        self.plt = modules.get('plt')

    def _init_preferences_manager(self):
        """Initialize the preferences manager"""
        try:
            from .preferences import PreferencesManager
            self.preferences_manager = PreferencesManager()
            
            # Connect to preference changes
            self.preferences_manager.preferences_changed.connect(self._on_preferences_changed)
            
        except Exception as e:
            print(f"WARNING: Failed to initialize preferences manager: {e}")
            self.preferences_manager = None

    def _init_enhanced_data_loader(self):
        """Initialize the enhanced data loader system"""
        try:
            from ..logic.enhanced_data_loader import EnhancedDataLoader, BatchProcessingConfig
            
            # Create configuration from preferences
            config = BatchProcessingConfig()
            if hasattr(self, 'preferences_manager') and self.preferences_manager:
                auto_config = self.preferences_manager.get_auto_processing_config()
                config.auto_processing_enabled = auto_config.get('auto_processing_enabled', False)
                config.cache_enabled = auto_config.get('cache_enabled', True)
                config.cache_size_mb = auto_config.get('cache_size_mb', 1024)
                config.batch_size = auto_config.get('batch_size', 5)
                config.max_concurrent_tasks = auto_config.get('max_concurrent_tasks', 3)
                config.auto_load_model = auto_config.get('auto_load_model', True)
                config.auto_inference = auto_config.get('auto_inference', True)
                config.auto_save_results = auto_config.get('auto_save_results', False)
            
            # Initialize enhanced data loader
            self.enhanced_data_loader = EnhancedDataLoader(self, config)
            
            # Connect signals
            self.enhanced_data_loader.progress_updated.connect(self._on_enhanced_progress)
            self.enhanced_data_loader.task_completed.connect(self._on_task_completed)
            self.enhanced_data_loader.batch_completed.connect(self._on_batch_completed)
            self.enhanced_data_loader.error_occurred.connect(self._on_processing_error)
            
            print("Enhanced data loader initialized successfully")
            
        except Exception as e:
            print(f"WARNING: Failed to initialize enhanced data loader: {e}")
            self.enhanced_data_loader = None

    def _init_image_renderer(self):
        """Initialize the image renderer"""
        try:
            from ..logic.image_renderer import ImageRenderer
            self.image_renderer = ImageRenderer(self)
            
            # Pass VTK components to image renderer if they exist
            if (hasattr(self, 'actor1') and hasattr(self, 'actor2') and
                hasattr(self, 'mapper1') and hasattr(self, 'mapper2') and
                hasattr(self, 'widget') and hasattr(self, 'ren')):
                
                self.image_renderer.set_vtk_components(
                    self.actor1, self.actor2, self.mapper1, self.mapper2,
                    self.widget, self.vtkWidget, self.ren, self.iren
                )
                print("VTK components successfully passed to ImageRenderer")
            else:
                print("Warning: VTK components not available for ImageRenderer")
            
            # Connect signals
            self.image_renderer.rendering_completed.connect(self._on_image_rendered)
            self.image_renderer.error_occurred.connect(self._on_image_render_error)
            self.image_renderer.ui_controls_setup.connect(self._on_ui_controls_setup)
            self.image_renderer.image_loaded.connect(self._on_image_loaded)
            
        except Exception as e:
            print(f"Failed to initialize image renderer: {e}")
            self.image_renderer = None

    def _init_geometry_calculator(self):
        """Initialize the geometry calculator"""
        try:
            from ..logic.geometry_calculator import GeometryCalculator
            self.geometry_calculator = GeometryCalculator(self)
            
            # Connect signals
            self.geometry_calculator.metrics_calculated.connect(self._on_geometry_metrics_calculated)
            self.geometry_calculator.calculation_error.connect(self._on_geometry_calculation_error)
            
            print("Geometry calculator initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize geometry calculator: {e}")
            self.geometry_calculator = None

    def _on_enhanced_progress(self, progress, message):
        """Handle progress updates from enhanced data loader"""
        pass

    def _on_task_completed(self, file_path, results):
        """Handle individual task completion"""
        print(f"Task completed for {file_path}: {results}")

    def _on_batch_completed(self, completed_tasks):
        """Handle batch completion"""
        print(f"Batch processing completed: {len(completed_tasks)} tasks")

    def _on_processing_error(self, file_path, error_message):
        """Handle processing errors"""
        print(f"Processing error for {file_path}: {error_message}")

    def _on_preferences_changed(self, preferences):
        """Handle preferences change"""
        print(f"Preferences changed: {preferences}")
        if hasattr(self, 'enhanced_data_loader') and self.enhanced_data_loader:
            self._update_enhanced_data_loader_config()

    def _update_enhanced_data_loader_config(self):
        """Update enhanced data loader configuration from preferences"""
        if hasattr(self, 'enhanced_data_loader') and self.enhanced_data_loader and hasattr(self, 'preferences_manager'):
            auto_config = self.preferences_manager.get_auto_processing_config()
            
            # Update configuration
            config = self.enhanced_data_loader.config
            config.auto_processing_enabled = auto_config.get('auto_processing_enabled', False)
            config.cache_enabled = auto_config.get('cache_enabled', True)
            config.cache_size_mb = auto_config.get('cache_size_mb', 1024)
            config.batch_size = auto_config.get('batch_size', 5)
            config.max_concurrent_tasks = auto_config.get('max_concurrent_tasks', 3)
            config.auto_load_model = auto_config.get('auto_load_model', True)
            config.auto_inference = auto_config.get('auto_inference', True)
            config.auto_save_results = auto_config.get('auto_save_results', False)
            
            print("Enhanced data loader configuration updated")

    def enable_auto_processing(self, enabled=True):
        """Enable or disable auto-processing mode"""
        if hasattr(self, 'enhanced_data_loader') and self.enhanced_data_loader:
            self.enhanced_data_loader.config.auto_processing_enabled = enabled
            if enabled:
                self.progress_label.setText("Auto-processing enabled")
            else:
                self.progress_label.setText("Auto-processing disabled")
            self.progress_label.setVisible(True)
            QTimer.singleShot(2000, lambda: self.progress_label.setVisible(False))

    def get_processing_stats(self):
        """Get processing statistics from enhanced data loader"""
        if hasattr(self, 'enhanced_data_loader') and self.enhanced_data_loader:
            return self.enhanced_data_loader.get_processing_stats()
        return {}

    def debug_import_status(self):
        """Debug method to check import status of threading classes"""
        global ModelLoadingThread, ModelInferenceThread, HeavyComponentsLoadingThread
        
        self.logger.debug("=== IMPORT STATUS DEBUG ===")
        self.logger.debug(f"ModelLoadingThread: {ModelLoadingThread is not None}")
        self.logger.debug(f"ModelInferenceThread: {ModelInferenceThread is not None}")
        self.logger.debug(f"HeavyComponentsLoadingThread: {HeavyComponentsLoadingThread is not None}")
        self.logger.debug(f"_heavy_modules_loaded: {getattr(self, '_heavy_modules_loaded', False)}")
        self.logger.debug(f"_vtk_modules_loaded: {getattr(self, '_vtk_modules_loaded', False)}")
        self.logger.debug(f"_heavy_components_loaded: {getattr(self, '_heavy_components_loaded', False)}")
        self.logger.debug(f"tifffile available: {tifffile is not None}")
        
        ImageLoadingThread = self._import_image_loading_thread()
        self.logger.debug(f"ImageLoadingThread on-demand: {ImageLoadingThread is not None}")
        self.logger.debug("=== END IMPORT STATUS ===")

    def _on_thread_finished(self, thread):
        """Handle thread finishing - remove from active threads list"""
        try:
            if thread in self.active_threads:
                self.active_threads.remove(thread)
                self.logger.debug(f"Thread removed from active list. Active threads: {len(self.active_threads)}")
        except Exception as e:
            self.logger.warning(f"Error removing finished thread: {e}")

    def _cleanup_threads(self):
        """Clean up all active threads before application shutdown"""
        self.logger.debug("Starting thread cleanup...")
        
        for thread in self.active_threads[:]:  # Create a copy to iterate safely
            try:
                if thread and thread.isRunning():
                    self.logger.debug(f"Stopping thread: {type(thread).__name__}")
                    
                    # Try graceful stop if available
                    if hasattr(thread, 'stop_gracefully'):
                        thread.stop_gracefully()
                    
                    # Request interruption
                    thread.requestInterruption()
                    
                    # Wait for thread to finish (max 2 seconds)
                    if not thread.wait(2000):
                        self.logger.warning(f"Thread {type(thread).__name__} did not finish gracefully, terminating...")
                        thread.terminate()
                        thread.wait(1000)  # Give it 1 more second to terminate
                    
                    self.logger.debug(f"Thread {type(thread).__name__} cleanup completed")
                    
            except Exception as e:
                self.logger.error(f"Error cleaning up thread: {e}")
        
        self.active_threads.clear()
        self.logger.debug("Thread cleanup completed")

    def set_cli_args(self, args):
        """Set CLI arguments for auto-loading"""
        self._cli_args = args

    def setup_done(self):
        """Signal that setup is complete"""
        self.setup_done_signal.emit()
        
        # Perform CLI auto-loading after setup is complete
        if self._cli_args and not self._cli_auto_load_done:
            QTimer.singleShot(100, self._perform_cli_auto_load)

    def _perform_cli_auto_load(self):
        """Perform CLI auto-loading using the CLI loader utility"""
        if self._cli_auto_load_done or not self._cli_args:
            return
            
        self._cli_auto_load_done = True
        
        # Use the CLI loader utility
        from ..utils.cli_loader import perform_cli_auto_load
        perform_cli_auto_load(self, self._cli_args)

    def closeEvent(self, event):
        """Handle application close event - ensure proper thread and VTK cleanup"""
        try:
            self.logger.debug("Application close event received")
            
            # Clean up all active threads
            self._cleanup_threads()
            
            # Clean up image renderer if it exists
            if hasattr(self, 'image_renderer') and self.image_renderer:
                if hasattr(self.image_renderer, 'cleanup'):
                    self.image_renderer.cleanup()
            
            # Clean up geometry calculator if it exists
            if hasattr(self, 'geometry_calculator') and self.geometry_calculator:
                if hasattr(self.geometry_calculator, 'cleanup'):
                    self.geometry_calculator.cleanup()
            
            # Close any additional windows
            if hasattr(self, 'geometric_features_window') and self.geometric_features_window:
                self.geometric_features_window.close()
            
            if hasattr(self, 'embedded_features_window') and self.embedded_features_window:
                self.embedded_features_window.close()
            
            # Accept the close event
            event.accept()
            self.logger.debug("Application close event handled successfully")
            
        except Exception as e:
            self.logger.error(f"Error during application close: {e}")
            # Still accept the event to avoid hanging
            event.accept()