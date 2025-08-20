from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QDialogButtonBox, QLabel, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt

class StatisticalThresholdDialog(QDialog):
    def __init__(self, parent=None, threshold_name="Threshold"):
        super().__init__(parent)
        self.setWindowTitle(f"Statistical {threshold_name} Settings")
        self.setModal(True)
        self.setFixedSize(350, 200)

        layout = QVBoxLayout(self)

        # Main form layout
        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignLeft)

        # Statistical method selection
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Mean", "Percentile"])
        self.method_combo.setCurrentIndex(0)  # Default to Mean

        # Percentile value input (initially hidden)
        self.percentile_spinbox = QSpinBox()
        self.percentile_spinbox.setRange(0, 100)
        self.percentile_spinbox.setValue(50)  # Default to 50th percentile (median)
        self.percentile_spinbox.setSuffix("%")

        # Create horizontal layout for method selection
        method_layout = QHBoxLayout()
        method_layout.addWidget(self.method_combo)
        method_layout.addWidget(self.percentile_spinbox)
        method_layout.addStretch(1)

        self.formLayout.addRow(QLabel("Statistical Method:"), method_layout)

        # Connect signal to show/hide percentile input
        self.method_combo.currentIndexChanged.connect(self._update_percentile_visibility)
        self._update_percentile_visibility()
        
        layout.addLayout(self.formLayout)

        # Add hint label
        hint_label = QLabel("Hint: Mean uses average intensity, Percentile uses specified percentage of intensity distribution.")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(hint_label)

        # Dialog buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.buttonBox)

    def _update_percentile_visibility(self):
        """Show/hide percentile input based on selected method"""
        is_percentile = self.method_combo.currentText() == "Percentile"
        self.percentile_spinbox.setVisible(is_percentile)

    def get_values(self):
        """Return the selected method and value"""
        method = self.method_combo.currentText().lower()
        if method == 'percentile':
            return method, self.percentile_spinbox.value()
        else:
            return method, None

    def set_current_method(self, method, value=None):
        """Set the current method and value"""
        if method.lower() == 'mean':
            self.method_combo.setCurrentIndex(0)
        elif method.lower() == 'percentile':
            self.method_combo.setCurrentIndex(1)
            if value is not None:
                self.percentile_spinbox.setValue(value)