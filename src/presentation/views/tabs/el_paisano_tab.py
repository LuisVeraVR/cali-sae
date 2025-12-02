
"""
El Paisano Tab - Procesa carpetas con XML/PDF y exporta a Reggis
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QProgressBar, QMessageBox, QFrame, QListWidget, QScrollArea, QLineEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Optional
import subprocess
import platform
from pathlib import Path


class PaisanoProcessingThread(QThread):
    """Thread for processing El Paisano invoices without blocking UI"""

    progress_update = pyqtSignal(int, int)
    finished = pyqtSignal(bool, str, int)

    def __init__(self, controller, file_paths: List[str]):
        super().__init__()
        self.controller = controller
        self.file_paths = file_paths

    def run(self):
        success, message, records = self.controller.process_paisano_invoices(
            file_paths=self.file_paths,
            progress_callback=self.progress_update.emit
        )
        self.finished.emit(success, message, records)


class ElPaisanoTab(QWidget):
    """Tab for El Paisano processing from XML folders"""

    def __init__(self, main_controller):
        super().__init__()
        self.main_controller = main_controller
        self.file_paths: List[str] = []
        self.processing_thread: Optional[PaisanoProcessingThread] = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        main_layout.addWidget(scroll_area)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("EL PAISANO")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #e67e22;")
        layout.addWidget(title)

        subtitle = QLabel("Procesar XML/PDF y exportar a plantilla Reggis")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)

        layout.addWidget(self._create_folder_section())
        layout.addWidget(self._create_conversion_section())

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 24px;
            }
            QProgressBar::chunk {
                background-color: #e67e22;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 10pt;")
        layout.addWidget(self.status_label)

        process_btn = QPushButton("PROCESAR XML A REGGIS")
        process_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #cf5f12;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        process_btn.clicked.connect(self.process_invoices)
        process_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(process_btn)

        layout.addStretch()

    def _create_folder_section(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; padding: 15px; }")

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Carpetas o archivos XML/PDF:")
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(label)

        self.xml_list = QListWidget()
        self.xml_list.setMinimumHeight(160)
        layout.addWidget(self.xml_list)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        add_btn = QPushButton("Agregar carpeta/XML/PDF")
        add_btn.setStyleSheet(self._get_button_style("#e67e22"))
        add_btn.clicked.connect(self.add_xml_paths)
        btn_layout.addWidget(add_btn)

        clear_btn = QPushButton("Limpiar lista")
        clear_btn.setStyleSheet(self._get_button_style("#95a5a6"))
        clear_btn.clicked.connect(self.clear_xml_paths)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)
        return frame

    def _create_conversion_section(self) -> QFrame:
        """UI to add/update conversion factors"""
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; padding: 15px; }")

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Agregar conversión (producto → factor a Kg)")
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(label)

        name_row = QHBoxLayout()
        self.conv_name_input = QLineEdit()
        self.conv_name_input.setPlaceholderText("Ej: ACEITE SOYA*1000CC SAN MIGUEL EX")
        name_row.addWidget(self.conv_name_input, 1)

        self.conv_factor_input = QDoubleSpinBox()
        self.conv_factor_input.setRange(0.0001, 100000)
        self.conv_factor_input.setDecimals(4)
        self.conv_factor_input.setValue(1.0)
        self.conv_factor_input.setSuffix(" factor")
        name_row.addWidget(self.conv_factor_input)

        layout.addLayout(name_row)

        save_btn = QPushButton("Guardar conversión")
        save_btn.setStyleSheet(self._get_button_style("#2ecc71"))
        save_btn.clicked.connect(self.save_conversion)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(save_btn)

        return frame

    def add_xml_paths(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta con XML o PDF",
            ""
        )
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos XML/PDF (opcional)",
            "",
            "XML/PDF Files (*.xml *.pdf);;Todos los archivos (*.*)"
        )

        added = False
        if folder:
            if folder not in self.file_paths:
                self.file_paths.append(folder)
                self.xml_list.addItem(f"Carpeta: {folder}")
                added = True
        if files:
            for f in files:
                if f not in self.file_paths:
                    self.file_paths.append(f)
                    self.xml_list.addItem(f"Archivo: {f}")
                    added = True

        if not added:
            QMessageBox.information(self, "Sin cambios", "No se agregaron nuevas rutas.")

    def clear_xml_paths(self):
        self.file_paths.clear()
        self.xml_list.clear()

    def process_invoices(self):
        if not self.file_paths:
            QMessageBox.warning(self, "Error", "Seleccione al menos una carpeta o archivo XML o PDF")
            return

        self.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Procesando archivos y exportando a Reggis...")

        self.processing_thread = PaisanoProcessingThread(
            self.main_controller,
            self.file_paths
        )
        self.processing_thread.progress_update.connect(self._on_progress_update)
        self.processing_thread.finished.connect(self._on_processing_finished)
        self.processing_thread.start()

    def _on_progress_update(self, current: int, total: int):
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)

    def _on_processing_finished(self, success: bool, message: str, records: int):
        self.setEnabled(True)
        self.progress_bar.setValue(100 if success else 0)
        self.status_label.setText(
            f"Proceso completado. Registros procesados: {records}" if success else "Error en el procesamiento"
        )

        if success:
            self._show_success_dialog(message)
        else:
            QMessageBox.critical(self, "Error", message)

    def _show_success_dialog(self, message: str):
        """Show success dialog and automatically open folder"""
        # Extract file path from message
        file_path = self._extract_file_path_from_message(message)

        # Automatically open folder if file path exists
        if file_path:
            self._open_file_location(file_path)

        # Show success message
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Éxito")
        msg_box.setText(message)
        msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

    def _extract_file_path_from_message(self, message: str) -> Optional[str]:
        """Extract file path from success message"""
        # Messages typically contain the path after a colon or newline
        lines = message.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('/') or line.startswith('data/')):
                # Check if it's a valid file path
                path = Path(line)
                if path.exists():
                    return str(path.absolute())
        return None

    def _open_file_location(self, file_path: str):
        """Open the folder containing the file in the system file explorer"""
        try:
            path = Path(file_path)
            folder_path = path.parent if path.is_file() else path

            system = platform.system()
            if system == "Windows":
                subprocess.run(['explorer', '/select,', str(path.absolute())])
            elif system == "Darwin":  # macOS
                subprocess.run(['open', '-R', str(path.absolute())])
            else:  # Linux and others
                subprocess.run(['xdg-open', str(folder_path.absolute())])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir la carpeta: {str(e)}")

    def save_conversion(self):
        """Persist a new conversion factor"""
        name = self.conv_name_input.text().strip()
        factor = float(self.conv_factor_input.value())

        if not name:
            QMessageBox.warning(self, "Error", "Ingrese el nombre del producto")
            return
        if factor <= 0:
            QMessageBox.warning(self, "Error", "El factor debe ser mayor que 0")
            return

        success, msg = self.main_controller.add_paisano_conversion(name, factor)
        if success:
            QMessageBox.information(self, "Éxito", msg)
            self.conv_name_input.clear()
            self.conv_factor_input.setValue(1.0)
        else:
            QMessageBox.warning(self, "Error", msg)

    def _get_button_style(self, color: str) -> str:
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 12px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
        """

    def _darken_color(self, color: str, factor: float = 0.9) -> str:
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
