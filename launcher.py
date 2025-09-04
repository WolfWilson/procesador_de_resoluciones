# launcher.py

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QProgressBar, QMessageBox,
    QTextEdit, QHBoxLayout, QFileDialog, QLabel, QSplitter, QFrame
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize, QObject, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QFont

import sys
import os
import json
import io
from datetime import datetime

# Importamos la función principal de procesamiento
from main import ejecutar_proceso_completo, load_config

# Importa ResourceManager para cargar íconos
from modules.resource_manager import ResourceManager

# Importa la función para aplicar estilo (opcional)
from gui.style import apply_stylesheet


# Clase para redireccionar la salida estándar y capturarla para el log
class OutputRedirector(QObject):
    output_written = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.buffer = io.StringIO()
        
    def write(self, text):
        if text and not text.isspace():
            self.output_written.emit(text.rstrip())
            # También escribimos a stdout original para que aparezca en la consola
            sys.__stdout__.write(text)
        
    def flush(self):
        sys.__stdout__.flush()


class ProcesoThread(QThread):
    progreso = pyqtSignal(int)
    terminado = pyqtSignal(bool, str, str, str, int)
    log_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Crear redireccionador para capturar salida estándar
        self.stdout_redirector = OutputRedirector()
        self.stdout_redirector.output_written.connect(self.capturar_salida)
        
    @pyqtSlot(str)
    def capturar_salida(self, texto):
        """Recibe texto de la salida estándar y lo envía al log"""
        self.log_update.emit(texto)
        
    def run(self):
        # Redirigir stdout durante la ejecución del hilo
        original_stdout = sys.stdout
        sys.stdout = self.stdout_redirector
        
        try:
            config = load_config()
            progress_steps = config.get("progress_steps", [25, 50, 75, 100])
            
            # Primer paso: inicio
            self.log_update.emit("Iniciando proceso de carga de resoluciones...")
            self.progreso.emit(progress_steps[0] if len(progress_steps) > 0 else 25)
            
            # Segundo paso: copia de archivos
            self.log_update.emit("Copiando archivos...")
            if len(progress_steps) > 1:
                self.progreso.emit(progress_steps[1])
                
            # Tercer paso: procesamiento
            self.log_update.emit("Procesando archivos...")
            if len(progress_steps) > 2:
                self.progreso.emit(progress_steps[2])
                
            # Cuarto paso: base de datos
            self.log_update.emit("Actualizando base de datos...")
            if len(progress_steps) > 3:
                self.progreso.emit(progress_steps[3])
            
            # Ejecutamos el proceso completo
            exito, registro_path, log_path, cleanup_log, deleted_count = ejecutar_proceso_completo()
            
            # Paso final
            self.progreso.emit(100)
            
            if deleted_count > 0:
                self.log_update.emit(f"Se eliminaron {deleted_count} archivos temporales antiguos.")
            
            if exito:
                self.log_update.emit("¡Proceso finalizado con éxito!")
            else:
                self.log_update.emit("No se encontraron archivos válidos para procesar.")
                
            self.terminado.emit(exito, registro_path, log_path, cleanup_log, deleted_count)
        
        finally:
            # Restaurar stdout original
            sys.stdout = original_stdout


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procesador de Resoluciones")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Cargar configuración
        self.config = load_config()

        # Establecer icono de ventana con ResourceManager
        icono_ventana = QIcon(ResourceManager.paper_icon())
        self.setWindowIcon(icono_ventana)

        # Botones principales
        self.boton_procesar = QPushButton("Procesar")
        self.boton_procesar.clicked.connect(self.iniciar_proceso)
        self.boton_procesar.setMinimumHeight(40)
        
        self.boton_abrir = QPushButton("Abrir Procesados")
        self.boton_abrir.clicked.connect(self.abrir_procesados)
        self.boton_abrir.setMinimumHeight(40)
        
        self.boton_limpiar_log = QPushButton("Limpiar Log")
        self.boton_limpiar_log.clicked.connect(self.limpiar_log)
        
        # Barra de progreso
        self.barra = QProgressBar()
        self.barra.setValue(0)
        self.barra.setMinimumHeight(30)
        
        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 10))
        self.log_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)  # No envolver líneas
        # Asegurar colores correctos independientemente del tema
        self.log_area.setStyleSheet("color: #e0e0e0; background-color: #1e1e1e;")
        # Habilitar interpretación de HTML
        self.log_area.setAcceptRichText(True)
        
        # Crear un splitter para dividir la interfaz
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Panel superior para botones y barra
        top_panel = QFrame()
        top_layout = QVBoxLayout(top_panel)
        
        # Layout para botones (horizontal)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.boton_procesar)
        buttons_layout.addWidget(self.boton_abrir)
        
        top_layout.addLayout(buttons_layout)
        top_layout.addWidget(self.barra)
        
        # Panel inferior para el log
        bottom_panel = QFrame()
        bottom_layout = QVBoxLayout(bottom_panel)
        
        log_header_layout = QHBoxLayout()
        log_label = QLabel("Registro de Actividad:")
        log_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        log_header_layout.addWidget(log_label)
        log_header_layout.addStretch()
        log_header_layout.addWidget(self.boton_limpiar_log)
        
        bottom_layout.addLayout(log_header_layout)
        bottom_layout.addWidget(self.log_area)
        
        # Añadir paneles al splitter
        splitter.addWidget(top_panel)
        splitter.addWidget(bottom_panel)
        
        # Configurar tamaños iniciales del splitter
        splitter.setSizes([100, 500])
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Configurar el hilo
        self.hilo = ProcesoThread()
        self.hilo.progreso.connect(self.barra.setValue)
        self.hilo.terminado.connect(self.mostrar_mensaje)
        self.hilo.log_update.connect(self.agregar_log)
        
        # Log inicial
        self.agregar_log("Aplicación inicializada. Esperando instrucciones...")
        
    def limpiar_log(self):
        """Limpia el área de log"""
        self.log_area.clear()
        self.agregar_log("Log limpiado.")
        
    def agregar_log(self, mensaje):
        """Añade una entrada al área de log con marca de tiempo y formato adecuado"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Si el mensaje tiene múltiples líneas, procesarlas individualmente
        for linea in mensaje.split('\n'):
            if not linea.strip():  # Omitir líneas vacías
                continue
                
            # Aplicar formatos según el contenido del mensaje
            formato_html = ""
            
            # Mensajes de error en rojo
            if "error" in linea.lower() or "excepción" in linea.lower() or "inválido" in linea.lower():
                formato_html = f"<span style='color:#ff6b6b;'>[{timestamp}] {linea}</span>"
            
            # Mensajes de éxito en verde
            elif "éxito" in linea.lower() or "completado" in linea.lower() or "correctamente" in linea.lower():
                formato_html = f"<span style='color:#6bff8c;'>[{timestamp}] {linea}</span>"
            
            # Mensajes de advertencia en amarillo
            elif "advertencia" in linea.lower() or "warning" in linea.lower() or "atención" in linea.lower():
                formato_html = f"<span style='color:#ffd76b;'>[{timestamp}] {linea}</span>"
                
            # Mensajes relacionados con archivos en azul claro
            elif "archivo" in linea.lower() or ".pdf" in linea.lower() or "copiando" in linea.lower():
                formato_html = f"<span style='color:#6bddff;'>[{timestamp}] {linea}</span>"
                
            # Mensajes de base de datos en violeta
            elif "base de datos" in linea.lower() or "tabla" in linea.lower() or "sql" in linea.lower():
                formato_html = f"<span style='color:#d16bff;'>[{timestamp}] {linea}</span>"
                
            # Mensaje normal
            else:
                formato_html = f"<span style='color:#e0e0e0;'>[{timestamp}] {linea}</span>"
            
            self.log_area.append(formato_html)
                
        # Desplazar al final
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

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
            self.boton_procesar.setEnabled(False)
            self.barra.setValue(0)
            self.agregar_log("Iniciando proceso...")
            self.hilo.start()
            
    def abrir_procesados(self):
        """Abre la carpeta de archivos procesados"""
        processed_dir = self.config.get("processed_dir", "C:\\Temp\\Procesados")
        
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir, exist_ok=True)
            
        # En Windows, usamos el comando 'explorer' para abrir carpetas
        os.startfile(processed_dir)
        self.agregar_log(f"Abriendo carpeta de procesados: {processed_dir}")

    def mostrar_mensaje(self, exito, registro_path, log_path, cleanup_log, deleted_count):
        self.boton_procesar.setEnabled(True)
        
        mensaje = "¡Proceso finalizado con éxito!" if exito else "No se encontraron archivos válidos para procesar."
        
        if deleted_count > 0:
            mensaje += f"\n\nSe eliminaron {deleted_count} archivos temporales antiguos."
        
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
        
        # Añadir detalles adicionales al log
        if registro_path and os.path.exists(registro_path):
            self.agregar_log(f"Registro de procesamiento guardado en: {registro_path}")
            
        if log_path and os.path.exists(log_path):
            self.agregar_log(f"Log de errores guardado en: {log_path}")
            
        if cleanup_log and os.path.exists(cleanup_log):
            self.agregar_log(f"Log de limpieza guardado en: {cleanup_log}")

        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app)  # opcional
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
