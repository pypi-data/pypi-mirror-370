"""
UI Processing Mixin for the MainWindow.
Handles background image processing and related callbacks.
"""
import os
import time
import numpy as np
from PyQt5.QtWidgets import QProgressDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
from ..ui.progress_dialog import LoadingProgressDialog
from ..logic.threads.image_processing_threads import FastRenderingThread, BackgroundMetricsThread
from ..logic.streamlined_image_manager import StreamlinedImageManager

class UiProcessingMixin:
    """Mixin containing image processing methods for MainWindow."""

    def start_streamlined_image_processing(self, file_path):
        """Start image processing using the new streamlined workflow"""
        print(f"DEBUG: start_streamlined_image_processing called for {file_path}")
        print(f"DEBUG: hasattr(self, 'streamlined_manager'): {hasattr(self, 'streamlined_manager')}")
        
        if hasattr(self, 'streamlined_manager'):
            print(f"DEBUG: self.streamlined_manager is None: {self.streamlined_manager is None}")
            print(f"DEBUG: self.streamlined_manager type: {type(self.streamlined_manager)}")
        else:
            print("DEBUG: streamlined_manager attribute does not exist")
        
        if not hasattr(self, 'streamlined_manager') or self.streamlined_manager is None:
            print("ERROR: StreamlinedImageManager not available, falling back to legacy processing")
            print("DEBUG: Checking if _init_streamlined_manager was called...")
            
            # Check if initialization was attempted
            if hasattr(self, '_heavy_components_loaded'):
                print(f"DEBUG: _heavy_components_loaded: {self._heavy_components_loaded}")
            else:
                print("DEBUG: _heavy_components_loaded attribute not found")
                
            # Try to initialize now if components are available
            if hasattr(self, '_init_streamlined_manager'):
                print("DEBUG: Attempting to initialize StreamlinedImageManager now...")
                try:
                    self._init_streamlined_manager()
                    if hasattr(self, 'streamlined_manager') and self.streamlined_manager is not None:
                        print("DEBUG: StreamlinedImageManager successfully initialized on retry")
                        return self.streamlined_manager.load_and_render_image(file_path)
                    else:
                        print("DEBUG: StreamlinedImageManager initialization retry failed")
                except Exception as e:
                    print(f"DEBUG: Exception during StreamlinedImageManager retry initialization: {e}")
            
            return self.start_image_processing(file_path)
        
        # Use the streamlined manager
        print("DEBUG: Using StreamlinedImageManager for processing")
        self.streamlined_manager.load_and_render_image(file_path)

    def _on_streamlined_image_loaded(self, file_path, image_data, thresholds):
        """Handle image loaded signal from streamlined manager"""
        try:
            print(f"DEBUG: Image loaded via streamlined workflow: {file_path}")
            print(f"DEBUG: Thresholds: {thresholds}")
            
            # Update main window compatibility
            self.img = image_data
            
            # Update UI controls with the thresholds from streamlined manager
            threshold1, threshold2 = thresholds
            
            # Update geometry calculator for measurement clearing functionality
            if hasattr(self, 'geometry_calculator') and self.geometry_calculator:
                # Clear previous measurements and show 'calculating...' placeholders
                self.geometry_calculator.update_ui_with_metrics({}, "_1")
                self.geometry_calculator.update_ui_with_metrics({}, "_2")
                
            # Clear classification plot if available using PyQtGraph
            if hasattr(self, 'canvasProb') and self.canvasProb:
                self.canvasProb.clear()
                self.canvasProb.setTitle("Classification Results")
                self.canvasProb.setLabel('left', '')
                self.canvasProb.setLabel('bottom', '')
            
            self.logger.info(f"Streamlined image loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            self.logger.error(f"Error handling streamlined image loaded: {e}")
        
    def _on_streamlined_rendering_complete(self, status_message):
        """Handle rendering complete signal from streamlined manager"""  
        try:
            print(f"DEBUG: Rendering complete via streamlined workflow: {status_message}")
            
            # Show brief status message
            self._show_progress_briefly(status_message, duration=2000)
            
            # Update feature windows with new data
            if hasattr(self, 'update_feature_windows'):
                self.update_feature_windows()
            
            self.logger.info(f"Streamlined rendering complete: {status_message}")
            
        except Exception as e:
            self.logger.error(f"Error handling streamlined rendering complete: {e}")
        
    def _on_streamlined_error(self, error_msg):
        """Handle error signal from streamlined manager"""
        try:
            print(f"ERROR: Streamlined workflow error: {error_msg}")
            self.logger.error(f"Streamlined workflow error: {error_msg}")
            
            # Show error message to user
            QMessageBox.warning(self, "Image Processing Error", 
                              f"Error in streamlined workflow:\n{error_msg}")
            
            # Ensure UI state is reset on error
            if hasattr(self, 'ui_state_manager') and self.ui_state_manager:
                self.ui_state_manager.force_reset_state()
                
        except Exception as e:
            self.logger.error(f"Error handling streamlined error: {e}")

    def _on_loading_state_changed(self, is_loading):
        """Handle loading state changes from UI state manager"""
        try:
            if is_loading:
                self.logger.debug("UI loading state enabled - elements disabled")
                # Clear measurements when starting to load
                self.clear_measurement_values()
            else:
                self.logger.debug("UI loading state disabled - elements enabled")
                # Reset status bar when loading complete
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage("Ready")
                    
        except Exception as e:
            self.logger.error(f"Error handling loading state change: {e}")

    def _on_ui_elements_updated(self, message):
        """Handle UI elements update messages from UI state manager"""
        try:
            self.logger.debug(f"UI elements updated: {message}")
            # Show the loading message in status bar if it's a loading message
            if "Loading" in message or "Processing" in message:
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage(message)
                    
        except Exception as e:
            self.logger.error(f"Error handling UI elements update: {e}")
    
    def _on_database_updated(self):
        """Handle database updated signal from streamlined manager"""
        try:
            print("DEBUG UI_PROCESSING: _on_database_updated signal received")
            self.logger.debug("Database updated - refreshing embedded features window")
            
            # Update embedded features window if it exists and is visible
            if hasattr(self, 'embedded_features_window') and self.embedded_features_window:
                print("DEBUG UI_PROCESSING: Embedded features window available, updating with database data")
                print(f"DEBUG UI_PROCESSING: Database has {len(self.result_db)} rows")
                self.logger.debug("Updating visible embedded features window with new database data")
                self.embedded_features_window.update_data_and_render(self.result_db)
                print("DEBUG UI_PROCESSING: Embedded features window update_data_and_render completed")
            else:
                print("DEBUG UI_PROCESSING: Embedded features window not available")
                print(f"DEBUG UI_PROCESSING: hasattr embedded_features_window: {hasattr(self, 'embedded_features_window')}")
                if hasattr(self, 'embedded_features_window'):
                    print(f"DEBUG UI_PROCESSING: embedded_features_window is None: {self.embedded_features_window is None}")
                self.logger.debug("Embedded features window not available for database update")
                
        except Exception as e:
            print(f"DEBUG UI_PROCESSING: Exception in _on_database_updated: {str(e)}")
            import traceback
            print(f"DEBUG UI_PROCESSING: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Error handling database update: {str(e)}")

    def start_image_processing(self, file_path):
        """Initiates the fast rendering and background processing threads."""
        print(f"DEBUG: start_image_processing called for {file_path}")
        print(f"DEBUG: Initial active_threads: {[f'{t.__class__.__name__}(ID:{id(t)})' for t in self.active_threads]}")
        
        # Clean up any finished threads first - be more aggressive about cleanup
        before_cleanup = len(self.active_threads)
        still_active = []
        for thread in self.active_threads:
            if thread.isRunning():
                # Double-check: if thread claims to be running but is actually finished, force cleanup
                if hasattr(thread, 'isFinished') and thread.isFinished():
                    print(f"DEBUG: Force removing finished thread {thread.__class__.__name__} that reported as running")
                else:
                    still_active.append(thread)
            else:
                print(f"DEBUG: Removing finished thread {thread.__class__.__name__}")
        
        self.active_threads = still_active
        after_cleanup = len(self.active_threads)
        print(f"DEBUG: Thread cleanup removed {before_cleanup - after_cleanup} finished threads")
        
        # Check for blocking threads (exclude BackgroundMetricsThread as it runs independently)
        blocking_threads = [thread for thread in self.active_threads
                          if thread.isRunning() and not isinstance(thread, BackgroundMetricsThread)]
        
        if blocking_threads:
            running_threads = [f'{thread.__class__.__name__}(ID:{id(thread)})' for thread in blocking_threads]
            print(f"DEBUG: Blocking threads found but allowing processing to continue: {running_threads}")
            # Note: Removed warning dialog as the race condition is now handled properly
        
        # Log background threads that will continue running
        background_threads = [thread for thread in self.active_threads
                            if thread.isRunning() and isinstance(thread, BackgroundMetricsThread)]
        if background_threads:
            bg_thread_info = [f'{thread.__class__.__name__}(ID:{id(thread)})' for thread in background_threads]
            print(f"DEBUG: Background threads will continue running: {bg_thread_info}")

        # 1. Clear previous measurement values
        self.clear_measurement_values()

        # 2. Create and configure FastRenderingThread
        record = self.result_db[self.result_db['Path'] == file_path]
        existing_thresholds = {}
        if not record.empty:
            existing_thresholds['threshold1'] = record.iloc[0].get('threshold1')
            existing_thresholds['threshold2'] = record.iloc[0].get('threshold2')

        self.fast_rendering_thread = FastRenderingThread(
            file_path,
            percentile1=0, # These could be configurable
            percentile2=2,
            existing_thresholds=existing_thresholds
        )
        self.active_threads.append(self.fast_rendering_thread)

        # 3. Create and show progress dialog
        # 3. Create and show progress dialog
        if not hasattr(self, 'progress_dialog') or self.progress_dialog is None:
            print("DEBUG: Creating new LoadingProgressDialog")
            self.progress_dialog = LoadingProgressDialog(self, title="Fast Rendering", message="Fast rendering...")
            self.progress_dialog.canceled.connect(self.cancel_all_threads)
            self.progress_dialog.finished.connect(self.on_progress_dialog_finished)
        else:
            print("DEBUG: Reusing existing LoadingProgressDialog")
            self.progress_dialog.setWindowTitle("Fast Rendering")
            self.progress_dialog.setLabelText("Fast rendering...")
            self.progress_dialog.setValue(0)

        # 4. Connect signals
        # The main cancellation signal is connected once when the dialog is created.
        # We just need to connect the signals for the new thread instance.
        self.fast_rendering_thread.progress_update.connect(self.update_progress_dialog)
        self.fast_rendering_thread.rendering_complete.connect(self._on_fast_rendering_complete)
        self.fast_rendering_thread.error_occurred.connect(self._on_image_processing_error)
        self.fast_rendering_thread.finished.connect(lambda: self._on_thread_finished(self.fast_rendering_thread))
        self.fast_rendering_thread.progress_update.connect(self.update_progress_dialog)
        self.fast_rendering_thread.rendering_complete.connect(self._on_fast_rendering_complete)
    def cancel_all_threads(self):
        """Safely cancel all running threads."""
        print("DEBUG: cancel_all_threads called")
        for thread in self.active_threads:
            if hasattr(thread, 'cancel'):
                print(f"DEBUG: Cancelling thread {thread.__class__.__name__}")
                thread.cancel()
        self.fast_rendering_thread.error_occurred.connect(self._on_image_processing_error)
        self.fast_rendering_thread.finished.connect(lambda: self._on_thread_finished(self.fast_rendering_thread))
        
        # Add diagnostic logging for thread lifecycle
        print(f"DEBUG: FastRenderingThread created and connected. Thread ID: {id(self.fast_rendering_thread)}")
        print(f"DEBUG: Progress dialog instance: {id(self.progress_dialog)}")

        self.fast_rendering_thread.start()
        self.progress_dialog.show()

    def on_progress_dialog_finished(self, result):
        """Callback for when the progress dialog is closed."""
        print(f"DEBUG: Progress dialog finished with result: {result}")
        # If the dialog was not canceled, but closed, we might need to clean up.
        if self.progress_dialog and not self.progress_dialog.was_canceled:
            print("DEBUG: Dialog closed without cancellation, cancelling threads.")
            self.cancel_all_threads()
        self.progress_dialog = None # Clear the reference
        print("DEBUG: self.progress_dialog set to None")

    def update_progress_dialog(self, value, message):
        """Updates the progress dialog's value and label."""
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(message)

    def clear_measurement_values(self):
        """
        Clears all measurement-related UI elements and shows 'calculating...' placeholders.
        This method is used by both legacy and streamlined workflows.
        """
        try:
            # Clear geometry metrics with 'calculating...' placeholders
            if hasattr(self, 'geometry_calculator') and self.geometry_calculator:
                # Create empty metrics dictionaries to clear displays
                empty_metrics = {}
                self.geometry_calculator.update_ui_with_metrics(empty_metrics, "_1")
                self.geometry_calculator.update_ui_with_metrics(empty_metrics, "_2")
                
                # Set 'calculating...' text for all metric labels
                metric_labels = [
                    'Area_1', 'Vol_1', 'NSI_1', 'Sphericity_1', 'SA_Vol_Ratio_1', 'Solidity_1', 'Elongation_1', 'Genus_1',
                    'Area_2', 'Vol_2', 'NSI_2', 'Sphericity_2', 'SA_Vol_Ratio_2', 'Solidity_2', 'Elongation_2', 'Genus_2'
                ]
                
                for label in metric_labels:
                    if hasattr(self, f'label{label}'):
                        getattr(self, f'label{label}').setText("calculating...")

            # Clear inference plot with placeholder using PyQtGraph
            if hasattr(self, 'canvasProb') and self.canvasProb:
                self.canvasProb.clear()
                
                # Add "Calculating..." text using PyQtGraph TextItem
                text_item = pg.TextItem("Calculating...", color=(0, 0, 255), anchor=(0.5, 0.5))
                text_item.setPos(1.5, 0.5)  # Center position for 4 classes (0-3)
                self.canvasProb.addItem(text_item)
                
                self.canvasProb.setTitle("Classification Results")
                self.canvasProb.setLabel('left', '')
                self.canvasProb.setLabel('bottom', '')
                self.canvasProb.setXRange(0, 3)
                self.canvasProb.setYRange(0, 1)

            # Clear secondary rendering displays
            if hasattr(self, 'secondary_renderers') and self.secondary_renderers:
                self.secondary_renderers.show_loading_message('slice', 'Loading...')
                self.secondary_renderers.show_loading_message('histogram', 'Loading...')

            # Reset status bar
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage("Processing...")
            if hasattr(self, 'status_progress_bar'):
                self.status_progress_bar.setVisible(False)

            self.logger.debug("Updated measurement values with 'calculating...' placeholders")

        except Exception as e:
            self.logger.error(f"Error clearing measurement values: {e}")
            print("DEBUG: Error clearing measurement values.")

    def _on_fast_rendering_complete(self, result):
        """Handles the completion of the fast rendering thread."""
        try:
            print(f"DEBUG: _on_fast_rendering_complete called at {time.time()}")
            if self.progress_dialog and not self.progress_dialog.was_canceled:
                self.progress_dialog.setValue(100)
                print(f"DEBUG: Progress dialog updated to 100% at {time.time()}")

            # Force immediate cleanup of the FastRenderingThread
            if hasattr(self, 'fast_rendering_thread') and self.fast_rendering_thread:
                if self.fast_rendering_thread in self.active_threads:
                    self.active_threads.remove(self.fast_rendering_thread)
                    print(f"DEBUG: FastRenderingThread removed from active_threads")

            # Defer heavy VTK rendering to allow the event loop to process dialog closure
            def deferred_render():
                print(f"DEBUG: Executing deferred render at {time.time()}")
                if hasattr(self, 'image_renderer') and self.image_renderer:
                    vtk_start_time = time.time()
                    self.image_renderer.set_image_and_surfaces(
                        result['image'],
                        result['polydata1'],
                        result['polydata2'],
                        result['threshold1'],
                        result['threshold2']
                    )
                    vtk_end_time = time.time()
                    print(f"DEBUG: VTK renderer updated with surfaces in {vtk_end_time - vtk_start_time:.3f}s")
                    
                    # Now that rendering is done, start the background processing
                    self._start_background_processing(result)

            QTimer.singleShot(0, deferred_render)
            print(f"DEBUG: Deferred render scheduled at {time.time()}. UI should be responsive now.")

        except Exception as e:
            self.logger.error(f"Error in _on_fast_rendering_complete: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred after rendering: {e}")

    def _start_background_processing(self, rendering_results):
        """Starts the background metrics and inference thread."""
        try:
            print(f"DEBUG: Starting background processing at {time.time()}")
            # Start BackgroundMetricsThread
            label_encoder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'label_encoder_classes.npy')
            self.background_metrics_thread = BackgroundMetricsThread(
                rendering_results=rendering_results,
                model=self.model,
                model_config=self.model_config,
                label_encoder_path=label_encoder_path
            )
            self.active_threads.append(self.background_metrics_thread)

            # Connect signals
            self.background_metrics_thread.progress_update.connect(self.update_status_bar)
            self.background_metrics_thread.metrics_complete.connect(self._on_metrics_complete)
            self.background_metrics_thread.inference_complete.connect(self._on_inference_complete)
            self.background_metrics_thread.error_occurred.connect(self._on_background_error)
            self.background_metrics_thread.finished.connect(lambda: self._on_thread_finished(self.background_metrics_thread))
            self.background_metrics_thread.finished.connect(self.reset_status_bar)

            self.background_metrics_thread.start()
            print(f"DEBUG: BackgroundMetricsThread started at {time.time()}")
            self.logger.info("Started background metrics and inference.")
        except Exception as e:
            self.logger.error(f"Error starting background processing: {e}")
            QMessageBox.critical(self, "Error", f"Could not start background processing: {e}")

    def update_status_bar(self, progress, message):
        """Updates the status bar with progress from background threads."""
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(message)

        if hasattr(self, 'status_progress_bar') and self.status_progress_bar:
            if not self.status_progress_bar.isVisible():
                self.status_progress_bar.setVisible(True)
            self.status_progress_bar.setValue(progress)

    def _on_metrics_complete(self, threshold_id, metrics):
        """Handles completion of metrics calculation for a single threshold."""
        try:
            self.logger.info(f"Metrics received for threshold {threshold_id}.")
            suffix = f"_{threshold_id}"

            # Update UI metrics
            if hasattr(self, 'geometry_calculator') and self.geometry_calculator:
                self.geometry_calculator.update_ui_with_metrics(metrics, suffix)

            # Update database
            file_path = self.background_metrics_thread.rendering_results['file_path']
            self._update_db_with_metrics(file_path, metrics, suffix)

            # Update feature windows
            self.update_feature_windows()

        except Exception as e:
            self.logger.error(f"Error in _on_metrics_complete for threshold {threshold_id}: {e}")
            QMessageBox.critical(self, "Metrics Error", f"Failed to process metrics for threshold {threshold_id}: {e}")

    def _on_inference_complete(self, classification_results):
        """Handles completion of model inference."""
        try:
            self.logger.info(f"Inference complete. Results: {classification_results}")

            if not classification_results:
                self.logger.warning("Inference completed with no results.")
                return

            # Update classification plot
            self._update_inference_plot(classification_results)

            # Update database
            file_path = self.background_metrics_thread.rendering_results['file_path']
            self._update_db_with_classification(file_path, classification_results)

            # The status bar is reset via the thread's finished signal connection
            self.logger.info("Classification UI and database updated successfully.")

        except Exception as e:
            self.logger.error(f"Error in _on_inference_complete: {e}")
            QMessageBox.critical(self, "Inference Error", f"Failed to process classification results: {e}")
    
    def _on_background_error(self, error_message):
        """Handles errors from the background metrics thread."""
        self.logger.error(f"Background processing error: {error_message}")
        QMessageBox.critical(self, "Background Processing Error", error_message)
        self.reset_status_bar()
        
        # Ensure failed background thread is removed from active threads
        if hasattr(self, 'background_metrics_thread') and self.background_metrics_thread:
            if self.background_metrics_thread in self.active_threads:
                self.active_threads.remove(self.background_metrics_thread)
                print(f"DEBUG: Removed failed background_metrics_thread from active threads")

    def reset_status_bar(self):
        """Resets the status bar to its default 'Ready' state."""
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage("Ready")
        if hasattr(self, 'status_progress_bar') and self.status_progress_bar:
            self.status_progress_bar.setVisible(False)
            self.status_progress_bar.setValue(0)

    def _on_thread_finished(self, thread):
        """Removes a thread from the active list when it has finished."""
        print(f"DEBUG: _on_thread_finished called for {thread.__class__.__name__} (ID: {id(thread)})")
        print(f"DEBUG: Thread.isRunning() = {thread.isRunning()}")
        print(f"DEBUG: Thread.isFinished() = {thread.isFinished()}")
        print(f"DEBUG: Active threads before cleanup: {[t.__class__.__name__ for t in self.active_threads]}")
        
        if thread in self.active_threads:
            self.active_threads.remove(thread)
            print(f"DEBUG: Removed {thread.__class__.__name__} from active_threads")
        else:
            print(f"DEBUG: {thread.__class__.__name__} was not in active_threads list")
            
        print(f"DEBUG: Active threads after cleanup: {[t.__class__.__name__ for t in self.active_threads]} (count: {len(self.active_threads)})")
        
        # Additional cleanup: ensure thread is properly finished
        if hasattr(thread, 'wait') and thread.isRunning():
            print(f"DEBUG: Thread {thread.__class__.__name__} still running after finished signal, waiting for completion...")
            thread.wait(1000)  # Wait up to 1 second
            if thread.isRunning():
                print(f"WARNING: Thread {thread.__class__.__name__} did not finish cleanly after 1 second wait")
                print(f"WARNING: Thread state - isRunning: {thread.isRunning()}, isFinished: {thread.isFinished()}")
            else:
                print(f"DEBUG: Thread {thread.__class__.__name__} finished after wait")

    def _on_image_processing_complete(self, result):
        """Handles the results from the image processing thread."""
        print("DEBUG: _on_image_processing_complete called")
        print(f"DEBUG: Result keys received: {list(result.keys()) if result else 'None'}")
        
        self.progress_dialog.close()
        print("DEBUG: Progress dialog closed")
        
        self.logger.info(f"Image processing took {result['processing_time']:.2f} seconds.")
        print("DEBUG: Logged processing time")

        print("DEBUG: About to set self.img...")
        self.img = result['image']
        print(f"DEBUG: Image set, shape: {self.img.shape if hasattr(self.img, 'shape') else 'No shape'}")
        
        # Update UI controls
        print("DEBUG: About to update UI controls...")
        data_max = np.iinfo(self.img.dtype).max
        print(f"DEBUG: Data max calculated: {data_max}")
        self._on_ui_controls_setup(data_max, result['threshold1'], result['threshold2'], hash(result['file_path']))
        print("DEBUG: UI controls setup completed")

        # Render the pre-calculated surfaces
        print("DEBUG: About to render surfaces...")
        if hasattr(self, 'image_renderer') and self.image_renderer:
            print("DEBUG: Image renderer available, setting surfaces...")
            self.image_renderer.set_image_and_surfaces(
                result['image'],
                result['polydata1'],
                result['polydata2'],
                result['threshold1'],
                result['threshold2']
            )
            print("DEBUG: Surfaces set successfully")
            # Note: 2D slice and histogram rendering will be triggered by both ui_controls_setup and image_loaded signals
        else:
            print("DEBUG: No image renderer available")

        # Update geometry metrics in the UI
        print("DEBUG: About to update geometry metrics...")
        if self.geometry_calculator:
            print("DEBUG: Geometry calculator available, updating metrics...")
            self.geometry_calculator.update_ui_with_metrics(result['metrics1'], "_1")
            self.geometry_calculator.update_ui_with_metrics(result['metrics2'], "_2")
            print("DEBUG: Geometry metrics updated")
        else:
            print("DEBUG: No geometry calculator available")

        # Update the database
        print("DEBUG: About to update database...")
        self._update_db_with_metrics(result['file_path'], result['metrics1'], "_1")
        print("DEBUG: Metrics1 updated in database")
        self._update_db_with_metrics(result['file_path'], result['metrics2'], "_2")
        print("DEBUG: Metrics2 updated in database")
        self._store_thresholds_in_db(result['file_path'], result['threshold1'], result['threshold2'])
        print("DEBUG: Thresholds stored in database")
        
        print("DEBUG: About to update feature windows...")
        self.update_feature_windows()
        print("DEBUG: Feature windows updated")

        print("DEBUG: About to check classification results...")
        if 'classification' in result and result['classification']:
            print(f"DEBUG: Classification results found: {result['classification']}")
            self._update_db_with_classification(result['file_path'], result['classification'])
            print("DEBUG: Classification results updated in database")
            
            # Update the inference plot
            print("DEBUG: About to update canvasProb with classification results...")
            self._update_inference_plot(result['classification'])
            print("DEBUG: canvasProb update completed")
        else:
            print("DEBUG: No classification results to update")
            
        print("DEBUG: _on_image_processing_complete finished successfully")

    def _update_inference_plot(self, classification_results):
        """Update the inference plot with classification probabilities using PyQtGraph."""
        print(f"DEBUG: _update_inference_plot called with: {classification_results}")
        
        try:
            # Check for PyQtGraph canvasProb widget (not matplotlib axProb)
            if not hasattr(self, 'canvasProb') or self.canvasProb is None:
                print("DEBUG: canvasProb not available, cannot update inference plot")
                return
                
            probabilities = classification_results.get('probabilities', [])
            predicted_class = classification_results.get('predicted_class', 'Unknown')
            confidence = classification_results.get('confidence', 0.0)
            
            print(f"DEBUG: Probabilities: {probabilities}")
            print(f"DEBUG: Predicted class: {predicted_class}")
            print(f"DEBUG: Confidence: {confidence}")
            
            if len(probabilities) == 0:
                print("DEBUG: No probabilities to display")
                return
            
            # Clear the existing PyQtGraph plot
            print("DEBUG: Clearing existing canvasProb plot")
            self.canvasProb.clear()
            
            # Always use 4-stage maturation labels (M, MM, BN, SN)
            class_labels = ['M', 'MM', 'BN', 'SN']
            
            # Calculate maturation score - linear weighted value from 0 to 1
            # M=0, MM=0.33, BN=0.67, SN=1.0
            maturation_weights = [0.0, 0.33, 0.67, 1.0]
            maturation_score = sum(prob * weight for prob, weight in zip(probabilities, maturation_weights))
            
            print(f"DEBUG: Class labels: {class_labels}")
            print(f"DEBUG: Calculated maturation score: {maturation_score:.3f}")
            
            # Create bar plot using PyQtGraph
            print("DEBUG: Creating PyQtGraph bar plot...")
            x_positions = list(range(len(class_labels)))
            
            # Find the predicted class index for highlighting
            max_idx = probabilities.argmax() if hasattr(probabilities, 'argmax') else max(range(len(probabilities)), key=probabilities.__getitem__)
            
            # Create bars with different colors for predicted vs non-predicted classes
            for i, prob in enumerate(probabilities):
                color = 'red' if i == max_idx else 'lightblue'
                # Create individual bar using BarGraphItem
                bar = pg.BarGraphItem(x=[i], height=[prob], width=0.6, brush=color)
                self.canvasProb.addItem(bar)
            
            # Set labels and title
            self.canvasProb.setLabel('left', 'Probability')
            self.canvasProb.setLabel('bottom', 'Classes')
            # Set multi-line title using HTML for proper line breaks and width control
            self.canvasProb.setTitle(
                f'<div style="text-align:left; white-space:pre-line; font-size:10pt; color:#333333;">'
                f'Classification Results<br>'
                f'Predicted: {predicted_class}<br>'
                f'Confidence: {confidence:.3f}<br>'
                f'Maturation Score: {maturation_score:.3f}'
                f'</div>'
            )
            
            # Set x-axis labels
            ax = self.canvasProb.getPlotItem().getAxis('bottom')
            ax.setTicks([[(i, label) for i, label in enumerate(class_labels)]])
            
            # Set y-axis range
            self.canvasProb.setYRange(0, 1)
            self.canvasProb.setXRange(-0.5, len(class_labels) - 0.5)
            
            print("DEBUG: PyQtGraph inference plot updated successfully")
            
        except Exception as e:
            print(f"DEBUG: Error updating inference plot: {e}")
            import traceback
            traceback.print_exc()

    def _on_image_processing_error(self, error_message):
        """Handles errors from the image processing thread."""
        self.progress_dialog.close()
        QMessageBox.critical(self, "Processing Error", error_message)

    def _fallback_image_loading(self, file_path):
        """Fallback image loading when ImageRenderer is not available"""
        try:
            ImageLoadingThread = self._import_image_loading_thread()
            
            if ImageLoadingThread is not None:
                self.logger.debug("Using ImageLoadingThread for fallback loading")
                
                if self.imageLoadingThread and self.imageLoadingThread.isRunning():
                    self.imageLoadingThread.stop_gracefully()
                    self.imageLoadingThread.wait(1000)
                
                self.imageLoadingThread = ImageLoadingThread(file_path)
                self.active_threads.append(self.imageLoadingThread)
                self.imageLoadingThread.result_signal.connect(self._on_fallback_image_loaded)
                self.imageLoadingThread.finished.connect(lambda: self._on_thread_finished(self.imageLoadingThread))
                self.imageLoadingThread.start()
                
                self.progress_label.setText("Loading image...")
                self.progress_label.setVisible(True)
            else:
                self.logger.warning("ImageLoadingThread not available, using synchronous loading")
                self._load_image_synchronously(file_path)
                
        except Exception as e:
            self.logger.error(f"Error in fallback image loading: {e}")
            self.progress_label.setText(f"Fallback loading failed: {str(e)}")
            self.progress_label.setVisible(True)

    def _load_image_synchronously(self, file_path):
        """Load image synchronously as last resort"""
        global tifffile
        try:
            self.logger.debug(f"Loading image synchronously: {os.path.basename(file_path)}")
            
            if tifffile is not None:
                img = tifffile.imread(file_path)
            else:
                import tifffile as tf_module
                img = tf_module.imread(file_path)
            
            self.img = img
            
            self.logger.info(f"Successfully loaded image synchronously: {os.path.basename(file_path)} (shape: {img.shape})")
            
            self.progress_label.setText(f"Image loaded: {os.path.basename(file_path)}")
            self.progress_label.setVisible(True)
            QTimer.singleShot(2000, lambda: self.progress_label.setVisible(False))
                
        except Exception as e:
            self.logger.error(f"Error in synchronous image loading: {e}")
            self.progress_label.setText(f"Failed to load image: {str(e)}")
            self.progress_label.setVisible(True)

    def _on_fallback_image_loaded(self, image_data):
        """Handle image loaded via fallback ImageLoadingThread"""
        try:
            self.img = image_data
            
            self.progress_label.setText("Image loaded successfully")
            self.progress_label.setVisible(True)
            QTimer.singleShot(2000, lambda: self.progress_label.setVisible(False))
                
        except Exception as e:
            print(f"Error handling fallback image load: {e}")

    def _import_image_loading_thread(self):
        """Import ImageLoadingThread on-demand when needed for image loading"""
        try:
            from ..logic.threads.utility_threads import ImageLoadingThread
            self.logger.debug("Successfully imported ImageLoadingThread on-demand via relative import")
            return ImageLoadingThread
        except ImportError:
            try:
                from app.logic.threads.utility_threads import ImageLoadingThread
                self.logger.debug("Successfully imported ImageLoadingThread on-demand via absolute import")
                return ImageLoadingThread
            except ImportError as e:
                self.logger.warning(f"Failed to import ImageLoadingThread on-demand: {e}")
                return None
