from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os

class ModelSummaryDialog(QDialog):
    def __init__(self, summary_str):
        super().__init__()
        self.setWindowTitle('Classification Model Summary')
        self.setGeometry(200, 200, 1200, 800)
        icon_path = os.path.join('assets', 'icon.png')
        self.setWindowIcon(QIcon(icon_path))
        # Remove the question mark from the title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.initUI(summary_str)

    def initUI(self, summary_str):
        layout = QVBoxLayout()

        # QTextEdit to display the summary
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)  # Make it read-only
        self.textEdit.setStyleSheet("font-family: Courier; font-size: pt;")  # Set font and size

        # Apply basic color formatting (e.g., layer names in blue, shapes in green)
        formatted_summary = self.format_summary(summary_str)
        self.textEdit.setHtml(formatted_summary)

        layout.addWidget(self.textEdit)
        self.setLayout(layout)

    def format_summary(self, summary_str):
        # Here we can add color and styling to different parts of the summary
        formatted_summary = ""

        for line in summary_str.splitlines():
            if 'Layer (type)' in line:
                # Header line (usually containing 'Layer (type)')
                formatted_summary += f'<b style="color: #ff6600;">{line}</b><br>'
            elif 'Trainable params:' in line or 'Non-trainable params:' in line or 'Total params:' in line:
                # Parameters line
                formatted_summary += f'<span style="color: #0066cc;">{line}</span><br>'
            elif 'Input Shape' in line or 'Output Shape' in line:
                # Shape details
                formatted_summary += f'<span style="color: #009900;">{line}</span><br>'
            else:
                # General lines
                formatted_summary += f'<span style="color: #000000;">{line}</span><br>'

        return formatted_summary