"""
UI State Manager - Manages UI element states during loading operations
Implements concurrent loading prevention through UI state control.
"""
import logging
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QLabel, QSlider, QSpinBox

from ..utils.logging_config import get_logger


class UIStateManager(QObject):
    """
    Manages UI element enable/disable functionality during loading operations.
    Prevents concurrent loading by controlling UI state transitions.
    """
    
    # Signals for state change notifications
    loading_state_changed = pyqtSignal(bool)  # is_loading
    ui_elements_updated = pyqtSignal(str)  # status_message
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.logger = get_logger('logic.ui_state_manager')
        
        # Current state
        self.is_loading = False
        self.loading_message = ""
        
        # UI element references (will be populated from main window)
        self.ui_elements = {
            'list_widget': None,
            'image_selection_buttons': [],
            'threshold_sliders': [],
            'threshold_spinboxes': [],
            'loading_label': None,
            'menu_items': [],
            'other_controls': []
        }
        
        # State history for debugging
        self.state_changes = []
        
        self._discover_ui_elements()
        
        self.logger.info("UIStateManager initialized")
    
    def _discover_ui_elements(self):
        """Discover and cache references to UI elements from main window"""
        try:
            # List widget for image selection
            if hasattr(self.main_window, 'listWidget'):
                self.ui_elements['list_widget'] = self.main_window.listWidget
            
            # Image selection buttons
            image_buttons = []
            if hasattr(self.main_window, 'pushButton_Images'):
                image_buttons.append(self.main_window.pushButton_Images)
            if hasattr(self.main_window, 'pushButton_ImageFolder'):
                image_buttons.append(self.main_window.pushButton_ImageFolder)
            if hasattr(self.main_window, 'selectImagesButton'):
                image_buttons.append(self.main_window.selectImagesButton)
            if hasattr(self.main_window, 'selectFolderButton'):
                image_buttons.append(self.main_window.selectFolderButton)
            self.ui_elements['image_selection_buttons'] = image_buttons
            
            # Threshold sliders
            threshold_sliders = []
            if hasattr(self.main_window, 'horizontalSlider_intensity1'):
                threshold_sliders.append(self.main_window.horizontalSlider_intensity1)
            if hasattr(self.main_window, 'horizontalSlider_intensity2'):
                threshold_sliders.append(self.main_window.horizontalSlider_intensity2)
            self.ui_elements['threshold_sliders'] = threshold_sliders
            
            # Threshold spinboxes
            threshold_spinboxes = []
            if hasattr(self.main_window, 'spinBox_intensity1'):
                threshold_spinboxes.append(self.main_window.spinBox_intensity1)
            if hasattr(self.main_window, 'spinBox_intensity2'):
                threshold_spinboxes.append(self.main_window.spinBox_intensity2)
            self.ui_elements['threshold_spinboxes'] = threshold_spinboxes
            
            # Loading indicator label
            if hasattr(self.main_window, 'progress_label'):
                self.ui_elements['loading_label'] = self.main_window.progress_label
            elif hasattr(self.main_window, 'loadingLabel'):
                self.ui_elements['loading_label'] = self.main_window.loadingLabel
            elif hasattr(self.main_window, 'statusBar'):
                # Use status bar as loading indicator if no dedicated label
                self.ui_elements['loading_label'] = self.main_window.statusBar()
            
            # Other controls that should be disabled during loading
            other_controls = []
            if hasattr(self.main_window, 'verticalScrollBarSlide'):
                other_controls.append(self.main_window.verticalScrollBarSlide)
            self.ui_elements['other_controls'] = other_controls
            
            discovered_count = sum(1 if elem else 0 for elem in [
                self.ui_elements['list_widget'],
                self.ui_elements['loading_label']
            ]) + sum(len(elem_list) for elem_list in [
                self.ui_elements['image_selection_buttons'],
                self.ui_elements['threshold_sliders'],
                self.ui_elements['threshold_spinboxes'],
                self.ui_elements['other_controls']
            ])
            
            self.logger.info(f"Discovered {discovered_count} UI elements for state management")
            
        except Exception as e:
            self.logger.error(f"Error discovering UI elements: {str(e)}")
    
    def set_loading_state(self, loading: bool, message: str = ""):
        """
        Set the loading state and update UI elements accordingly.
        
        Args:
            loading: True if loading should be enabled, False to disable
            message: Optional loading message to display
        """
        try:
            # Prevent redundant state changes
            if self.is_loading == loading and self.loading_message == message:
                return
            
            previous_state = self.is_loading
            self.is_loading = loading
            self.loading_message = message if message else (
                "Loading image..." if loading else "Ready"
            )
            
            # Record state change for debugging
            self.state_changes.append({
                'timestamp': self._get_timestamp(),
                'from_loading': previous_state,
                'to_loading': loading,
                'message': self.loading_message
            })
            
            # Update UI elements based on loading state
            if loading:
                self._enable_loading_state()
            else:
                self._disable_loading_state()
            
            # Emit state change signal
            self.loading_state_changed.emit(loading)
            self.ui_elements_updated.emit(self.loading_message)
            
            self.logger.debug(f"Loading state changed: {previous_state} -> {loading} ('{self.loading_message}')")
            
        except Exception as e:
            error_msg = f"Error setting loading state: {str(e)}"
            self.logger.error(error_msg)
    
    def _enable_loading_state(self):
        """Enable loading state - disable UI elements and show loading indicator"""
        try:
            # Disable list widget to prevent selection changes
            if self.ui_elements['list_widget']:
                self.ui_elements['list_widget'].setEnabled(False)
                self.logger.debug("List widget disabled")
            
            # Disable image selection buttons
            for button in self.ui_elements['image_selection_buttons']:
                if button:
                    button.setEnabled(False)
            if self.ui_elements['image_selection_buttons']:
                self.logger.debug(f"Disabled {len(self.ui_elements['image_selection_buttons'])} image selection buttons")
            
            # Keep threshold sliders enabled (per requirements)
            # Users should be able to adjust thresholds during loading
            
            # Disable other controls
            for control in self.ui_elements['other_controls']:
                if control:
                    control.setEnabled(False)
            if self.ui_elements['other_controls']:
                self.logger.debug(f"Disabled {len(self.ui_elements['other_controls'])} other controls")
            
            # Show loading indicator
            self._show_loading_indicator()
            
        except Exception as e:
            self.logger.error(f"Error enabling loading state: {str(e)}")
    
    def _disable_loading_state(self):
        """Disable loading state - re-enable UI elements and hide loading indicator"""
        try:
            # Re-enable list widget
            if self.ui_elements['list_widget']:
                self.ui_elements['list_widget'].setEnabled(True)
                self.logger.debug("List widget enabled")
            
            # Re-enable image selection buttons
            for button in self.ui_elements['image_selection_buttons']:
                if button:
                    button.setEnabled(True)
            if self.ui_elements['image_selection_buttons']:
                self.logger.debug(f"Enabled {len(self.ui_elements['image_selection_buttons'])} image selection buttons")
            
            # Re-enable other controls
            for control in self.ui_elements['other_controls']:
                if control:
                    control.setEnabled(True)
            if self.ui_elements['other_controls']:
                self.logger.debug(f"Enabled {len(self.ui_elements['other_controls'])} other controls")
            
            # Hide loading indicator
            self._hide_loading_indicator()
            
        except Exception as e:
            self.logger.error(f"Error disabling loading state: {str(e)}")
    
    def _show_loading_indicator(self):
        """Show loading indicator with current message"""
        try:
            loading_label = self.ui_elements['loading_label']
            
            if loading_label:
                if hasattr(loading_label, 'setText'):
                    # Regular QLabel
                    loading_label.setText(self.loading_message)
                    if hasattr(loading_label, 'setVisible'):
                        loading_label.setVisible(True)
                elif hasattr(loading_label, 'showMessage'):
                    # Status bar
                    loading_label.showMessage(self.loading_message)
                
                self.logger.debug(f"Loading indicator shown: '{self.loading_message}'")
            else:
                self.logger.debug("No loading indicator available")
                
        except Exception as e:
            self.logger.error(f"Error showing loading indicator: {str(e)}")
    
    def _hide_loading_indicator(self):
        """Hide loading indicator"""
        try:
            loading_label = self.ui_elements['loading_label']
            
            if loading_label:
                if hasattr(loading_label, 'setText') and hasattr(loading_label, 'setVisible'):
                    # Regular QLabel
                    loading_label.setText("Ready")
                    loading_label.setVisible(False)
                elif hasattr(loading_label, 'showMessage'):
                    # Status bar
                    loading_label.showMessage("Ready")
                
                self.logger.debug("Loading indicator hidden")
            
        except Exception as e:
            self.logger.error(f"Error hiding loading indicator: {str(e)}")
    
    def can_load_image(self) -> bool:
        """
        Check if image loading is allowed (not currently loading).
        
        Returns:
            True if loading is allowed, False if currently loading
        """
        return not self.is_loading
    
    def force_reset_state(self):
        """Force reset to ready state - use for error recovery"""
        try:
            self.logger.warning("Force resetting UI state to ready")
            self.set_loading_state(False, "Ready")
        except Exception as e:
            self.logger.error(f"Error force resetting state: {str(e)}")
    
    def set_progress_message(self, message: str):
        """
        Update the progress message without changing loading state.
        
        Args:
            message: Progress message to display
        """
        try:
            if self.is_loading:
                self.loading_message = message
                self._show_loading_indicator()
                self.ui_elements_updated.emit(message)
                self.logger.debug(f"Progress message updated: '{message}'")
            
        except Exception as e:
            self.logger.error(f"Error setting progress message: {str(e)}")
    
    def add_custom_ui_element(self, element: QWidget, element_type: str = 'other_controls'):
        """
        Add a custom UI element to be managed.
        
        Args:
            element: QWidget to be managed
            element_type: Type of element ('image_selection_buttons', 'threshold_sliders', etc.)
        """
        try:
            if element_type in self.ui_elements:
                if isinstance(self.ui_elements[element_type], list):
                    self.ui_elements[element_type].append(element)
                else:
                    # Convert single element to list
                    current = self.ui_elements[element_type]
                    self.ui_elements[element_type] = [current, element] if current else [element]
                
                self.logger.debug(f"Added custom UI element to {element_type}")
            else:
                self.logger.warning(f"Unknown element type: {element_type}")
                
        except Exception as e:
            self.logger.error(f"Error adding custom UI element: {str(e)}")
    
    def get_state_history(self) -> List[dict]:
        """
        Get the history of state changes for debugging.
        
        Returns:
            List of state change records
        """
        return self.state_changes.copy()
    
    def clear_state_history(self):
        """Clear the state change history"""
        self.state_changes.clear()
        self.logger.debug("State history cleared")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for state change tracking"""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    def get_ui_element_status(self) -> dict:
        """
        Get current status of all managed UI elements.
        
        Returns:
            Dictionary containing element status information
        """
        try:
            status = {
                'is_loading': self.is_loading,
                'loading_message': self.loading_message,
                'elements': {}
            }
            
            # Check list widget
            if self.ui_elements['list_widget']:
                status['elements']['list_widget'] = {
                    'enabled': self.ui_elements['list_widget'].isEnabled(),
                    'visible': self.ui_elements['list_widget'].isVisible()
                }
            
            # Check image selection buttons
            enabled_buttons = 0
            total_buttons = len(self.ui_elements['image_selection_buttons'])
            for button in self.ui_elements['image_selection_buttons']:
                if button and button.isEnabled():
                    enabled_buttons += 1
            
            status['elements']['image_selection_buttons'] = {
                'total': total_buttons,
                'enabled': enabled_buttons
            }
            
            # Check threshold controls
            enabled_sliders = 0
            total_sliders = len(self.ui_elements['threshold_sliders'])
            for slider in self.ui_elements['threshold_sliders']:
                if slider and slider.isEnabled():
                    enabled_sliders += 1
            
            status['elements']['threshold_sliders'] = {
                'total': total_sliders,
                'enabled': enabled_sliders
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting UI element status: {str(e)}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Clean up resources and reset state"""
        try:
            # Force reset to ready state
            if self.is_loading:
                self.set_loading_state(False, "Ready")
            
            # Clear state history
            self.clear_state_history()
            
            # Clear UI element references
            for key in self.ui_elements:
                if isinstance(self.ui_elements[key], list):
                    self.ui_elements[key].clear()
                else:
                    self.ui_elements[key] = None
            
            self.logger.info("UIStateManager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")