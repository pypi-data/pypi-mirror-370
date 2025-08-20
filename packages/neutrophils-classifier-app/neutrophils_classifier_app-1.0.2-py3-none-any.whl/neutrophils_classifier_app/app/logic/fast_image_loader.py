"""
Fast Image Loader - Efficient image loading with cache integration
Handles fast image loading, threshold calculation, and error handling
for the streamlined workflow.
"""
import os
import logging
import time
from typing import Tuple, Optional, Dict, Any
import numpy as np
import tifffile
from PyQt5.QtCore import QObject, pyqtSignal

from ..utils.logging_config import get_logger
from .frontend_cache_manager import get_frontend_cache_manager


class FastImageLoader(QObject):
    """
    Efficient image loader with cache integration for the streamlined workflow.
    Provides fast image loading, threshold calculation, and robust error handling.
    """
    
    # Signals for error reporting
    error_occurred = pyqtSignal(str)  # error_message
    loading_progress = pyqtSignal(str)  # progress_message
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger('logic.fast_image_loader')
        
        # Get cache manager
        self.cache_manager = get_frontend_cache_manager()
        self.cache_loader = self.cache_manager.get_loader()
        
        # Statistics for performance monitoring
        self.stats = {
            'images_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'load_times': [],
            'threshold_calc_times': []
        }
        
        self.logger.info("FastImageLoader initialized")
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load image using cache when available.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image data as numpy array, or None if loading failed
        """
        try:
            start_time = time.time()
            
            # Validate file path
            if not os.path.exists(image_path):
                error_msg = f"Image file not found: {image_path}"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return None
            
            # Check file size for memory management
            file_size = os.path.getsize(image_path)
            if file_size > 500 * 1024 * 1024:  # 500MB limit
                self.logger.warning(f"Large file detected: {file_size / (1024*1024):.1f}MB - {image_path}")
                # Could add additional memory management here if needed
            
            self.loading_progress.emit(f"Loading {os.path.basename(image_path)}...")
            
            # Try to load from cache first
            cached_data = self.cache_loader.cache.get(image_path)
            if cached_data is not None:
                self.stats['cache_hits'] += 1
                load_time = time.time() - start_time
                self.stats['load_times'].append(load_time)
                self.logger.debug(f"Cache hit for {os.path.basename(image_path)} - {load_time:.3f}s")
                return cached_data
            
            # Load from disk
            self.stats['cache_misses'] += 1
            image_data = self._load_from_disk(image_path)
            
            if image_data is not None:
                # Store in cache
                self.cache_loader.cache.put(image_path, image_data)
                
                # Update statistics
                load_time = time.time() - start_time
                self.stats['load_times'].append(load_time)
                self.stats['images_loaded'] += 1
                
                self.logger.info(f"Loaded {os.path.basename(image_path)} - "
                                f"Shape: {image_data.shape}, "
                                f"Type: {image_data.dtype}, "
                                f"Time: {load_time:.3f}s")
                
                return image_data
            else:
                return None
                
        except Exception as e:
            error_msg = f"Error loading image {os.path.basename(image_path)}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return None
    
    def _load_from_disk(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load image from disk with error handling for corrupted files.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image data as numpy array, or None if loading failed
        """
        try:
            # Use tifffile for TIFF images (most common format)
            if image_path.lower().endswith(('.tif', '.tiff')):
                image_data = tifffile.imread(image_path)
            else:
                # Fallback for other formats (though project mainly uses TIFF)
                import imageio
                image_data = imageio.imread(image_path)
            
            # Validate loaded data
            if image_data is None or image_data.size == 0:
                raise ValueError("Loaded image is empty")
            
            # Ensure proper data type
            if image_data.dtype == np.float64:
                image_data = image_data.astype(np.float32)  # Reduce memory usage
            
            # Basic corruption check
            if not np.isfinite(image_data).all():
                self.logger.warning(f"Image contains non-finite values: {image_path}")
                # Could optionally clean up the data here
            
            return image_data
            
        except Exception as e:
            error_msg = f"Failed to read image file {image_path}: {str(e)}"
            self.logger.error(error_msg)
            
            # Try to identify specific corruption issues
            if "not a TIFF file" in str(e).lower():
                error_msg = f"File is not a valid TIFF: {image_path}"
            elif "truncated" in str(e).lower():
                error_msg = f"Image file appears to be truncated: {image_path}"
            elif "corrupt" in str(e).lower():
                error_msg = f"Image file appears to be corrupted: {image_path}"
            
            self.error_occurred.emit(error_msg)
            return None
    
    def calculate_thresholds(self, image_data: np.ndarray) -> Tuple[int, int]:
        """
        Calculate threshold values using mean and 2nd percentile as defaults.
        This is the standard method to avoid duplicated calculations.
        
        Args:
            image_data: Image data as numpy array
            
        Returns:
            Tuple of (threshold1, threshold2) where:
            - threshold1: Mean-based threshold (primary threshold for nucleus)
            - threshold2: 2nd percentile threshold (secondary threshold for membrane/background)
        """
        try:
            start_time = time.time()
            
            if image_data is None or image_data.size == 0:
                self.logger.error("Cannot calculate thresholds for empty image data")
                return 1, 1
            
            # Threshold1: Mean intensity (primary threshold for nucleus)
            mean_value = np.mean(image_data)
            threshold1 = int(np.round(mean_value))
            
            # Threshold2: 2nd percentile (secondary threshold for membrane/background)
            percentile_2_value = np.percentile(image_data, 2)
            threshold2 = int(np.round(percentile_2_value))
            
            # Ensure thresholds are within valid range
            data_min = int(np.min(image_data))
            data_max = int(np.max(image_data))
            
            threshold1 = max(1, min(threshold1, data_max))
            threshold2 = max(1, min(threshold2, data_max))
            
            # Ensure threshold1 >= threshold2 (logical ordering)
            if threshold1 < threshold2:
                threshold1, threshold2 = threshold2, threshold1
            
            # Update statistics
            calc_time = time.time() - start_time
            self.stats['threshold_calc_times'].append(calc_time)
            
            self.logger.debug(f"Calculated default thresholds: T1={threshold1} (mean), T2={threshold2} (2nd percentile) - "
                             f"Range: [{data_min}, {data_max}], Time: {calc_time:.3f}s")
            
            return threshold1, threshold2
            
        except Exception as e:
            error_msg = f"Error calculating thresholds: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            # Return safe default values
            return 100, 50
    
    def preload_image(self, image_path: str) -> bool:
        """
        Preload image into cache for faster access later.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if preloading succeeded, False otherwise
        """
        try:
            if not os.path.exists(image_path):
                return False
            
            # Check if already cached
            if self.cache_loader.cache.get(image_path) is not None:
                return True
            
            # Load image
            image_data = self.load_image(image_path)
            return image_data is not None
            
        except Exception as e:
            self.logger.error(f"Error preloading image {image_path}: {str(e)}")
            return False
    
    def get_cached_thresholds(self, image_path: str) -> Optional[Tuple[int, int]]:
        """
        Get cached threshold values for an image if available.
        This would integrate with database caching in a full implementation.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (threshold1, threshold2) if cached, None otherwise
        """
        # For now, return None - this would be implemented with database integration
        # In the future, this could check a database table for cached threshold values
        return None
    
    def cache_thresholds(self, image_path: str, threshold1: int, threshold2: int) -> bool:
        """
        Cache threshold values for future use.
        This would integrate with database caching in a full implementation.
        
        Args:
            image_path: Path to the image file
            threshold1: First threshold value
            threshold2: Second threshold value
            
        Returns:
            True if caching succeeded, False otherwise
        """
        # For now, just log - this would be implemented with database integration
        self.logger.debug(f"Would cache thresholds for {image_path}: T1={threshold1}, T2={threshold2}")
        return True
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage information.
        
        Returns:
            Dictionary containing memory usage statistics
        """
        try:
            cache_stats = self.cache_loader.get_cache_stats()
            return {
                'cache_memory_mb': cache_stats.get('memory_usage_mb', 0),
                'cache_memory_percent': cache_stats.get('memory_usage_percent', 0),
                'cached_items': cache_stats.get('current_items', 0),
                'hit_rate': cache_stats.get('hit_rate', 0)
            }
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {str(e)}")
            return {}
    
    def clear_cache(self) -> None:
        """Clear the image cache to free memory."""
        try:
            self.cache_loader.clear_cache()
            self.logger.info("Image cache cleared")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for monitoring and optimization.
        
        Returns:
            Dictionary containing performance statistics
        """
        try:
            stats = self.stats.copy()
            
            # Calculate averages
            if stats['load_times']:
                stats['avg_load_time'] = np.mean(stats['load_times'])
                stats['max_load_time'] = np.max(stats['load_times'])
                stats['min_load_time'] = np.min(stats['load_times'])
            else:
                stats['avg_load_time'] = 0
                stats['max_load_time'] = 0
                stats['min_load_time'] = 0
            
            if stats['threshold_calc_times']:
                stats['avg_threshold_calc_time'] = np.mean(stats['threshold_calc_times'])
            else:
                stats['avg_threshold_calc_time'] = 0
            
            # Add cache statistics
            cache_stats = self.cache_loader.get_cache_stats()
            stats.update(cache_stats)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {str(e)}")
            return {}
    
    def cleanup(self) -> None:
        """Clean up resources and clear cache."""
        try:
            self.clear_cache()
            self.stats = {
                'images_loaded': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'load_times': [],
                'threshold_calc_times': []
            }
            self.logger.info("FastImageLoader cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")