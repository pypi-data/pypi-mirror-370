from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, pyqtSlot

class StatusLamp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._state = 'Initializing'
        self._colors = {
            'Initializing': QColor('orange'),
            'Loading': QColor('yellow'),
            'Ready': QColor('green'),
            'Error': QColor('red')
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = self._colors.get(self._state, QColor('gray'))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(0, 0, self.width(), self.height())

    @pyqtSlot(str)
    def setState(self, state: str):
        if state in self._colors:
            self._state = state
            self.setToolTip(f"{state}")
            self.update()  # Trigger a repaint