"""
Debug configuration utilities for the Neutrophils Classifier Application.
This module provides convenient functions to configure debugging levels across the application.
"""
import logging
from .logging_config import setup_global_logging, set_global_log_level, get_current_log_level

def configure_debug_level(level_name: str = "DEBUG"):
    """
    Configure the global debug level for the entire application.
    
    Args:
        level_name: Debug level name. Can be:
                   - "DEBUG": Show all debug information (most verbose)
                   - "INFO": Show info, warning, error, and critical messages
                   - "WARNING": Show warning, error, and critical messages
                   - "ERROR": Show error and critical messages only
                   - "CRITICAL": Show critical messages only
                   - "SILENT": Disable all logging
    """
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "SILENT": logging.CRITICAL + 1  # Higher than CRITICAL to disable all
    }
    
    level_name = level_name.upper()
    if level_name not in level_mapping:
        raise ValueError(f"Invalid debug level: {level_name}. Valid levels: {list(level_mapping.keys())}")
    
    level = level_mapping[level_name]
    set_global_log_level(level)
    
    print(f"Global debug level set to: {level_name}")
    return level

def enable_verbose_debugging():
    """Enable maximum verbosity for debugging."""
    return configure_debug_level("DEBUG")

def enable_normal_logging():
    """Enable normal logging (INFO level)."""
    return configure_debug_level("INFO")

def enable_error_only():
    """Enable error-only logging."""
    return configure_debug_level("ERROR")

def disable_all_logging():
    """Disable all logging."""
    return configure_debug_level("SILENT")

def get_debug_status():
    """Get current debug configuration status."""
    current_level = get_current_log_level()
    
    level_names = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO", 
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL"
    }
    
    level_name = level_names.get(current_level, f"CUSTOM({current_level})")
    
    if current_level > logging.CRITICAL:
        level_name = "SILENT"
    
    return {
        "level": current_level,
        "level_name": level_name,
        "is_debug_enabled": current_level <= logging.DEBUG,
        "is_verbose": current_level <= logging.INFO
    }

# Example usage functions that can be called from anywhere in the application
def setup_development_logging():
    """Set up logging configuration suitable for development."""
    setup_global_logging(
        level=logging.DEBUG,
        log_file="logs/neutrophils_debug.log",
        console_output=True
    )
    print("Development logging configured with DEBUG level")

def setup_production_logging():
    """Set up logging configuration suitable for production."""
    setup_global_logging(
        level=logging.WARNING,
        log_file="logs/neutrophils_production.log",
        console_output=False
    )
    print("Production logging configured with WARNING level")

def setup_testing_logging():
    """Set up logging configuration suitable for testing."""
    setup_global_logging(
        level=logging.ERROR,
        console_output=True
    )
    print("Testing logging configured with ERROR level")