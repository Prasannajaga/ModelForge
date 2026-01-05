from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from src.styles.theme import VIEW_LABEL_STYLE

class OptimizeView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Hello Optimize")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(VIEW_LABEL_STYLE)
        layout.addWidget(label)
