from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QVBoxLayout, QProgressDialog, QMessageBox
from PyQt5.QtCore import Qt
from ..logic.threaded_processes import BatchProcessingThread
from .threshold_dialog import ThresholdDialog
from .progress_dialog import BatchProgressDialog
from .csv_export_utils import export_dataframe_to_csv
import os
import pandas as pd
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters

class GeometricFeaturesWindow(QDialog):
    def __init__(self, parent=None, result_db_ref=None):
        super().__init__(parent)
        # Load the UI file
        ui_path = os.path.join(os.path.dirname(__file__), 'geometric_features.ui')
        uic.loadUi(ui_path, self)

        # Store a reference or copy of the result_db
        self.result_db = result_db_ref if result_db_ref is not None else pd.DataFrame()
        
        # Remove the question mark from the title bar (if desired for dialogs)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Setup Matplotlib FigureCanvas
        # Calculate plot size based on screen height
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            screen_size = screen.size()
            screen_width = screen_size.width()
            screen_height = screen_size.height()
            
            # Set default window size to 4/5 of the screen size
            self.resize(int(screen_width * 4 / 5), int(screen_height * 4 / 5))

        # Setup pyqtgraph PlotWidget for 1D histogram
        self.plotWidget1D = pg.PlotWidget()
        self.plotWidget1D.getViewBox().setAspectLocked(lock=True, ratio=1)
        
        # Assuming framePlotHist is a QFrame in your .ui file
        layout = QVBoxLayout(self.framePlotHist)
        layout.addWidget(self.plotWidget1D)
        self.framePlotHist.setLayout(layout)

        # Setup pyqtgraph PlotWidget for 2D plot
        self.plotWidget2D = pg.PlotWidget()
        self.plotWidget2D.getViewBox().setAspectLocked(lock=True, ratio=1)
        layout2D = QVBoxLayout(self.framePlotHist2D)
        layout2D.addWidget(self.plotWidget2D)
        self.framePlotHist2D.setLayout(layout2D)

        # Initial rendering of the table and populating combobox
        self.render_table_widget()

        # Connect combobox
        self.comboBoxPlotMeasurements.currentIndexChanged.connect(self.update_plot_1d)

        # Connect buttons from geometric_features.ui if their logic is to be handled here
        # For example:
        self.pushButtonBatchMeasure.clicked.connect(self.batch_measure)
        self.pushButtonExportCSV.clicked.connect(self.export_csv)
        self.comboBoxPlotMeasurements2D_x.currentIndexChanged.connect(self.update_plot_2d)
        self.comboBoxPlotMeasurements2D_y.currentIndexChanged.connect(self.update_plot_2d)

        self.pushButtonSavePlotHist.clicked.connect(self.save_plot_hist)
        self.pushButtonSavePlotHist2D.clicked.connect(self.save_plot_hist_2d)

        # Set initial plot size
        self.adjust_plot_sizes()

    def resizeEvent(self, event):
        """
        Handle the window resize event to adjust plot sizes dynamically.
        """
        super().resizeEvent(event)
        self.adjust_plot_sizes()

    def adjust_plot_sizes(self):
        """
        Calculates and sets the size for the plot frames based on the window's current height.
        """
        # Make plot_size adaptive to the main window's height
        plot_size = int(self.height() / 3)

        # Update the size of the plot frames
        self.framePlotHist.setFixedSize(plot_size, plot_size)
        self.framePlotHist2D.setFixedSize(plot_size, plot_size)

    def update_data_and_render(self, new_result_db):
        """
        Updates the internal reference to the result_db and re-renders the table.
        """
        self.result_db = new_result_db
        self.render_table_widget()

    def render_table_widget(self):
        """
        Populates the tableWidget with data from self.result_db.
        Also populates the comboBoxPlotMeasurements with numeric columns.
        """
        if self.result_db is None or self.result_db.empty:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            self.comboBoxPlotMeasurements.clear()
            self.comboBoxPlotMeasurements2D_x.clear()
            self.comboBoxPlotMeasurements2D_y.clear()
            self.plotWidget1D.clear()
            self.plotWidget2D.clear()
            return

        # Columns to exclude from the table
        exclude_columns = [
            'ManualAnnotation', 'Model', 'ClassProb_M', 'ClassProb_MM',
            'ClassProb_BN', 'ClassProb_SN', 'MaturationScore'
        ]
        
        # Filter the DataFrame for display by excluding specified columns
        display_columns = [col for col in self.result_db.columns if col not in exclude_columns]
        
        if not display_columns:
            filtered_db_for_display = pd.DataFrame()
        else:
            filtered_db_for_display = self.result_db[display_columns]

        self.tableWidget.setRowCount(filtered_db_for_display.shape[0])
        self.tableWidget.setColumnCount(filtered_db_for_display.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(filtered_db_for_display.columns)

        for i in range(filtered_db_for_display.shape[0]):
            for j in range(filtered_db_for_display.shape[1]):
                item_value = filtered_db_for_display.iloc[i, j]
                column_name = filtered_db_for_display.columns[j]

                # Ensure item_value is a string for QTableWidgetItem
                if pd.isna(item_value):
                    display_value = ""
                elif column_name == 'Genus':
                    # Handle Genus specifically: display as int or empty string
                    display_value = str(int(item_value)) if not pd.isna(item_value) else ""
                elif isinstance(item_value, float):
                    # Format other floats to a reasonable number of decimal places
                    display_value = "{:.4f}".format(item_value)
                else:
                    display_value = str(item_value)
                
                item = QTableWidgetItem(display_value)
                self.tableWidget.setItem(i, j, item)
        
        self.tableWidget.resizeColumnsToContents()

        # Populate comboBoxPlotMeasurements with numeric columns from the original result_db
        numeric_dtypes = [
            np.int8, np.int16, np.int32, np.int64,
            np.uint8, np.uint16, np.uint32, np.uint64,
            np.float16, np.float32, np.float64,
            np.complex64, np.complex128
        ]

        # Select only columns where all values are numeric or np.nan
        def is_numeric_or_nan(col):
            try:
                # Try to convert to numeric, coercing errors to NaN
                numeric_col = pd.to_numeric(col, errors='coerce')
                # Check if the conversion was successful (not all NaN from conversion)
                return not numeric_col.isna().all()
            except:
                return False

        # manual exclusion
        exclude_columns = [
            'ManualAnnotation',
            'Model',
            'ClassProb_M',
            'ClassProb_MM',
            'ClassProb_BN',
            'ClassProb_SN',
            'MaturationScore',
        ]

        numeric_cols = self.result_db.columns[self.result_db.apply(is_numeric_or_nan)]
        numeric_cols = [x for x in numeric_cols if not (x in exclude_columns)]

        self.comboBoxPlotMeasurements.clear()
        self.comboBoxPlotMeasurements2D_x.clear()
        self.comboBoxPlotMeasurements2D_y.clear()
        if len(numeric_cols)>0:
            self.comboBoxPlotMeasurements.addItems(numeric_cols)
            self.comboBoxPlotMeasurements2D_x.addItems(numeric_cols)
            self.comboBoxPlotMeasurements2D_y.addItems(numeric_cols)
            self.update_plot_1d() # Initial plot for the first item
            self.update_plot_2d() # Initial plot for 2D
        else:
            self.plotWidget1D.clear()
            self.plotWidget2D.clear()

    # Placeholder methods for functionality within this dialog
    # def batch_measure(self):
    #     # This would likely need to interact back with the MainWindow 
    #     # or have its own logic if it operates solely on the displayed data.
    #     print("Batch Measure clicked in GeometricFeaturesWindow")
    #     # Example: self.parent().perform_batch_measurement_on_all_files()

    def export_csv(self):
        """
        Export the current result_db DataFrame to a CSV file.
        """
        export_dataframe_to_csv(
            parent_widget=self,
            dataframe=self.result_db,
            default_filename="neutrophils_geom.csv",
            dialog_title="Save CSV File"
        )

    # def update_plot_1d(self):
    #     # Logic to update the 1D plot (framePlotHist) based on comboBoxPlotMeasurements
    #     print("Update 1D plot in GeometricFeaturesWindow")
    
    def update_plot_1d(self):
        """
        Updates the 1D histogram plot based on the selected item in comboBoxPlotMeasurements.
        """
        if not self.result_db.empty and self.comboBoxPlotMeasurements.count() > 0:
            selected_column = self.comboBoxPlotMeasurements.currentText()
            if selected_column and selected_column in self.result_db.columns:
                # Convert to numeric and drop NaN values
                data_series = pd.to_numeric(self.result_db[selected_column], errors='coerce')
                data_to_plot = data_series.dropna()
                
                self.plotWidget1D.clear()
                
                # Check if we have any valid numeric data
                if len(data_to_plot) == 0:
                    self.plotWidget1D.setTitle(f'No numeric data available for {selected_column}')
                    return
                
                try:
                    # Create histogram using numpy
                    hist, bin_edges = np.histogram(data_to_plot.values, bins='auto')
                    
                    # Create bar graph using pyqtgraph
                    x = bin_edges[:-1]  # Use left edges of bins
                    width = bin_edges[1] - bin_edges[0]  # Bin width
                    
                    # Create BarGraphItem
                    bargraph = pg.BarGraphItem(x=x, height=hist, width=width,
                                             brush=pg.mkBrush(135, 206, 235, 150),  # skyblue with transparency
                                             pen=pg.mkPen('black'))
                    self.plotWidget1D.addItem(bargraph)
                    
                    # Set labels and title
                    self.plotWidget1D.setLabel('bottom', selected_column)
                    self.plotWidget1D.setLabel('left', 'Frequency')
                    self.plotWidget1D.setTitle(f'Histogram of {selected_column}')
                    self.plotWidget1D.getViewBox().setAspectLocked(lock=True, ratio=1)
                except Exception as e:
                    self.plotWidget1D.setTitle(f'Error plotting {selected_column}: {str(e)}')
            else: # No valid column selected or column not found (should not happen if populated correctly)
                self.plotWidget1D.clear()
        else: # No data or no items in combobox
            self.plotWidget1D.clear()


    def update_plot_2d(self):
        """
        Updates the 2D scatter plot based on the selected items in
        comboBoxPlotMeasurements2D_x and comboBoxPlotMeasurements2D_y.
        """
        if not self.result_db.empty and self.comboBoxPlotMeasurements2D_x.count() > 0 and self.comboBoxPlotMeasurements2D_y.count() > 0:
            col_x = self.comboBoxPlotMeasurements2D_x.currentText()
            col_y = self.comboBoxPlotMeasurements2D_y.currentText()

            if col_x and col_y and col_x in self.result_db.columns and col_y in self.result_db.columns:
                # Convert to numeric and handle NaN values
                x_series = pd.to_numeric(self.result_db[col_x], errors='coerce')
                y_series = pd.to_numeric(self.result_db[col_y], errors='coerce')
                
                # Create a combined dataframe to align data and drop rows with NaN in either column
                combined_data = pd.DataFrame({'x': x_series, 'y': y_series}).dropna()
                
                self.plotWidget2D.clear()
                
                # Check if we have any valid numeric data
                if len(combined_data) == 0:
                    self.plotWidget2D.setTitle(f'No valid numeric data for {col_y} vs. {col_x}')
                    return
                
                try:
                    x_data = combined_data['x'].values
                    y_data = combined_data['y'].values
                    
                    scatter = pg.ScatterPlotItem(x=x_data, y=y_data, pen=None, brush=pg.mkBrush(30, 255, 255, 150), size=8)
                    self.plotWidget2D.addItem(scatter)
                    self.plotWidget2D.getViewBox().setAspectLocked(lock=True, ratio=1)
                    self.plotWidget2D.setLabel('bottom', col_x)
                    self.plotWidget2D.setLabel('left', col_y)
                    self.plotWidget2D.setTitle(f'{col_y} vs. {col_x}')
                except Exception as e:
                    self.plotWidget2D.setTitle(f'Error plotting {col_y} vs. {col_x}: {str(e)}')
            else:
                self.plotWidget2D.clear()
        else:
            self.plotWidget2D.clear()

    def save_plot_hist(self):
        """
        Saves the 1D histogram plot.
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Plot",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )
        if path:
            # Ensure the file has an extension, default to .png
            if not os.path.splitext(path)[1]:
                path += '.png'

            # Check if file exists and ask for confirmation to overwrite
            if os.path.exists(path):
                reply = QtWidgets.QMessageBox.question(self, 'File Exists',
                                                     f"The file '{os.path.basename(path)}' already exists. Do you want to overwrite it?",
                                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.No:
                    QtWidgets.QMessageBox.information(self, "Save Cancelled", "Save operation has been cancelled.")
                    return
            
            try:
                exporter = pg.exporters.ImageExporter(self.plotWidget1D.plotItem)
                exporter.export(path)
                QtWidgets.QMessageBox.information(self, "Save Successful", f"Plot saved to {path}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Save Failed", f"Could not save plot: {e}")

    def save_plot_hist_2d(self):
        """
        Saves the 2D scatter plot.
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Plot",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )
        if path:
            # Ensure the file has an extension, default to .png
            if not os.path.splitext(path)[1]:
                path += '.png'

            # Check if file exists and ask for confirmation to overwrite
            if os.path.exists(path):
                reply = QtWidgets.QMessageBox.question(self, 'File Exists',
                                                     f"The file '{os.path.basename(path)}' already exists. Do you want to overwrite it?",
                                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.No:
                    QtWidgets.QMessageBox.information(self, "Save Cancelled", "Save operation has been cancelled.")
                    return

            try:
                exporter = pg.exporters.ImageExporter(self.plotWidget2D.plotItem)
                exporter.export(path)
                QtWidgets.QMessageBox.information(self, "Save Successful", f"Plot saved to {path}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Save Failed", f"Could not save plot: {e}")

    def batch_measure(self):
        """
        Run batch measurement process.
        """
        if self.result_db.empty:
            QMessageBox.warning(self, "Warning", "No data to process. Please load images first.")
            return

        dialog = ThresholdDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            percentile1, percentile2 = dialog.get_values()

            # Use our custom BatchProgressDialog with task ratio display
            total_images = len(self.result_db)
            self.progress_dialog = BatchProgressDialog(self, "Batch Processing", total_images)
            self.progress_dialog.show()

            self.batch_thread = BatchProcessingThread(self.result_db.copy(), percentile1, percentile2)
            self.batch_thread.progress_update.connect(self.on_batch_progress_update)
            self.batch_thread.processing_complete.connect(self.on_batch_processing_complete)
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

    def on_batch_processing_complete(self, updated_db):
        """
        Handle completion of batch processing.
        """
        import time
        from PyQt5.QtCore import QThread
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        thread_id = int(str(QThread.currentThreadId()))
        print(f"[{timestamp}] [GeometricFeaturesWindow::on_batch_processing_complete::{thread_id}] Received batch processing completion signal.")

        self.result_db = updated_db
        self.progress_dialog.setValue(100)
        
        # Calculate summary statistics for the completion dialog
        summary_message = self._generate_batch_summary(updated_db)
        QMessageBox.information(self, "Success", summary_message)
        
        self.update_data_and_render(self.result_db)
        # also update the main window's db
        if self.parent():
            self.parent().result_db = self.result_db
            self.parent().update_feature_windows()
        
        print(f"[{timestamp}] [GeometricFeaturesWindow::on_batch_processing_complete::{thread_id}] Finished handling completion.")

    def _generate_batch_summary(self, db):
        """
        Generate a summary message with statistics from batch processing.
        """
        if db is None or db.empty:
            return "Batch processing completed with no data."
        
        total_images = len(db)
        summary_lines = [f"Batch processing completed successfully!"]
        summary_lines.append(f"Processed {total_images} images.")
        
        return "\n".join(summary_lines)

    def on_batch_processing_error(self, error_message):
        """
        Handle errors during batch processing.
        """
        self.progress_dialog.close()
        QMessageBox.critical(self, "Error", f"An error occurred during batch processing:\n{error_message}")


if __name__ == '__main__':
    # This is for testing the dialog independently
    app = QtWidgets.QApplication([])
    
    # Create a dummy DataFrame for testing
    data = {
        'Path': ['/path/to/image1.tif', '/path/to/image2.tif'],
        'ImageName': ['image1', 'image2'],
        'Area_1': [100.5, 150.23],
        'Vol_1': [500.12, 750.9],
        'NSI_1': [0.8, 0.85]
    }
    dummy_df = pd.DataFrame(data)

    dialog = GeometricFeaturesWindow(result_db_ref=dummy_df)
    dialog.show()
    app.exec_()
