"""
Image processing threading classes.
"""
import os
import time
import threading
import numpy as np
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool
from neutrophils_core.loader.optimized_image_data_generator_3d import OptimizedImageDataGenerator3D
from .geometry_utils import calculate_metrics_from_polydata


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    '''
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int, str)


class ImageProcessor(QRunnable):
    '''
    Worker thread for processing a single image.
    '''
    def __init__(self, file_path, percentile1, percentile2, existing_thresholds=None, model=None, model_config=None, label_encoder_path=None):
        super(ImageProcessor, self).__init__()
        self.file_path = file_path
        self.percentile1 = percentile1
        self.percentile2 = percentile2
        self.existing_thresholds = existing_thresholds or {}
        self.signals = WorkerSignals()
        self.model = model
        self.model_config = model_config
        self.label_encoder_path = label_encoder_path

    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress.emit(20, "Reading image file...")
            import tifffile
            import vtk
            from vtk.util import numpy_support
            import traceback
            
            print("Reading image file:", self.file_path)
            if not os.path.exists(self.file_path):
                self.signals.error.emit(f"File not found: {self.file_path}")
                return

            img = tifffile.imread(self.file_path)
            print("Image loaded successfully.")

            
            print("calculating thresholds...")
            self.signals.progress.emit(30, "Calculating thresholds...")

            threshold1 = self.existing_thresholds.get('threshold1')
            threshold2 = self.existing_thresholds.get('threshold2')

            if threshold1 is None or pd.isna(threshold1):
                if self.percentile1 == 'mean':
                    threshold1 = int(np.mean(img))
                else:
                    threshold1 = int(np.percentile(img, self.percentile1))
            
            if threshold2 is None or pd.isna(threshold2):
                if self.percentile2 == 'mean':
                    threshold2 = int(np.mean(img))
                else:
                    threshold2 = int(np.percentile(img, self.percentile2))

            threshold1 = max(1, threshold1)
            threshold2 = max(1, threshold2)
            
            print(f"Using thresholds: threshold1={threshold1}, threshold2={threshold2}")

            self.signals.progress.emit(40, "Converting to VTK data...")
            vtk_data = vtk.vtkImageData()
            vtk_data.SetDimensions(img.shape)
            vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_SHORT, 1)
            flat_data = img.flatten()
            vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT)
            vtk_data.GetPointData().SetScalars(vtk_array)

            print("Generating surface for threshold 1...")
            self.signals.progress.emit(50, "Generating surface for threshold 1...")
            contour1 = vtk.vtkMarchingCubes()
            contour1.SetInputData(vtk_data)
            contour1.SetValue(0, threshold1)
            contour1.Update()
            polydata1 = contour1.GetOutput()

            print("Generating surface for threshold 2...")
            self.signals.progress.emit(60, "Generating surface for threshold 2...")
            contour2 = vtk.vtkMarchingCubes()
            contour2.SetInputData(vtk_data)
            contour2.SetValue(0, threshold2)
            contour2.Update()
            polydata2 = contour2.GetOutput()

            print("Calculating metrics for threshold 1...")
            self.signals.progress.emit(70, "Calculating metrics for threshold 1...")
            metrics1 = calculate_metrics_from_polydata(vtk, polydata1)

            print("Calculating metrics for threshold 2...")
            self.signals.progress.emit(80, "Calculating metrics for threshold 2...")
            metrics2 = calculate_metrics_from_polydata(vtk, polydata2)

            print("Calling classification model if available...")
            classification_results = {}
            if self.model and self.model_config and self.label_encoder_path:
                self.signals.progress.emit(85, "Running classification...")
                print("DEBUG: Starting classification process...")
                classification_results = self._run_classification(img)
                print(f"DEBUG: Classification completed, results: {classification_results}")
            else:
                print("DEBUG: Skipping classification - model/config/encoder not available")

            print("DEBUG: About to finalize results...")
            self.signals.progress.emit(90, "Finalizing results...")
            print("DEBUG: Creating final result dictionary...")
            result = {
                "file_path": self.file_path,
                "threshold1": threshold1,
                "threshold2": threshold2,
                "metrics1": metrics1,
                "metrics2": metrics2,
                "polydata1": polydata1,
                "polydata2": polydata2,
                "image": img,
                "classification": classification_results
            }
            print(f"DEBUG: Final result dictionary created with keys: {list(result.keys())}")
            print("DEBUG: About to emit result signal...")
            self.signals.result.emit(result)
            print("DEBUG: Result signal emitted successfully")
        except Exception as e:
            self.signals.error.emit(f"Error processing {self.file_path}: {e}")
        finally:
            self.signals.finished.emit(self.file_path)

    def _run_classification(self, img):
        try:
            print("Starting classification...")
            print(f"Label encoder path: {self.label_encoder_path}")
            label_encoder_classes = np.load(self.label_encoder_path, allow_pickle=True)
            print(f"Loaded label encoder classes: {label_encoder_classes}")

            inference_df = pd.DataFrame({'filepath': [os.path.basename(self.file_path)]})
            print(f"Inference DataFrame: {inference_df}")

            data_config = self.model_config["data"]
            print(f"Model data config: {data_config}")

            datagen = OptimizedImageDataGenerator3D(
                df=inference_df,
                data_dir=os.path.dirname(self.file_path),
                batch_size=1,
                image_size=data_config["image_size"],
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
            print("Data generator created.")

            print("DEBUG: About to get batch from data generator...")
            try:
                batch_images, _ = datagen[0]
                print(f"Batch images shape: {batch_images.shape}")
                print(f"DEBUG: Batch images dtype: {batch_images.dtype}")
                print(f"DEBUG: Batch images min/max: {np.min(batch_images)}/{np.max(batch_images)}")
            except Exception as e:
                print(f"DEBUG: Error getting batch from data generator: {e}")
                raise e

            print("Running model prediction...")
            try:
                predictions = self.model.predict(batch_images, verbose=0)
                print(f"Predictions: {predictions}")
                print(f"DEBUG: Predictions shape: {predictions.shape}")
                print(f"DEBUG: Predictions dtype: {predictions.dtype}")
            except Exception as e:
                print(f"DEBUG: Error during model prediction: {e}")
                raise e

            predicted_class_indices = np.argmax(predictions, axis=1)
            print(f"Predicted class indices: {predicted_class_indices}")

            confidence_scores = np.max(predictions, axis=1)
            print(f"Confidence scores: {confidence_scores}")

            predicted_class_names = [str(label_encoder_classes[i]) for i in predicted_class_indices]
            print(f"Predicted class names: {predicted_class_names}")
            
            print("DEBUG: Creating classification result dictionary...")
            try:
                result_dict = {
                    'predicted_class': predicted_class_names[0],
                    'confidence': confidence_scores[0],
                    'probabilities': predictions[0]
                }
                print(f"DEBUG: Classification result created: {result_dict}")
                print("DEBUG: About to return classification results...")
                return result_dict
            except Exception as e:
                print(f"DEBUG: Error creating classification result dict: {e}")
                print(f"DEBUG: predicted_class_names: {predicted_class_names}")
                print(f"DEBUG: confidence_scores: {confidence_scores}")
                print(f"DEBUG: predictions shape: {predictions.shape if hasattr(predictions, 'shape') else 'No shape'}")
                raise e
        except Exception as e:
            print(f"Classification failed: {e}")
            traceback.print_exc()
            return {}


class ImageProcessingThread(QThread):
    """Thread for heavy image processing including loading, surface generation, and metrics."""
    processing_complete = pyqtSignal(dict)
    progress_update = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path, percentile1=0, percentile2=2, existing_thresholds=None, model=None, model_config=None, label_encoder_path=None):
        super().__init__()
        self.file_path = file_path
        self.percentile1 = percentile1
        self.percentile2 = percentile2
        self.existing_thresholds = existing_thresholds
        self.model = model
        self.model_config = model_config
        self.label_encoder_path = label_encoder_path
        self._is_interrupted = False

    def run(self):
        """Run image processing directly in this thread to avoid nested threading issues."""
        try:
            self.start_time = time.time()
            self.progress_update.emit(10, "Starting cell analysis...")
            
            # Run the image processing directly in this thread
            self.progress_update.emit(20, "Reading image file...")
            import tifffile
            import vtk
            from vtk.util import numpy_support
            import traceback
            
            print("Reading image file:", self.file_path)
            if not os.path.exists(self.file_path):
                self.error_occurred.emit(f"File not found: {self.file_path}")
                return

            img = tifffile.imread(self.file_path)
            print("Image loaded successfully.")

            print("calculating thresholds...")
            self.progress_update.emit(30, "Calculating thresholds...")

            threshold1 = self.existing_thresholds.get('threshold1') if self.existing_thresholds else None
            threshold2 = self.existing_thresholds.get('threshold2') if self.existing_thresholds else None

            if threshold1 is None or pd.isna(threshold1):
                if self.percentile1 == 'mean':
                    threshold1 = int(np.mean(img))
                else:
                    threshold1 = int(np.percentile(img, self.percentile1))
            
            if threshold2 is None or pd.isna(threshold2):
                if self.percentile2 == 'mean':
                    threshold2 = int(np.mean(img))
                else:
                    threshold2 = int(np.percentile(img, self.percentile2))

            threshold1 = max(1, threshold1)
            threshold2 = max(1, threshold2)
            
            print(f"Using thresholds: threshold1={threshold1}, threshold2={threshold2}")

            self.progress_update.emit(40, "Converting to VTK data...")
            vtk_data = vtk.vtkImageData()
            vtk_data.SetDimensions(img.shape)
            vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_SHORT, 1)
            flat_data = img.flatten()
            vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT)
            vtk_data.GetPointData().SetScalars(vtk_array)

            print("Generating surface for threshold 1...")
            self.progress_update.emit(50, "Generating surface for threshold 1...")
            contour1 = vtk.vtkMarchingCubes()
            contour1.SetInputData(vtk_data)
            contour1.SetValue(0, threshold1)
            contour1.Update()
            polydata1 = contour1.GetOutput()

            print("Generating surface for threshold 2...")
            self.progress_update.emit(60, "Generating surface for threshold 2...")
            contour2 = vtk.vtkMarchingCubes()
            contour2.SetInputData(vtk_data)
            contour2.SetValue(0, threshold2)
            contour2.Update()
            polydata2 = contour2.GetOutput()

            print("Calculating metrics for threshold 1...")
            self.progress_update.emit(70, "Calculating metrics for threshold 1...")
            metrics1 = calculate_metrics_from_polydata(vtk, polydata1)

            print("Calculating metrics for threshold 2...")
            self.progress_update.emit(80, "Calculating metrics for threshold 2...")
            metrics2 = calculate_metrics_from_polydata(vtk, polydata2)

            print("Calling classification model if available...")
            classification_results = {}
            if self.model and self.model_config and self.label_encoder_path:
                self.progress_update.emit(85, "Running classification...")
                print("DEBUG: Starting classification process...")
                classification_results = self._run_classification(img)
                print(f"DEBUG: Classification completed, results: {classification_results}")
            else:
                print("DEBUG: Skipping classification - model/config/encoder not available")

            print("DEBUG: About to finalize results...")
            self.progress_update.emit(90, "Finalizing results...")
            processing_time = time.time() - self.start_time
            
            result = {
                "file_path": self.file_path,
                "threshold1": threshold1,
                "threshold2": threshold2,
                "metrics1": metrics1,
                "metrics2": metrics2,
                "polydata1": polydata1,
                "polydata2": polydata2,
                "image": img,
                "classification": classification_results,
                "processing_time": processing_time
            }
            
            print("DEBUG: About to emit processing_complete signal...")
            self.processing_complete.emit(result)
            print("DEBUG: processing_complete signal emitted")
            self.progress_update.emit(100, "Processing complete.")
            
        except Exception as e:
            self.error_occurred.emit(f"Error processing {self.file_path}: {e}")
            
    def _run_classification(self, img):
        try:
            print("Starting classification...")
            print(f"Label encoder path: {self.label_encoder_path}")
            label_encoder_classes = np.load(self.label_encoder_path, allow_pickle=True)
            print(f"Loaded label encoder classes: {label_encoder_classes}")

            inference_df = pd.DataFrame({'filepath': [os.path.basename(self.file_path)]})
            print(f"Inference DataFrame: {inference_df}")

            data_config = self.model_config["data"]
            print(f"Model data config: {data_config}")

            datagen = OptimizedImageDataGenerator3D(
                df=inference_df,
                data_dir=os.path.dirname(self.file_path),
                batch_size=1,
                image_size=data_config["image_size"],
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
            print("Data generator created.")

            print("DEBUG: About to get batch from data generator...")
            try:
                batch_images, _ = datagen[0]
                print(f"Batch images shape: {batch_images.shape}")
            except Exception as e:
                print(f"DEBUG: Error getting batch from data generator: {e}")
                raise e

            print("Running model prediction...")
            try:
                predictions = self.model.predict(batch_images, verbose=0)
                print(f"Predictions: {predictions}")
            except Exception as e:
                print(f"DEBUG: Error during model prediction: {e}")
                raise e

            predicted_class_indices = np.argmax(predictions, axis=1)
            confidence_scores = np.max(predictions, axis=1)
            predicted_class_names = [str(label_encoder_classes[i]) for i in predicted_class_indices]
            
            result_dict = {
                'predicted_class': predicted_class_names[0],
                'confidence': confidence_scores[0],
                'probabilities': predictions[0]
            }
            print("DEBUG: About to return classification results...")
            return result_dict
        except Exception as e:
            print(f"Classification failed: {e}")
            traceback.print_exc()
            return {}

    def stop(self):
        self._is_interrupted = True

class FastRenderingThread(QThread):
    """
    A thread dedicated to fast initial rendering of image data.
    This thread handles image loading, threshold calculation, and VTK polydata generation.
    It is designed to provide a quick visual representation of the cell surface,
    while more computationally intensive tasks like metrics calculation and model
    inference are deferred to other threads.
    """
    progress_update = pyqtSignal(int, str)
    rendering_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path, percentile1, percentile2, existing_thresholds=None, parent=None):
        """
        Initializes the FastRenderingThread.

        Args:
            file_path (str): The path to the image file to process.
            percentile1 (float): The first percentile for thresholding.
            percentile2 (float): The second percentile for thresholding.
            existing_thresholds (dict, optional): A dictionary with existing threshold values.
                                                  Defaults to None.
            parent (QObject, optional): The parent object. Defaults to None.
        """
        super().__init__(parent)
        self.file_path = file_path
        self.percentile1 = percentile1
        self.percentile2 = percentile2
        self.existing_thresholds = existing_thresholds or {}
        self._is_cancelled = False

    def run(self):
        """
        The main execution method of the thread.
        Loads the image, calculates thresholds, and generates polydata.
        """
        import time
        fast_start_time = time.time()
        print(f"DEBUG: FastRenderingThread.run() started at {fast_start_time} (ID: {id(self)})")
        try:
            self.progress_update.emit(0, "Loading image...")
            import tifffile
            import vtk
            from vtk.util import numpy_support
            import traceback

            if not os.path.exists(self.file_path):
                print(f"DEBUG: FastRenderingThread - File not found: {self.file_path}")
                self.error_occurred.emit(f"File not found: {self.file_path}")
                return

            if self._is_cancelled:
                print(f"DEBUG: FastRenderingThread - Cancelled before image loading")
                return

            img = tifffile.imread(self.file_path)
            self.progress_update.emit(15, "Image loaded.")

            if self._is_cancelled:
                return

            self.progress_update.emit(20, "Calculating thresholds...")
            
            threshold1 = self.existing_thresholds.get('threshold1')
            threshold2 = self.existing_thresholds.get('threshold2')

            if threshold1 is None or pd.isna(threshold1):
                if self.percentile1 == 'mean':
                    threshold1 = int(np.mean(img))
                else:
                    threshold1 = int(np.percentile(img, self.percentile1))
            
            if threshold2 is None or pd.isna(threshold2):
                if self.percentile2 == 'mean':
                    threshold2 = int(np.mean(img))
                else:
                    threshold2 = int(np.percentile(img, self.percentile2))

            threshold1 = max(1, threshold1)
            threshold2 = max(1, threshold2)

            self.progress_update.emit(30, "Thresholds calculated.")

            if self._is_cancelled:
                return

            self.progress_update.emit(35, "Converting to VTK data...")
            vtk_data = vtk.vtkImageData()
            vtk_data.SetDimensions(img.shape)
            vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_SHORT, 1)
            flat_data = img.flatten()
            vtk_array = numpy_support.numpy_to_vtk(num_array=flat_data, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT)
            vtk_data.GetPointData().SetScalars(vtk_array)

            if self._is_cancelled:
                return

            self.progress_update.emit(50, "Generating surface for threshold 1...")
            contour1 = vtk.vtkMarchingCubes()
            contour1.SetInputData(vtk_data)
            contour1.SetValue(0, threshold1)
            contour1.Update()
            polydata1 = contour1.GetOutput()

            if self._is_cancelled:
                return

            self.progress_update.emit(75, "Generating surface for threshold 2...")
            contour2 = vtk.vtkMarchingCubes()
            contour2.SetInputData(vtk_data)
            contour2.SetValue(0, threshold2)
            contour2.Update()
            polydata2 = contour2.GetOutput()

            if self._is_cancelled:
                return

            self.progress_update.emit(100, "Rendering complete.")
            
            result = {
                "file_path": self.file_path,
                "threshold1": threshold1,
                "threshold2": threshold2,
                "polydata1": polydata1,
                "polydata2": polydata2,
                "image": img,
                "image_shape": img.shape,
            }
            fast_end_time = time.time()
            fast_total_time = fast_end_time - fast_start_time
            print(f"DEBUG: FastRenderingThread - About to emit rendering_complete signal at {fast_end_time}")
            print(f"DEBUG: FastRenderingThread - Total rendering time: {fast_total_time:.3f}s")
            print(f"DEBUG: FastRenderingThread - UI should become interactive after this signal")
            self.rendering_complete.emit(result)
            print(f"DEBUG: FastRenderingThread - rendering_complete signal emitted successfully")

        except Exception as e:
            import traceback
            print(f"DEBUG: FastRenderingThread - Exception occurred: {e}")
            print(f"DEBUG: FastRenderingThread - Traceback: {traceback.format_exc()}")
            self.error_occurred.emit(f"Rendering failed for {os.path.basename(self.file_path)}: {e}\n{traceback.format_exc()}")
        finally:
            print(f"DEBUG: FastRenderingThread.run() finished (ID: {id(self)})")
        
    def cancel(self):
        """
        Signals the thread to terminate its operation at the next safe opportunity.
        """
        print(f"DEBUG: FastRenderingThread.cancel() called (ID: {id(self)})")
        self._is_cancelled = True

class ParallelMetricsWorker(QRunnable):
    """
    A QRunnable worker for calculating geometric metrics from polydata in parallel.
    This worker is designed to be used with a QThreadPool to offload metrics
    calculations from the main processing threads, allowing for concurrent
    computation of metrics for different thresholds.
    """
    def __init__(self, polydata, threshold_id, progress_callback, completion_callback, error_callback):
        """
        Initializes the ParallelMetricsWorker.

        Args:
            polydata: The VTK polydata to process.
            threshold_id (int): An identifier for the threshold (e.g., 1 or 2).
            progress_callback (callable): A function to call with progress updates.
                                          It should accept a string message.
            completion_callback (callable): A function to call upon successful completion.
                                            It should accept the threshold_id and a dict of metrics.
            error_callback (callable): A function to call when an error occurs.
                                       It should accept the threshold_id and an error message.
        """
        super().__init__()
        self.polydata = polydata
        self.threshold_id = threshold_id
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.error_callback = error_callback

    @pyqtSlot()
    def run(self):
        """
        The main execution method of the worker.
        Calculates geometric metrics for the provided polydata.
        """
        try:
            import vtk
            self.progress_callback(f"T{self.threshold_id}: Calculating metrics...")
            
            # Since this runs in a separate thread, we need to be careful with VTK objects.
            # It's generally safer to pass serialized or simple data, but here we pass the polydata
            # with the assumption that it's not being modified elsewhere concurrently.
            # FIX: The function only accepts 2 parameters (vtk, polydata), not 4
            metrics = calculate_metrics_from_polydata(vtk, self.polydata)
            
            self.progress_callback(f"T{self.threshold_id}: Metrics calculation complete.")
            self.completion_callback(self.threshold_id, metrics)
        except Exception as e:
            import traceback
            error_message = f"Error in metrics worker T{self.threshold_id}: {e}\n{traceback.format_exc()}"
            self.error_callback(self.threshold_id, error_message)

class BackgroundMetricsThread(QThread):
    """
    A thread for background processing of metrics and model inference.
    This thread takes the polydata generated by FastRenderingThread, calculates
    geometric metrics in parallel using a QThreadPool, and then runs model
    inference on the original image data.
    """
    progress_update = pyqtSignal(int, str)
    metrics_complete = pyqtSignal(int, dict)  # threshold_id, metrics_dict
    inference_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, rendering_results, model, model_config, label_encoder_path, parent=None):
        super().__init__(parent)
        self.rendering_results = rendering_results
        self.model = model
        self.model_config = model_config
        self.label_encoder_path = label_encoder_path

        self.file_path = rendering_results['file_path']
        self.polydata1 = rendering_results['polydata1']
        self.polydata2 = rendering_results['polydata2']

        self._is_cancelled = False
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(2)

        self.metrics_results = {}
        self.error_results = {}
        self.completed_count = 0
        self.progress_counter = 0
        self.lock = threading.Lock()

    def run(self):
        """
        The main execution method of the thread.
        It coordinates parallel metrics calculation and subsequent model inference.
        """
        try:
            import time
            bg_start_time = time.time()
            print(f"DEBUG: BackgroundMetricsThread.run() started at {bg_start_time}")
            self.progress_update.emit(0, "Starting background analysis...")

            if self._is_cancelled:
                return

            worker1 = ParallelMetricsWorker(
                polydata=self.polydata1,
                threshold_id=1,
                progress_callback=self._handle_progress,
                completion_callback=self._handle_completion,
                error_callback=self._handle_error
            )

            worker2 = ParallelMetricsWorker(
                polydata=self.polydata2,
                threshold_id=2,
                progress_callback=self._handle_progress,
                completion_callback=self._handle_completion,
                error_callback=self._handle_error
            )

            print(f"DEBUG: Starting parallel workers at {time.time()}")
            self.thread_pool.start(worker1)
            self.thread_pool.start(worker2)
            
            print(f"DEBUG: Starting parallel workers at {time.time()}")
            self.thread_pool.start(worker1)
            self.thread_pool.start(worker2)
            
            # The run method now finishes, and the thread will be driven by worker signals
            print(f"DEBUG: BackgroundMetricsThread.run() completed. Workers are running in the background.")

        except Exception as e:
            import traceback
            self.error_occurred.emit(f"Error starting background workers: {e}\n{traceback.format_exc()}")

    def _handle_progress(self, message):
        """Handles progress messages from workers."""
        if "Calculating" in message and "metrics..." not in message:
            with self.lock:
                self.progress_counter += 1
                # Assuming 8 metrics per worker, 16 total. 80% total progress for metrics.
                # 80 / 16 = 5% per metric.
                progress = self.progress_counter * 5
                self.progress_update.emit(progress, message)
        else:
            self.progress_update.emit(-1, message)

    def _handle_completion(self, threshold_id, metrics):
        """Handles completion of a metrics worker."""
        with self.lock:
            if self.completed_count == -1: # Already finished
                return
            
            self.completed_count += 1
            self.metrics_results[threshold_id] = metrics
            self.metrics_complete.emit(threshold_id, metrics)
            
            progress = self.completed_count * 40
            self.progress_update.emit(progress, f"Metrics for T{threshold_id} complete.")
            
            if self.completed_count == 2:
                self._start_classification_phase()

    def _handle_error(self, threshold_id, error_message):
        """Handles errors from a metrics worker."""
        with self.lock:
            if self.completed_count == -1: # Already finished
                return

            self.completed_count += 1
            self.error_results[threshold_id] = error_message
            self.error_occurred.emit(f"Error calculating metrics for T{threshold_id}.")
            
            progress = self.completed_count * 40
            self.progress_update.emit(progress, f"Metrics for T{threshold_id} failed.")
            
            if self.completed_count == 2:
                self._start_classification_phase()

    def _start_classification_phase(self):
        """
        This method is called once all parallel metric workers have finished.
        It handles errors and proceeds with model inference.
        """
        with self.lock:
            self.completed_count = -1 # Mark as finished to prevent re-entry

        if self._is_cancelled:
            return

        if self.error_results:
            full_error = "\n".join(self.error_results.values())
            self.error_occurred.emit(f"Errors during metrics calculation:\n{full_error}")
            return

        try:
            import time
            print(f"DEBUG: Starting classification phase at {time.time()}")
            self.progress_update.emit(80, "Running classification...")
            
            import tifffile
            img_load_start = time.time()
            img = tifffile.imread(self.file_path)
            img_load_end = time.time()
            print(f"DEBUG: Image reloaded for classification in {img_load_end - img_load_start:.3f}s")

            if self._is_cancelled:
                return

            classification_results = {}
            if self.model and self.model_config and self.label_encoder_path:
                classification_start = time.time()
                classification_results = self._run_classification(img)
                classification_end = time.time()
                print(f"DEBUG: Classification completed in {classification_end - classification_start:.3f}s")
            
            print(f"DEBUG: About to emit inference_complete signal at {time.time()}")
            self.inference_complete.emit(classification_results)
            self.progress_update.emit(100, "Background analysis complete.")

        except Exception as e:
            import traceback
            self.error_occurred.emit(f"Classification phase failed: {e}\n{traceback.format_exc()}")

    def _run_classification(self, img):
        """Runs model inference on the image."""
        try:
            print("Starting classification...")
            print(f"Label encoder path: {self.label_encoder_path}")
            label_encoder_classes = np.load(self.label_encoder_path, allow_pickle=True)
            print(f"Loaded label encoder classes: {label_encoder_classes}")

            inference_df = pd.DataFrame({'filepath': [os.path.basename(self.file_path)]})
            print(f"Inference DataFrame: {inference_df}")

            data_config = self.model_config["data"]
            print(f"Model data config: {data_config}")

            datagen = OptimizedImageDataGenerator3D(
                df=inference_df,
                data_dir=os.path.dirname(self.file_path),
                batch_size=1,
                image_size=data_config["image_size"],
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
            print("Data generator created.")

            print("DEBUG: About to get batch from data generator...")
            try:
                batch_images, _ = datagen[0]
                print(f"Batch images shape: {batch_images.shape}")
            except Exception as e:
                print(f"DEBUG: Error getting batch from data generator: {e}")
                raise e

            print("Running model prediction...")
            try:
                predictions = self.model.predict(batch_images, verbose=0)
                print(f"Predictions: {predictions}")
            except Exception as e:
                print(f"DEBUG: Error during model prediction: {e}")
                raise e

            predicted_class_indices = np.argmax(predictions, axis=1)
            confidence_scores = np.max(predictions, axis=1)
            predicted_class_names = [str(label_encoder_classes[i]) for i in predicted_class_indices]
            
            result_dict = {
                'predicted_class': predicted_class_names[0],
                'confidence': confidence_scores[0],
                'probabilities': predictions[0]
            }
            print("DEBUG: About to return classification results...")
            return result_dict
        except Exception as e:
            import traceback
            print(f"Classification failed: {e}")
            traceback.print_exc()
            self.error_occurred.emit(f"Classification failed: {e}")
            return {}

    def cancel(self):
        """Cancels the thread's operation."""
        self._is_cancelled = True
        self.thread_pool.clear()