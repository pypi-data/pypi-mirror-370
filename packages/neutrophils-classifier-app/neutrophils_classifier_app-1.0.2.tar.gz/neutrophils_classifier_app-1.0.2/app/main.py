"""
Main entry point for the Neutrophils Classifier Application.
"""
import sys
import os
import argparse
import numpy as np
import pandas as pd

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import utilities
from app.utils.benchmark import log_benchmark, print_benchmark_summary
from app.utils.imports import import_critical_pyqt_components, import_lightweight_modules
from app.utils.resource_loader import get_asset_path, get_safe_resource_path

# Import PyQt critical components
pyqt_components = import_critical_pyqt_components()
QApplication = pyqt_components['QApplication']
QSplashScreen = pyqt_components['QSplashScreen']
QTimer = pyqt_components['QTimer']
Qt = pyqt_components['Qt']
QtGui = pyqt_components['QtGui']
QtWidgets = pyqt_components['QtWidgets']

# Import the main window
from app.ui.main_window import MainWindow


def main():
    """Main entry point for the application"""
    log_benchmark("MAINWINDOW_CLASS_DEFINITION")  # Mark end of class definition
    log_benchmark("MAIN_FUNCTION")
    
    parser = argparse.ArgumentParser(description="Neutrophils Classifier Application")
    parser.add_argument('--data-dir', type=str, help='Directory to load data on startup.')
    parser.add_argument('--image-file', type=str, help='Path to a single image file to load on startup.')
    args = parser.parse_args()

    log_benchmark("QAPPLICATION_CREATION")
    print("DEBUG: About to create QApplication...")
    app = QApplication(sys.argv)

    # Set application name and icon for better OS integration
    app.setApplicationName("Neutrophils Classifier")
    app.setApplicationDisplayName("Neutrophils Classifier")
    
    # Use packaging utilities for cross-platform icon loading
    icon_path = get_safe_resource_path('assets/icon.png', 'assets/icon.ico')
    if icon_path:
        app.setWindowIcon(QtGui.QIcon(str(icon_path)))
    else:
        print("WARNING: Application icon not found")
    print("DEBUG: QApplication created successfully")
    log_benchmark("QAPPLICATION_CREATION")

    # Show the splash screen IMMEDIATELY after QApplication creation
    log_benchmark("SPLASH_SCREEN_CREATION")
    print("DEBUG: About to create splash screen...")
    
    # Use packaging utilities for splash screen icon
    splash_icon_path = get_safe_resource_path('assets/icon.png', 'assets/icon.ico')
    if splash_icon_path:
        splash_pix = QtGui.QPixmap(str(splash_icon_path))
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
    else:
        print("WARNING: Splash screen icon not found, creating minimal splash")
        # Create a minimal splash screen if icon is missing
        splash_pix = QtGui.QPixmap(200, 100)
        splash_pix.fill(QtGui.QColor(50, 50, 50))
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    
    # Set initial splash screen message and show immediately
    # splash.showMessage("Initializing Neutrophils Classifier...", Qt.AlignBottom | Qt.AlignCenter, QtGui.QColor(255, 255, 255))
    splash.show()
    
    # Force immediate rendering of splash screen with multiple processEvents calls
    app.processEvents()
    QtWidgets.QApplication.processEvents()
    app.processEvents()  # Triple-ensure splash screen is rendered immediately
    print("DEBUG: Splash screen created and shown")
    log_benchmark("SPLASH_SCREEN_CREATION")

    # Add a small delay to let splash screen render before heavy MainWindow creation
    def create_main_window():
        # splash.showMessage("Loading main window...", Qt.AlignBottom | Qt.AlignCenter, QtGui.QColor(255, 255, 255))
        app.processEvents()
        
        log_benchmark("MAINWINDOW_INSTANTIATION")
        window = MainWindow()
        log_benchmark("MAINWINDOW_INSTANTIATION")
        
        # Continue with the rest of the setup
        setup_application_logic(window, splash, args, app)
    
    # Use QTimer to delay MainWindow creation, allowing splash to show first
    QTimer.singleShot(50, create_main_window)
    
    # Start the event loop immediately to show splash screen
    sys.exit(app.exec())


def setup_application_logic(window, splash, args, app):
    """Setup application logic after MainWindow is created"""
    # Store splash reference for later access
    app._splash = splash
    
    # Pass CLI arguments to the window for auto-loading
    window.set_cli_args(args)

    # Setup a timer to simulate a long loading process and show the main window
    QTimer.singleShot(1000, lambda: window.setup_done())  # Simulate delay of 1 second

    # Signal to close splash screen when the main window is initialized
    window.setup_done_signal.connect(lambda: splash.close())
    window.show()
    
    log_benchmark("MAIN_FUNCTION")  # Mark end of main function setup
    print_benchmark_summary()  # Print comprehensive timing summary


if __name__ == "__main__":
    main()