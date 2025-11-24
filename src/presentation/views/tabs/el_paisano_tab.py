"""
El Paisano Tab - Invoice processing interface for El Paisano
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ElPaisanoTab(QWidget):
    """Tab for El Paisano (ready to be customized with specific functionality)"""

    def __init__(self, main_controller):
        super().__init__()
        self.main_controller = main_controller
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel("EL PAISANO")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #e67e22;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Info message
        info = QLabel("Tab de procesamiento para El Paisano\n\n"
                     "Esta pestaña está lista para ser configurada\n"
                     "con la funcionalidad específica del cliente")
        info.setFont(QFont("Arial", 12))
        info.setStyleSheet("color: #7f8c8d;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)

        self.setLayout(layout)
