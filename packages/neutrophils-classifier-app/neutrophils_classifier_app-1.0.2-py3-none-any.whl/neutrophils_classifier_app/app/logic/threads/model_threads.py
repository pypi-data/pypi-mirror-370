"""
Model-related threading classes for loading and inference.
"""
import os
import numpy as np
import pandas as pd
import toml
import time
from typing import Optional, Dict, Any
from PyQt5.QtCore import QThread, pyqtSignal
from tensorflow.keras.models import load_model

from neutrophils_core.loader.optimized_image_data_generator_3d import OptimizedImageDataGenerator3D
from neutrophils_core.models.simclr import SimCLREncoder, SimCLRModel
from ...utils.logging_config import get_logger
from .geometry_utils import pad_image, crop_center

try:
    from neutrophils_core.models.heads import ClassificationHead
except ImportError:
    ClassificationHead = None


class ModelLoadingThread(QThread):
    modelLoaded = pyqtSignal(object)
    loadingStarted = pyqtSignal()
    loadingFailed = pyqtSignal(str)

    def __init__(self, model_path, config_path):
        super().__init__()
        self.model_path = model_path
        self.config_path = config_path
        self._stop_requested = False

    def run(self):
        try:
            self.loadingStarted.emit()
            print("Loading model from:", self.model_path)
            if self._stop_requested:
                return

            import tensorflow as tf
            import toml
            
            if self._stop_requested:
                return

            custom_objects = {
                'SimCLREncoder': SimCLREncoder,
                'SimCLRModel': SimCLRModel
            }
            if ClassificationHead is not None:
                custom_objects['ClassificationHead'] = ClassificationHead
            
            model = load_model(self.model_path, custom_objects=custom_objects, compile=False)
            print("Model loaded successfully.")
            
            print("Loading configuration from:", self.config_path)
            with open(self.config_path, 'r') as f:
                config = toml.load(f)
            print("Configuration loaded successfully.")

            # Add model_name to the config dictionary
            config['model_name'] = os.path.splitext(os.path.basename(self.model_path))[0]

            if not self._stop_requested:
                self.modelLoaded.emit((model, config))
        except Exception as e:
            if not self._stop_requested:
                error_msg = f"Error in ModelLoadingThread: {e}"
                print(error_msg)
                self.loadingFailed.emit(error_msg)
    
    def stop_gracefully(self):
        """Request the thread to stop gracefully"""
        self._stop_requested = True

class SingleInferenceThread(QThread):
    """
    Simplified thread for background CNN inference on a single image.
    Runs model prediction on image data.
    """
    
    # Signals
    inference_complete = pyqtSignal(dict)  # classification_results
    progress_update = pyqtSignal(int, str)  # progress, message
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, datagen, model, model_config: dict,
                 label_encoder_path: str, parent=None):
        super().__init__(parent)
        self.datagen = datagen
        self.model = model
        self.model_config = model_config
        self.label_encoder_path = label_encoder_path
        self._cancelled = False
        self.logger = get_logger('logic.background_threads.inference')
        
    def run(self):
        """Main execution method for CNN inference."""
        try:
            self.logger.info("Starting background CNN inference")
            start_time = time.time()
            
            # Check cancellation before starting
            if self._cancelled:
                return
            
            self.progress_update.emit(10, "Preparing data for inference...")
            
            # Run inference
            classification_results = self._run_inference_safe()
            
            if self._cancelled:
                return
            
            if classification_results:
                self.progress_update.emit(100, "CNN inference complete")
                self.inference_complete.emit(classification_results)
                
                total_time = time.time() - start_time
                self.logger.info(f"Background CNN inference completed in {total_time:.3f}s")
            else:
                self.error_occurred.emit("CNN inference failed to produce results")
                
        except Exception as e:
            if not self._cancelled:
                error_msg = f"Error in CNN inference thread: {str(e)}"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
    
    def cancel(self):
        """Cancel the CNN inference."""
        self.logger.info("Cancelling CNN inference thread")
        self._cancelled = True
    
    def cleanup(self):
        """Clean up thread resources."""
        self.cancel()  # Set cancellation flag first
        if self.isRunning():
            self.wait(3000)  # Wait up to 3 seconds for graceful termination
            if self.isRunning():
                self.logger.warning("Force terminating CNN inference thread")
                self.terminate()
                self.wait(1000)  # Wait 1 more second after terminate
    
    def _run_inference_safe(self) -> Optional[Dict[str, Any]]:
        """
        Safely run CNN inference with cancellation checks.
        
        Returns:
            Dictionary of classification results or None if failed/cancelled
        """
        try:
            if self._cancelled:
                return None
            
            self.progress_update.emit(20, "Loading label encoder...")
            
            # Load label encoder
            if not os.path.exists(self.label_encoder_path):
                self.logger.error(f"Label encoder not found: {self.label_encoder_path}")
                return None
            
            label_encoder_classes = np.load(self.label_encoder_path, allow_pickle=True)
            
            if self._cancelled:
                return None
            
            self.progress_update.emit(40, "Preprocessing image...")
            
            # Preprocess image for model using existing utilities
            processed_image = self._preprocess_image_for_model()
            
            if self._cancelled:
                return None
            
            self.progress_update.emit(80, "Running model prediction...")
            
            # Run model prediction
            predictions = self.model.predict(processed_image, verbose=0)
            
            if self._cancelled:
                return None
            
            self.progress_update.emit(90, "Processing results...")
            
            # Process prediction results
            if len(predictions.shape) > 1:
                predictions = predictions[0]  # Take first element if batch dimension exists
            
            predicted_class_index = np.argmax(predictions)
            confidence_score = np.max(predictions)
            predicted_class_name = str(label_encoder_classes[predicted_class_index])
            
            classification_results = {
                'predicted_class': predicted_class_name,
                'confidence': float(confidence_score),
                'probabilities': predictions.tolist()
            }
            
            self.logger.debug(f"CNN inference results: {predicted_class_name} ({confidence_score:.3f})")
            return classification_results
            
        except Exception as e:
            self.logger.error(f"Error in CNN inference: {str(e)}")
            return None
    
    def _preprocess_image_for_model(self) -> Optional[np.ndarray]:
        """
        Preprocess image data for model input using the provided datagen.
        
        Returns:
            Preprocessed image ready for model
        """
        try:
            if self._cancelled:
                return None

            # Get batch from data generator
            if len(self.datagen) == 0:
                self.logger.error("No batches available from data generator")
                return None
            
            batch_images, _ = self.datagen[0]
            return batch_images

        except Exception as e:
            self.logger.error(f"Error preprocessing image: {str(e)}")
            return None

class BatchInferenceThread(QThread):
    """Thread for batch inference using CNN models with OptimizedImageDataGenerator3D."""
    processing_complete = pyqtSignal(object)
    progress_update = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, db, model, model_config, label_encoder_path, datagen, parent=None):
        super().__init__(parent)
        self.db = db
        self.model = model
        self.model_config = model_config
        self.label_encoder_path = label_encoder_path
        self.datagen = datagen
        self._is_interrupted = False
        self.processed_count = 0
        self.total_files = len(self.db)
    
    def run(self):
        """Run batch inference using OptimizedImageDataGenerator3D for proper data loading."""
        try:
            # Force TensorFlow to use CPU to avoid conflicts with VTK's OpenGL context on the GPU.
            # This is a critical step to prevent wglMakeCurrent errors and subsequent crashes.
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
            print("[BatchInferenceThread] Starting batch inference on CPU...")
            
            # Load label encoder
            if not os.path.exists(self.label_encoder_path):
                error_msg = f"Label encoder not found at {self.label_encoder_path}"
                print("[BatchInferenceThread]", error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            print(f"[BatchInferenceThread] Loading label encoder from: {self.label_encoder_path}")
            label_encoder_classes = np.load(self.label_encoder_path, allow_pickle=True)
            print(f"[BatchInferenceThread] Loaded label encoder classes: {label_encoder_classes}")
            
            # Ensure classification columns exist
            if 'Predicted_Class' not in self.db.columns:
                print("[BatchInferenceThread] Adding 'Predicted_Class' column to database.")
                self.db['Predicted_Class'] = ''
            if 'confidence' not in self.db.columns:
                print("[BatchInferenceThread] Adding 'confidence' column to database.")
                self.db['confidence'] = np.nan
            
            # Add class probability columns dynamically based on label encoder
            for class_name in label_encoder_classes:
                col_name = f'ClassProb_{class_name}'
                if col_name not in self.db.columns:
                    print(f"[BatchInferenceThread] Adding '{col_name}' column to database.")
                    self.db[col_name] = np.nan

            # Prepare data for OptimizedImageDataGenerator3D
            file_paths = self.db['Path'].tolist()
            
            if not file_paths:
                error_msg = "No file paths found in database"
                print("[BatchInferenceThread]", error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            # Find common base directory
            from pathlib import Path
            path_objects = [Path(p) for p in file_paths]
            
            # Try to find a common parent directory
            try:
                base_dir = path_objects[0].parent
                relative_paths = []
                for path_obj in path_objects:
                    try:
                        rel_path = path_obj.relative_to(base_dir)
                        relative_paths.append(str(rel_path))
                    except ValueError:
                        base_dir = Path("/") if os.name != 'nt' else Path("C:/")
                        relative_paths = [str(p) for p in path_objects]
                        print("[BatchInferenceThread] Could not find common base directory, using absolute paths.")
                        break
                print(f"[BatchInferenceThread] Using base directory: {base_dir}")
            except Exception as e:
                base_dir = Path("/") if os.name != 'nt' else Path("C:/")
                relative_paths = file_paths
                print(f"[BatchInferenceThread] Exception finding base directory: {e}. Using absolute paths.")

            # Create DataFrame for the data generator
            inference_df = pd.DataFrame({'filepath': relative_paths})
            print(f"[BatchInferenceThread] Created inference DataFrame with {len(inference_df)} entries.")

            # Get data configuration
            data_config = self.model_config.get("data", {})
            print(f"[BatchInferenceThread] Data config: {data_config}")
            
            # Create OptimizedImageDataGenerator3D
            print("[BatchInferenceThread] Initializing OptimizedImageDataGenerator3D...")
            print(f"[BatchInferenceThread] Data generator initialized with {len(self.datagen)} batches.")

            num_batches = len(self.datagen)
            all_predictions = []
            processed_files = []
            
            # Run inference batch by batch
            for i in range(num_batches):
                if self._is_interrupted:
                    print("[BatchInferenceThread] Inference interrupted by user.")
                    break
                
                try:
                    print(f"[BatchInferenceThread] Processing batch {i+1}/{num_batches}...")
                    batch_data = self.datagen[i]
                    if len(batch_data) == 2:
                        batch_images, batch_paths = batch_data
                    else:
                        batch_images = batch_data
                        batch_paths = None
                    
                    print(f"[BatchInferenceThread] Predicting on batch {i+1} with {len(batch_images)} images...")
                    batch_predictions = self.model.predict(batch_images, verbose=0)
                    print(f"[BatchInferenceThread] Batch {i+1} predictions shape: {batch_predictions.shape}")
                    all_predictions.append(batch_predictions)
                    
                    # Track processed files
                    if batch_paths is not None:
                        processed_files.extend(batch_paths)
                    
                    # Update progress
                    self.processed_count = min(self.total_files, (i + 1) * self.datagen.batch_size)
                    progress = int((self.processed_count / self.total_files) * 100)
                    print(f"[BatchInferenceThread] Progress: {progress}% ({self.processed_count}/{self.total_files})")
                    self.progress_update.emit(progress, f"Processed batch {i+1}/{num_batches}")
                    
                except Exception as e:
                    error_msg = f"Error processing batch {i}: {str(e)}"
                    print("[BatchInferenceThread]", error_msg)
                    self.error_occurred.emit(error_msg)
                    continue
            
            if self._is_interrupted:
                print("[BatchInferenceThread] Inference stopped before completion.")
                return
            
            # Concatenate all predictions
            if all_predictions:
                print("[BatchInferenceThread] Concatenating predictions...")
                predictions = np.vstack(all_predictions)
                print(f"[BatchInferenceThread] Total predictions shape: {predictions.shape}")
                
                # Ensure we have the right number of predictions
                predictions = predictions[:len(self.db)]
                print(f"[BatchInferenceThread] Trimmed predictions to {len(predictions)} samples.")

                # Process predictions
                predicted_class_indices = np.argmax(predictions, axis=1)
                confidence_scores = np.max(predictions, axis=1)
                predicted_class_names = [str(label_encoder_classes[i]) for i in predicted_class_indices]
                
                # Ensure MaturationScore column exists
                if 'MaturationScore' not in self.db.columns:
                    print("[BatchInferenceThread] Adding 'MaturationScore' column to database.")
                    self.db['MaturationScore'] = np.nan
                
                print("[BatchInferenceThread] Updating database with predictions...")
                for idx, (pred_class, confidence, pred_probs) in enumerate(zip(
                    predicted_class_names, confidence_scores, predictions)):
                    
                    if idx >= len(self.db):
                        print(f"[BatchInferenceThread] Warning: idx {idx} exceeds database length.")
                        break
                        
                    self.db.iloc[idx, self.db.columns.get_loc('Predicted_Class')] = pred_class
                    self.db.iloc[idx, self.db.columns.get_loc('confidence')] = confidence
                    
                    # Update class probabilities
                    for j, class_name in enumerate(label_encoder_classes):
                        col_name = f'ClassProb_{class_name}'
                        if col_name in self.db.columns and j < len(pred_probs):
                            self.db.iloc[idx, self.db.columns.get_loc(col_name)] = pred_probs[j]
                    
                    # Calculate maturation score - linear weighted value from 0 to 1
                    # M=0, MM=0.33, BN=0.67, SN=1.0
                    if len(pred_probs) >= 4:
                        maturation_weights = [0.0, 0.33, 0.67, 1.0]
                        maturation_score = sum(prob * weight for prob, weight in zip(pred_probs, maturation_weights))
                        self.db.iloc[idx, self.db.columns.get_loc('MaturationScore')] = maturation_score
                    else:
                        self.db.iloc[idx, self.db.columns.get_loc('MaturationScore')] = np.nan
                
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                thread_id = str(self.currentThreadId())
                print(f"[{timestamp}] [BatchInferenceThread::{thread_id}] Batch inference complete. Emitting results.")
                self.processing_complete.emit(self.db)
            else:
                error_msg = "No predictions were generated"
                print("[BatchInferenceThread]", error_msg)
                self.error_occurred.emit(error_msg)
                
        except Exception as e:
            self.error_occurred.emit(f"Error in batch inference: {str(e)}")

    def stop(self):
        """Stop the batch inference process."""
        print("[BatchInferenceThread] Stopping batch inference thread...")
        self._is_interrupted = True