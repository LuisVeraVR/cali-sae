
"""
El Paisano Tab - Invoice processing interface for El Paisano
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        main_layout.addWidget(scroll_area)

        content = QWidget()
        scroll_area.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: white; border-radius: 10px; padding: 24px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel("EL PAISANO")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #e67e22;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        # Info message
        info = QLabel("Tab de procesamiento para El Paisano\n\nEsta pesta?a est? lista para ser configurada con la funcionalidad espec?fica del cliente")
        info.setFont(QFont("Arial", 12))
        info.setStyleSheet("color: #7f8c8d;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        card_layout.addWidget(info)

        layout.addWidget(card)
        layout.addStretch()
