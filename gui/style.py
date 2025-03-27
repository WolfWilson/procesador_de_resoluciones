# gui/style.py

def apply_stylesheet(app):
    """
    Aplica la hoja de estilo a la aplicación.
    """
    stylesheet = """
    /* General */
    QWidget {
        background-color: #F7F7F7; /* Color de fondo general */
        color: #333;              /* Color de texto por defecto */
        font-family: 'Segoe UI', sans-serif; /* Fuente general */
        font-size: 13px;
    }

    /* QMainWindow, si usas QMainWindow en algún lugar */
    QMainWindow {
        background-color: #FFFFFF; /* Fondo blanco para main window */
    }

    /* Barra de menú (si existe) */
    QMenuBar {
        background-color: #F0F0F0;
        border: 1px solid #C8C8C8;
    }
    QMenuBar::item:selected {
        background-color: #E0E0E0;
    }
    
    /* QProgressBar */
    QProgressBar {
        text-align: center;
        background-color: #E0E0E0;
        border: 1px solid #AAA;
        border-radius: 5px;
        height: 16px;
    }
    QProgressBar::chunk {
        background-color: #007BFF; /* Color de la barra rellena */
        border-radius: 5px;
    }

    /* QPushButton */
    QPushButton {
        background-color: #007BFF;
        border: none;
        border-radius: 4px;
        color: #FFFFFF;
        padding: 8px 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }
    QPushButton:disabled {
        background-color: #AACCF7;
        color: #FFFFFF;
    }

    /* QLineEdit, si lo utilizas en el formulario */
    QLineEdit {
        border: 1px solid #999;
        border-radius: 4px;
        padding: 4px;
    }
    QLineEdit:focus {
        border: 1px solid #007BFF;
    }

    /* QMessageBox */
    QMessageBox {
        background-color: #FFFFFF;
    }
    QMessageBox QLabel {
        color: #333;
    }
    QMessageBox QPushButton {
        min-width: 70px;
    }

    /* QLabel en general */
    QLabel {
        color: #333;
    }

    /*
     * Si quieres añadir algún efecto visual adicional (p.ej. 
     * sombra en la ventana) se suelen usar QGraphicsDropShadowEffect 
     * vía código, no en la hoja de estilos.
     */
    """
    app.setStyleSheet(stylesheet)
