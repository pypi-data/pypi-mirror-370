import os
import logging
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTimer

# Setup logging for debugging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

def load_single_image_files_dialog(parent_widget):
    """
    Opens a dialog for the user to select one or more TIFF image files.
    Returns a list of paths to the selected files.
    """
    files, _ = QFileDialog.getOpenFileNames(parent_widget, 
                                            caption="Select Image Files", 
                                            filter="TIFF (*.tif *.tiff)")
    return files if files else []

def load_image_directory_dialog(parent_widget):
    """
    Opens a dialog for the user to select a directory.
    Lists all TIFF files within that directory.
    Returns a list of full paths to these TIFF files.
    """
    directory = QFileDialog.getExistingDirectory(parent_widget, "Select Image Directory")
    selected_files = []
    if directory:
        for f_name in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, f_name)) and \
               (f_name.lower().endswith(".tif") or f_name.lower().endswith(".tiff")):
                selected_files.append(os.path.join(directory, f_name))
    return selected_files

def populate_file_list(parent_widget, clear_first=False, trigger_update=True):
    """
    Populate the list widget with loaded files.
    By default, appends files to maintain already loaded images.
    
    Args:
        parent_widget: The parent widget containing the file list
        clear_first: If True, clear the list before populating (default: False)
    """
    if not (hasattr(parent_widget, 'listWidget') and hasattr(parent_widget, 'files')):
        logger.warning("populate_file_list: Missing listWidget or files attribute")
        return
    
    logger.debug(f"=== STARTING populate_file_list (clear_first={clear_first}) ===")
    
    # Store current selection if we're not clearing
    current_selection = None
    if not clear_first and parent_widget.listWidget.currentItem():
        current_selection = parent_widget.listWidget.currentItem().text()
        logger.debug(f"Current selection: {current_selection}")
    
    # Clear list if requested (for complete replacement)
    if clear_first:
        logger.debug("Clearing listWidget")
        parent_widget.listWidget.clear()
    
    # Get existing items to avoid duplicates when appending
    existing_items = set()
    if not clear_first:
        for i in range(parent_widget.listWidget.count()):
            item = parent_widget.listWidget.item(i)
            if item:
                existing_items.add(item.text())
    
    # Add new files
    files_added = 0
    for file_path in parent_widget.files:
        file_name = os.path.basename(file_path)
        if file_name not in existing_items:
            parent_widget.listWidget.addItem(file_name)
            files_added += 1
            if files_added <= 3:  # Log first few items for debugging
                logger.debug(f"Added item: {file_name}")
    
    logger.debug(f"Added {files_added} new items, listWidget now has {parent_widget.listWidget.count()} total items")
    
    # Set selection and trigger main window update
    if parent_widget.listWidget.count() > 0:
        selection_row = 0
        
        # Try to restore previous selection if it still exists
        if current_selection and not clear_first:
            for i in range(parent_widget.listWidget.count()):
                if parent_widget.listWidget.item(i).text() == current_selection:
                    selection_row = i
                    logger.debug(f"Restored previous selection: {current_selection} at row {i}")
                    break
        
        # Set the current row
        parent_widget.listWidget.setCurrentRow(selection_row)
        logger.debug(f"Set current row to: {selection_row}")
        
        # If we're clearing and repopulating (clear_first=True), or if this is the first file,
        # we need to explicitly trigger the main window update since setCurrentRow might not
        # trigger the signal if the row was already at that position
        if trigger_update and (clear_first or (files_added > 0 and parent_widget.listWidget.count() == files_added)):
            logger.debug("Triggering main window update after populate_file_list")
            # Use QTimer to ensure the list widget update is complete before triggering
            QTimer.singleShot(10, lambda: _trigger_main_window_update(parent_widget))
        
        logger.debug("File list populated - main window update will be triggered")
    
    logger.debug("=== COMPLETED populate_file_list ===")

def _update_progress_label(parent_widget, message, delay_ms=1500):
    """Helper function to update progress label with auto-reset to 'Ready'"""
    if hasattr(parent_widget, 'progress_label') and parent_widget.progress_label:
        parent_widget.progress_label.setText(message)
        parent_widget.progress_label.setVisible(True)
        # Show "Ready" after delay
        QTimer.singleShot(delay_ms, 
                         lambda: parent_widget.progress_label.setText("Ready") 
                         if hasattr(parent_widget, 'progress_label') and parent_widget.progress_label 
                         else None)

def _populate_result_db(parent_widget, new_files):
    """
    Populate the result_db DataFrame with new file entries.
    """
    if not hasattr(parent_widget, 'result_db') or not new_files:
        return

    logger.debug(f"Populating result_db with {len(new_files)} new files.")
    
    try:
        # Create a list of new records to be added
        records_to_add = []
        
        # Need pandas for this
        try:
            import pandas as pd
        except ImportError:
            logger.error("Pandas module not found, cannot populate result_db.")
            return

        for file_path in new_files:
            # Check if record already exists to avoid duplicates
            if parent_widget.result_db.empty or not (parent_widget.result_db['Path'] == file_path).any():
                filename = os.path.basename(file_path)
                new_record = {
                    'ImageName': filename,
                    'Path': file_path,
                    'ManualAnnotation': '', 'Model': '',
                    'ClassProb_M': np.nan, 'ClassProb_MM': np.nan, 'ClassProb_BN': np.nan, 'ClassProb_SN': np.nan, 'MaturationScore': np.nan,
                    'Area_1': np.nan, 'Vol_1': np.nan, 'NSI_1': np.nan, 'Sphericity_1': np.nan, 'SA_Vol_Ratio_1': np.nan, 'Solidity_1': np.nan, 'Elongation_1': np.nan, 'Genus_1': np.nan,
                    'Area_2': np.nan, 'Vol_2': np.nan, 'NSI_2': np.nan, 'Sphericity_2': np.nan, 'SA_Vol_Ratio_2': np.nan, 'Solidity_2': np.nan, 'Elongation_2': np.nan, 'Genus_2': np.nan,
                    'threshold1': np.nan, 'threshold2': np.nan,
                }
                records_to_add.append(new_record)

        # Add all new records at once for efficiency
        if records_to_add:
            parent_widget.result_db = pd.concat([parent_widget.result_db, pd.DataFrame(records_to_add)], ignore_index=True)
            logger.debug(f"Added {len(records_to_add)} new entries to result_db. Total size: {len(parent_widget.result_db)}")

    except Exception as e:
        logger.error(f"Failed to populate result_db: {e}", exc_info=True)

def _update_features_windows(parent_widget):
    """
    Update all feature windows by calling the parent's update method.
    This is a centralized way to refresh UI components that depend on result_db.
    """
    if hasattr(parent_widget, 'update_feature_windows'):
        logger.debug("Calling parent's update_feature_windows method.")
        try:
            parent_widget.update_feature_windows()
        except Exception as e:
            logger.error(f"Failed to call update_feature_windows on parent: {e}", exc_info=True)

def _trigger_main_window_update(parent_widget):
    """
    Trigger main window update to load and display the current image.
    This ensures the main window is updated after files are loaded.
    """
    try:
        if not (hasattr(parent_widget, 'listWidget') and hasattr(parent_widget, 'files')):
            logger.warning("Cannot trigger main window update: missing listWidget or files")
            return
        
        if not parent_widget.files or parent_widget.listWidget.count() == 0:
            logger.debug("No files to trigger update for")
            return
        
        current_row = parent_widget.listWidget.currentRow()
        logger.debug(f"Current listWidget row before update: {current_row}")
        
        # If no row is selected or invalid selection, select the first item
        if current_row < 0 or current_row >= len(parent_widget.files):
            parent_widget.listWidget.setCurrentRow(0)
            current_row = 0
            logger.debug("Set current row to 0")
        
        # Explicitly trigger the on_list_changed method to load the image
        if hasattr(parent_widget, 'on_list_changed'):
            logger.debug("Explicitly calling on_list_changed to update main window")
            parent_widget.on_list_changed()
        else:
            logger.warning("Main window does not have on_list_changed method")
        
        logger.debug(f"Main window update triggered for row {current_row}")
        
    except Exception as e:
        logger.error(f"Error triggering main window update: {e}")

def _load_files_common(parent_widget, files, source_description=""):
    """
    Common logic for loading files regardless of source (files or directory).
    This function now only populates the file list and database without loading
    the actual image data. Data loading is triggered by user selection.
    Returns the number of new files added.
    """
    if not files:
        logger.debug(f"No {source_description} selected")
        return 0

    logger.debug(f"Queueing {len(files)} {source_description} for loading")

    current_files = getattr(parent_widget, 'files', [])
    existing_files_set = set(current_files)
    new_files = [f for f in files if f not in existing_files_set]

    if not new_files:
        logger.debug("No new files to load.")
        _update_progress_label(parent_widget, "No new images to add.")
        return 0

    # Update the main file list
    parent_widget.files.extend(new_files)
    logger.debug(f"Current: {len(current_files)}, New: {len(new_files)}, Total: {len(parent_widget.files)}")

    try:
        # Populate the UI list widget
        # Pass trigger_update=False to prevent immediate loading
        populate_file_list(parent_widget, clear_first=False, trigger_update=False)

        # Populate the database with new file entries
        _populate_result_db(parent_widget, new_files)

        # Update feature windows which rely on the database
        _update_features_windows(parent_widget)

        action = "Appended" if current_files else "Loaded"
        suffix = f" from {source_description}" if source_description else ""
        _update_progress_label(parent_widget, f"{action} {len(new_files)} new image(s){suffix}.")
        logger.debug(f"Successfully queued {len(new_files)} files. Total files: {len(parent_widget.files)}")

        return len(new_files)

    except Exception as e:
        logger.error(f"Exception in _load_files_common: {str(e)}", exc_info=True)
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(parent_widget, "Error", f"Failed to load {source_description}: {str(e)}")
        return 0

def load_image_files(parent_widget):
    """
    Load image files and update the parent widget's file list.
    If a single new image is loaded, processing is triggered automatically.
    """
    logger.debug("=== STARTING load_image_files ===")
    
    files = load_single_image_files_dialog(parent_widget)
    num_new_files = _load_files_common(parent_widget, files, "files")
    
    if num_new_files == 1:
        # A single new file was added, trigger processing for it.
        # The new file is the last one in the list.
        if parent_widget.listWidget.count() > 0:
            new_row = parent_widget.listWidget.count() - 1
            parent_widget.listWidget.setCurrentRow(new_row)
            logger.debug(f"Single new file loaded, triggering processing for row {new_row}.")
            # Use QTimer to ensure UI updates are processed before triggering the next step.
            QTimer.singleShot(50, lambda: _trigger_main_window_update(parent_widget))
    
    logger.debug(f"=== COMPLETED load_image_files: {num_new_files > 0} ===")
    return num_new_files > 0

def load_image_directory(parent_widget):
    """
    Load all images from a directory and update the parent widget's file list.
    Always appends to existing files to maintain already loaded images.
    Uses enhanced data loader with batch operations and caching when available.
    """
    logger.debug("=== STARTING load_image_directory ===")
    
    files = load_image_directory_dialog(parent_widget)
    num_new_files = _load_files_common(parent_widget, files, "directory")
    
    logger.debug(f"=== COMPLETED load_image_directory: {num_new_files > 0} ===")
    return num_new_files > 0

def clear_image_list(parent_widget):
    """
    Clear all loaded images from the list.
    This function provides explicit clearing functionality.
    """
    logger.debug("=== STARTING clear_image_list ===")
    
    if hasattr(parent_widget, 'files'):
        parent_widget.files = []
    
    if hasattr(parent_widget, 'listWidget'):
        parent_widget.listWidget.clear()
    
    # Clear enhanced data loader cache if available
    if hasattr(parent_widget, 'enhanced_data_loader') and parent_widget.enhanced_data_loader:
        if hasattr(parent_widget.enhanced_data_loader, 'image_loader') and parent_widget.enhanced_data_loader.image_loader:
            if hasattr(parent_widget.enhanced_data_loader.image_loader, 'clear_cache'):
                parent_widget.enhanced_data_loader.image_loader.clear_cache()
    
    _update_progress_label(parent_widget, "Cleared all images")
    logger.debug("=== COMPLETED clear_image_list ===")

def remove_selected_image(parent_widget):
    """
    Remove the currently selected image from the list.
    This function provides individual file removal functionality.
    """
    logger.debug("=== STARTING remove_selected_image ===")
    
    if not (hasattr(parent_widget, 'listWidget') and hasattr(parent_widget, 'files')):
        logger.warning("Missing listWidget or files attribute")
        return False
    
    current_row = parent_widget.listWidget.currentRow()
    if current_row < 0 or current_row >= len(parent_widget.files):
        logger.debug("No valid selection to remove")
        return False
    
    # Remove from files list
    removed_file = parent_widget.files.pop(current_row)
    logger.debug(f"Removed file: {os.path.basename(removed_file)}")
    
    # Remove from list widget
    parent_widget.listWidget.takeItem(current_row)
    
    # Update selection and trigger main window update
    if parent_widget.listWidget.count() > 0:
        # Select the same row, or the last item if we removed the last one
        new_row = min(current_row, parent_widget.listWidget.count() - 1)
        parent_widget.listWidget.setCurrentRow(new_row)
        
        # Explicitly trigger main window update to load the new current image
        logger.debug("Triggering main window update after image removal")
        QTimer.singleShot(10, lambda: _trigger_main_window_update(parent_widget))
        
        logger.debug("Image removed - main window update triggered")
    
    _update_progress_label(parent_widget, f"Removed {os.path.basename(removed_file)}")
    logger.debug("=== COMPLETED remove_selected_image ===")
    return True

def debug_file_loading_state(parent_widget):
    """
    Debug function to print comprehensive state information about file loading.
    """
    logger.debug("=== DEBUG FILE LOADING STATE ===")
    logger.debug(f"parent_widget type: {type(parent_widget)}")
    logger.debug(f"parent_widget.__dict__.keys(): {list(parent_widget.__dict__.keys()) if hasattr(parent_widget, '__dict__') else 'No __dict__'}")
    
    # Check files attribute
    if hasattr(parent_widget, 'files'):
        files = parent_widget.files
        logger.debug(f"files attribute exists: {len(files)} files")
        for i, f in enumerate(files[:5]):  # Show first 5 files
            logger.debug(f"  File {i}: {f}")
        if len(files) > 5:
            logger.debug(f"  ... and {len(files) - 5} more files")
    else:
        logger.debug("NO files attribute found")
    
    # Check listWidget
    if hasattr(parent_widget, 'listWidget'):
        listWidget = parent_widget.listWidget
        logger.debug(f"listWidget exists: {listWidget.count()} items")
        for i in range(min(5, listWidget.count())):  # Show first 5 items
            item = listWidget.item(i)
            logger.debug(f"  Item {i}: {item.text() if item else 'None'}")
        if listWidget.count() > 5:
            logger.debug(f"  ... and {listWidget.count() - 5} more items")
        logger.debug(f"listWidget current row: {listWidget.currentRow()}")
    else:
        logger.debug("NO listWidget found")
    
    # Check enhanced data loader
    if hasattr(parent_widget, 'enhanced_data_loader'):
        edl = parent_widget.enhanced_data_loader
        logger.debug(f"enhanced_data_loader exists: {edl}")
        if edl and hasattr(edl, 'get_processing_stats'):
            try:
                stats = edl.get_processing_stats()
                logger.debug(f"Enhanced data loader stats: {stats}")
            except Exception as e:
                logger.debug(f"Failed to get enhanced data loader stats: {e}")
    else:
        logger.debug("NO enhanced_data_loader found")
    
    # Check image rendering method
    if hasattr(parent_widget, 'on_list_changed'):
        logger.debug("on_list_changed method exists")
    else:
        logger.debug("NO on_list_changed method found")
    
    # Check progress label
    if hasattr(parent_widget, 'progress_label'):
        pl = parent_widget.progress_label
        logger.debug(f"progress_label exists: visible={pl.isVisible() if pl else 'None'}, text='{pl.text() if pl else 'None'}'")
    else:
        logger.debug("NO progress_label found")
    
    logger.debug("=== END DEBUG FILE LOADING STATE ===")

# Backward compatibility aliases (deprecated - use main functions instead)
def append_image_files(parent_widget):
    """
    DEPRECATED: Use load_image_files() instead.
    All loading now appends by default to maintain already loaded images.
    """
    logger.warning("append_image_files is deprecated. Use load_image_files() instead.")
    return load_image_files(parent_widget)

def append_image_directory(parent_widget):
    """
    DEPRECATED: Use load_image_directory() instead.
    All loading now appends by default to maintain already loaded images.
    """
    logger.warning("append_image_directory is deprecated. Use load_image_directory() instead.")
    return load_image_directory(parent_widget)

def populate_file_list_enhanced(parent_widget):
    """
    DEPRECATED: Use populate_file_list() instead.
    The main function now includes all enhanced features.
    """
    logger.warning("populate_file_list_enhanced is deprecated. Use populate_file_list() instead.")
    return populate_file_list(parent_widget, clear_first=True)


def trigger_image_processing(parent_widget, file_path):
    """
    Starts the image processing for a given file path.
    This function is designed to be called from the UI, e.g., when a
    list item is selected.
    """
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"Invalid file path provided for processing: {file_path}")
        return

    logger.debug(f"Triggering image processing for: {file_path}")

    # Use the streamlined image processing workflow if available, otherwise fall back to legacy  
    if hasattr(parent_widget, 'start_streamlined_image_processing'):
        try:
            parent_widget.start_streamlined_image_processing(file_path)
        except Exception as e:
            logger.error(f"Failed to start streamlined image processing for {file_path}: {e}", exc_info=True)
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(parent_widget, "Error", f"Could not start image processing: {e}")
    elif hasattr(parent_widget, 'start_image_processing'):
        try:
            parent_widget.start_image_processing(file_path)
        except Exception as e:
            logger.error(f"Failed to start image processing for {file_path}: {e}", exc_info=True)
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(parent_widget, "Error", f"Could not start image processing: {e}")
    else:
        logger.error("Parent widget does not have image processing methods.")

def import_csv_results(parent_widget):
    """
    Import results from a CSV file, update the database, and refresh UI.
    """
    if not hasattr(parent_widget, 'result_db'):
        logger.error("import_csv_results: parent_widget has no result_db attribute.")
        return

    try:
        import pandas as pd
        from PyQt5.QtWidgets import QMessageBox
    except ImportError:
        logger.error("Pandas or PyQt5 not found, cannot import CSV.")
        return

    file_path, _ = QFileDialog.getOpenFileName(parent_widget,
                                                 "Import Results from CSV",
                                                 "",
                                                 "CSV Files (*.csv)")

    if not file_path:
        return

    try:
        new_data = pd.read_csv(file_path)
        logger.debug(f"Successfully loaded CSV from {file_path}")

        # --- Basic Validation ---
        required_columns = {'ImageName', 'Path'}
        if not required_columns.issubset(new_data.columns):
            missing = required_columns - set(new_data.columns)
            QMessageBox.critical(parent_widget, "Import Error",
                                 f"The selected CSV is missing required columns: {', '.join(missing)}")
            return

        # --- Merge with existing data ---
        # Use 'Path' as the unique key for merging
        existing_paths = set(parent_widget.result_db['Path'])
        new_entries = new_data[~new_data['Path'].isin(existing_paths)]
        
        if not new_entries.empty:
            # Add new files to the main file list
            new_file_paths = new_entries['Path'].tolist()
            parent_widget.files.extend(new_file_paths)
            
            # Ensure all columns from the main db are present in new_entries
            for col in parent_widget.result_db.columns:
                if col not in new_entries.columns:
                    new_entries[col] = pd.NA
            
            # Reorder columns to match main db and concatenate
            new_entries = new_entries[parent_widget.result_db.columns]
            parent_widget.result_db = pd.concat([parent_widget.result_db, new_entries], ignore_index=True)
            
            logger.info(f"Added {len(new_entries)} new entries from CSV.")
        
        # Update existing entries
        update_data = new_data[new_data['Path'].isin(existing_paths)]
        if not update_data.empty:
            parent_widget.result_db.set_index('Path', inplace=True)
            update_data.set_index('Path', inplace=True)
            parent_widget.result_db.update(update_data)
            parent_widget.result_db.reset_index(inplace=True)
            logger.info(f"Updated {len(update_data)} existing entries from CSV.")

        # --- Refresh UI ---
        populate_file_list(parent_widget, clear_first=True, trigger_update=True)
        _update_features_windows(parent_widget)

        QMessageBox.information(parent_widget, "Import Successful",
                                f"Successfully imported data from {os.path.basename(file_path)}.\n"
                                f"Added: {len(new_entries)} new entries.\n"
                                f"Updated: {len(update_data)} existing entries.")

    except Exception as e:
        logger.error(f"Failed to import CSV file: {e}", exc_info=True)
        QMessageBox.critical(parent_widget, "Import Error", f"An error occurred while reading the CSV file: {e}")
