import os
import sys

class ResourceManager:
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """
        Devuelve la ruta absoluta del recurso para ejecución local o con PyInstaller.
        """
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS  # Carpeta temporal donde PyInstaller extrae los recursos
        else:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, "assets", relative_path)

    @staticmethod
    def paper_icon():
        return ResourceManager.resource_path("paper.png")

    # Podés agregar más recursos centralizados aquí
    # @staticmethod
    # def icon_nombre():
    #     return ResourceManager.resource_path("nombre.png")
