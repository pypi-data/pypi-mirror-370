"""
CLI auto-loading utility for the Neutrophils Classifier Application.
Handles command-line argument processing and auto-loading of images.
"""
import os
import numpy as np
import pandas as pd


def perform_cli_auto_load(window, cli_args):
    """
    Perform CLI auto-loading using the same methods as normal UI loading.
    
    Args:
        window: MainWindow instance
        cli_args: Parsed command line arguments
    """
    if not cli_args:
        return
        
    print("Performing CLI auto-load after UI setup...")
    
    try:
        # Import file loading functions
        from ..logic.file_io import populate_file_list
        
        loaded_files = []
        
        # Prioritize single image file if provided
        if cli_args.image_file:
            if os.path.isfile(cli_args.image_file) and (
                cli_args.image_file.endswith(".tif") or 
                cli_args.image_file.endswith(".tiff")
            ):
                print(f"Auto-loading single image: {cli_args.image_file}")
                loaded_files = [cli_args.image_file]
            else:
                print(f"Provided image file does not exist or is not a .tif/.tiff file: {cli_args.image_file}")
        
        # Only load from directory if single image wasn't provided
        elif cli_args.data_dir:
            if os.path.isdir(cli_args.data_dir):
                print(f"Auto-loading data from directory: {cli_args.data_dir}")
                loaded_files = [
                    os.path.join(cli_args.data_dir, f) 
                    for f in os.listdir(cli_args.data_dir) 
                    if os.path.isfile(os.path.join(cli_args.data_dir, f)) and 
                    (f.endswith(".tif") or f.endswith(".tiff"))
                ]
                
                if not loaded_files:
                    print(f"No .tif or .tiff files found in {cli_args.data_dir}")
            else:
                print(f"Provided data directory does not exist: {cli_args.data_dir}")
        
        # Load files using the same pattern as normal UI loading
        if loaded_files:
            _load_files_to_ui(window, loaded_files)
        else:
            print("No valid files found to auto-load")
            # Show "Ready" when no files found but process completed
            if hasattr(window, 'progress_label') and window.progress_label:
                window.progress_label.setText("Ready")
                window.progress_label.setVisible(True)
            
    except Exception as e:
        print(f"Error during CLI auto-load: {e}")
        if hasattr(window, 'progress_label') and window.progress_label:
            window.progress_label.setText(f"Error auto-loading: {str(e)}")
            window.progress_label.setVisible(True)


def _load_files_to_ui(window, loaded_files):
    """
    Load files to the UI using the same pattern as normal loading.
    
    Args:
        window: MainWindow instance
        loaded_files: List of file paths to load
    """
    from ..logic.file_io import populate_file_list
    
    # Filter out already loaded files
    new_files = [f for f in loaded_files if f not in window.files]
    
    if new_files:
        # Update files list (same as normal UI loading)
        window.files.extend(new_files)
        
        # Populate the file list using the same method as UI loading
        populate_file_list(window)
        
        # Create database entries for new files (same structure as normal loading)
        new_data_rows = []
        for f_path in new_files:
            # Check if path already exists in result_db to prevent duplicates
            if not (window.result_db['Path'] == f_path).any():
                new_data_rows.append({
                    "Path": f_path,
                    "ImageName": os.path.basename(f_path),
                    "Model": np.nan, "ClassProb_M": np.nan, "ClassProb_MM": np.nan,
                    "ClassProb_BN": np.nan, "ClassProb_SN": np.nan, "MaturationScore": np.nan,
                    "Area_1": np.nan, "Vol_1": np.nan, "NSI_1": np.nan, "Sphericity_1": np.nan,
                    "SA_Vol_Ratio_1": np.nan, "Solidity_1": np.nan, "Elongation_1": np.nan, "Genus_1": np.nan,
                    "Area_2": np.nan, "Vol_2": np.nan, "NSI_2": np.nan, "Sphericity_2": np.nan,
                    "SA_Vol_Ratio_2": np.nan, "Solidity_2": np.nan, "Elongation_2": np.nan, "Genus_2": np.nan,
                    "ManualAnnotation": np.nan
                })
        
        # Add new rows to result_db if any
        if new_data_rows:
            window.result_db = pd.concat([window.result_db, pd.DataFrame(new_data_rows)], ignore_index=True)
        
        # Show "Ready" status when process completes successfully
        if hasattr(window, 'progress_label') and window.progress_label:
            window.progress_label.setText("Ready")
            window.progress_label.setVisible(True)
        
        print(f"Successfully auto-loaded {len(new_files)} file(s) from CLI arguments")
    else:
        print("All specified files are already loaded")
        # Show "Ready" when all files already loaded but process completed
        if hasattr(window, 'progress_label') and window.progress_label:
            window.progress_label.setText("Ready")
            window.progress_label.setVisible(True)