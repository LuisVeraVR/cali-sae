"""
Juan Camilo Rosas Tab - Invoice processing interface for Juan Camilo Rosas
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class JuanCamiloRosasTab(QWidget):
    """Tab for Juan Camilo Rosas (ready to be customized with specific functionality)"""

    def __init__(self, main_controller):
        super().__init__()
        self.main_controller = main_controller
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel("JUAN CAMILO ROSAS")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #3498db;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Info message
        info = QLabel("Tab de procesamiento para Juan Camilo Rosas\n\n"
                     "Esta pestaña está lista para ser configurada\n"
                     "con la funcionalidad específica del cliente")
        info.setFont(QFont("Arial", 12))
        info.setStyleSheet("color: #7f8c8d;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)

        self.setLayout(layout)
