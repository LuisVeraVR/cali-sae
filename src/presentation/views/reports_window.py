"""
Reports Window - Admin panel for viewing and exporting reports
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime


class ReportsWindow(QDialog):
    """Window for viewing and exporting reports (admin only)"""

    def __init__(self, reports_controller, parent=None):
        super().__init__(parent)
        self.reports_controller = reports_controller
        self.init_ui()
        self.load_reports()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Cali SAE - Reportes")
        self.setMinimumSize(1000, 650)
        self.resize(1100, 700)
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Cali SAE - Reportes")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Panel de Administración")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Usuario", "Empresa", "Archivo", "Registros",
            "Fecha", "Tamaño"
        ])

        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)

        # Adjust column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setFont(QFont("Arial", 11))
        refresh_btn.setStyleSheet(self._get_button_style("#3498db"))
        refresh_btn.clicked.connect(self.load_reports)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(refresh_btn)

        export_btn = QPushButton("Exportar")
        export_btn.setFont(QFont("Arial", 11))
        export_btn.setStyleSheet(self._get_button_style("#27ae60"))
        export_btn.clicked.connect(self.export_reports)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(export_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.setFont(QFont("Arial", 11))
        close_btn.setStyleSheet(self._get_button_style("#e74c3c"))
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.center_on_screen()

    def load_reports(self):
        """Load all reports from the database"""
        try:
            reports = self.reports_controller.get_all_reports()

            self.table.setRowCount(0)  # Clear table

            for report in reports:
                row = self.table.rowCount()
                self.table.insertRow(row)

                # Username
                self.table.setItem(row, 0, QTableWidgetItem(report.username))

                # Company
                self.table.setItem(row, 1, QTableWidgetItem(report.company))

                # Filename
                self.table.setItem(row, 2, QTableWidgetItem(report.filename))

                # Records processed
                self.table.setItem(row, 3, QTableWidgetItem(str(report.records_processed)))

                # Date
                self.table.setItem(row, 4, QTableWidgetItem(report.get_datetime()))

                # File size
                size_mb = f"{report.get_file_size_mb():.2f} MB"
                self.table.setItem(row, 5, QTableWidgetItem(size_mb))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando reportes: {str(e)}")

    def export_reports(self):
        """Export reports to CSV"""
        try:
            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"Reportes_Sistema_{timestamp}.csv"

            # Ask user for save location
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reportes",
                default_filename,
                "CSV Files (*.csv)"
            )

            if filename:
                success, message = self.reports_controller.export_reports(filename)

                if success:
                    QMessageBox.information(self, "Éxito", message)
                else:
                    QMessageBox.critical(self, "Error", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exportando reportes: {str(e)}")

    def center_on_screen(self):
        """Center the window on screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _get_button_style(self, color: str) -> str:
        """Get button stylesheet"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                min-width: 100px;
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
