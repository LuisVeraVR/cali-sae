"""
Main Window - Main application window with tabs for different companies
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .tabs.agrobuitron_tab import AgrobuitronTab
from .tabs.juan_camilo_rosas_tab import JuanCamiloRosasTab
from .tabs.el_paisano_tab import ElPaisanoTab


class MainWindow(QMainWindow):
    """Main application window with tabs"""

    # Signal emitted when user logs out
    logout_requested = pyqtSignal()

    # Signal emitted when reports button is clicked
    reports_requested = pyqtSignal()

    def __init__(self, main_controller, reports_controller):
        super().__init__()
        self.main_controller = main_controller
        self.reports_controller = reports_controller
        self.init_ui()
        self.check_for_updates()

    def init_ui(self):
        """Initialize the user interface"""
        username = self.main_controller.get_username()
        user_type = self.main_controller.get_user_type()

        self.setWindowTitle(f"Sistema de Facturas Electrónicas - Usuario: {username}")
        self.setGeometry(100, 100, 1000, 750)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self._create_header(username, user_type)
        main_layout.addWidget(header)

        # Content
        content = self._create_content()
        main_layout.addWidget(content)

        central_widget.setLayout(main_layout)
        self.center_on_screen()

    def _create_header(self, username: str, user_type: str) -> QFrame:
        """Create the header with user info and action buttons"""
        header = QFrame()
        header.setStyleSheet("background-color: #34495e; padding: 15px;")
        header.setFixedHeight(70)

        layout = QHBoxLayout()

        # User info
        user_info = QLabel(f"Usuario: {username} | Tipo: {user_type.upper()}")
        user_info.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        user_info.setStyleSheet("color: white;")
        layout.addWidget(user_info)

        layout.addStretch()

        # Reports button (only for admin)
        if self.main_controller.is_admin():
            reports_btn = QPushButton("Ver Reportes")
            reports_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            reports_btn.setStyleSheet(self._get_header_button_style("#f39c12"))
            reports_btn.clicked.connect(self.open_reports)
            reports_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(reports_btn)

        # Logout button
        logout_btn = QPushButton("Cerrar Sesión")
        logout_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        logout_btn.setStyleSheet(self._get_header_button_style("#e74c3c"))
        logout_btn.clicked.connect(self.logout)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(logout_btn)

        header.setLayout(layout)
        return header

    def _create_content(self) -> QWidget:
        """Create the main content area with tabs"""
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Sistema de Extracción de Facturas Electrónicas")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 11))
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
        """)

        # Add tabs
        self.agrobuitron_tab = AgrobuitronTab(self.main_controller)
        self.tabs.addTab(self.agrobuitron_tab, "AGROBUITRON")

        self.juan_camilo_tab = JuanCamiloRosasTab(self.main_controller)
        self.tabs.addTab(self.juan_camilo_tab, "JUAN CAMILO ROSAS")

        self.el_paisano_tab = ElPaisanoTab(self.main_controller)
        self.tabs.addTab(self.el_paisano_tab, "EL PAISANO")

        layout.addWidget(self.tabs)

        content.setLayout(layout)
        return content

    def check_for_updates(self):
        """Check for updates on startup"""
        try:
            update_available, latest_version, download_url, release_notes = self.main_controller.check_updates()

            if update_available:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Actualización Disponible")
                msg.setText(f"Nueva versión disponible: {latest_version}")
                msg.setInformativeText("¿Desea descargar la actualización?")
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if msg.exec() == QMessageBox.StandardButton.Yes:
                    self._download_update(download_url)

        except Exception as e:
            # Silently fail if update check fails (e.g., no internet)
            print(f"Error checking for updates: {str(e)}")

    def _download_update(self, download_url: str):
        """Download update"""
        output_path = "invoice_system_update.exe"

        try:
            success, message = self.main_controller.download_update(download_url, output_path)

            if success:
                QMessageBox.information(self, "Éxito", message)
            else:
                QMessageBox.warning(self, "Error", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error descargando actualización: {str(e)}")

    def open_reports(self):
        """Emit signal to open reports window"""
        self.reports_requested.emit()

    def logout(self):
        """Confirm and emit logout signal"""
        reply = QMessageBox.question(
            self,
            "Cerrar Sesión",
            "¿Está seguro que desea cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
            self.close()

    def center_on_screen(self):
        """Center the window on screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _get_header_button_style(self, color: str) -> str:
        """Get button stylesheet for header buttons"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
        """

    def _darken_color(self, color: str, factor: float = 0.9) -> str:
        """Darken a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
