"""
Resource loader utilities for packaged resources.

This module provides functions to load resources (models, assets, UI files) 
from the installed package using importlib.resources for Python 3.9+ compatibility.
"""

import sys
from pathlib import Path
from typing import Union

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files


def get_resource_path(package: str, resource: str) -> Path:
    """
    Get the path to a resource within a package.
    
    Args:
        package: Package name (e.g., 'app.ui', 'models', 'assets')
        resource: Resource filename
        
    Returns:
        Path to the resource
    """
    try:
        # Try to use importlib.resources for packaged resources
        package_files = files(package)
        resource_path = package_files / resource
        
        if resource_path.is_file():
            return Path(str(resource_path))
    except (ImportError, ModuleNotFoundError):
        pass
    
    # Fallback to development/local paths
    if package == 'models':
        return Path(__file__).parent.parent.parent / 'models' / resource
    elif package == 'assets':
        return Path(__file__).parent.parent.parent / 'assets' / resource
    elif package.startswith('app.ui'):
        return Path(__file__).parent.parent / 'ui' / resource
    else:
        # Generic fallback
        package_path = package.replace('.', '/')
        return Path(__file__).parent.parent.parent / package_path / resource


def get_model_path(model_filename: str) -> Path:
    """
    Get the path to a model file.
    
    Args:
        model_filename: Name of the model file (e.g., 'SimCLR_rep50.keras')
        
    Returns:
        Path to the model file
    """
    return get_resource_path('models', model_filename)


def get_asset_path(asset_filename: str) -> Path:
    """
    Get the path to an asset file.
    
    Args:
        asset_filename: Name of the asset file (e.g., 'icon.png')
        
    Returns:
        Path to the asset file
    """
    return get_resource_path('assets', asset_filename)


def get_ui_file_path(ui_filename: str) -> Path:
    """
    Get the path to a UI file.
    
    Args:
        ui_filename: Name of the UI file (e.g., 'mainWindow.ui')
        
    Returns:
        Path to the UI file
    """
    return get_resource_path('app.ui', ui_filename)


def get_safe_resource_path(*paths: Union[str, Path]) -> Union[Path, None]:
    """
    Get a resource path with graceful fallback handling.
    
    Args:
        *paths: Resource paths to try in order (e.g., 'assets/icon.png', 'assets/icon.ico')
        
    Returns:
        Path or None: Path to first existing resource, or None if none exist
    """
    for path in paths:
        try:
            if isinstance(path, str):
                # Parse path to determine package and resource
                if path.startswith('assets/'):
                    resource_path = get_asset_path(path.replace('assets/', ''))
                elif path.startswith('app/ui/'):
                    resource_path = get_ui_file_path(path.replace('app/ui/', ''))
                elif path.startswith('models/'):
                    resource_path = get_model_path(path.replace('models/', ''))
                else:
                    # Generic fallback
                    parts = path.split('/')
                    if len(parts) >= 2:
                        package = parts[0] if parts[0] != 'app' else '.'.join(parts[:2])
                        resource = '/'.join(parts[1:]) if parts[0] != 'app' else parts[2]
                        resource_path = get_resource_path(package, resource)
                    else:
                        continue
            else:
                resource_path = path
            
            if resource_path.exists():
                return resource_path
        except Exception:
            continue
    return None


def resource_exists(package: str, resource: str) -> bool:
    """
    Check if a resource exists within a package.
    
    Args:
        package: Package name
        resource: Resource filename
        
    Returns:
        True if resource exists, False otherwise
    """
    try:
        resource_path = get_resource_path(package, resource)
        return resource_path.exists()
    except Exception:
        return False