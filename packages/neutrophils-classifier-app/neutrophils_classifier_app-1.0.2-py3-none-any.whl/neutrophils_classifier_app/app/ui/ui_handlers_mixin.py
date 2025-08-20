"""
UI Handlers Mixin for the MainWindow.
Handles user interactions, events, and signal connections.
"""
import gc
import pandas as pd
from PyQt5.QtWidgets import QMessageBox, QDialog, QApplication, QSizePolicy
from PyQt5.QtCore import Qt

class UiHandlersMixin:
    """Mixin containing UI event handlers and interaction methods for MainWindow."""

    def _setup_basic_connections(self):
        """Set up signal connections that don't depend on heavy components"""
        self.pushButton_Images.clicked.connect(self.load_image_file)
        self.pushButton_ImageFolder.clicked.connect(self.load_directory)
        self.pushButton_GeometricFeatures.clicked.connect(self.show_geometric_features_window)
        self.pushButton_EmbeddedFeatures.clicked.connect(self.show_embedded_features_window)
        self.pushButtonImportCSV.clicked.connect(self.on_import_csv)

        # Connect single inference button (note: UI has typo "SingleInferene")
        if hasattr(self, 'pushButton_SingleInferene'):
            self.pushButton_SingleInferene.clicked.connect(self.on_single_inference_clicked)

        self.actionSelect_Images.triggered.connect(self.load_image_file)
        self.actionSelect_Image_Folder.triggered.connect(self.load_directory)
        self.actionLoad_Model.triggered.connect(self.load_model)
        self.actionImport_CSV.triggered.connect(self.on_import_csv)
        self.actionModel_Architecture.triggered.connect(self.display_model_summary)
        self.action_Preferences.triggered.connect(self.display_preferences)
        self.actionGeometric_Features.triggered.connect(self.show_geometric_features_window)
        self.actionEmbedded_Features.triggered.connect(self.show_embedded_features_window)

        self.listWidget.currentRowChanged.connect(self.on_list_changed)

    def _setup_heavy_component_connections(self):
        """Set up signal connections that depend on heavy components"""
        self.comboBoxModel.currentIndexChanged.connect(self.model_changed)
        self.pushButton_Model.clicked.connect(self.load_model)
        self.comboBoxManualAnnotation.currentIndexChanged.connect(self.on_manual_annotation_changed)
        
        self.horizontalSlider_intensity1.valueChanged.connect(self.spinBox_intensity1.setValue)
        self.spinBox_intensity1.valueChanged.connect(self.horizontalSlider_intensity1.setValue)
        self.horizontalSlider_intensity2.valueChanged.connect(self.spinBox_intensity2.setValue)
        self.spinBox_intensity2.valueChanged.connect(self.horizontalSlider_intensity2.setValue)
        
        # Connect threshold sliders to streamlined threshold update
        self.horizontalSlider_intensity1.valueChanged.connect(self._on_threshold_changed)
        self.horizontalSlider_intensity2.valueChanged.connect(self._on_threshold_changed)
        # Connect vertical scroll bar for 2D slice updates
        self.verticalScrollBarSlide.valueChanged.connect(self._on_slice_changed)
        self.verticalScrollBarSlide.installEventFilter(self)
        
        # Connect statistical threshold buttons
        self.pushButton_Stat1.clicked.connect(self._on_statistical_threshold1_clicked)
        self.pushButton_Stat2.clicked.connect(self._on_statistical_threshold2_clicked)

        # Initial call to set plot sizes
        self._update_plot_sizes()

    def resizeEvent(self, event):
        """Handle window resize events to adjust plot sizes."""
        # Call the parent class resizeEvent method if it exists
        # Since this is a mixin, we need to check if the method exists in the MRO
        for cls in self.__class__.__mro__:
            if hasattr(cls, 'resizeEvent') and cls is not UiHandlersMixin:
                cls.resizeEvent(self, event)
                break
        self._update_plot_sizes()

        # Force the VTK window to re-render to prevent artifacts after resizing
        if hasattr(self, 'widget') and self.widget:
            self.widget.GetRenderWindow().Render()

    def _update_plot_sizes(self):
        """
        Update plot and VTK window heights to be responsive.
        - Plot heights are constrained by screen height.
        - VTK window expands to fill available space.
        """
        # Define plot frames and the VTK frame
        plot_frames = ['frameSlide', 'framePlotHist', 'framePlot']
        vtk_frame_name = 'frame_vtk'

        # Check if any relevant frames exist
        if not any(hasattr(self, name) for name in plot_frames + [vtk_frame_name]):
            return

        # --- Height Calculation for 2D plots ---
        screen = QApplication.screenAt(self.pos())
        if not screen:
            screen = QApplication.primaryScreen()
        screen_height = screen.geometry().height()

        # Calculate a responsive plot height based on window and screen size
        # - Plots should not be too small (min 80px), nor too large (max 1/4*0.8 of screen or 1/4*0.8 of window)
        min_plot_height = 80
        max_plot_height = int(screen_height * 0.25 * 0.8)
        window_based_height = int(self.height() * 0.25 * 0.8)
        final_plot_height = max(min_plot_height, min(window_based_height, max_plot_height))

        # --- Apply sizing policies ---

        # Apply fixed height to 2D plot frames
        for frame_name in plot_frames:
            if hasattr(self, frame_name):
                frame = getattr(self, frame_name)
                if frame:
                    frame.setFixedHeight(final_plot_height)
                    frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Apply expanding policy to the VTK frame
        if hasattr(self, vtk_frame_name):
            vtk_frame = getattr(self, vtk_frame_name)
            if vtk_frame:
                # To allow expanding height, unset any fixed height by resetting max height
                vtk_frame.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
                vtk_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def load_image_file(self):
        """Load single image files using file dialog with streamlined workflow"""
        try:
            # Check if streamlined manager is available
            if hasattr(self, 'streamlined_manager') and self.streamlined_manager:
                # Use streamlined workflow for file selection
                selected_files = self.streamlined_manager.select_images()
                if selected_files:
                    self.streamlined_manager.update_list_widget(selected_files)
                    self.logger.info(f"Added {len(selected_files)} images via streamlined workflow")
            else:
                # Fallback to legacy file loading
                from ..logic.file_io import load_image_files
                load_image_files(self)
        except Exception as e:
            self.logger.error(f"Error loading image files: {e}")

    def load_directory(self):
        """Load all images from a directory with streamlined workflow"""
        try:
            # For directory loading, we'll use the legacy method for now
            # as the streamlined manager focuses on individual image selection
            from ..logic.file_io import load_image_directory
            load_image_directory(self)
        except Exception as e:
            self.logger.error(f"Error loading directory: {e}")

    def on_import_csv(self):
        """Handle importing results from a CSV file."""
        from ..logic.file_io import import_csv_results
        import_csv_results(self)

    def show_geometric_features_window(self):
        """Show the geometric features window and update its data."""
        try:
            if not hasattr(self, 'GeometricFeaturesWindow') or self.GeometricFeaturesWindow is None:
                QMessageBox.warning(self, "Warning", "Geometric features window is not available yet.")
                return
            
            if self.geometric_features_window:
                # Debug information about the data being passed
                if hasattr(self, 'result_db'):
                    self.logger.debug(f"Updating geometric features window with {len(self.result_db)} rows")
                    if not self.result_db.empty:
                        self.logger.debug(f"Database columns: {list(self.result_db.columns)}")
                        # Check for problematic data types
                        for col in self.result_db.columns:
                            dtype = self.result_db[col].dtype
                            if dtype == 'object':
                                unique_types = set(type(x).__name__ for x in self.result_db[col].dropna())
                                self.logger.debug(f"Column '{col}' has object dtype with types: {unique_types}")
                
                self.geometric_features_window.update_data_and_render(self.result_db)
                self.geometric_features_window.show()
            self.geometric_features_window.raise_()
            self.geometric_features_window.activateWindow()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.logger.error(f"Failed to show geometric features window: {error_details}")
            QMessageBox.critical(self, "Error", f"Failed to show geometric features window: {str(e)}")

    def show_embedded_features_window(self):
        """Show the embedded features window and update its data."""
        try:
            if not hasattr(self, 'EmbeddedFeaturesWindow') or self.EmbeddedFeaturesWindow is None:
                QMessageBox.warning(self, "Warning", "Embedded features window is not available yet.")
                return

            if self.embedded_features_window:
                self.embedded_features_window.update_classifier(self.classifier)
                self.embedded_features_window.update_data_and_render(self.result_db)
                self.embedded_features_window.show()
            self.embedded_features_window.raise_()
            self.embedded_features_window.activateWindow()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show embedded features window: {str(e)}")

    def load_model(self):
        """Load a model"""
        QMessageBox.information(self, "Info", "Model loading functionality to be implemented")

    def display_model_summary(self):
        """Display model summary"""
        QMessageBox.information(self, "Info", "Model summary functionality to be implemented")

    def display_preferences(self):
        """Display preferences dialog"""
        try:
            if hasattr(self, 'ui_preferences') and hasattr(self, 'preferences_manager'):
                self.preferences_manager.load_ui_values(self.ui_preferences)
                self.preferences_manager.setup_ui_connections(self.ui_preferences)
                if self.ui_preferences.exec_() == QDialog.Accepted:
                    if self.preferences_manager.save_ui_values(self.ui_preferences):
                        if hasattr(self, 'enhanced_data_loader') and self.enhanced_data_loader:
                            self._update_enhanced_data_loader_config()
            else:
                QMessageBox.warning(self, "Warning", "Preferences dialog not initialized")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display preferences: {str(e)}")

    def model_changed(self):
        """Handle model selection change using neutrophils-core Classifier"""
        # Clean up existing models
        if hasattr(self, 'model') and self.model:
            del self.model
            self.model = None
        if hasattr(self, 'classifier') and self.classifier:
            del self.classifier
            self.classifier = None
        gc.collect()

        model_index = self.comboBoxModel.currentIndex()
        if model_index < 0 or model_index >= len(self.models):
            return

        model_path = self.models[model_index]
        config_path = self.configs[model_index]
        
        # Use threaded loading but now load Classifier instead of direct model
        from ..logic.threads.model_threads import ModelLoadingThread
        self.model_loading_thread = ModelLoadingThread(model_path, config_path)
        
        # Connect to the new status signals
        self.model_loading_thread.loadingStarted.connect(self._on_model_load_started)
        self.model_loading_thread.modelLoaded.connect(self._on_model_load_success)
        self.model_loading_thread.loadingFailed.connect(self._on_model_load_failure)
        
        self.model_loading_thread.start()

    def _on_model_load_started(self):
        """Handle model loading started signal"""
        if hasattr(self, 'status_lamp') and self.status_lamp:
            self.status_lamp.setState('Loading')
        self.logger.info("Model loading started")

    def _on_model_load_success(self, result):
        """Handle successful model loading"""
        if hasattr(self, 'status_lamp') and self.status_lamp:
            self.status_lamp.setState('Ready')
        
        # Enable relevant UI controls
        self._set_image_controls_enabled(True)
        
        # Call the existing model loaded handler
        self.on_model_loaded(result)

    def _on_model_load_failure(self, error_msg):
        """Handle model loading failure"""
        if hasattr(self, 'status_lamp') and self.status_lamp:
            self.status_lamp.setState('Error')
        
        # Disable relevant UI controls
        self._set_image_controls_enabled(False)
        
        # Show error message to user
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Model Loading Error", f"Failed to load model:\n{error_msg}")
        self.logger.error(f"Model loading failed: {error_msg}")

    def on_model_loaded(self, result):
        print("DEBUG: on_model_loaded - Starting model loading process...")
        self.model, self.model_config = result
        
        print(f"DEBUG: on_model_loaded - Model loaded: {self.model is not None}")
        print(f"DEBUG: on_model_loaded - Model type: {type(self.model)}")
        print(f"DEBUG: on_model_loaded - Model config loaded: {self.model_config is not None}")
        print(f"DEBUG: on_model_loaded - Model config type: {type(self.model_config)}")
        
        # Safely get model_name, defaulting to 'N/A' if config is missing or key is absent
        model_name = self.model_config.get('model_name', 'N/A') if self.model_config else 'N/A'
        print(f"DEBUG: on_model_loaded - Model name: {model_name}")
        
        self.logger.info(f"Model config loaded: {model_name if model_name != 'N/A' else 'N/A. please check'}")

        # FIX: Set label_encoder_path to resolve "Model components not available for inference" warning
        print("DEBUG: on_model_loaded - Setting label_encoder_path...")
        try:
            import os
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
            if os.path.exists(models_dir):
                label_encoder_files = [f for f in os.listdir(models_dir) if 'label_encoder' in f.lower() and f.endswith('.npy')]
                
                if label_encoder_files:
                    self.label_encoder_path = os.path.join(models_dir, label_encoder_files[0])
                    print(f"DEBUG: on_model_loaded - Label encoder path set: {self.label_encoder_path}")
                    self.logger.info(f"Label encoder path set: {self.label_encoder_path}")
                else:
                    self.label_encoder_path = None
                    print("DEBUG: on_model_loaded - No label encoder files found")
                    self.logger.warning("No label encoder files found in models directory")
            else:
                self.label_encoder_path = None
                print(f"DEBUG: on_model_loaded - Models directory not found: {models_dir}")
                self.logger.warning(f"Models directory not found: {models_dir}")
        except Exception as e:
            self.label_encoder_path = None
            print(f"DEBUG: on_model_loaded - Error setting label_encoder_path: {e}")
            self.logger.error(f"Error setting label_encoder_path: {e}")

        print(f"DEBUG: on_model_loaded - Has Classifier attribute: {hasattr(self, 'Classifier')}")
        if hasattr(self, 'Classifier'):
            print(f"DEBUG: on_model_loaded - Classifier class: {self.Classifier}")
            print(f"DEBUG: on_model_loaded - Classifier class type: {type(self.Classifier)}")

        # Create Classifier instance using loaded model and config
        if self.model and hasattr(self, 'Classifier') and self.Classifier:
            print("DEBUG: on_model_loaded - Attempting to create Classifier instance...")
            try:
                # Get the model path from the currently selected model
                model_index = self.comboBoxModel.currentIndex()
                print(f"DEBUG: on_model_loaded - Current model index: {model_index}")
                print(f"DEBUG: on_model_loaded - Total models available: {len(self.models)}")
                
                if model_index >= 0 and model_index < len(self.models):
                    model_path = self.models[model_index]
                    print(f"DEBUG: on_model_loaded - Model path: {model_path}")
                    
                    # Initialize Classifier with the loaded configuration
                    print("DEBUG: on_model_loaded - Creating Classifier instance...")
                    self.classifier = self.Classifier(
                        model=self.model,
                        config=self.model_config
                    )
                    print(f"DEBUG: on_model_loaded - Classifier created successfully: {self.classifier}")
                    print(f"DEBUG: on_model_loaded - Classifier type: {type(self.classifier)}")
                    print(f"DEBUG: on_model_loaded - Classifier is None: {self.classifier is None}")
                    
                    self.logger.info(f"Classifier instantiated successfully for model: {model_name}")
                    self._show_progress_briefly(f"Model '{model_name}' and Classifier loaded successfully.", duration=3000)
                    
                    # Update the classifier in the embedded features window
                    if hasattr(self, 'embedded_features_window') and self.embedded_features_window:
                        self.embedded_features_window.update_classifier(self.classifier)
                else:
                    print(f"DEBUG: on_model_loaded - Invalid model index {model_index} for models list of length {len(self.models)}")
                    self.logger.warning("Could not determine model path for Classifier initialization")
                    self._show_progress_briefly(f"Model '{model_name}' loaded but Classifier initialization failed.", duration=3000)
            except Exception as e:
                print(f"DEBUG: on_model_loaded - Exception creating Classifier: {e}")
                print(f"DEBUG: on_model_loaded - Exception type: {type(e)}")
                import traceback
                traceback_str = traceback.format_exc()
                print(f"DEBUG: on_model_loaded - Traceback: {traceback_str}")
                self.classifier = None  # Ensure classifier is set to None on failure
                print(f"DEBUG: on_model_loaded - Classifier set to None after exception")
                self.logger.error(f"Failed to create Classifier instance: {e}")
                QMessageBox.critical(self, "Classifier Error", f"Failed to create the classifier.\n\nError: {e}\n\nTraceback:\n{traceback_str}")
                self._show_progress_briefly(f"Model '{model_name}' loaded but Classifier creation failed.", duration=3000)
        elif self.model:
            print("DEBUG: on_model_loaded - Model loaded but Classifier class not available")
            self.classifier = None  # Ensure classifier is None if not available
            self._show_progress_briefly(f"Model '{model_name}' loaded successfully (Classifier not available).", duration=3000)
        else:
            print("DEBUG: on_model_loaded - Model is invalid or None")
            self.classifier = None  # Ensure classifier is None if model is invalid
            self._show_progress_briefly("Model loaded but is invalid.", duration=3000)
        
        # Enable image loading and processing controls now that a model is ready
        self._set_image_controls_enabled(True)

        # FIX: Verify all model components are now available for inference
        print("DEBUG: on_model_loaded - Verifying model components for inference...")
        model_components_available = all([
            getattr(self, 'model', None),
            getattr(self, 'model_config', None),
            getattr(self, 'label_encoder_path', None)
        ])
        print(f"DEBUG: on_model_loaded - Model components available: {model_components_available}")
        if model_components_available:
            print("DEBUG: on_model_loaded - ✅ All model components ready for inference")
            self.logger.info("All model components ready for inference")
        else:
            print("DEBUG: on_model_loaded - ❌ Some model components missing for inference")
            missing_components = []
            if not getattr(self, 'model', None):
                missing_components.append('model')
            if not getattr(self, 'model_config', None):
                missing_components.append('model_config')
            if not getattr(self, 'label_encoder_path', None):
                missing_components.append('label_encoder_path')
            print(f"DEBUG: on_model_loaded - Missing components: {missing_components}")
            self.logger.warning(f"Some model components missing for inference: {missing_components}")

    def on_manual_annotation_changed(self):
        """Handle manual annotation change and update database."""
        current_row = self.listWidget.currentRow()
        if current_row < 0 or current_row >= len(self.files):
            return

        path = self.files[current_row]
        annotation = self.comboBoxManualAnnotation.currentText()
        self.update_annotation_in_db(path, annotation)

    def _refresh_annotation_ui(self):
        """Refreshes the manual annotation combobox from the result_db for the current selection."""
        current_row = self.listWidget.currentRow()
        if current_row < 0 or current_row >= len(self.files):
            self.comboBoxManualAnnotation.blockSignals(True)
            self.comboBoxManualAnnotation.setCurrentIndex(0)
            self.comboBoxManualAnnotation.blockSignals(False)
            return

        selected_file = self.files[current_row]
        
        self.comboBoxManualAnnotation.blockSignals(True)
        try:
            record = self.result_db[self.result_db['Path'] == selected_file]
            if not record.empty:
                annotation = record.iloc[0].get('ManualAnnotation', '')
                if pd.isna(annotation):
                    annotation = ''
                index = self.comboBoxManualAnnotation.findText(str(annotation), Qt.MatchFixedString)
                self.comboBoxManualAnnotation.setCurrentIndex(index if index >= 0 else 0)
            else:
                self.comboBoxManualAnnotation.setCurrentIndex(0)
        finally:
            self.comboBoxManualAnnotation.blockSignals(False)

    def on_list_changed(self):
        """
        Handle list widget selection change with loading state check.
        Uses the streamlined workflow for efficient image processing.
        """
        self._refresh_annotation_ui()

        current_row = self.listWidget.currentRow()
        if current_row >= 0 and current_row < len(self.files):
            selected_file = self.files[current_row]
            
            # DIAGNOSTIC LOGGING: Check streamlined manager state
            print(f"DEBUG DIAGNOSIS: on_list_changed called for {selected_file}")
            print(f"DEBUG DIAGNOSIS: hasattr(self, 'streamlined_manager'): {hasattr(self, 'streamlined_manager')}")
            if hasattr(self, 'streamlined_manager'):
                print(f"DEBUG DIAGNOSIS: self.streamlined_manager is None: {self.streamlined_manager is None}")
                print(f"DEBUG DIAGNOSIS: self.streamlined_manager type: {type(self.streamlined_manager)}")
                if self.streamlined_manager:
                    print(f"DEBUG DIAGNOSIS: can_load_image(): {self.streamlined_manager.can_load_image()}")
                    print(f"DEBUG DIAGNOSIS: is_loading: {self.streamlined_manager.is_loading}")
            else:
                print("DEBUG DIAGNOSIS: streamlined_manager attribute does not exist")
            
            # Check if streamlined manager is available and can load images
            if (hasattr(self, 'streamlined_manager') and self.streamlined_manager and
                self.streamlined_manager.can_load_image()):
                
                print(f"DEBUG DIAGNOSIS: Using streamlined workflow for: {selected_file}")
                self.logger.info(f"Using streamlined workflow for: {selected_file}")
                result = self.streamlined_manager.load_and_render_image(selected_file)
                print(f"DEBUG DIAGNOSIS: load_and_render_image returned: {result}")
                
            elif (hasattr(self, 'ui_state_manager') and self.ui_state_manager and
                  not self.ui_state_manager.can_load_image()):
                
                # Currently loading - prevent concurrent operations
                print(f"DEBUG DIAGNOSIS: Cannot load image - UI state manager blocking")
                self.logger.warning(f"Cannot load image {selected_file} - already loading")
                return
                
            else:
                # Fallback to legacy processing
                print(f"DEBUG DIAGNOSIS: Using legacy workflow for: {selected_file}")
                self.logger.info(f"Using legacy workflow for: {selected_file}")
                from ..logic.file_io import trigger_image_processing
                trigger_image_processing(self, selected_file)

    def _on_image_rendered(self, message):
        """Handle successful image rendering"""
        self._show_progress_briefly(message)
    
    def _on_image_render_error(self, error_message):
        """Handle image rendering errors"""
        self.progress_label.setText(f"Render error: {error_message}")
        self.progress_label.setVisible(True)
    
    def _on_ui_controls_setup(self, data_max, threshold1, threshold2, path_hash):
        """Handle UI controls setup from ImageRenderer signal"""
        self.horizontalSlider_intensity1.setRange(1, data_max)
        self.horizontalSlider_intensity1.setValue(threshold1)
        self.spinBox_intensity1.setRange(1, data_max)
        self.spinBox_intensity1.setValue(threshold1)
        
        self.horizontalSlider_intensity2.setRange(1, data_max)
        self.horizontalSlider_intensity2.setValue(threshold2)
        self.spinBox_intensity2.setRange(1, data_max)
        self.spinBox_intensity2.setValue(threshold2)
        
        self.logger.debug(f"UI controls updated: range 1-{data_max}, T1={threshold1}, T2={threshold2}")
        
        # Set slice slider to the middle and trigger rendering
        if hasattr(self, 'image_renderer') and self.image_renderer:
            if self.img is not None and self.img.ndim >= 3:
                z_max = self.img.shape[0] - 1
                mid_slice = z_max // 2
                self.verticalScrollBarSlide.setRange(0, z_max)
                self.verticalScrollBarSlide.setValue(mid_slice)
                z_slice = mid_slice
            else:
                z_slice = self.verticalScrollBarSlide.value() if hasattr(self, 'verticalScrollBarSlide') else 0
            
            self.image_renderer.render_2d_slice_with_contours(z_slice, threshold1, threshold2)
            self.image_renderer.render_histogram(threshold1, threshold2)

    def _on_image_loaded(self, image_data):
        """
        Handle image loaded signal.
        The main rendering logic is now in _on_ui_controls_setup to avoid race conditions.
        This handler can be used for any logic that must run after an image is confirmed loaded.
        """
        self.logger.debug(f"Image loaded signal received for image with shape {image_data.shape}")

    def _on_geometry_calculation_error(self, error_message, label_suffix):
        """Handle geometry calculation errors"""
        self.logger.error(f"Geometry calculation error for suffix '{label_suffix}': {error_message}")
        self._show_progress_briefly(f"Geometry calc error: {error_message}", duration=3000)

    def _on_threshold_changed(self):
        """Handle threshold slider changes using streamlined workflow"""
        try:
            # Get current threshold values
            threshold1 = self.horizontalSlider_intensity1.value()
            threshold2 = self.horizontalSlider_intensity2.value()
            
            # Use streamlined manager if available
            if (hasattr(self, 'streamlined_manager') and self.streamlined_manager and 
                self.streamlined_manager.current_image_data is not None):
                
                self.streamlined_manager.update_thresholds(threshold1, threshold2)
                
            else:
                # Fallback to legacy rendering
                if hasattr(self, 'render_image'):
                    self.render_image()
                    
        except Exception as e:
            self.logger.error(f"Error updating thresholds: {e}")

    def _on_slice_changed(self):
        """Handle Z-slice changes for 2D rendering"""
        try:
            z_slice = self.verticalScrollBarSlide.value()
            
            # Use secondary renderers if available
            if (hasattr(self, 'secondary_renderers') and self.secondary_renderers and
                hasattr(self.secondary_renderers, 'current_image_data') and
                self.secondary_renderers.current_image_data is not None):
                
                self.secondary_renderers.update_z_slice(z_slice)
                
            else:
                # Fallback to legacy rendering
                if hasattr(self, 'render_image'):
                    self.render_image()
                    
        except Exception as e:
            self.logger.error(f"Error updating z-slice: {e}")

    def eventFilter(self, obj, event):
        """Event filter to handle tooltip display for vertical scroll bar"""
        from PyQt5.QtCore import QEvent, QObject
        from PyQt5.QtWidgets import QToolTip
        if obj == self.verticalScrollBarSlide and event.type() == QEvent.ToolTip:
            value = self.verticalScrollBarSlide.value()
            max_value = self.verticalScrollBarSlide.maximum()
            QToolTip.showText(event.globalPos(), f"Z-Slice: {value}/{max_value}", self.verticalScrollBarSlide)
            return True
        return QObject.eventFilter(self, obj, event)

    def _check_model_ready(self):
        """Check if the model is ready for operations"""
        if not hasattr(self, 'status_lamp') or not self.status_lamp:
            return False
        return self.status_lamp._state == 'Ready'

    def on_single_inference_clicked(self):
        """Handle single inference button click with model readiness check"""
        if not self._check_model_ready():
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Model Not Ready",
                              "Please wait for the model to load before running inference.")
            return
        
        # Model is ready, proceed with inference
        self.logger.info("Single inference requested - model is ready")
        # TODO: Implement single inference logic here
        QMessageBox.information(self, "Single Inference",
                              "Single inference functionality to be implemented.")

    def _on_statistical_threshold1_clicked(self):
        """Handle statistical threshold button 1 click"""
        self._show_statistical_threshold_dialog(1, "Intensity 1", default_method="mean")

    def _on_statistical_threshold2_clicked(self):
        """Handle statistical threshold button 2 click"""
        self._show_statistical_threshold_dialog(2, "Intensity 2", default_method="percentile", default_percentile=2)

    def _show_statistical_threshold_dialog(self, threshold_number, threshold_name, default_method="mean", default_percentile=50):
        """Show statistical threshold dialog and update threshold values"""
        # Check if image is loaded
        if not hasattr(self, 'img') or self.img is None:
            QMessageBox.warning(self, "No Image Loaded",
                              "Please load an image before setting statistical thresholds.")
            return

        try:
            from .statistical_threshold_dialog import StatisticalThresholdDialog
            
            dialog = StatisticalThresholdDialog(self, threshold_name)
            
            # Set default values based on current settings
            if default_method == "percentile":
                dialog.set_current_method("percentile", default_percentile)
            else:
                dialog.set_current_method("mean")
            
            if dialog.exec_() == QDialog.Accepted:
                method, value = dialog.get_values()
                self._apply_statistical_threshold(threshold_number, method, value)
                
        except Exception as e:
            self.logger.error(f"Error showing statistical threshold dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show threshold dialog: {str(e)}")

    def _apply_statistical_threshold(self, threshold_number, method, value):
        """Apply the selected statistical threshold method"""
        try:
            import numpy as np
            
            if self.img is None:
                self.logger.warning("No image loaded for threshold calculation")
                return
            
            # Calculate threshold value based on method
            if method == "mean":
                threshold_value = int(np.mean(self.img))
                method_description = "mean"
            elif method == "percentile":
                threshold_value = int(np.percentile(self.img, value))
                method_description = f"{value}th percentile"
            else:
                self.logger.error(f"Unknown threshold method: {method}")
                return
            
            # Update the appropriate slider and spinbox
            if threshold_number == 1:
                self.horizontalSlider_intensity1.setValue(threshold_value)
                self.spinBox_intensity1.setValue(threshold_value)
                slider_name = "Intensity 1"
            elif threshold_number == 2:
                self.horizontalSlider_intensity2.setValue(threshold_value)
                self.spinBox_intensity2.setValue(threshold_value)
                slider_name = "Intensity 2"
            else:
                self.logger.error(f"Invalid threshold number: {threshold_number}")
                return
            
            # Log the change and show brief feedback
            self.logger.info(f"Applied {method_description} threshold to {slider_name}: {threshold_value}")
            self._show_progress_briefly(f"{slider_name} set to {threshold_value} ({method_description})", duration=2000)
            
        except Exception as e:
            self.logger.error(f"Error applying statistical threshold: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply threshold: {str(e)}")