# 🗂️ Procesador de Resoluciones

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?style=for-the-badge&logo=qt)
![SQL Server](https://img.shields.io/badge/Base%20de%20Datos-SQL%20Server-red?style=for-the-badge&logo=microsoftsqlserver)
![Windows](https://img.shields.io/badge/OS-Windows%2010%2B-lightgrey?style=for-the-badge&logo=windows)
![Estado](https://img.shields.io/badge/Estado-Estable-brightgreen?style=for-the-badge)

---

Automatiza la gestión de documentos PDF de resoluciones institucionales: copia desde carpetas de red, valida nomenclatura, extrae texto, actualiza **SQL Server** y organiza los archivos en su destino final. Incluye interfaz gráfica **PyQt6** con log en tiempo real, resumen de proceso y manejo seguro de archivos con nomenclatura incorrecta.

---

## 🚀 Características

- 📥 **Copia y manifiesto**: copia todos los PDFs desde `\\fs01\Resoluciones_Temp` hacia un directorio temporal y genera un manifiesto JSON del lote.
- 🧾 **Validación estricta de nomenclatura**: cada archivo debe cumplir el patrón `<Letra>-<Actuacion>-<Ejercicio>.pdf` con reglas precisas (ver sección de Nomenclatura).
- ⚠️ **Protección de archivos inválidos**: los archivos con nombre incorrecto **no se eliminan del origen**. Quedan en `source_dir` para que el usuario los corrija y vuelva a ejecutar el proceso.
- 🗃️ **Base de datos SQL Server**: inserta en tablas `Wilson`, `Wilson2` y actualiza la tabla principal `Maestro` con texto extraído del PDF por OCR (PyPDF2).
- 📦 **Backup y organización**: mueve los archivos procesados a `PDFs_BK` y los copia al destino final organizados por año (`\\fs01\Resoluciones\<año>`).
- 🧹 **Limpieza automática**: al inicio de cada ejecución elimina archivos temporales más antiguos que `cleanup_days` días (configurable).
- 🖥️ **Interfaz gráfica PyQt6**: log en tiempo real con colores por categoría, barra de progreso, botón para abrir carpeta de procesados y diálogo de resumen al finalizar.
- 📋 **Resumen final**: al terminar se muestra un cuadro con totales de archivos procesados/inválidos y el detalle de cada problema encontrado.
- 🪵 **Logs persistentes**: errores de nomenclatura en `log_errores.txt`, registro de movimientos con timestamp y log de limpieza.

---

## 📁 Estructura del Proyecto

```plaintext
procesador_de_resoluciones/
├── launcher.py          # Punto de entrada: GUI PyQt6 + hilo de procesamiento
├── main.py              # Lógica completa del proceso (sin GUI)
├── config.json          # Configuración de rutas y parámetros
├── build.bat            # Script de compilación con PyInstaller
├── requirements.txt     # Dependencias del entorno
├── README.md
├── gui/
│   ├── main_window.py   # Ventana alternativa (uso interno/pruebas)
│   └── style.py         # Hoja de estilos PyQt6
├── modules/
│   ├── db_conexion.py
│   └── resource_manager.py  # Carga de íconos y recursos empaquetados
└── assets/
    └── icon.ico         # Ícono de la aplicación
```

---

## 🧾 Nomenclatura de Archivos

Los PDFs deben seguir exactamente el patrón:

```
<Letra>-<Actuacion>-<Ejercicio>.pdf
```

| Campo       | Regla                                          | Ejemplo  |
|-------------|------------------------------------------------|----------|
| `Letra`     | Un único dígito numérico (`1`, `2`, `3`, …)    | `2`      |
| `Actuacion` | Exactamente **6 dígitos** numéricos            | `000590` |
| `Ejercicio` | Año numérico ≤ año actual                      | `2026`   |

**Ejemplos válidos:** `1-000123-2026.pdf`, `2-000590-2025.pdf`  
**Ejemplos inválidos:**
- `E-000590-2026.pdf` → letra no numérica
- `2-00590-2026.pdf` → actuación con 5 dígitos (falta un cero)
- `2-000590-2035.pdf` → ejercicio en el futuro

Cuando se detecta un archivo inválido el sistema informa el motivo exacto en el log y **lo conserva intacto en el origen** para su corrección.

---

## ⚙️ Configuración (`config.json`)

```json
{
    "temp_dir":       "C:\\Temp",
    "processed_dir":  "C:\\Temp\\Procesados",
    "backup_dir":     "C:\\Temp\\Procesados\\PDFs_BK",
    "source_dir":     "\\\\fs01\\Resoluciones_Temp",
    "target_dir":     "\\\\fs01\\Resoluciones",
    "cleanup_days":   60,
    "progress_steps": [10, 25, 50, 75, 100]
}
```

| Clave           | Descripción                                                      |
|-----------------|------------------------------------------------------------------|
| `temp_dir`      | Directorio de trabajo local donde se copian los PDFs            |
| `processed_dir` | Carpeta de logs y registros de procesamiento                    |
| `backup_dir`    | Backup local de PDFs procesados                                 |
| `source_dir`    | Origen de red donde se depositan los PDFs nuevos                |
| `target_dir`    | Destino final en red, organizado por subdirectorio de año       |
| `cleanup_days`  | Días de antigüedad para eliminar archivos temporales            |
| `progress_steps`| Valores de la barra de progreso en cada etapa                   |

---

## 🔧 Requisitos

```plaintext
Python 3.12+
Windows 10+
SQL Server con autenticación de Windows habilitada
Drivers ODBC: "SQL Server Native Client 11.0" / "SQL Server" / "SQL Server Native Client 10.0"
```

**Dependencias Python:**
```plaintext
pyodbc
PyPDF2
PyQt6
```

---

## 📦 Instalación y Uso

### 1. Clonar el repositorio
```sh
git clone https://github.com/WolfWilson/procesador_de_resoluciones.git
cd procesador_de_resoluciones
```

### 2. Crear y activar entorno virtual
```sh
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```sh
pip install pyodbc PyPDF2 pyqt6
```

### 4. Ejecutar la aplicación
```sh
python launcher.py
```

---

## 🔄 Flujo de Trabajo

```plaintext
1. cleanup_old_files()
   └─ Elimina del temp/backup/logs archivos más antiguos de cleanup_days días.

2. copy_files()
   └─ Copia todos los PDFs de source_dir → temp_dir.
   └─ Genera last_run_manifest.json con la lista del lote.

3. process_files()
   └─ Valida cada archivo contra la nomenclatura.
   └─ Archivos válidos   → processed_files (lista para DB y movimiento).
   └─ Archivos inválidos → invalid_files  (se informa motivo, NO se tocan).

4. generate_invalid_files_log()   [solo si hay inválidos]
   └─ Imprime bloque visible en log con detalle de cada problema.
   └─ Persiste en C:\Temp\Procesados\log_errores.txt (modo append).

5. insert_and_update_db()
   └─ TRUNCATE Wilson, Wilson2.
   └─ INSERT en Wilson y Wilson2 con los valores ya validados por Python.
   └─ INSERT en Maestro solo registros que no existan (WHERE NOT EXISTS).
   └─ Extrae texto de cada PDF (PyPDF2) y actualiza campo extracto en Maestro.

6. clean_and_move_files()
   └─ PDF procesado  → movido a backup_dir, copiado a target_dir/<año>/.
   └─ PDF inválido   → copia temporal eliminada de temp_dir.
   └─ Origen (source_dir) → se eliminan SOLO los PDFs procesados exitosamente.
                            Los inválidos permanecen para corrección manual.
   └─ Genera registro_<timestamp>.txt con detalle de movimientos.

7. _construir_resumen()
   └─ Imprime bloque de resumen al final del log.
   └─ Se muestra en ventana modal (Consolas) que el usuario debe aceptar.
```

---

## 🖥️ Interfaz Gráfica

La aplicación corre como ejecutable con ventana PyQt6:

| Elemento          | Descripción                                                         |
|-------------------|---------------------------------------------------------------------|
| **Procesar**      | Muestra confirmación y lanza el proceso en hilo separado            |
| **Abrir Procesados** | Abre el explorador en la carpeta de logs/registros             |
| **Limpiar Log**   | Borra el contenido del área de log en pantalla                      |
| **Barra de progreso** | Avanza en los pasos definidos en `progress_steps`             |
| **Log en tiempo real** | Código de colores: 🔴 error · 🟢 éxito · 🟡 advertencia · 🔵 archivo · 🟣 base de datos |
| **Resumen final** | Ventana modal con totales y detalle de archivos problemáticos       |

---

## 🛠️ Compilar el Ejecutable

Ejecutar `build.bat` desde la raíz del proyecto (activa el venv automáticamente):

```bat
build.bat
```

O manualmente:

```sh
pyinstaller --onefile --windowed --name "Procesador de Resoluciones" --distpath "C:\My Software Folder" --icon="assets/icon.ico" --add-data "assets;assets" --add-data "config.json;." launcher.py
```

El ejecutable generado queda en `C:\My Software Folder\Procesador de Resoluciones.exe`.  
`build.bat` elimina versiones anteriores y limpia los directorios `build/` y `dist/` antes de cada compilación.

---

## 📂 Archivos de Log Generados

| Archivo                            | Contenido                                              |
|------------------------------------|--------------------------------------------------------|
| `last_run_manifest.json`           | Lista de PDFs del último lote copiado                  |
| `registro_<timestamp>.txt`         | Detalle de cada archivo movido/copiado en esa ejecución|
| `log_errores.txt`                  | Historial acumulado de archivos con nomenclatura inválida |
| `cleanup_log.txt`                  | Historial de archivos eliminados por antigüedad        |

---

### 📝 Licencia
Este proyecto es de uso interno (INSSSEP) y no se distribuye públicamente.

© 2025 INSSSEP — Todos los derechos reservados.

