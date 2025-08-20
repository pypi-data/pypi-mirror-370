"""
Utility threading classes for various background operations.
"""
import os
import json
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QThreadPool
from .geometry_utils import _format_metric_key
from .image_processing_threads import ImageProcessor


class ImageLoadingThread(QThread):
    """Lightweight image loading thread - imports dependencies on-demand"""
    result_signal = pyqtSignal(np.ndarray)

    def __init__(self, path):
        super().__init__()
        self.path = path
        self._stop_requested = False

    def run(self):
        try:
            # Check if stop was requested before starting
            if self._stop_requested:
                return
                
            # Import tifffile on-demand to avoid heavy loading during initialization
            import tifffile
            
            # Check again after import (in case it takes time)
            if self._stop_requested:
                return
                
            img = tifffile.imread(self.path)
            
            # Final check before emitting
            if not self._stop_requested:
                self.result_signal.emit(img)
        except Exception:
            # Don't emit anything on failure - let caller handle timeout
            return
    
    def stop_gracefully(self):
        """Request the thread to stop gracefully"""
        self._stop_requested = True


class HeavyComponentsLoadingThread(QThread):
    progress_signal = pyqtSignal(int, str)  # progress percentage, status message
    components_loaded_signal = pyqtSignal(object)  # loaded components tuple
    
    def __init__(self):
        super().__init__()
        self._stop_requested = False
    
    def run(self):
        """Load heavy components in background with progress updates"""
        try:
            components = []
            
            # Step 1: Initialize component loading (10%)
            if self._stop_requested:
                return
            self.progress_signal.emit(10, "Initializing component loading")
            
            # Step 2: Loading configuration files (25%)
            if self._stop_requested:
                return
            self.progress_signal.emit(25, "Loading configuration files")
            
            # Step 3: Load geometric info JSON (40%)
            if self._stop_requested:
                return
            self.progress_signal.emit(40, "Loading geometric information database")
            metric_info = self._load_geometric_info()
            components.append(metric_info)
            
            # Step 4: Scanning models directory (55%)
            if self._stop_requested:
                return
            self.progress_signal.emit(55, "Scanning models directory")
            
            # Step 5: Discovering and validating models (70%)
            if self._stop_requested:
                return
            self.progress_signal.emit(70, "Discovering and validating models")
            discovered_models = self._discover_models()
            components.append(discovered_models)
            
            # Step 6: Preparing components for UI integration (85%)
            if self._stop_requested:
                return
            self.progress_signal.emit(85, "Preparing components for UI integration")
            
            # Step 7: Finalizing component setup (95%)
            if self._stop_requested:
                return
            self.progress_signal.emit(95, "Finalizing component setup")
            
            # Step 8: Complete (100%)
            if self._stop_requested:
                return
            self.progress_signal.emit(100, "Heavy components loaded successfully")
            self.components_loaded_signal.emit(tuple(components))
            
        except Exception as e:
            if not self._stop_requested:
                print(f"ERROR: Exception in HeavyComponentsLoadingThread.run(): {e}")
                self.progress_signal.emit(0, f"Error loading components: {str(e)}")
    
    def stop_gracefully(self):
        """Request the thread to stop gracefully"""
        self._stop_requested = True
    
    def _load_geometric_info(self):
        """Load geometric info JSON file"""
        geometric_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'assets', 'geometric_info.json')
        try:
            with open(geometric_info_path, 'r') as f:
                data = json.load(f)
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load geometric info: {e}")
            return {}
        
    def _discover_models(self):
        """Discover available Keras models and their configurations"""
        models = []
        configs = []
        
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'models')
        
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith(('.keras', '.h5'))]
            config_files = [f for f in os.listdir(models_dir) if f.endswith('.toml')]

            if not model_files:
                return ([], [])

            # If there's only one config file, assume it applies to all models
            if len(config_files) == 1:
                config_path = os.path.join(models_dir, config_files[0])
                for model_file in model_files:
                    models.append(os.path.join(models_dir, model_file))
                    configs.append(config_path)
            else:
                # Fallback to original logic if there are multiple or no config files, but with more flexibility
                for model_path in model_files:
                    base_name = os.path.splitext(model_path)[0]
                    
                    # Check for exact name match (e.g., model.toml for model.keras)
                    config_path_match = os.path.join(models_dir, f"{base_name}.toml")
                    if not os.path.exists(config_path_match):
                        # Check for _config suffix (e.g., model_config.toml)
                        config_path_match = os.path.join(models_dir, f"{base_name}_config.toml")

                    if os.path.exists(config_path_match):
                        full_model_path = os.path.join(models_dir, model_path)
                        models.append(full_model_path)
                        configs.append(config_path_match)
        
        return (models, configs)


class BatchProcessingThread(QThread):
    """Thread for batch processing of images."""
    processing_complete = pyqtSignal(object)
    progress_update = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, db, percentile1, percentile2, model=None, model_config=None, label_encoder_path=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.percentile1 = percentile1
        self.percentile2 = percentile2
        self.model = model
        self.model_config = model_config
        self.label_encoder_path = label_encoder_path
        self._is_interrupted = False
        self.processed_count = 0
        self.total_files = len(self.db)
        self.threadpool = QThreadPool()

    def run(self):
        self.processed_count = 0
        
        # Pre-create columns to ensure they exist even if no metrics are generated
        metric_keys = [
            "area", "vol", "nsi", "sphericity", "sa_vol_ratio",
            "solidity", "elongation", "genus"
        ]
        for key in metric_keys:
            col_name_1 = f'{_format_metric_key(key)}_1'
            col_name_2 = f'{_format_metric_key(key)}_2'
            if col_name_1 not in self.db.columns:
                self.db[col_name_1] = np.nan
            if col_name_2 not in self.db.columns:
                self.db[col_name_2] = np.nan

        for index, row in self.db.iterrows():
            if self._is_interrupted:
                break
            
            existing_thresholds = {'threshold1': row.get('threshold1'), 'threshold2': row.get('threshold2')}
            worker = ImageProcessor(row['Path'], self.percentile1, self.percentile2, existing_thresholds, self.model, self.model_config, self.label_encoder_path)
            worker.signals.result.connect(self.handle_result)
            worker.signals.error.connect(self.error_occurred.emit)
            worker.signals.finished.connect(self.update_progress)
            self.threadpool.start(worker)

        self.threadpool.waitForDone()
        if not self._is_interrupted:
            self.processing_complete.emit(self.db)

    def handle_result(self, result):
        idx = self.db[self.db['Path'] == result['file_path']].index
        if not idx.empty:
            index = idx[0]
            self.db.loc[index, 'threshold1'] = result['threshold1']
            self.db.loc[index, 'threshold2'] = result['threshold2']
            for k, v in result['metrics1'].items():
                self.db.loc[index, f'{_format_metric_key(k)}_1'] = v
            for k, v in result['metrics2'].items():
                self.db.loc[index, f'{_format_metric_key(k)}_2'] = v
            if 'classification' in result and result['classification']:
                self.db.loc[index, 'predicted_class'] = result['classification'].get('predicted_class')
                self.db.loc[index, 'confidence'] = result['classification'].get('confidence')

    def update_progress(self, file_path):
        self.processed_count += 1
        progress = int((self.processed_count / self.total_files) * 100)
        self.progress_update.emit(progress, f"Processed {os.path.basename(file_path)}")

    def stop(self):
        self._is_interrupted = True
        self.threadpool.clear()