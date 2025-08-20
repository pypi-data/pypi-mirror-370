from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QProgressDialog, QMessageBox, QComboBox, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QThread
from ..logic.threaded_processes import BatchInferenceThread, QdrantFetchThread
from neutrophils_core.loader.optimized_image_data_generator_3d import OptimizedImageDataGenerator3D
from ..utils.resource_loader import get_ui_file_path
from .progress_dialog import BatchProgressDialog
from .csv_export_utils import export_dataframe_to_csv
import os
import pandas as pd
import sys
import pyqtgraph as pg
import numpy as np
from qdrant_client import QdrantClient
from umap import UMAP

class EmbeddedFeaturesWindow(QDialog):
    """
    A dialog window to display embedded features from model predictions.
    
    This class loads a UI file and populates a QTableWidget with data from a
    pandas DataFrame. It serves as a placeholder and can be extended with
    more functionality like plotting.
    """
    def __init__(self, parent=None, result_db_ref=None, classifier=None):
        """
        Initializes the EmbeddedFeaturesWindow.

        Args:
            parent: The parent widget of this dialog.
            result_db_ref (pd.DataFrame, optional): A DataFrame containing the
                feature data to be displayed. Defaults to None.
            classifier: The classifier instance.
        """
        super().__init__(parent)
        # Load the UI file using packaging utilities
        ui_path = get_ui_file_path('embedded_features.ui')
        uic.loadUi(str(ui_path), self)

        # Store a reference or copy of the result_db
        self.result_db = result_db_ref if result_db_ref is not None else pd.DataFrame()
        self.classifier = classifier
        
        # Remove the question mark from the title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Set tableWidget min horizontal size to be half of current screen width
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            screen_width = screen.availableGeometry().width()
            self.tableWidget.setMinimumWidth(int(screen_width // 2.5))
            self.framePlotScatter.setMinimumWidth(int(screen_width // 4.5))

        # Initial rendering of the table
        self.render_table_widget()
        
        # Connect the batch inference button
        self.pushButtonBatchInference.clicked.connect(self.batch_inference)
        
        # Connect the export CSV button
        self.pushButtonExportCSV.clicked.connect(self.export_csv)

        # Set default IP
        self.lineEditURL.setText("129.67.90.207")

        self.setup_plot()

        # Connections for Qdrant
        self.pushButtonRefresh.clicked.connect(self.start_fetching_embeddings)
        self.update_collections_timer = QTimer(self)
        self.update_collections_timer.setSingleShot(True)
        self.update_collections_timer.timeout.connect(self.update_collections)
        self.lineEditURL.textChanged.connect(self.on_url_text_changed)
        self.spinBoxPort.valueChanged.connect(self.update_collections)

        self.update_collections()

    def setup_plot(self):
        """
        Sets up the pyqtgraph scatter plot.
        """
        self.plotWidget = pg.PlotWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plotWidget)
        self.framePlotScatter.setLayout(layout)

        self.scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        self.plotWidget.addItem(self.scatter)
        self.plotWidget.getViewBox().setAspectLocked(True)
        
        # Add initial centered text
        font = QtGui.QFont()
        font.setPointSize(18)
        text = pg.TextItem("Vector Embeddings Plot", color=(128, 128, 128), anchor=(0.5, 0.5))
        text.setFont(font)
        self.plotWidget.addItem(text)
        self.plotWidget.getViewBox().setMouseEnabled(x=True, y=True)

    def on_url_text_changed(self):
        """
        Starts a timer to update collections after the user stops typing.
        """
        self.update_collections_timer.start(2000) # 2000ms delay

    def update_collections(self):
        """
        Connects to the Qdrant server and populates the collection combobox.
        """
        try:
            host = self.lineEditURL.text()
            port = self.spinBoxPort.value()
            client = QdrantClient(host=host, port=port, timeout=2)
            collections = client.get_collections().collections
            self.comboBoxCollection.clear()
            for collection in collections:
                self.comboBoxCollection.addItem(collection.name)
        except Exception as e:
            self.comboBoxCollection.clear()
            self.comboBoxCollection.addItem("Connection Error")
            print(f"Could not connect to Qdrant to fetch collections: {e}")

    def start_fetching_embeddings(self):
        """
        Starts the thread to fetch embeddings from Qdrant.
        """
        host = self.lineEditURL.text()
        port = self.spinBoxPort.value()
        collection_name = self.comboBoxCollection.currentText()
        max_points = self.spinBoxMaxPoints.value()

        if not collection_name or collection_name == "Connection Error":
            QMessageBox.warning(self, "Warning", "Please select a valid collection.")
            return

        self.progress_dialog = QProgressDialog("Fetching embeddings...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        self.fetch_thread = QdrantFetchThread(host, port, collection_name, max_points)
        self.fetch_thread.progress_update.connect(self.on_fetch_progress)
        self.fetch_thread.processing_complete.connect(self.on_fetch_complete)
        self.fetch_thread.error_occurred.connect(self.on_fetch_error)
        self.progress_dialog.canceled.connect(self.fetch_thread.stop)
        self.fetch_thread.start()

    def on_fetch_progress(self, value, message):
        self.progress_dialog.setValue(value)
        self.progress_dialog.setLabelText(message)

    def on_fetch_error(self, message):
        self.progress_dialog.close()
        QMessageBox.critical(self, "Error", f"An error occurred while fetching embeddings:\n{message}")

    def on_fetch_complete(self, embeddings, labels):
        import time
        from PyQt5.QtCore import QThread
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        thread_id = int(str(QThread.currentThreadId()))
        print(f"[{timestamp}] [EmbeddedFeaturesWindow::on_fetch_complete::{thread_id}] Received fetch completion signal.")

        self.progress_dialog.setValue(100)
        QMessageBox.information(self, "Success", f"Successfully fetched {len(embeddings)} embeddings.")
        
        # Use UMAP to reduce dimensionality
        if embeddings.shape[1] > 2:
            umap_reducer = UMAP(n_components=2, random_state=42)
            embeddings_2d = umap_reducer.fit_transform(embeddings)
        else:
            embeddings_2d = embeddings
            
        self.render_scatter_plot(embeddings_2d, labels)
        print(f"[{timestamp}] [EmbeddedFeaturesWindow::on_fetch_complete::{thread_id}] Finished handling fetch completion.")

    def render_scatter_plot(self, embeddings, labels):
        self.plotWidget.clear()
        self.scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None))
        self.plotWidget.addItem(self.scatter)

        label_colors = {
            'M': 'm',    # magenta
            'MM': 'c',   # cyan
            'BN': 'y',   # yellow
            'SN': (255, 165, 0)  # orange (RGB tuple)
        }
        
        spots = []
        for i in range(len(embeddings)):
            color = label_colors.get(labels[i], 'w')
            spots.append({'pos': embeddings[i], 'data': 1, 'brush': pg.mkBrush(color)})
        
        self.scatter.addPoints(spots)

    def update_classifier(self, classifier):
        """
        Updates the classifier instance.
        """
        self.classifier = classifier

    def update_data_and_render(self, new_result_db):
        """
        Updates the internal DataFrame and re-renders the table.

        Args:
            new_result_db (pd.DataFrame): The new DataFrame to display.
        """
        self.result_db = new_result_db
        self.render_table_widget()

    def render_table_widget(self):
        """
        Populates the tableWidget with specific columns from self.result_db.
        The 'ManualAnnotation' column is rendered with a QComboBox.
        """
        if self.result_db is None or self.result_db.empty:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        # Define all columns that could be displayed
        all_display_columns = [
            'ImageName',
            'ManualAnnotation', 'Predicted_Class', 'ClassProb_M', 'ClassProb_MM',
            'ClassProb_BN', 'ClassProb_SN', 'MaturationScore', 'Path'
        ]

        # Filter for columns that actually exist in the result_db
        display_columns = [col for col in all_display_columns if col in self.result_db.columns]

        if not display_columns:
            filtered_db = pd.DataFrame()
        else:
            filtered_db = self.result_db[display_columns]

        self.tableWidget.setRowCount(filtered_db.shape[0])
        self.tableWidget.setColumnCount(filtered_db.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(filtered_db.columns)

        # Get the column index for 'ManualAnnotation'
        try:
            manual_annotation_col_index = display_columns.index('ManualAnnotation')
        except ValueError:
            manual_annotation_col_index = -1

        for i in range(filtered_db.shape[0]):
            for j in range(filtered_db.shape[1]):
                if j == manual_annotation_col_index:
                    # Only ManualAnnotation column gets a combobox
                    combobox = QComboBox()
                    options = ['', 'M', 'MM', 'BN', 'SN']
                    combobox.addItems(options)

                    current_value = str(filtered_db.iloc[i, j])
                    if pd.isna(filtered_db.iloc[i, j]):
                        current_value = ''
                    
                    if current_value in options:
                        combobox.setCurrentText(current_value)

                    combobox.currentTextChanged.connect(
                        lambda text, row=i: self.on_manual_annotation_changed(text, row)
                    )
                    self.tableWidget.setCellWidget(i, j, combobox)
                else:
                    # All other columns (including Predicted_Class) are read-only text items
                    item_value = filtered_db.iloc[i, j]
                    column_name = display_columns[j]
                    
                    if pd.isna(item_value):
                        display_value = ""
                    else:
                        try:
                            # Try to format as float if possible
                            display_value = f"{float(item_value):.4f}"
                        except (ValueError, TypeError):
                            display_value = str(item_value)
                    
                    item = QTableWidgetItem(display_value)
                    
                    # Make Predicted_Class column read-only (non-editable)
                    if column_name == 'Predicted_Class':
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    self.tableWidget.setItem(i, j, item)
        
        self.tableWidget.resizeColumnsToContents()

    def on_manual_annotation_changed(self, text, row):
        """
        Handles changes in the manual annotation combobox.
        Updates the DataFrame and notifies the parent window.
        """
        try:
            # Get the column index for 'ManualAnnotation' in the main DataFrame
            col_idx = self.result_db.columns.get_loc('ManualAnnotation')
            
            # Update the internal DataFrame using the positional index
            self.result_db.iloc[row, col_idx] = text
            
            # Notify the parent window to update its views
            if self.parent():
                # This syncs the entire DataFrame back to the parent
                self.parent().result_db = self.result_db
                # This tells the parent to update any other windows that might be open
                self.parent().update_feature_windows()
                print(f"Updated row {row} with annotation '{text}' and notified parent.")

        except Exception as e:
            print(f"Error updating manual annotation for row {row}: {e}")
            QMessageBox.critical(self, "Error", f"Could not update annotation: {e}")

    def export_csv(self):
        """
        Export the current result_db DataFrame to a CSV file.
        """
        export_dataframe_to_csv(
            parent_widget=self,
            dataframe=self.result_db,
            default_filename="neutrophils_embedded.csv",
            dialog_title="Save CSV File"
        )

    def get_safe_db_copy(self):
        """
        Creates a deep copy of the result_db to be used in a separate thread.
        This prevents any race conditions or issues with shared data.
        """
        return self.result_db.copy(deep=True)

    def batch_inference(self):
        """
        Run batch inference process for CNN model predictions.
        """
        print("DEBUG BATCH: batch_inference method called")
        self.pushButtonBatchInference.setEnabled(False)
        
        # Verbose check for data availability
        if self.result_db.empty:
            QMessageBox.warning(self, "Warning", "No data to process. Please load images first.")
            self.pushButtonBatchInference.setEnabled(True)
            return
        
        # Check if model is ready using the status lamp
        if (hasattr(self.parent(), 'status_lamp') and self.parent().status_lamp and
            self.parent().status_lamp._state != 'Ready'):
            QMessageBox.warning(self, "Model Not Ready",
                              "Please wait for the model to load before running batch inference.")
            self.pushButtonBatchInference.setEnabled(True)
            return
        
        if not self.classifier:
            if hasattr(self.parent(), 'classifier') and self.parent().classifier:
                self.classifier = self.parent().classifier
            else:
                QMessageBox.warning(self, "Warning", "No classifier available. Please load a model first.")
                self.pushButtonBatchInference.setEnabled(True)
                return

        # Use our custom BatchProgressDialog with task ratio display
        total_images = len(self.result_db)
        self.progress_dialog = BatchProgressDialog(self, "Batch Inference", total_images)
        self.progress_dialog.show()

        # Get model and model parameters from parent window
        if hasattr(self.classifier, 'model'):
            model = self.classifier.model
        else:
            model = self.classifier
            
        model_config = self.parent().model_config
        label_encoder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'label_encoder_classes.npy')
        
        # Create a safe copy of the database for the thread
        db_copy = self.get_safe_db_copy()

        # Prepare data for OptimizedImageDataGenerator3D
        file_paths = db_copy['Path'].tolist()
        
        from pathlib import Path
        path_objects = [Path(p) for p in file_paths]
        
        try:
            base_dir = path_objects[0].parent
            relative_paths = [str(p.relative_to(base_dir)) for p in path_objects]
        except ValueError:
            base_dir = Path(os.path.abspath(os.sep))
            relative_paths = [str(p) for p in path_objects]

        inference_df = pd.DataFrame({'filepath': relative_paths})
        data_config = model_config.get("data", {})

        datagen = OptimizedImageDataGenerator3D(
            df=inference_df,
            data_dir=base_dir,
            batch_size=data_config.get("inference_batch_size", data_config.get("batch_size", 16)),
            image_size=data_config.get("image_size", [64, 64, 64]),
            mip=data_config.get("use_mip", False),
            classes=None,
            shuffle=False,
            train=False,
            to_fit=False,
            get_paths=True,
            use_tf_data_optimization=True,
            augmentation_config=None,
            intensity_input_percentiles=(1, 99),
            intensity_out_range=(0, 255)
        )

        self.batch_thread = BatchInferenceThread(
            db_copy,
            model,
            model_config,
            label_encoder_path,
            datagen
        )
        self.batch_thread.progress_update.connect(self.on_batch_progress_update)
        self.batch_thread.processing_complete.connect(self.update_results_from_thread)
        self.batch_thread.error_occurred.connect(self.on_batch_processing_error)
        self.progress_dialog.canceled.connect(self.batch_thread.stop)
        self.batch_thread.start()

    def on_batch_progress_update(self, progress, message):
        """
        Handle batch processing progress updates with task counting.
        """
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            # Extract current task name from message if available
            current_task = None
            if message and "Processed" in message:
                # Extract filename from "Processed filename.tif" message
                current_task = message.replace("Processed ", "")
            
            # Calculate completed count from progress percentage
            total_tasks = self.progress_dialog.total_tasks
            completed_count = int((progress / 100.0) * total_tasks)
            
            self.progress_dialog.update_progress(progress, completed_count, current_task)

    def update_results_from_thread(self, updated_db):
        """
        Handle completion of batch processing by updating the main DataFrame.
        """
        import time
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        thread = QThread.currentThread()
        thread_id = str(thread.objectName()) if thread else "main"
        print(f"[{timestamp}] [EmbeddedFeaturesWindow::update_results_from_thread::{thread_id}] Received batch processing completion signal.")

        try:
            print("DEBUG BATCH_INFERENCE: Starting batch processing completion handler")
            self.result_db = updated_db
            print("DEBUG BATCH_INFERENCE: Updated result_db")

            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                print("DEBUG BATCH_INFERENCE: Closing progress dialog")
                self.progress_dialog.setValue(100)
                self.progress_dialog.close()
                print("DEBUG BATCH_INFERENCE: Progress dialog closed")

            print("DEBUG BATCH_INFERENCE: Updating data and rendering")
            self.update_data_and_render(self.result_db)
            print("DEBUG BATCH_INFERENCE: Data and rendering updated")

            # Defer parent update to avoid VTK crashes.
            # The crash is likely due to immediate VTK rendering calls triggered
            # by the parent window update, conflicting with the current event processing.
            # A short delay allows the event loop to process pending events.
            QTimer.singleShot(100, self._deferred_parent_update)

        except Exception as e:
            print(f"DEBUG BATCH_INFERENCE: Error in batch processing completion handler: {e}")
            import traceback
            print(f"DEBUG BATCH_INFERENCE: Traceback: {traceback.format_exc()}")
            QMessageBox.critical(self, "Error", f"An error occurred after batch processing: {e}")
        finally:
            self.pushButtonBatchInference.setEnabled(True)
            print(f"[{timestamp}] [EmbeddedFeaturesWindow::update_results_from_thread::{thread_id}] Finished handling completion.")

    def _deferred_parent_update(self):
        """
        Updates the parent window's data and UI. This is deferred to avoid
        conflicts with VTK rendering, which can cause crashes if not handled
        on the main event loop correctly.
        """
        if self.parent():
            try:
                print("DEBUG BATCH_INFERENCE: Deferred update: Updating parent window database")
                self.parent().result_db = self.result_db
                if hasattr(self.parent(), 'update_feature_windows'):
                    print("DEBUG BATCH_INFERENCE: Deferred update: Updating parent feature windows")
                    self.parent().update_feature_windows()
                    print("DEBUG BATCH_INFERENCE: Deferred update: Parent feature windows updated")
                
                # Now that the parent is updated, we can show the success message.
                self.finalize_batch_processing()

            except Exception as e:
                print(f"DEBUG BATCH_INFERENCE: Warning: Could not update parent window during deferred update: {e}")
                QMessageBox.critical(self, "Error", f"An error occurred while updating the main window: {e}")

    def finalize_batch_processing(self):
        """Finalize batch processing on the main thread."""
        try:
            # Show success message AFTER all VTK operations are complete to prevent segfault
            # Use QTimer to ensure this happens after VTK operations
            QTimer.singleShot(200, self._show_success_message)

        except Exception as e:
            print(f"DEBUG VTK: Error in finalize_batch_processing: {e}")
            import traceback
            print(f"DEBUG VTK: Traceback: {traceback.format_exc()}")
            QMessageBox.critical(self, "Error", f"An error occurred during finalization: {e}")
    
    def _show_success_message(self):
        """Show success message safely after all VTK operations are complete."""
        try:
            print("DEBUG VTK: Showing success message")
            QMessageBox.information(self, "Success", "Batch inference completed.")
            print("DEBUG VTK: Success message shown")
        except Exception as e:
            print(f"DEBUG VTK: Warning: Could not show success message: {e}")

    def on_batch_processing_error(self, error_message):
        """
        Handle errors during batch processing.
        """
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Error", f"An error occurred during batch inference:\n{error_message}")
        self.pushButtonBatchInference.setEnabled(True)

    def closeEvent(self, event):
        """Handle window close event - clean up VTK/OpenGL resources"""
        try:
            print("DEBUG VTK: EmbeddedFeaturesWindow closeEvent")
        except Exception as e:
            print(f"DEBUG VTK: Error during EmbeddedFeaturesWindow close: {e}")
            import traceback
            print(f"DEBUG VTK: Close error traceback: {traceback.format_exc()}")
            # Still accept the event to avoid hanging, but only for this widget
            event.accept()

if __name__ == '__main__':
    # This is for testing the dialog independently
    app = QtWidgets.QApplication(sys.argv)
    
    # Create a dummy DataFrame for testing
    data = {
        'Path': ['/path/to/image1.tif', '/path/to/image2.tif'],
        'ImageName': ['image1', 'image2'],
        'Embedding_1': [0.12345, 0.67890],
        'Embedding_2': [0.54321, 0.09876],
    }
    dummy_df = pd.DataFrame(data)

    # This test requires a 'embedded_features.ui' file with a QTableWidget named 'tableWidget'.
    # If you get an error, make sure the UI file is present and correctly configured.
    try:
        dialog = EmbeddedFeaturesWindow(result_db_ref=dummy_df)
        dialog.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred. This might be because 'embedded_features.ui' is missing or doesn't contain a 'tableWidget'. Error: {e}")