"""
Juan Camilo Rosas Tab - Invoice processing interface for Juan Camilo Rosas
Processes CSV/TXT files and converts to Reggis format with unit conversions
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QFileDialog, QProgressBar, QMessageBox, QFrame,
    QLineEdit, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Optional


class JCRProcessingThread(QThread):
    """Thread for processing JCR invoices without blocking UI"""

    progress_update = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(bool, str, int)  # success, message, records

    def __init__(self, controller, csv_files, municipality, iva_percentage):
        super().__init__()
        self.controller = controller
        self.csv_files = csv_files
        self.municipality = municipality
        self.iva_percentage = iva_percentage

    def run(self):
        """Run processing in background thread"""
        success, message, records = self.controller.process_jcr_invoices(
            csv_files=self.csv_files,
            municipality=self.municipality,
            iva_percentage=self.iva_percentage,
            progress_callback=self.progress_update.emit
        )
        self.finished.emit(success, message, records)


class JuanCamiloRosasTab(QWidget):
    """Tab for Juan Camilo Rosas invoice processing"""

    def __init__(self, main_controller):
        super().__init__()
        self.main_controller = main_controller
        self.csv_files: List[str] = []
        self.processing_thread: Optional[JCRProcessingThread] = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll_area)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Company title
        title = QLabel("JUAN CAMILO ROSAS")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #3498db;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Procesador de Facturas - Formato Reggis")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)

        # CSV files section
        layout.addWidget(self._create_csv_section())

        # Configuration section
        layout.addWidget(self._create_config_section())

        # Conversion info section
        layout.addWidget(self._create_conversion_info())

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 10pt;")
        layout.addWidget(self.status_label)

        # Process button
        process_btn = QPushButton("PROCESAR Y EXPORTAR A REGGIS")
        process_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        process_btn.clicked.connect(self.process_invoices)
        process_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(process_btn)

        layout.addStretch()

    def _create_csv_section(self) -> QFrame:
        """Create CSV/TXT files selection section"""
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 5px; padding: 15px; }")

        layout = QVBoxLayout()
        layout.setSpacing(10)

        label = QLabel("Archivos CSV/TXT de Facturas:")
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(label)

        self.csv_list = QListWidget()
        self.csv_list.setMaximumHeight(150)
        layout.addWidget(self.csv_list)

        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Agregar Archivos")
        add_btn.clicked.connect(self.add_csv_files)
        add_btn.setStyleSheet(self._get_button_style("#3498db"))
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("Quitar Seleccionado")
        remove_btn.clicked.connect(self.remove_csv_file)
        remove_btn.setStyleSheet(self._get_button_style("#e74c3c"))
        btn_layout.addWidget(remove_btn)

        clear_btn = QPushButton("Limpiar Todo")
        clear_btn.clicked.connect(self.clear_csv_files)
        clear_btn.setStyleSheet(self._get_button_style("#95a5a6"))
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)
        frame.setLayout(layout)
        return frame

    def _create_config_section(self) -> QFrame:
        """Create configuration section"""
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 5px; padding: 15px; }")

        layout = QVBoxLayout()
        layout.setSpacing(10)

        label = QLabel("Configuración de Exportación:")
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(label)

        # Municipality
        muni_layout = QHBoxLayout()
        muni_label = QLabel("Municipio:")
        muni_label.setMinimumWidth(100)
        self.municipality_input = QLineEdit()
        self.municipality_input.setPlaceholderText("Ej: Cali, Bogotá, Medellín")
        self.municipality_input.setText("Cali")  # Default value
        muni_layout.addWidget(muni_label)
        muni_layout.addWidget(self.municipality_input)
        layout.addLayout(muni_layout)

        # IVA Percentage
        iva_layout = QHBoxLayout()
        iva_label = QLabel("IVA (%):")
        iva_label.setMinimumWidth(100)
        self.iva_input = QLineEdit()
        self.iva_input.setPlaceholderText("Ej: 0, 5, 19")
        self.iva_input.setText("0")  # Default value
        iva_layout.addWidget(iva_label)
        iva_layout.addWidget(self.iva_input)
        layout.addLayout(iva_layout)

        frame.setLayout(layout)
        return frame

    def _create_conversion_info(self) -> QFrame:
        """Create conversion information section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(8)

        label = QLabel("📊 Conversiones de Unidades Aplicadas:")
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(label)

        conversions = [
            "• MEGA: 5 UNIDADES DE 7 LIBRAS C/U = 17.5 KILOS",
            "• REDONDA: 48 UNIDADES DE 1 LIBRA C/U = 24 KILOS",
            "• LIBRAS: 10 UNIDADES DE 4 LIBRAS C/U = 20 KILOS",
            "• KAO: 20 UNIDADES",
            "• PASTUANIO: 16 KILOS",
            "• PASTILLA LIBRA: 32 UNIDADES"
        ]

        info_text = QLabel("\n".join(conversions))
        info_text.setFont(QFont("Arial", 9))
        info_text.setStyleSheet("color: #34495e; padding-left: 10px;")
        info_text.setWordWrap(True)
        layout.addWidget(info_text)

        note = QLabel("Nota: El precio unitario se calcula automáticamente dividiendo el valor total por la cantidad convertida.")
        note.setFont(QFont("Arial", 8))
        note.setStyleSheet("color: #7f8c8d; font-style: italic; padding-left: 10px;")
        note.setWordWrap(True)
        layout.addWidget(note)

        frame.setLayout(layout)
        return frame

    def add_csv_files(self):
        """Add CSV/TXT files to the list"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar Archivos CSV/TXT",
            "",
            "CSV/TXT Files (*.csv *.txt);;All Files (*.*)"
        )

        if files:
            for file in files:
                if file not in self.csv_files:
                    self.csv_files.append(file)
                    self.csv_list.addItem(file)

    def remove_csv_file(self):
        """Remove selected CSV file"""
        current_row = self.csv_list.currentRow()
        if current_row >= 0:
            self.csv_files.pop(current_row)
            self.csv_list.takeItem(current_row)

    def clear_csv_files(self):
        """Clear all CSV files"""
        self.csv_files.clear()
        self.csv_list.clear()

    def process_invoices(self):
        """Process invoice CSV/TXT files"""
        if not self.csv_files:
            QMessageBox.warning(
                self,
                "Error",
                "Por favor seleccione al menos un archivo CSV/TXT"
            )
            return

        municipality = self.municipality_input.text().strip()
        if not municipality:
            QMessageBox.warning(
                self,
                "Error",
                "Por favor ingrese el municipio"
            )
            return

        iva_percentage = self.iva_input.text().strip()
        if not iva_percentage:
            iva_percentage = "0"

        # Validate IVA is a number
        try:
            float(iva_percentage)
        except ValueError:
            QMessageBox.warning(
                self,
                "Error",
                "El IVA debe ser un número válido"
            )
            return

        # Disable UI during processing
        self.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Procesando facturas y aplicando conversiones...")

        # Start processing in background thread
        self.processing_thread = JCRProcessingThread(
            self.main_controller,
            self.csv_files,
            municipality,
            iva_percentage
        )

        self.processing_thread.progress_update.connect(self._on_progress_update)
        self.processing_thread.finished.connect(self._on_processing_finished)
        self.processing_thread.start()

    def _on_progress_update(self, current: int, total: int):
        """Handle progress update"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)

    def _on_processing_finished(self, success: bool, message: str, records: int):
        """Handle processing completion"""
        self.setEnabled(True)
        self.progress_bar.setValue(100 if success else 0)
        self.status_label.setText(
            f"Proceso completado. Registros procesados: {records}"
            if success
            else "Error en el procesamiento"
        )

        if success:
            QMessageBox.information(self, "Éxito", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def _get_button_style(self, color: str) -> str:
        """Get button stylesheet"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
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
