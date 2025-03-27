# modules/resource_manager.py
import os
import sys

class ResourceManager:
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """
        Devuelve la ruta absoluta del recurso (iconos, imágenes, etc.)
        funcionando en ejecución normal o con PyInstaller.
        """
        if hasattr(sys, '_MEIPASS'):
            # Carpeta temporal donde PyInstaller extrae los recursos
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, "assets", relative_path)

    @staticmethod
    def paper_icon():
        """
        Devuelve la ruta al archivo 'paper.png' dentro de 'assets/'.
        """
        return ResourceManager.resource_path("paper.png")

    # Si necesitas más iconos/imágenes, puedes seguir este patrón:
    # @staticmethod
    # def otro_icono():
    #     return ResourceManager.resource_path("otro.png")

    @staticmethod
    def cora_icon():
        return ResourceManager.resource_path("cora.png")
