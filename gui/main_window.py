# gui/main_window.py

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QProgressBar, QMessageBox, QApplication, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
import sys

# Importa el ResourceManager
from modules.resource_manager import ResourceManager

# Importar funciones del script principal
from main import copy_files, process_files, insert_and_update_db, clean_and_move_files, generate_invalid_files_log

class ProcesamientoThread(QThread):
    progreso = pyqtSignal(int)
    terminado = pyqtSignal(str)

    def run(self):
        try:
            self.progreso.emit(10)
            copy_files()
            self.progreso.emit(30)
            processed_files, invalid_files = process_files()

            if invalid_files:
                generate_invalid_files_log(invalid_files)

            if processed_files:
                self.progreso.emit(60)
                insert_and_update_db(processed_files)
                self.progreso.emit(90)
                clean_and_move_files(processed_files)
                self.progreso.emit(100)
                self.terminado.emit("¡Procesamiento finalizado con éxito!")
            else:
                self.terminado.emit("No se encontraron archivos válidos.")
        except Exception as e:
            self.terminado.emit(f"Error durante el procesamiento: {e}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procesador de Resoluciones")
        self.setMinimumWidth(400)

        # Se puede usar el ícono para la ventana completa
        self.setWindowIcon(QIcon(ResourceManager.paper_icon()))

        # Muestra el icono en un QLabel si así se desea
        self.label_icono = QLabel()
        pixmap = QPixmap(ResourceManager.paper_icon())
        self.label_icono.setPixmap(pixmap)

        # Botón
        self.boton = QPushButton("Procesar")
        self.boton.clicked.connect(self.iniciar_proceso)

        # Barra de progreso
        self.progreso = QProgressBar()
        self.progreso.setValue(0)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_icono)
        layout.addWidget(self.boton)
        layout.addWidget(self.progreso)
        self.setLayout(layout)

        # Hilo de procesamiento
        self.hilo = ProcesamientoThread()
        self.hilo.progreso.connect(self.progreso.setValue)
        self.hilo.terminado.connect(self.mostrar_mensaje)

    def iniciar_proceso(self):
        self.progreso.setValue(0)
        self.boton.setEnabled(False)
        self.hilo.start()

    def mostrar_mensaje(self, mensaje):
        self.boton.setEnabled(True)
        QMessageBox.information(self, "Resultado del Proceso", mensaje)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())
