"""
Secondary Renderers - Fast 2D slice and histogram rendering
Implements efficient secondary rendering components for the streamlined workflow.
Handles 2D slice rendering with contours, histogram rendering with threshold lines,
and loading message display functionality using existing matplotlib canvas components.
"""
import os
import time
import logging
from typing import Tuple, Optional, Any
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QLabel

from ..utils.logging_config import get_logger


class SecondaryRenderers(QObject):
    """
    Secondary rendering components for 2D slices and histograms.
    Provides fast rendering with optimized performance and proper error handling.
    Uses existing matplotlib canvas components from main window.
    """
    
    # Signals for communication with UI
    slice_rendered = pyqtSignal(int, int, int)  # z_slice, threshold1, threshold2
    histogram_rendered = pyqtSignal(int, int)  # threshold1, threshold2
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.logger = get_logger('logic.secondary_renderers')
        
        # Matplotlib components (will be imported dynamically)
        self.plt = None
        self.FigureCanvas = None
        self.Figure = None
        
        # Current state
        self.current_image_data = None
        self.current_z_slice = 0
        
        # UI components (will be set by main window) - reuse existing canvas
        self.canvas = None  # Matplotlib canvas for 2D slice
        self.ax = None  # Matplotlib axes for 2D slice
        self.canvasHist = None  # Matplotlib canvas for histogram
        self.axHist = None  # Matplotlib axes for histogram
        
        # Performance tracking
        self.render_times = {'slice': [], 'histogram': []}
        
        # Cache for histogram data to improve performance
        self._histogram_cache = {}
        self._colorbar_added = {'slice': False, 'histogram': False}
        
        self._init_matplotlib_modules()
        
        self.logger.info("SecondaryRenderers initialized")
    
    def _init_matplotlib_modules(self):
        """Initialize matplotlib modules"""
        # Matplotlib modules removed for performance optimization
        self.plt = None
        self.FigureCanvas = None
        self.Figure = None
        
        self.logger.info("Matplotlib modules deprecated - using pyqtgraph only")
    
    def set_ui_components(self, canvas=None, ax=None, canvasHist=None, axHist=None):
        """
        Set UI components from main window after they are created.
        Reuses existing matplotlib canvas components following ui_rendering_mixin pattern.
        
        Args:
            canvas: Matplotlib canvas for 2D slice rendering
            ax: Matplotlib axes for 2D slice rendering
            canvasHist: Matplotlib canvas for histogram rendering
            axHist: Matplotlib axes for histogram rendering
        """
        try:
            self.canvas = canvas
            self.ax = ax
            self.canvasHist = canvasHist
            self.axHist = axHist
            
            self.logger.info("UI components set in SecondaryRenderers")
            
        except Exception as e:
            error_msg = f"Error setting UI components: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def render_2d_slice(self, image_data: np.ndarray, z_slice: int, thresholds: Tuple[int, int]) -> bool:
        """
        Render 2D slice with contours for the given thresholds.
        Follows the same pattern as _render_2d_slice_with_contours_legacy in ui_rendering_mixin.
        
        Args:
            image_data: Image data as numpy array (3D or 2D)
            z_slice: Z-slice index to render (ignored for 2D images)
            thresholds: Tuple of (threshold1, threshold2) values
            
        Returns:
            True if rendering succeeded, False otherwise
        """
        try:
            start_time = time.time()
            
            # Use pyqtgraph rendering only (matplotlib deprecated)
            return self._render_2d_slice_pyqtgraph(image_data, z_slice, thresholds)
            
        except Exception as e:
            error_msg = f"Error rendering 2D slice: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
    
    def render_histogram(self, image_data: np.ndarray, thresholds: Tuple[int, int]) -> bool:
        """
        Render histogram with threshold lines using pyqtgraph PlotWidget.
        
        Args:
            image_data: Image data as numpy array
            thresholds: Tuple of (threshold1, threshold2) values
            
        Returns:
            True if rendering succeeded, False otherwise
        """
        try:
            start_time = time.time()
            
            # Use pyqtgraph rendering only (matplotlib deprecated)
            return self._render_histogram_pyqtgraph(image_data, thresholds)
            
        except Exception as e:
            error_msg = f"Error rendering histogram: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
    
    def update_thresholds(self, image_data: np.ndarray, threshold1: int, threshold2: int) -> bool:
        """
        Update both 2D slice and histogram displays with new thresholds.
        This method calls the existing render methods to maintain consistency.
        
        Args:
            image_data: Image data as numpy array
            threshold1: First threshold value (nucleus)
            threshold2: Second threshold value (membrane)
            
        Returns:
            True if both displays updated successfully, False otherwise
        """
        try:
            success = True
            
            # Update 2D slice display with new thresholds
            if self.current_image_data is not None:
                # Use stored image data and current z-slice
                slice_success = self.render_2d_slice(
                    self.current_image_data, 
                    self.current_z_slice, 
                    (threshold1, threshold2)
                )
                success = success and slice_success
            else:
                # Use provided image_data with middle z-slice
                z_slice = 0
                if image_data.ndim >= 3:
                    z_slice = image_data.shape[0] // 2
                    if hasattr(self.main_window, 'verticalScrollBarSlide'):
                        z_slice = self.main_window.verticalScrollBarSlide.value()
                
                slice_success = self.render_2d_slice(image_data, z_slice, (threshold1, threshold2))
                success = success and slice_success
            
            # Update histogram display with new thresholds
            hist_success = self.render_histogram(image_data, (threshold1, threshold2))
            success = success and hist_success
            
            if success:
                self.logger.debug(f"Updated secondary renderers with thresholds: T1={threshold1}, T2={threshold2}")
            else:
                self.logger.warning(f"Some secondary renderer updates failed for thresholds: T1={threshold1}, T2={threshold2}")
            
            return success
            
        except Exception as e:
            error_msg = f"Error updating thresholds in secondary renderers: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def show_loading_message(self, component: str, message: str = "Loading..."):
        """
        Show 'Loading...' message for specified component.
        
        Args:
            component: Component name ('slice' or 'histogram')
            message: Loading message to display
        """
        try:
            if component == 'slice' and hasattr(self, 'canvas') and self.canvas is not None:
                # Clear pyqtgraph ImageView and show loading message
                self.canvas.clear()
                import pyqtgraph as pg
                text_item = pg.TextItem(message, color=(0, 0, 255), anchor=(0.5, 0.5))
                text_item.setPos(0.5, 0.5)
                self.canvas.getView().addItem(text_item)
                    
            elif component == 'histogram' and hasattr(self, 'canvasHist') and self.canvasHist is not None:
                # Clear pyqtgraph PlotWidget and show loading message
                self.canvasHist.clear()
                import pyqtgraph as pg
                text_item = pg.TextItem(message, color=(0, 0, 255), anchor=(0.5, 0.5))
                text_item.setPos(0.5, 0.5)
                self.canvasHist.addItem(text_item)
            
            self.logger.debug(f"Showing loading message for {component}: {message}")
            
        except Exception as e:
            error_msg = f"Error showing loading message for {component}: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _render_2d_slice_pyqtgraph(self, image_data: np.ndarray, z_slice: int, thresholds: Tuple[int, int]) -> bool:
        """Render 2D slice using pyqtgraph for faster performance"""
        try:
            start_time = time.time()
            
            if not hasattr(self, 'canvas') or self.canvas is None:
                self.error_occurred.emit("pyqtgraph canvas not available for 2D rendering")
                return False

            if image_data is None or image_data.size == 0:
                self.error_occurred.emit("Invalid image data for pyqtgraph rendering")
                return False

            threshold1, threshold2 = thresholds
            self.current_image_data = image_data
            self.current_z_slice = z_slice
            
            slice_2d = self._extract_2d_slice(image_data, z_slice)
            if slice_2d is None:
                return False

            # Calculate intensity range using 5th and 95th percentiles of the whole 3D image
            if hasattr(self, 'current_image_data') and self.current_image_data is not None:
                # Use the stored full 3D image for percentile calculation
                full_image = self.current_image_data
            else:
                # Fallback to provided image_data
                full_image = image_data
            
            # Calculate percentiles for intensity range
            p5 = np.percentile(full_image, 1)
            p95 = np.percentile(full_image, 99)
            
            # Set levels to [5%, 95%] percentile range for proper contrast
            self.canvas.setImage(slice_2d, autoLevels=False, levels=(p5, p95))
            
            # Clear existing contour items and remove "Slice Viewer" text
            # Use the correct pyqtgraph API to access items in the ViewBox
            viewbox = self.canvas.getView()
            for item in viewbox.allChildren():
                if 'IsocurveItem' in str(type(item)) or 'contour' in str(type(item)).lower():
                    viewbox.removeItem(item)
                elif 'TextItem' in str(type(item)):
                    # Remove any existing text items (like "Slice Viewer")
                    viewbox.removeItem(item)
            
            # Add contours using pyqtgraph
            import pyqtgraph as pg
            PEN_WIDTH = 2
            contour1 = pg.IsocurveItem(level=threshold1, pen=pg.mkPen('cyan', width=PEN_WIDTH))
            contour1.setData(slice_2d)
            self.canvas.getView().addItem(contour1)

            contour2 = pg.IsocurveItem(level=threshold2, pen=pg.mkPen((200, 200, 200), width=PEN_WIDTH))  # Set pen color to gray RGB
            contour2.setData(slice_2d)
            self.canvas.getView().addItem(contour2)
            
            # Add Z-slice title at the top middle of the image
            if image_data.ndim >= 3:
                title_text = pg.TextItem(
                    f'Z-slice: {z_slice}/{image_data.shape[0]-1}',
                    color=(200, 200, 200),
                    anchor=(0.5, 0),
                    border=None,
                    fill=None
                )
                title_text.setFont(pg.QtGui.QFont("Arial", 12, pg.QtGui.QFont.Bold))
                # Position at top center of the image view
                title_text.setPos(slice_2d.shape[1]//2, 0)
                self.canvas.getView().addItem(title_text)
                print(f"Setting text: Z-slice: {z_slice}/{image_data.shape[0]-1}")
            
            render_time = time.time() - start_time
            self.render_times['slice'].append(render_time)
            self.slice_rendered.emit(z_slice, threshold1, threshold2)
            
            self.logger.debug(f"Rendered 2D slice {z_slice} with pyqtgraph in {render_time:.3f}s")
            return True

        except Exception as e:
            error_msg = f"Error in pyqtgraph rendering: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False


    def _extract_2d_slice(self, image_data: np.ndarray, z_slice: int) -> Optional[np.ndarray]:
        """
        Extract 2D slice from image data.
        Follows the same pattern as ui_rendering_mixin._render_2d_slice_with_contours_legacy.
        
        Args:
            image_data: Image data as numpy array
            z_slice: Z-slice index
            
        Returns:
            2D slice as numpy array, or None if extraction failed
        """
        try:
            # Ensure z_slice is within bounds (following ui_rendering_mixin pattern)
            if len(image_data.shape) >= 3:
                # 3D image - extract specific z-slice
                z_max = image_data.shape[0] - 1
                z_slice = max(0, min(z_slice, z_max))
                
                # Update vertical slider range in main window if available
                if (hasattr(self.main_window, 'verticalScrollBarSlide') and 
                    self.main_window.verticalScrollBarSlide):
                    if self.main_window.verticalScrollBarSlide.maximum() != z_max:
                        self.main_window.verticalScrollBarSlide.setRange(0, z_max)
                
                slice_2d = image_data[z_slice, :, :]
            else:
                # For 2D images, use the full image
                slice_2d = image_data
            
            return slice_2d
            
        except Exception as e:
            self.logger.error(f"Error extracting 2D slice: {str(e)}")
            return None
    
    
    
    
    def _calculate_histogram(self, image_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate histogram with optimized bin count.
        
        Args:
            image_data: Image data as numpy array
            
        Returns:
            Tuple of (histogram_data, bin_edges)
        """
        try:
            # Flatten image data
            flat_data = image_data.flatten()
            
            # Calculate optimal number of bins based on data range and size
            data_range = flat_data.max() - flat_data.min()
            optimal_bins = min(256, max(50, int(data_range / 10)))
            
            # Calculate histogram
            hist_data, bin_edges = np.histogram(flat_data, bins=optimal_bins, density=False)
            
            return hist_data, bin_edges
            
        except Exception as e:
            self.logger.error(f"Error calculating histogram: {str(e)}")
            # Return empty histogram as fallback
            return np.array([]), np.array([0, 1])
    
    def _render_histogram_pyqtgraph(self, image_data: np.ndarray, thresholds: Tuple[int, int]) -> bool:
        """Render histogram using pyqtgraph PlotWidget for better performance"""
        try:
            start_time = time.time()
            
            if not hasattr(self, 'canvasHist') or self.canvasHist is None:
                error_msg = "pyqtgraph PlotWidget not available for histogram rendering"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            if image_data is None or image_data.size == 0:
                error_msg = "Invalid image data provided for histogram rendering"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            threshold1, threshold2 = thresholds
            
            # Check cache for histogram data to improve performance
            image_hash = hash(image_data.tobytes())
            if image_hash in self._histogram_cache:
                hist_data, bin_edges = self._histogram_cache[image_hash]
                self.logger.debug("Using cached histogram data")
            else:
                # Calculate histogram with optimized bin count
                hist_data, bin_edges = self._calculate_histogram(image_data)
                self._histogram_cache[image_hash] = (hist_data, bin_edges)
                
                # Limit cache size to prevent memory issues
                if len(self._histogram_cache) > 10:
                    # Remove oldest entry
                    oldest_key = next(iter(self._histogram_cache))
                    del self._histogram_cache[oldest_key]
            
            # Clear previous plot
            self.canvasHist.clear()
            
            # Plot histogram using pyqtgraph
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            # Create histogram curve
            import pyqtgraph as pg
            curve = self.canvasHist.plot(bin_centers, hist_data, pen='k', name='Histogram')
            
            # Add filled histogram area
            self.canvasHist.plot(bin_centers, hist_data, fillLevel=0, fillBrush=(128, 128, 128, 100))
            
            # Add threshold lines with corrected colors
            threshold_line1 = pg.InfiniteLine(
                pos=threshold1,
                angle=90,
                pen=pg.mkPen('c', width=2, style=pg.QtCore.Qt.DashLine),  # Changed to cyan
                label=f'T1: {threshold1}',
                labelOpts={'position': 0.95, 'color': (0, 255, 255), 'fill': (255, 255, 255, 200)}
            )
            self.canvasHist.addItem(threshold_line1)
            
            threshold_line2 = pg.InfiniteLine(
                pos=threshold2,
                angle=90,
                pen=pg.mkPen('gray', width=2, style=pg.QtCore.Qt.DashLine),  # Changed to gray
                label=f'T2: {threshold2}',
                labelOpts={'position': 0.85, 'color': (128, 128, 128), 'fill': (255, 255, 255, 200)}
            )
            self.canvasHist.addItem(threshold_line2)
            
            # Set labels and title with darker colors
            self.canvasHist.setLabel('left', 'Frequency', color=(64, 64, 64))  # Dark gray
            self.canvasHist.setLabel('bottom', 'Intensity', color=(64, 64, 64))  # Dark gray
            self.canvasHist.setTitle('Image Histogram with Thresholds', color=(32, 32, 32))  # Darker gray/black
            self.canvasHist.showGrid(x=True, y=True, alpha=0.3)
            
            # Set x-axis range to [0, max_image_intensity * 1.05]
            max_intensity = int(np.max(image_data))
            self.canvasHist.setXRange(0, max_intensity * 1.05)
            
            # Use log scale for the y-axis
            self.canvasHist.setLogMode(x=False, y=True)
            
            # Performance tracking
            render_time = time.time() - start_time
            self.render_times['histogram'].append(render_time)
            
            # Emit signals
            self.histogram_rendered.emit(threshold1, threshold2)
            
            self.logger.debug(f"Rendered histogram with pyqtgraph in {render_time:.3f}s")
            return True
            
        except Exception as e:
            error_msg = f"Error in pyqtgraph histogram rendering: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False



    def update_z_slice(self, z_slice: int):
        """
        Update the current z-slice and re-render if image data is available.
        
        Args:
            z_slice: New z-slice index
        """
        try:
            if (self.current_image_data is not None and
                hasattr(self.main_window, 'horizontalSlider_intensity1') and
                hasattr(self.main_window, 'horizontalSlider_intensity2')):
                
                threshold1 = self.main_window.horizontalSlider_intensity1.value()
                threshold2 = self.main_window.horizontalSlider_intensity2.value()
                
                self.render_2d_slice(self.current_image_data, z_slice, (threshold1, threshold2))
                
        except Exception as e:
            error_msg = f"Error updating z-slice: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def clear_displays(self):
        """Clear both 2D slice and histogram displays"""
        try:
            # Clear pyqtgraph displays
            if hasattr(self, 'canvas') and self.canvas is not None:
                self.canvas.clear()
            
            if hasattr(self, 'canvasHist') and self.canvasHist is not None:
                self.canvasHist.clear()
            
            # Reset colorbar flags
            self._colorbar_added = {'slice': False, 'histogram': False}
            
            self.logger.debug("Cleared secondary rendering displays")
            
        except Exception as e:
            self.logger.error(f"Error clearing displays: {str(e)}")
    
    def get_performance_stats(self) -> dict:
        """
        Get performance statistics for monitoring.
        
        Returns:
            Dictionary containing performance statistics
        """
        try:
            stats = {}
            
            for component in ['slice', 'histogram']:
                times = self.render_times[component]
                if times:
                    stats[f'{component}_renders'] = len(times)
                    stats[f'{component}_avg_time'] = np.mean(times)
                    stats[f'{component}_min_time'] = np.min(times)
                    stats[f'{component}_max_time'] = np.max(times)
                    stats[f'{component}_last_time'] = times[-1]
                else:
                    stats[f'{component}_renders'] = 0
                    stats[f'{component}_avg_time'] = 0
                    stats[f'{component}_min_time'] = 0
                    stats[f'{component}_max_time'] = 0
                    stats[f'{component}_last_time'] = 0
            
            stats['cache_size'] = len(self._histogram_cache)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {str(e)}")
            return {}
    
    def cleanup(self):
        """Clean up resources and clear current state"""
        try:
            # Clear current state
            self.current_image_data = None
            self.current_z_slice = 0
            
            # Clear performance tracking
            self.render_times = {'slice': [], 'histogram': []}
            
            # Clear histogram cache
            self._histogram_cache.clear()
            
            # Reset colorbar flags
            self._colorbar_added = {'slice': False, 'histogram': False}
            
            # Clear displays
            self.clear_displays()
            
            self.logger.info("SecondaryRenderers cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")