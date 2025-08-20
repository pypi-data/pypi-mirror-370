"""
UI Data Mixin for the MainWindow.
Handles data management operations including database updates and threshold calculations.
"""
import os
import numpy as np
import pandas as pd
from PyQt5.QtCore import QTimer

class UiDataMixin:
    """Mixin containing data management methods for MainWindow."""

    def _get_or_calculate_thresholds(self, path):
        """Get or calculate threshold values for the image, checking measurement DB first"""
        try:
            filename = os.path.basename(path)
            
            # Check if thresholds exist in measurement database
            if hasattr(self, 'result_db') and not self.result_db.empty:
                existing_record = self.result_db[self.result_db['Path'] == path]
                if not existing_record.empty:
                    # Extract existing threshold values
                    if 'threshold1' in self.result_db.columns and 'threshold2' in self.result_db.columns:
                        threshold1 = int(existing_record.iloc[0]['threshold1'])
                        threshold2 = int(existing_record.iloc[0]['threshold2'])
                        self._show_progress(80, f"Using cached thresholds: T1={threshold1}, T2={threshold2}")
                        self.logger.info(f"Using cached thresholds for {filename}: T1={threshold1}, T2={threshold2}")
                        return threshold1, threshold2
            
            # Calculate new thresholds
            self._show_progress(75, "Calculating optimal thresholds...")
            threshold1 = int(np.mean(self.img))
            threshold2 = int(np.percentile(self.img, 2))
            
            # Store thresholds in measurement database for future use
            self._store_thresholds_in_db(path, threshold1, threshold2)
            
            self._show_progress(85, f"Thresholds calculated: T1={threshold1} (mean), T2={threshold2} (2nd percentile)")
            self.logger.info(f"Calculated new thresholds for {filename}: T1={threshold1}, T2={threshold2}")
            
            return threshold1, threshold2
            
        except Exception as e:
            self.logger.error(f"Error getting/calculating thresholds for {path}: {e}")
            # Fallback to simple calculations
            threshold1 = int(np.mean(self.img)) if self.img is not None else 1000
            threshold2 = int(np.percentile(self.img, 2)) if self.img is not None else 100
            return threshold1, threshold2

    def _store_thresholds_in_db(self, path, threshold1, threshold2):
        """Store calculated thresholds in measurement database"""
        try:
            filename = os.path.basename(path)
            
            # Create or update record in result_db
            new_record = {
                'ImageName': filename,
                'Path': path,
                'threshold1': threshold1,
                'threshold2': threshold2,
                # Add other default values as needed
                'ManualAnnotation': '',
                'Predicted_Class': '',  # Add Predicted_Class column
                'Model': '',
                'ClassProb_M': np.nan, 'ClassProb_MM': np.nan, 'ClassProb_BN': np.nan, 'ClassProb_SN': np.nan,
                'MaturationScore': np.nan,
                'Area_1': np.nan, 'Vol_1': np.nan, 'NSI_1': np.nan, 'Sphericity_1': np.nan, 'SA_Vol_Ratio_1': np.nan, 'Solidity_1': np.nan, 'Elongation_1': np.nan, 'Genus_1': np.nan,
                'Area_2': np.nan, 'Vol_2': np.nan, 'NSI_2': np.nan, 'Sphericity_2': np.nan, 'SA_Vol_Ratio_2': np.nan, 'Solidity_2': np.nan, 'Elongation_2': np.nan, 'Genus_2': np.nan
            }
            
            # Check if record already exists
            existing_idx = self.result_db[self.result_db['Path'] == path].index
            if not existing_idx.empty:
                # Update existing record
                for key, value in new_record.items():
                    if key in ['threshold1', 'threshold2']:  # Only update threshold values
                        self.result_db.loc[existing_idx[0], key] = value
            else:
                # Add new record
                self.result_db = pd.concat([self.result_db, pd.DataFrame([new_record])], ignore_index=True)
                
            self.logger.debug(f"Stored thresholds in database for {filename}")
            
        except Exception as e:
            self.logger.warning(f"Failed to store thresholds in database: {e}")

    def _update_db_with_metrics(self, path, metrics, label_suffix):
        """Update the database with calculated metrics."""
        try:
            self.logger.debug(f"Geometry metrics received for suffix '{label_suffix}'")
            
            filename = os.path.basename(path)
            
            # Find the record in the database
            existing_idx = self.result_db[self.result_db['Path'] == path].index
            if existing_idx.empty:
                self.logger.warning(f"No record found in result_db for {filename}. Cannot update metrics.")
                return

            record_idx = existing_idx[0]

            # Prepare the update data
            update_data = {}

            # Add metrics with the correct suffix (e.g., 'Area_1', 'Vol_1')
            # Special handling for keys that don't follow simple capitalization
            for key, value in metrics.items():
                if key == 'nsi':
                    col_name = f"NSI{label_suffix}"
                elif key == 'sa_vol_ratio':
                    col_name = f"SA_Vol_Ratio{label_suffix}"
                else:
                    col_name = f"{key.capitalize()}{label_suffix}"
                update_data[col_name] = value

            # Also update the threshold value for the corresponding suffix
            if label_suffix == "_1":
                update_data['threshold1'] = self.horizontalSlider_intensity1.value()
            elif label_suffix == "_2":
                update_data['threshold2'] = self.horizontalSlider_intensity2.value()

            # Update the DataFrame
            for key, value in update_data.items():
                if key in self.result_db.columns:
                    self.result_db.loc[record_idx, key] = value
            
            self.logger.info(f"Updated geometry metrics for {label_suffix} in database for {filename}")

            # Update any open feature windows
            self.update_feature_windows()

        except Exception as e:
            self.logger.error(f"Error updating geometry in database from signal: {e}")

    def update_annotation_in_db(self, path, annotation):
        """Update manual annotation in the database."""
        try:
            # Find the record in the database
            existing_idx = self.result_db[self.result_db['Path'] == path].index
            if not existing_idx.empty:
                record_idx = existing_idx[0]
                self.result_db.loc[record_idx, 'ManualAnnotation'] = annotation
                self.logger.info(f"Updated manual annotation for {os.path.basename(path)} to '{annotation}'")
                self.update_feature_windows()
            else:
                self.logger.warning(f"No record found for {os.path.basename(path)} to update annotation.")

        except Exception as e:
            self.logger.error(f"Error updating manual annotation: {e}")

    def update_feature_windows(self):
        """
        Update both geometric and embedded feature windows if they are open.
        This serves as a centralized method to refresh UI components that depend on result_db.
        """
        print("DEBUG: update_feature_windows called")
        self.logger.debug("Attempting to update feature windows.")
        
        try:
            print("DEBUG: Checking geometric features window...")
            if self.geometric_features_window and self.geometric_features_window.isVisible():
                print("DEBUG: Updating geometric features window...")
                self.logger.debug("Updating geometric features window.")
                self.geometric_features_window.update_data_and_render(self.result_db)
                print("DEBUG: Geometric features window updated")
            else:
                print("DEBUG: Geometric features window not available or not visible")
            
            print("DEBUG: Checking embedded features window...")
            if self.embedded_features_window and self.embedded_features_window.isVisible():
                print("DEBUG: Updating embedded features window...")
                self.logger.debug("Updating embedded features window.")
                self.embedded_features_window.update_data_and_render(self.result_db)
                print("DEBUG: Embedded features window updated")
            else:
                print("DEBUG: Embedded features window not available or not visible")
                
            # Also refresh the main window's annotation combobox
            if hasattr(self, '_refresh_annotation_ui'):
                self._refresh_annotation_ui()

            print("DEBUG: Feature windows update check completed")
            self.logger.debug("Feature windows update check completed.")
            
        except Exception as e:
            print(f"DEBUG: Exception in update_feature_windows: {e}")
            import traceback
            traceback.print_exc()
            self.logger.error(f"Error updating feature windows: {e}", exc_info=True)
            raise e

    def _on_geometry_metrics_calculated(self, metrics, label_suffix):
        """Handle successful geometry metrics calculation and update the database."""
        if hasattr(self, 'files') and self.listWidget.currentRow() >= 0:
            self._update_db_with_metrics(self.files[self.listWidget.currentRow()], metrics, label_suffix)

    def _update_db_with_classification(self, path, classification_results):
        """Update the database with classification results."""
        print(f"DEBUG: _update_db_with_classification called with path: {path}")
        print(f"DEBUG: Classification results: {classification_results}")
        try:
            filename = os.path.basename(path)
            print(f"DEBUG: Filename: {filename}")
            existing_idx = self.result_db[self.result_db['Path'] == path].index
            print(f"DEBUG: Existing index: {existing_idx}")
            if existing_idx.empty:
                self.logger.warning(f"No record found in result_db for {filename}. Cannot update classification results.")
                return

            record_idx = existing_idx[0]
            print(f"DEBUG: Record index: {record_idx}")
            
            print("DEBUG: About to update Model field...")
            self.result_db.loc[record_idx, 'Model'] = self.comboBoxModel.currentText()
            print("DEBUG: About to update Predicted_Class field...")
            self.result_db.loc[record_idx, 'Predicted_Class'] = classification_results.get('predicted_class')
            print("DEBUG: About to update confidence field...")
            self.result_db.loc[record_idx, 'confidence'] = classification_results.get('confidence')
            print("DEBUG: Basic fields updated")

            # Assuming probabilities are ordered M, MM, BN, SN
            print("DEBUG: About to update probabilities...")
            if 'probabilities' in classification_results:
                probs = classification_results['probabilities']
                print(f"DEBUG: Probabilities array: {probs}")
                print(f"DEBUG: Probabilities length: {len(probs)}")
                self.result_db.loc[record_idx, 'ClassProb_M'] = probs[0] if len(probs) > 0 else np.nan
                self.result_db.loc[record_idx, 'ClassProb_MM'] = probs[1] if len(probs) > 1 else np.nan
                self.result_db.loc[record_idx, 'ClassProb_BN'] = probs[2] if len(probs) > 2 else np.nan
                self.result_db.loc[record_idx, 'ClassProb_SN'] = probs[3] if len(probs) > 3 else np.nan
                
                # Calculate and store maturation score
                if len(probs) >= 4:
                    maturation_weights = [0.0, 0.33, 0.67, 1.0]
                    maturation_score = sum(prob * weight for prob, weight in zip(probs, maturation_weights))
                    self.result_db.loc[record_idx, 'MaturationScore'] = maturation_score
                    print(f"DEBUG: Maturation score calculated and stored: {maturation_score:.3f}")
                else:
                    self.result_db.loc[record_idx, 'MaturationScore'] = np.nan
                    print("DEBUG: Not enough probabilities for maturation score")
                
                print("DEBUG: Probabilities updated")
            else:
                print("DEBUG: No probabilities in classification results")

            self.logger.info(f"Updated classification results in database for {filename}")
            print("DEBUG: About to call update_feature_windows...")
            self.update_feature_windows()
            print("DEBUG: update_feature_windows completed")
            print("DEBUG: _update_db_with_classification completed successfully")

        except Exception as e:
            print(f"DEBUG: Exception in _update_db_with_classification: {e}")
            import traceback
            traceback.print_exc()
            self.logger.error(f"Error updating classification results in database: {e}")
            raise e

    def _discover_models_sync(self):
        """Synchronously discover available models on main thread"""
        models = []
        configs = []

        # Corrected path to point to the root 'models' directory
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')

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