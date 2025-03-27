# modules/resource_manager.py

import os
import sys

def resource_path(relative_path: str) -> str:
    """
    Devuelve la ruta absoluta para el recurso, tanto en desarrollo
    como en el entorno compilado con PyInstaller.
    """
    # Cuando se compila con PyInstaller, la ruta base se guarda en sys._MEIPASS
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class ResourceManager:
    @staticmethod
    def paper_icon() -> str:
        """Devuelve la ruta completa al icono 'paper.png'."""
        return resource_path("assets/paper.png")
