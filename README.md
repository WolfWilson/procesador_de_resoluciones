# 🗂️ Procesador de Resoluciones

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?style=for-the-badge&logo=qt)
![SQL Server](https://img.shields.io/badge/Base%20de%20Datos-SQL%20Server-red?style=for-the-badge&logo=microsoftsqlserver)
![Windows](https://img.shields.io/badge/OS-Windows%2010%2B-lightgrey?style=for-the-badge&logo=windows)
![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-orange?style=for-the-badge)

---

Este proyecto **Procesador de Resoluciones** automatiza la gestión de documentos PDF en un entorno estructurado con carpetas de red y base de datos **SQL Server**.  
Incluye validación de nombres de archivo, extracción de texto desde PDFs, inserción en tablas de base de datos y mantenimiento automatizado de directorios, con una arquitectura preparada para integrarse con **PyQt6**.

---

## 🚀 Características Principales

- 📥 Copiado y verificación de archivos PDF desde un origen de red hacia un directorio temporal.
- 🧾 Validación de nombres de archivo según el patrón: `<Letra>-<Actuacion>-<Ejercicio>.pdf`.
- 🗃️ Inserción en tablas **Wilson**, **Wilson2** y actualización de la tabla principal **Maestro**.
- 📚 Extracción de texto desde los PDFs utilizando **PyPDF2**, almacenando en el campo `extracto`.
- 🚫 Registro de errores y generación de logs para archivos con nombre inválido o año no reconocido.
- 🧹 Traslado automático y backup de archivos procesados, con logs detallados.
- 🖼️ Infraestructura lista para integrar una interfaz gráfica con **PyQt6** *(en desarrollo)*.

---

## 📁 Estructura del Proyecto

```plaintext
Procesador_Resoluciones/
├── main.py                # Punto de entrada principal
├── README.md              # Documentación del proyecto
├── requirements.txt       # Dependencias del entorno

# Estructura futura:
├── gui/                   # Interfaces gráficas PyQt6
├── modules/               # Lógica del proceso y funciones auxiliares
└── assets/                # Recursos (íconos, imágenes, estilos)

```

## 🔧 Requisitos y Configuración
```plaintext
Python 3.12+

Dependencias (ver requirements.txt):
- pyodbc
- PyPDF2
- PyQt6

Requisitos de entorno:
- SQL Server con acceso habilitado mediante autenticación de Windows
- Directorios existentes:
  • \\fs01\Resoluciones_Temp   → Origen de los PDFs
  • C:\Temp                    → Carpeta temporal de trabajo
  • \\fs01\Resoluciones        → Destino final organizado por año

```

## 📦 **Instalación y Uso**

### 1️⃣ **Clonar el repositorio**
```sh
git clone https://github.com/WolfWilson/procesador_de_resoluciones.git
cd procesador_de_resoluciones
```

###  2️⃣ **Crear y activar un entorno virtual**

```sh
python -m venv venv
```

###  3️⃣ **Instalar dependencias**

```sh
pip install pyodbc
pip install pyqt6
pip install pypdf2
```
###4️⃣ **Ejecutar la aplicación**

```sh
python main.py

```


## 🧩 Flujo de Trabajo Simplificado


copy_files()
🔸 Copia todos los archivos PDF desde \\fs01\Resoluciones_Temp hacia C:\Temp.

process_files()
🔸 Valida que los archivos tengan el formato <Letra>-<Actuacion>-<Ejercicio>.pdf.
🔸 Filtra y descarta archivos con nombres no válidos.

insert_and_update_db()
🔸 Elimina registros previos en las tablas Wilson y Wilson2.
🔸 Inserta nuevos registros en ambas tablas con información básica.
🔸 Inserta o actualiza datos en la tabla Maestro, incluyendo el extracto del texto del PDF.

clean_and_move_files()
🔸 Mueve los archivos procesados a \\fs01\Resoluciones\<Ejercicio>.
🔸 Crea un respaldo en C:\Temp\Procesados\PDFs_BK.
🔸 Registra los movimientos en un archivo de log con timestamp.

generate_invalid_files_log()
🔸 Registra en C:\Temp\Procesados\log_errores.txt los nombres de archivos rechazados por patrón incorrecto o año inválido.



## ⚙️ Integración con PyQt6 (Próximamente)

Se está diseñando una interfaz gráfica utilizando PyQt6, orientada a facilitar la interacción del usuario con el proceso de manejo de resoluciones. Esta GUI ofrecerá una experiencia más amigable, con múltiples funcionalidades clave:

📂 Selección de Rutas y Parámetros de Conexión
↪ Permitirá definir las ubicaciones de entrada/salida de los archivos y configurar detalles de conexión a la base de datos.

📋 Previsualización de Archivos Válidos/Inválidos
↪ Antes de ejecutar el proceso, la interfaz mostrará una lista clasificada de archivos detectados según el patrón esperado.

🧾 Visualización de Logs en Tiempo Real
↪ Se podrá observar el log de ejecución directamente desde la interfaz, incluyendo los resultados de inserción y procesamiento.

🔗 Integración con Otras Funcionalidades Organizacionales
↪ La aplicación buscará conectarse con herramientas ya existentes para una gestión centralizada de resoluciones.


## 🏗️ Funcionalidades en Desarrollo

Estas son las mejoras en curso que enriquecerán tanto la robustez del sistema como la experiencia del usuario:

🪜 Ejecución Paso a Paso desde la Interfaz
↪ Permite ejecutar cada etapa del flujo de forma controlada, ideal para depuración o uso manual.

⚙️ Configuración Dinámica de Parámetros
↪ Desde la GUI se podrá ajustar rutas, servidor, nombre de base de datos y otros parámetros sin modificar el código fuente.

📑 Generación de Reportes Detallados en PDF
↪ Al finalizar el proceso, se podrá exportar un informe completo con resultados, estadísticas y errores encontrados.

🚨 Manejo Mejorado de Excepciones
↪ Se incorporarán controles para errores comunes como fallas de red, permisos de archivos, y problemas con el acceso a la base de datos.



### 📝 Licencia
Este proyecto es de uso interno (INSSSEP) y no se distribuye públicamente.

© 2025 INSSSEP - Todos los derechos reservados.

