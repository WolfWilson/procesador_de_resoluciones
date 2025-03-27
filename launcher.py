# launcher.py

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QProgressBar, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon

import sys

# Importamos la función principal de procesamiento
from main import ejecutar_proceso_completo

# Importa ResourceManager para cargar íconos
from modules.resource_manager import ResourceManager

# Importa la función para aplicar estilo (opcional)
from gui.style import apply_stylesheet


class ProcesoThread(QThread):
    progreso = pyqtSignal(int)
    terminado = pyqtSignal(str)

    def run(self):
        # Simulación sencilla de progreso
        self.progreso.emit(25)
        exito = ejecutar_proceso_completo()
        self.progreso.emit(100)

        if exito:
            self.terminado.emit("¡Proceso finalizado con éxito!")
        else:
            self.terminado.emit("No se encontraron archivos válidos.")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procesador de Resoluciones")
        self.setMinimumWidth(400)

        # Establecer icono de ventana con ResourceManager
        icono_ventana = QIcon(ResourceManager.paper_icon())
        self.setWindowIcon(icono_ventana)

        self.boton = QPushButton("Procesar")
        self.boton.clicked.connect(self.iniciar_proceso)

        self.barra = QProgressBar()
        self.barra.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.boton)
        layout.addWidget(self.barra)
        self.setLayout(layout)

        self.hilo = ProcesoThread()
        self.hilo.progreso.connect(self.barra.setValue)
        self.hilo.terminado.connect(self.mostrar_mensaje)

    def iniciar_proceso(self):
        respuesta = QMessageBox.question(
            self,
            "Confirmación de Proceso",
            "¿Desea iniciar el proceso de carga de Resoluciones?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.boton.setEnabled(False)
            self.barra.setValue(0)
            self.hilo.start()

    def mostrar_mensaje(self, mensaje):
        self.boton.setEnabled(True)
        QMessageBox.information(self, "Resultado", mensaje)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Aplica la hoja de estilo, si lo deseas
    apply_stylesheet(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
