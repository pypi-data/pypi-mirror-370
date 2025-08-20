"""
Common utilities for CSV export functionality across different UI windows.
"""

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import pandas as pd


def export_dataframe_to_csv(parent_widget, dataframe, default_filename="data.csv", dialog_title="Save CSV File"):
    """
    Common function to export a pandas DataFrame to CSV with file dialog and error handling.
    
    Args:
        parent_widget: The parent widget for the file dialog and message boxes
        dataframe (pd.DataFrame): The DataFrame to export
        default_filename (str): Default filename for the save dialog
        dialog_title (str): Title for the file save dialog
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    if dataframe is None or dataframe.empty:
        QMessageBox.warning(parent_widget, "No Data", "There is no data to export.")
        return False
    
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    path, _ = QtWidgets.QFileDialog.getSaveFileName(
        parent_widget,
        dialog_title,
        default_filename,
        "CSV Files (*.csv)",
        options=options
    )
    
    if path:
        try:
            dataframe.to_csv(path, index=False)
            QMessageBox.information(parent_widget, "Export Successful", f"Data successfully exported to {path}")
            return True
        except Exception as e:
            QMessageBox.critical(parent_widget, "Export Failed", f"An error occurred while exporting the file: {e}")
            return False
    
    return False