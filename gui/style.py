# gui/style.py

def apply_stylesheet(app):
    """
    Aplica la hoja de estilo a la aplicación.
    """
    stylesheet = """
    /* General */
    QWidget {
        background-color: #2c2c2c; /* Color de fondo general */
        color: #ffffff;            /* Color de texto claro para que sea visible en fondo oscuro */
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
QProgressBar {
    text-align: center;
    background-color: #E0E0E0;
    border: 1px solid #AAA;
    border-radius: 5px;
    height: 16px;
}

QProgressBar::chunk {
    border-radius: 5px;
    /* Gradiente pastel de izquierda (x1=0) a derecha (x2=1) */
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0,
        x2: 1, y2: 0,
        stop: 0    #FFB3BA,  /* pastel red    */
        stop: 0.17 #FFDFBA,  /* pastel orange */
        stop: 0.34 #FFFFBA,  /* pastel yellow */
        stop: 0.50 #BAFFC9,  /* pastel green  */
        stop: 0.66 #BAE1FF,  /* pastel blue   */
        stop: 0.83 #C9BAFF,  /* pastel purple */
        stop: 1    #FCC0FF   /* pastel violet/pink */
    );
}
    /* QPushButton */
    QPushButton {
        background-color: #707070;
        border: none;
        border-radius: 4px;
        color: #FFFFFF;
        padding: 8px 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #a891af;
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
    
    /* QTextEdit para el área de log */
    QTextEdit {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #444;
        border-radius: 4px;
        font-family: 'Consolas', 'Courier New', monospace;
        selection-background-color: #264f78;
        selection-color: #ffffff;
    }
    
    /* Scrollbars para QTextEdit */
    QScrollBar:vertical {
        background: #2c2c2c;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #555;
        min-height: 20px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical:hover {
        background: #777;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        background: #2c2c2c;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: #555;
        min-width: 20px;
        border-radius: 3px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #777;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* QMessageBox */
    QMessageBox {
        background-color: #2c2c2c;
    }
    QMessageBox QLabel {
        color: #ffffff;
        font-size: 14px;
    }
    QMessageBox QPushButton {
        min-width: 80px;
        min-height: 30px;
    }
    
    /* QFrame para los paneles */
    QFrame {
        background-color: #333333;
        border-radius: 5px;
    }
    
    /* QSplitter */
    QSplitter::handle {
        background-color: #444444;
    }
    QSplitter::handle:horizontal {
        width: 4px;
    }
    QSplitter::handle:vertical {
        height: 4px;
    }

    /* QLabel en general */
    QLabel {
        color: #ffffff;
    }

    /*
     * Si quieres añadir algún efecto visual adicional (p.ej. 
     * sombra en la ventana) se suelen usar QGraphicsDropShadowEffect 
     * vía código, no en la hoja de estilos.
     */
    """
    app.setStyleSheet(stylesheet)
