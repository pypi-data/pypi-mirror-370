#!/usr/bin/env python3
"""
Preferences handler for the Neutrophils Classifier Application.
Manages preferences logic while the UI design is handled by preferences.ui
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from PyQt5.QtCore import pyqtSignal, QObject


class PreferencesManager(QObject):
    """Manager for application preferences persistence and logic"""
    
    preferences_changed = pyqtSignal(dict)  # Emitted when preferences change
    
    def __init__(self, config_file_path: Optional[str] = None):
        super().__init__()
        if config_file_path is None:
            # Default to app directory
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_file_path = os.path.join(app_dir, 'app_preferences.json')
        
        self.config_file_path = config_file_path
        self.logger = logging.getLogger(__name__)
        self._current_preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from file"""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as f:
                    preferences = json.load(f)
                self.logger.info(f"Loaded preferences from {self.config_file_path}")
                return self._validate_preferences(preferences)
            else:
                self.logger.info("No preferences file found, using defaults")
                return self._get_default_preferences()
        except Exception as e:
            self.logger.warning(f"Failed to load preferences: {e}, using defaults")
            return self._get_default_preferences()
    
    def save_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Save preferences to file"""
        try:
            # Validate before saving
            preferences = self._validate_preferences(preferences)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            
            with open(self.config_file_path, 'w') as f:
                json.dump(preferences, f, indent=2)
            
            self._current_preferences = preferences
            self.preferences_changed.emit(preferences)
            
            self.logger.info(f"Saved preferences to {self.config_file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save preferences: {e}")
            return False
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get current preferences"""
        return self._current_preferences.copy()
    
    def get_auto_processing_config(self) -> Dict[str, Any]:
        """Get auto-processing configuration for EnhancedDataLoader"""
        auto_prefs = self._current_preferences.get('auto_processing', {})
        return {
            'auto_processing_enabled': auto_prefs.get('enabled', False),
            'auto_load_model': auto_prefs.get('auto_load_model', True),
            'auto_inference': auto_prefs.get('auto_inference', True),
            'auto_save_results': auto_prefs.get('auto_save_results', False),
            'batch_size': auto_prefs.get('batch_size', 5),
            'cache_enabled': auto_prefs.get('cache_enabled', True),
            'cache_size_mb': auto_prefs.get('cache_size_mb', 512),
            'max_concurrent_tasks': auto_prefs.get('max_concurrent_tasks', 3),
            'progress_update_interval': auto_prefs.get('progress_update_interval', 100)
        }
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences"""
        return {
            # General settings
            'pixel_size_x': 0.145,
            'pixel_size_y': 0.145,
            'pixel_size_z': 0.145,
            
            # Auto-processing settings
            'auto_processing': {
                'enabled': False,
                'auto_load_model': True,
                'auto_inference': True,
                'auto_save_results': False,
                'batch_size': 5,
                'max_concurrent_tasks': 3,
                'cache_enabled': True,
                'cache_size_mb': 512,
                'progress_update_interval': 100
            }
        }
    
    def _validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize preferences"""
        default_prefs = self._get_default_preferences()
        
        # Ensure all required sections exist
        if 'auto_processing' not in preferences:
            preferences['auto_processing'] = default_prefs['auto_processing']
        
        # Validate general settings
        preferences['pixel_size_x'] = max(0.01, min(20.0, preferences.get('pixel_size_x', 0.145)))
        preferences['pixel_size_y'] = max(0.01, min(20.0, preferences.get('pixel_size_y', 0.145)))
        preferences['pixel_size_z'] = max(0.01, min(20.0, preferences.get('pixel_size_z', 0.145)))
        
        # Validate auto-processing settings
        auto_prefs = preferences['auto_processing']
        auto_defaults = default_prefs['auto_processing']
        
        for key, default_value in auto_defaults.items():
            if key not in auto_prefs:
                auto_prefs[key] = default_value
        
        # Validate numeric ranges
        auto_prefs['batch_size'] = max(1, min(20, auto_prefs.get('batch_size', 5)))
        auto_prefs['max_concurrent_tasks'] = max(1, min(10, auto_prefs.get('max_concurrent_tasks', 3)))
        auto_prefs['cache_size_mb'] = max(128, min(8192, auto_prefs.get('cache_size_mb', 1024)))
        auto_prefs['progress_update_interval'] = max(50, min(1000, auto_prefs.get('progress_update_interval', 100)))
        
        return preferences
    
    def load_ui_values(self, ui_dialog):
        """Load preference values into UI dialog controls"""
        try:
            # General settings
            ui_dialog.doubleSpinBoxPixelSizeX.setValue(self._current_preferences.get('pixel_size_x', 0.145))
            ui_dialog.doubleSpinBoxPixelSizeY.setValue(self._current_preferences.get('pixel_size_y', 0.145))
            ui_dialog.doubleSpinBoxPixelSizeZ.setValue(self._current_preferences.get('pixel_size_z', 0.145))

            # Batch processing settings
            auto_prefs = self._current_preferences.get('auto_processing', {})
            ui_dialog.spinBoxBatchSize.setValue(auto_prefs.get('batch_size', 5))

        except Exception as e:
            self.logger.error(f"Failed to load UI values: {e}")
    
    def save_ui_values(self, ui_dialog) -> bool:
        """Save UI dialog values to preferences"""
        try:
            prefs_to_update = self.get_preferences()

            # Update general settings from UI
            prefs_to_update['pixel_size_x'] = ui_dialog.doubleSpinBoxPixelSizeX.value()
            prefs_to_update['pixel_size_y'] = ui_dialog.doubleSpinBoxPixelSizeY.value()
            prefs_to_update['pixel_size_z'] = ui_dialog.doubleSpinBoxPixelSizeZ.value()

            # Update batch processing settings from UI
            if 'auto_processing' not in prefs_to_update:
                prefs_to_update['auto_processing'] = {}

            prefs_to_update['auto_processing']['batch_size'] = ui_dialog.spinBoxBatchSize.value()

            return self.save_preferences(prefs_to_update)

        except Exception as e:
            self.logger.error(f"Failed to save UI values: {e}")
            return False
    
    def setup_ui_connections(self, ui_dialog):
        """Setup UI signal connections for dynamic behavior"""
        try:
            # No dynamic connections needed in the simplified UI
            pass
        except Exception as e:
            self.logger.error(f"Failed to setup UI connections: {e}")