# main.py
import os
import shutil
import json
import time
from datetime import timedelta, datetime
import pyodbc
import PyPDF2

def get_db_connection():
    server = 'sql01'
    database = 'Gestion'
    drivers = [
        "SQL Server Native Client 11.0",
        "SQL Server",
        "SQL Server Native Client 10.0"
    ]
    for driver in drivers:
        try:
            conn = pyodbc.connect(
                f'DRIVER={{{driver}}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'Trusted_Connection=yes;'
            )
            print(f"Conexión exitosa con el driver: {driver}")
            return conn
        except pyodbc.Error:
            print(f"No se pudo conectar con el driver: {driver}. Intentando con el siguiente...")
            continue
    raise Exception("No se pudo conectar a la base de datos con ninguno de los drivers disponibles.")

def load_config():
    """Carga la configuración desde el archivo JSON"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        # Si hay un error, devuelve la configuración predeterminada
        print(f"Error al cargar la configuración: {e}")
        return {
            "temp_dir": "C:\\Temp",
            "processed_dir": "C:\\Temp\\Procesados",
            "backup_dir": "C:\\Temp\\Procesados\\PDFs_BK",
            "source_dir": "\\\\fs01\\Resoluciones_Temp",
            "target_dir": "\\\\fs01\\Resoluciones",
            "cleanup_days": 60,
            "progress_steps": [10, 25, 50, 75, 100]
        }

def copy_files(config=None):
    if config is None:
        config = load_config()
    
    source_dir = config["source_dir"]
    dest_dir = config["temp_dir"]
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Directorio temporal creado: {dest_dir}")

    print(f"Buscando archivos PDF en: {source_dir}")
    archivos_encontrados = 0
    
    for subdir, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.pdf'):
                full_file_name = os.path.join(subdir, file)
                if os.path.isfile(full_file_name):
                    print(f"Copiando: {full_file_name} -> {dest_dir}")
                    shutil.copy(full_file_name, dest_dir)
                    archivos_encontrados += 1
    
    print(f"Total de archivos copiados: {archivos_encontrados}")
    return archivos_encontrados

def extract_text_from_pdf(pdf_path):
    try:
        print(f"Extrayendo texto del PDF: {pdf_path}")
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            total_pages = len(reader.pages)
            print(f"El PDF tiene {total_pages} páginas")
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ''
                text += page_text
                print(f"Página {i+1}/{total_pages}: {len(page_text)} caracteres extraídos")
                
        text_length = len(text.strip())
        print(f"Extracción completada: {text_length} caracteres totales")
        return text.strip()
    except Exception as e:
        print(f"Error al leer el archivo PDF {pdf_path}: {e}")
        raise Exception(f"Error al leer el archivo PDF {pdf_path}: {e}")

def process_files(config=None):
    if config is None:
        config = load_config()
        
    dest_dir = config["temp_dir"]
    files = [f for f in os.listdir(dest_dir) if f.endswith('.pdf')]
    processed_files = []
    invalid_files = []
    current_year = datetime.now().year
    
    print(f"Procesando {len(files)} archivos en {dest_dir}")
    
    for file in files:
        print(f"Analizando archivo: {file}")
        file_without_extension = os.path.splitext(file)[0]
        parts = file_without_extension.split('-')
        if len(parts) == 3:
            letra, actuacion, ejercicio = parts
            if ejercicio.isdigit() and int(ejercicio) <= current_year:
                print(f"Archivo válido: Letra={letra}, Actuación={actuacion}, Ejercicio={ejercicio}")
                processed_files.append((letra, actuacion, ejercicio, file))
            else:
                print(f"Archivo inválido (ejercicio no válido): {file}")
                invalid_files.append(file)
        else:
            print(f"Archivo inválido (formato incorrecto): {file}")
            invalid_files.append(file)

    print(f"Total archivos válidos: {len(processed_files)}")
    print(f"Total archivos inválidos: {len(invalid_files)}")
    
    return processed_files, invalid_files

def insert_and_update_db(processed_files, config=None):
    if config is None:
        config = load_config()
        
    print("Iniciando conexión con la base de datos...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Limpiando tablas temporales...")
    cursor.execute("TRUNCATE TABLE gestion..Wilson")
    cursor.execute("TRUNCATE TABLE gestion..Wilson2")
    conn.commit()
    print("Tablas temporales limpiadas correctamente.")

    print("Insertando registros en tabla Wilson...")
    for letra, actuacion, ejercicio, file in processed_files:
        archivo = f'{letra}-{actuacion}-{ejercicio}.pdf'
        print(f"Insertando archivo: {archivo}")
        cursor.execute("INSERT INTO gestion..Wilson (archivo) VALUES (?)", (archivo,))
    conn.commit()
    print("Registros insertados en tabla Wilson correctamente.")

    print("Procesando datos para tabla Wilson2...")
    cursor.execute("""
        INSERT INTO Wilson2 (Letra, actuacion, ejercicio)
        SELECT 
            SUBSTRING(archivo, 1, 1),
            SUBSTRING(archivo, 3, 6),
            SUBSTRING(archivo, 10, 4)
        FROM Wilson
    """)
    conn.commit()
    print("Datos procesados y almacenados en tabla Wilson2 correctamente.")

    print("Actualizando tabla Maestro con nuevos registros...")
    cursor.execute("""
        INSERT INTO [Gestion].[dbo].[Maestro]
        ([Boca],[letra],[actuacion],[ejercicio],[apeynom],[extracto],[fech_alta],[estado],[folio],[origen_nomenc],[Subtramite])
        SELECT 
            2, a.Letra, a.Actuacion, a.Ejercicio,
            CASE 
                WHEN a.Letra = '1' THEN 'RESOLUCION DE PRESIDENCIA' 
                WHEN a.Letra = '2' THEN 'RESOLUCION DE DIRECTORIO' 
                ELSE 'DISPOSICION DE JUBILACIONES' 
            END,
            'Reconocimiento optico de caracteres: ', GETDATE(), 'N', 1, 100180, 900999
        FROM Wilson2 a
        WHERE NOT EXISTS (
            SELECT 1 FROM gestion..Maestro b
            WHERE b.letra = a.letra AND b.actuacion = a.actuacion AND b.ejercicio = a.ejercicio
        )
    """)
    conn.commit()
    print("Tabla Maestro actualizada correctamente.")

    print("Extrayendo texto de los PDFs y actualizando registros...")
    total_actualizados = 0
    for letra, actuacion, ejercicio, file in processed_files:
        pdf_path = os.path.join(config["temp_dir"], file)
        print(f"Procesando texto del PDF: {pdf_path}")
        try:
            extracted_text = extract_text_from_pdf(pdf_path)
            print(f"Texto extraído correctamente. Actualizando registro...")
            updated = update_record(letra, actuacion, ejercicio, extracted_text, conn)
            if updated:
                total_actualizados += 1
        except Exception as e:
            print(f"Error al procesar {pdf_path}: {e}")
    
    print(f"Proceso de extracción y actualización completado. Total actualizados: {total_actualizados}")
    cursor.close()
    conn.close()
    print("Conexión con la base de datos cerrada.")

def update_record(letra, actuacion, ejercicio, extracted_text, connection):
    cursor = connection.cursor()
    print(f"Buscando registro para actualizar: letra={letra}, actuacion={actuacion}, ejercicio={ejercicio}")
    
    cursor.execute("""
        SELECT extracto FROM Maestro
        WHERE letra = ? AND actuacion = ? AND ejercicio = ?
    """, letra, actuacion, ejercicio)

    rows = cursor.fetchall()
    if rows:
        print(f"Se encontraron {len(rows)} registros para actualizar")
        actualizados = 0
        for row in rows:
            extracto = row[0] or ''
            if 'Reconocimiento optico de caracteres:' in extracto:
                new_extracto = f"{extracto.strip()} {extracted_text}"
            else:
                new_extracto = f"Reconocimiento optico de caracteres: {extracted_text}"

            print(f"Actualizando extracto del registro...")
            cursor.execute("""
                UPDATE Maestro SET extracto = ?
                WHERE letra = ? AND actuacion = ? AND ejercicio = ?
            """, new_extracto, letra, actuacion, ejercicio)
            connection.commit()
            actualizados += 1
        
        print(f"Total de registros actualizados: {actualizados}")
        return actualizados > 0
    else:
        print(f"No se encontraron registros para actualizar")
        return False

def handle_file_collision(file_path, backup_dir):
    base_name = os.path.basename(file_path)
    new_file_path = os.path.join(backup_dir, base_name)
    if os.path.exists(new_file_path):
        file_name, file_ext = os.path.splitext(base_name)
        counter = 1
        while os.path.exists(new_file_path):
            new_file_name = f"{file_name}_{counter}{file_ext}"
            new_file_path = os.path.join(backup_dir, new_file_name)
            counter += 1
    return new_file_path

def clean_and_move_files(processed_files, config=None):
    if config is None:
        config = load_config()
        
    source_dir = config["source_dir"]
    target_dir = config["target_dir"]
    processed_dir = config["processed_dir"]
    backup_dir = config["backup_dir"]
    temp_dir = config["temp_dir"]
    
    print(f"Preparando directorios para mover archivos procesados...")
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Directorios creados: {processed_dir}, {backup_dir}")

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    registro_path = os.path.join(processed_dir, f'registro_{timestamp}.txt')
    print(f"Creando archivo de registro: {registro_path}")

    with open(registro_path, 'w', encoding='utf-8') as registro_file:
        registro_file.write(f"Proceso ejecutado el: {timestamp}\nArchivos procesados:\n")
        print(f"Moviendo {len(processed_files)} archivos procesados...")

        for (letra, actuacion, ejercicio, file) in processed_files:
            src_path = os.path.join(temp_dir, file)
            year_dir = os.path.join(target_dir, ejercicio)
            os.makedirs(year_dir, exist_ok=True)
            print(f"Directorio de destino para año {ejercicio}: {year_dir}")

            dest_backup_path = handle_file_collision(src_path, backup_dir)
            print(f"Copiando archivo a backup: {src_path} -> {dest_backup_path}")
            shutil.copy(src_path, dest_backup_path)

            dest_path_year = os.path.join(year_dir, file)
            if os.path.exists(dest_path_year):
                file_name, file_ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(dest_path_year):
                    new_file = f"{file_name}_{counter}{file_ext}"
                    dest_path_year = os.path.join(year_dir, new_file)
                    counter += 1
                print(f"Archivo existente, renombrando a: {dest_path_year}")
            else:
                print(f"Moviendo archivo a destino final: {src_path} -> {dest_path_year}")

            shutil.move(src_path, dest_path_year)
            registro_file.write(f"{file} copiado en BK -> {dest_backup_path} y movido a {dest_path_year}\n")

    print(f"Limpiando archivos originales en directorio fuente: {source_dir}")
    archivos_eliminados = 0
    for subdir, dirs, files in os.walk(source_dir, topdown=False):
        for file in files:
            if file.endswith('.pdf'):
                file_path = os.path.join(subdir, file)
                print(f"Eliminando archivo original: {file_path}")
                os.remove(file_path)
                archivos_eliminados += 1
        for dir in dirs:
            dir_path = os.path.join(subdir, dir)
            if not os.listdir(dir_path):
                print(f"Eliminando directorio vacío: {dir_path}")
                os.rmdir(dir_path)
    
    print(f"Total de archivos originales eliminados: {archivos_eliminados}")            
    return registro_path

def generate_invalid_files_log(invalid_files, config=None):
    if config is None:
        config = load_config()
        
    log_dir = config["processed_dir"]
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'log_errores.txt')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    print(f"Generando log de archivos inválidos: {log_path}")
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"\nErrores encontrados el: {timestamp}\n")
        for file in invalid_files:
            log_file.write(f"- {file}\n")
            print(f"Archivo inválido registrado: {file}")
    
    print(f"Log de errores guardado con {len(invalid_files)} archivos registrados")
    return log_path

def cleanup_old_files(config=None):
    """Elimina archivos temporales más antiguos que el número de días especificado"""
    if config is None:
        config = load_config()
    
    cleanup_days = config.get("cleanup_days", 60)
    temp_dir = config["temp_dir"]
    processed_dir = config["processed_dir"]
    backup_dir = config["backup_dir"]
    
    print(f"Iniciando limpieza de archivos antiguos (más de {cleanup_days} días)...")
    cutoff_date = datetime.now() - timedelta(days=cleanup_days)
    print(f"Fecha límite para limpieza: {cutoff_date.strftime('%Y-%m-%d')}")
    
    deleted_files = []
    
    # Función auxiliar para eliminar archivos antiguos en una carpeta
    def delete_old_files_in_dir(directory):
        local_deleted = []
        if os.path.exists(directory):
            print(f"Analizando directorio: {directory}")
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_mod_time < cutoff_date:
                        print(f"Eliminando archivo antiguo: {file_path} (modificado: {file_mod_time.strftime('%Y-%m-%d')})")
                        os.remove(file_path)
                        local_deleted.append(file_path)
        return local_deleted
    
    # Eliminar archivos antiguos en carpetas temporales
    print("Limpiando archivos en directorio temporal...")
    deleted_files.extend(delete_old_files_in_dir(temp_dir))
    
    print("Limpiando archivos en directorio de backup...")
    deleted_files.extend(delete_old_files_in_dir(backup_dir))
    
    # Eliminar logs y registros antiguos
    print("Limpiando logs y registros antiguos...")
    deleted_files.extend(delete_old_files_in_dir(processed_dir))
    
    # Registrar la limpieza
    if deleted_files:
        log_path = os.path.join(processed_dir, 'cleanup_log.txt')
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        print(f"Generando log de limpieza: {log_path}")
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"\nLimpieza realizada el: {timestamp}\n")
            log_file.write(f"Se eliminaron {len(deleted_files)} archivos más antiguos de {cleanup_days} días:\n")
            for file in deleted_files:
                log_file.write(f"- {file}\n")
        
        print(f"Limpieza completada. Se eliminaron {len(deleted_files)} archivos.")
        return log_path, len(deleted_files)
    
    print("Limpieza completada. No se encontraron archivos para eliminar.")
    return None, 0

def ejecutar_proceso_completo():
    print("=== INICIANDO PROCESO COMPLETO ===")
    config = load_config()
    print(f"Configuración cargada: {config}")
    
    try:
        # Limpiar archivos antiguos antes de comenzar
        print("Iniciando limpieza de archivos antiguos...")
        cleanup_log, deleted_count = cleanup_old_files(config)
        if cleanup_log:
            print(f"Limpieza completada, log generado en: {cleanup_log}")
        
        print("Copiando archivos desde origen...")
        archivos_copiados = copy_files(config)
        print(f"Copia completada: {archivos_copiados} archivos copiados")
        
        print("Procesando archivos...")
        processed_files, invalid_files = process_files(config)
        print(f"Procesamiento completado: {len(processed_files)} válidos, {len(invalid_files)} inválidos")
        
        log_path = None
        if invalid_files:
            print("Generando log de archivos inválidos...")
            log_path = generate_invalid_files_log(invalid_files, config)
            
        registro_path = None
        if processed_files:
            print("Actualizando base de datos...")
            insert_and_update_db(processed_files, config)
            
            print("Moviendo archivos procesados...")
            registro_path = clean_and_move_files(processed_files, config)
            print(f"Proceso completado con éxito. Registro generado en: {registro_path}")
            return True, registro_path, log_path, cleanup_log, deleted_count
        else:
            print("No se encontraron archivos válidos para procesar.")
            return False, None, log_path, cleanup_log, deleted_count
    except Exception as e:
        print(f"ERROR EN EL PROCESO: {e}")
        import traceback
        print(traceback.format_exc())
        return False, None, None, None, 0
    finally:
        print("=== PROCESO FINALIZADO ===")    

