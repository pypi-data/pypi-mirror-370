from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QDialogButtonBox, QLabel, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt

class ThresholdDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Auto Thresholding Percentiles")

        layout = QVBoxLayout(self)

        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignLeft)

        # Threshold 1 controls
        self.threshold1_mode_combo = QComboBox()
        self.threshold1_mode_combo.addItems(["Mean", "Percentile"])
        self.percentile1_spinbox = QSpinBox()
        self.percentile1_spinbox.setRange(0, 100)
        self.percentile1_spinbox.setValue(50)  # Default to 50% for percentile (median)

        threshold1_layout = QHBoxLayout()
        threshold1_layout.addWidget(self.threshold1_mode_combo)
        threshold1_layout.addWidget(self.percentile1_spinbox)
        threshold1_layout.addStretch(1)

        # Threshold 2 controls
        self.threshold2_mode_combo = QComboBox()
        self.threshold2_mode_combo.addItems(["Mean", "Percentile"])
        self.percentile2_spinbox = QSpinBox()
        self.percentile2_spinbox.setRange(0, 100)
        self.percentile2_spinbox.setValue(2)  # Default to 2% for percentile

        threshold2_layout = QHBoxLayout()
        threshold2_layout.addWidget(self.threshold2_mode_combo)
        threshold2_layout.addWidget(self.percentile2_spinbox)
        threshold2_layout.addStretch(1)

        self.formLayout.addRow(QLabel("Threshold 1:"), threshold1_layout)
        self.formLayout.addRow(QLabel("Threshold 2:"), threshold2_layout)

        self.threshold1_mode_combo.currentIndexChanged.connect(self._update_threshold1_visibility)
        self.threshold2_mode_combo.currentIndexChanged.connect(self._update_threshold2_visibility)
        self._update_threshold1_visibility()
        self._update_threshold2_visibility()
        
        layout.addLayout(self.formLayout)

        # Add hint label
        hint_label = QLabel("Hint: Median is the 50th percentile.")
        hint_label.setAlignment(Qt.AlignRight)
        layout.addWidget(hint_label)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.buttonBox)

    def _update_threshold1_visibility(self):
        is_percentile = self.threshold1_mode_combo.currentText() == "Percentile"
        self.percentile1_spinbox.setVisible(is_percentile)

    def _update_threshold2_visibility(self):
        is_percentile = self.threshold2_mode_combo.currentText() == "Percentile"
        self.percentile2_spinbox.setVisible(is_percentile)

    def get_values(self):
        mode1 = self.threshold1_mode_combo.currentText().lower()
        val1 = self.percentile1_spinbox.value() if mode1 == 'percentile' else 'mean'
        
        mode2 = self.threshold2_mode_combo.currentText().lower()
        val2 = self.percentile2_spinbox.value() if mode2 == 'percentile' else 'mean'
        
        return val1, val2