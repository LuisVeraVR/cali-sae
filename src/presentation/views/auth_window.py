# -*- coding: utf-8 -*-

"""
Authentication Window - Login and password change interface
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class AuthWindow(QWidget):
    """Authentication window with login and password change functionality"""

    # Signal emitted when login is successful
    login_successful = pyqtSignal(object)  # Emits User object

    def __init__(self, auth_controller):
        """
        Initialize authentication window

        Args:
            auth_controller: Authentication controller
        """
        super().__init__()
        self.auth_controller = auth_controller
        self.login_frame = None
        self.change_password_frame = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Cali SAE - Iniciar Sesión")
        self.setMinimumSize(520, 640)
        self.setStyleSheet("background-color: #f5f7fb;")

        # Outer layout with scroll to avoid cuts on small screens
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        outer_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(22)

        # Title
        title = QLabel("Cali SAE")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #1f2d3d; letter-spacing: 1px;")
        main_layout.addWidget(title)

        subtitle = QLabel("Sistema de Facturas Electrónicas")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7a8ca5;")
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(12)

        # Login frame
        self.login_frame = self._create_login_frame()
        main_layout.addWidget(self.login_frame)

        # Change password frame (initially hidden)
        self.change_password_frame = self._create_change_password_frame()
        self.change_password_frame.hide()
        main_layout.addWidget(self.change_password_frame)

        main_layout.addStretch()

        self.setLayout(outer_layout)
        self.center_on_screen()

    def _create_login_frame(self) -> QFrame:
        """Create the login frame"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 14px;
                padding: 22px;
                border: 1px solid #e3e8f0;
                box-shadow: 0 8px 24px rgba(31, 45, 61, 0.08);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(14)

        # Username
        username_label = QLabel("Usuario:")
        username_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su usuario")
        self.username_input.setStyleSheet(self._get_input_style())
        self.username_input.setFont(QFont("Arial", 10))
        layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Contraseña:")
        password_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self._get_input_style())
        self.password_input.setFont(QFont("Arial", 10))
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)

        # Show password checkbox
        self.show_password_checkbox = QCheckBox("Mostrar contraseña")
        self.show_password_checkbox.setFont(QFont("Arial", 9))
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        # Login button
        login_btn = QPushButton("Iniciar Sesión")
        login_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        login_btn.setStyleSheet(self._get_button_style("#27ae60"))
        login_btn.clicked.connect(self.handle_login)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(login_btn)

        # Change password button
        change_pwd_btn = QPushButton("Cambiar contraseña")
        change_pwd_btn.setFont(QFont("Arial", 9))
        change_pwd_btn.setStyleSheet(self._get_button_style("#3498db", small=True))
        change_pwd_btn.clicked.connect(self.show_change_password)
        change_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(change_pwd_btn)

        frame.setLayout(layout)
        return frame

    def _create_change_password_frame(self) -> QFrame:
        """Create the change password frame"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 14px;
                padding: 22px;
                border: 1px solid #e3e8f0;
                box-shadow: 0 8px 24px rgba(31, 45, 61, 0.08);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(14)

        # Title
        title = QLabel("Cambiar contraseña")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Username
        username_label = QLabel("Usuario:")
        username_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(username_label)

        self.change_username_input = QLineEdit()
        self.change_username_input.setStyleSheet(self._get_input_style())
        self.change_username_input.setFont(QFont("Arial", 10))
        layout.addWidget(self.change_username_input)

        # Current password
        current_pwd_label = QLabel("Contraseña actual:")
        current_pwd_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(current_pwd_label)

        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_input.setStyleSheet(self._get_input_style())
        self.current_password_input.setFont(QFont("Arial", 10))
        layout.addWidget(self.current_password_input)

        # New password
        new_pwd_label = QLabel("Nueva contraseña:")
        new_pwd_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(new_pwd_label)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setStyleSheet(self._get_input_style())
        self.new_password_input.setFont(QFont("Arial", 10))
        layout.addWidget(self.new_password_input)

        # Buttons
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Guardar")
        save_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        save_btn.setStyleSheet(self._get_button_style("#27ae60"))
        save_btn.clicked.connect(self.handle_change_password)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFont(QFont("Arial", 10))
        cancel_btn.setStyleSheet(self._get_button_style("#95a5a6"))
        cancel_btn.clicked.connect(self.hide_change_password)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        frame.setLayout(layout)
        return frame

    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña")
            return

        # Use controller to authenticate
        success, user, message = self.auth_controller.authenticate(username, password)

        if success:
            self.login_successful.emit(user)
            self.close()
        else:
            QMessageBox.critical(self, "Error", message)
            self.password_input.clear()

    def show_change_password(self):
        """Show change password frame"""
        self.login_frame.hide()
        self.change_password_frame.show()

    def hide_change_password(self):
        """Hide change password frame"""
        self.change_password_frame.hide()
        self.login_frame.show()
        self._clear_change_password_fields()

    def handle_change_password(self):
        """Handle change password button click"""
        username = self.change_username_input.text().strip()
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()

        if not username or not current_password or not new_password:
            QMessageBox.warning(self, "Error", "Todos los campos son requeridos")
            return

        # Use controller to change password
        success, message = self.auth_controller.change_password(
            username,
            current_password,
            new_password
        )

        if success:
            QMessageBox.information(self, "Éxito", message)
            self.hide_change_password()
        else:
            QMessageBox.critical(self, "Error", message)

    def toggle_password_visibility(self, state):
        """Toggle password visibility"""
        if state == Qt.CheckState.Checked.value:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def _clear_change_password_fields(self):
        """Clear change password fields"""
        self.change_username_input.clear()
        self.current_password_input.clear()
        self.new_password_input.clear()

    def center_on_screen(self):
        """Center the window on screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _get_input_style(self) -> str:
        """Get input field stylesheet"""
        return """
            QLineEdit {
                padding: 12px;
                border: 2px solid #dfe6ee;
                border-radius: 8px;
                font-size: 11pt;
                background-color: #fbfcfe;
                min-height: 22px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background-color: #fff;
            }
        """

    def _get_button_style(self, color: str, small: bool = False) -> str:
        """Get button stylesheet"""
        padding = "8px 12px" if small else "12px 16px"
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: {padding};
                font-weight: 600;
                letter-spacing: 0.2px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.8)};
            }}
        """

    def _darken_color(self, color: str, factor: float = 0.9) -> str:
        """Darken a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
