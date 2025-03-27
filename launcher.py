# launcher.py

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QProgressBar, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QPixmap

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
        # Creamos un QMessageBox manual para la pregunta
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmación de Proceso")
        msg_box.setText("¿Desea iniciar el proceso de carga de Resoluciones?")
        msg_box.setIcon(QMessageBox.Icon.NoIcon)  # Quita el ícono por defecto

        # Ícono interrogación
        pix_interrogacion = QPixmap(ResourceManager.interrogacion_icon())
        pix_interrogacion = pix_interrogacion.scaled(
            50, 50,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
            transformMode=Qt.TransformationMode.SmoothTransformation
        )
        msg_box.setIconPixmap(pix_interrogacion)

        # Añade botones de Sí/No
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

        # Muestra el mensaje y obtén la respuesta
        respuesta = msg_box.exec()

        if respuesta == QMessageBox.StandardButton.Yes:
            self.boton.setEnabled(False)
            self.barra.setValue(0)
            self.hilo.start()

    def mostrar_mensaje(self, mensaje):
        self.boton.setEnabled(True)
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Resultado")
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.NoIcon)

        # Ícono exclamación
        pix_exclamacion = QPixmap(ResourceManager.exclamacion_icon())
        pix_exclamacion = pix_exclamacion.scaled(
            48, 48,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
            transformMode=Qt.TransformationMode.SmoothTransformation
        )
        msg_box.setIconPixmap(pix_exclamacion)

        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app)  # opcional
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
