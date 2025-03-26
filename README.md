# procesador_de_resolucionesfrom pathlib import Path

readme_content = """# 🗂️ PROCESADOR DE RESOLUCIONES

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?style=for-the-badge&logo=qt)
![SQL Server](https://img.shields.io/badge/Base%20de%20Datos-SQL%20Server-red?style=for-the-badge&logo=microsoftsqlserver)
![Windows](https://img.shields.io/badge/OS-Windows%2010%2B-lightgrey?style=for-the-badge&logo=windows)
![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-orange?style=for-the-badge)

Este proyecto **PROCESADOR DE RESOLUCIONES** automatiza la gestión de documentos PDF (Resoluciones) en una **estructura de directorios y base de datos** Microsoft SQL Server. Integra la verificación del formato de nombres de archivo, la extracción de texto desde PDFs y la posterior actualización de registros en la tabla **Maestro**. También maneja copias de seguridad y limpieza de archivos.

---

## 🚀 **Características Principales**
- **Copiado y verificación de archivos PDF** desde un directorio de origen a uno temporal.
- **Validación de la estructura del nombre** de archivo, garantizando que coincida con el patrón `<Letra>-<Actuacion>-<Ejercicio>.pdf`.
- **Inserción de datos** en tablas intermedias (**Wilson** y **Wilson2**) y actualización final en **Maestro**.
- **Extracción de texto** desde PDFs usando **PyPDF2**, para almacenar en el campo `extracto`.
- **Registro y manejo de errores** (nombres de archivo inválidos o años no válidos).
- **Traslado y copias de seguridad** de archivos a la carpeta correspondiente al año, manteniendo un log de ejecución.
- **Estructura lista** para integrar con una interfaz gráfica **PyQt6** (próximamente).

---

## 📂 **Estructura Inicial (Código Base)**
```plaintext
📦 Procesador_Resoluciones/
│
├── main.py                          # Punto de entrada principal
├── README.md                        # Documentación del proyecto (este archivo)
├── requirements.txt                 # Dependencias del proyecto
│
├── # En el futuro:
│   ├── gui/                         # Módulos e interfaces PyQt6
│   ├── modules/                     # Módulos de lógica y helpers
│   └── assets/                      # Recursos (íconos, imágenes, estilos)
```

## 🔧 Requisitos y Configuración
```plaintext
Python 3.12 (o superior).

Librerías indicadas en requirements.txt (ej. pyodbc, PyPDF2, etc.).

Servidor SQL Server accesible con autenticación de Windows.

Carpetas adecuadas en el filesystem (rutas de origen y destino):

\\fs01\Resoluciones_Temp (origen de PDFs)

C:\Temp (directorio temporal)

\\fs01\Resoluciones (directorio final, organizado por año)
```

### 📥 Instalación de Dependencias
```sh
pip install -r requirements.txt
```


El script:

Copiará los PDFs válidos.

Validará el nombre y año de los archivos.

Insertará, actualizará y registrará la información en la base de datos.

Generará logs para archivos inválidos y para la limpieza final.

## 🧩 Flujo de Trabajo Simplificado

copy_files()
Copia PDFs desde \\fs01\Resoluciones_Temp a C:\Temp.

process_files()
Verifica el patrón <Letra>-<Actuacion>-<Ejercicio>.pdf y filtra archivos no válidos.

insert_and_update_db()

Limpia tablas Wilson, Wilson2.

Inserta los registros básicos en Wilson y Wilson2.

Inserta/actualiza datos en Maestro (incluyendo extracto con texto del PDF).

clean_and_move_files()
Mueve los PDFs procesados desde C:\Temp a la carpeta \\fs01\Resoluciones\<Ejercicio>, y crea una copia de seguridad en C:\Temp\Procesados\PDFs_BK.
Registra detalles en un archivo de log con timestamp.

generate_invalid_files_log()
Registra los nombres de archivo que no cumplieron con el patrón o el año válido en C:\Temp\Procesados\log_errores.txt.


## ⚙️ Integración con PyQt6 (Próximamente)
Se planea desarrollar una interfaz gráfica utilizando PyQt6 que permita:

Seleccionar rutas y configurar parámetros de conexión.

Mostrar una lista de archivos válidos e inválidos antes de procesarlos.

Visualizar el log de ejecución y resultado de la inserción en la base.

Integrarse con otras funcionalidades de la organización para manejo de resoluciones.

## 🏗️ Funcionalidades en Desarrollo
Interfaz amigable para ejecutar el proceso paso a paso.

Parámetros configurables (rutas, servidor, nombre de BD) desde la GUI.

Reporte detallado en formato PDF con los resultados de la ejecución.

Manejo de excepciones mejorado (errores de red, permisos de archivos, etc.).

### 📝 Licencia
Este proyecto es de uso interno (INSSSEP) y no se distribuye públicamente.

© 2025 INSSSEP - Todos los derechos reservados.

