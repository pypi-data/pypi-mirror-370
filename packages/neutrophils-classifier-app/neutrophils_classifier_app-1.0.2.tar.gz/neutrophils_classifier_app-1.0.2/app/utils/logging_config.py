"""
Global logging configuration for the Neutrophils Classifier Application.
This module provides centralized logging setup that can be used across all files.
"""
import logging
import os
import sys
from typing import Optional

# Global logger instance
_global_logger: Optional[logging.Logger] = None
_log_level = logging.DEBUG  # Default global log level

def setup_global_logging(
    level: int = logging.DEBUG,
    log_file: Optional[str] = None,
    console_output: bool = True,
    formatter_pattern: Optional[str] = None
) -> logging.Logger:
    """
    Set up global logging configuration for the entire application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, only console logging is used.
        console_output: Whether to output logs to console
        formatter_pattern: Custom formatter pattern. If None, uses default.
    
    Returns:
        Configured logger instance
    """
    global _global_logger, _log_level
    
    _log_level = level
    
    # Create root logger for the application
    _global_logger = logging.getLogger('neutrophils_classifier')
    _global_logger.setLevel(level)
    
    # Clear any existing handlers to avoid duplicates
    _global_logger.handlers.clear()
    
    # Set up formatter
    if formatter_pattern is None:
        formatter_pattern = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    
    formatter = logging.Formatter(formatter_pattern)
    
    # Set up console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        _global_logger.addHandler(console_handler)
    
    # Set up file handler if specified
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            _global_logger.addHandler(file_handler)
        except Exception as e:
            print(f"WARNING: Failed to create log file handler: {e}")
    
    # Prevent propagation to avoid duplicate logs
    _global_logger.propagate = False
    
    return _global_logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the global configuration.
    
    Args:
        name: Logger name. If None, uses the calling module's name.
    
    Returns:
        Configured logger instance
    """
    global _global_logger, _log_level
    
    # If no global logger is set up, create a default one
    if _global_logger is None:
        setup_global_logging()
    
    # Create a child logger with the specified name
    if name is None:
        # Try to get the calling module's name
        import inspect
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame)
        if module:
            name = module.__name__
        else:
            name = 'unknown'
    
    logger = logging.getLogger(f'neutrophils_classifier.{name}')
    logger.setLevel(_log_level)
    
    # Child loggers inherit handlers from parent, but we need to ensure
    # they don't duplicate logs
    if not logger.handlers:
        logger.parent = _global_logger
    
    return logger

def set_global_log_level(level: int):
    """
    Set the global log level for all loggers.
    
    Args:
        level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global _global_logger, _log_level
    
    _log_level = level
    
    if _global_logger:
        _global_logger.setLevel(level)
        # Update all handlers
        for handler in _global_logger.handlers:
            handler.setLevel(level)
    
    # Update all existing child loggers
    for logger_name in logging.Logger.manager.loggerDict:
        if logger_name.startswith('neutrophils_classifier.'):
            existing_logger = logging.getLogger(logger_name)
            existing_logger.setLevel(level)

def get_current_log_level() -> int:
    """Get the current global log level."""
    return _log_level

def log_debug_separator(logger: logging.Logger, title: str, char: str = "="):
    """Log a debug separator line for better readability."""
    separator_line = f" {char * 10} {title.upper()} {char * 10} "
    logger.debug(separator_line)

def log_method_entry(logger: logging.Logger, method_name: str, **kwargs):
    """Log method entry with parameters."""
    params_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()]) if kwargs else "no params"
    logger.debug(f"ENTERING {method_name}({params_str})")

def log_method_exit(logger: logging.Logger, method_name: str, result=None):
    """Log method exit with optional result."""
    result_str = f" -> {result}" if result is not None else ""
    logger.debug(f"EXITING {method_name}{result_str}")

def log_state_check(logger: logging.Logger, state_name: str, state_value, expected=None):
    """Log state check with optional expected value comparison."""
    if expected is not None:
        status = "✓" if state_value == expected else "✗"
        logger.debug(f"STATE CHECK {status}: {state_name} = {state_value} (expected: {expected})")
    else:
        logger.debug(f"STATE CHECK: {state_name} = {state_value}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: str = "", exc_info: bool = True):
    """Log error with additional context information."""
    context_str = f" in {context}" if context else ""
    logger.error(f"ERROR{context_str}: {str(error)}", exc_info=exc_info)

# Initialize default logging on module import
setup_global_logging()