import os
import re
import shutil
import pyodbc
import PyPDF2
from datetime import datetime

# Configuración de la base de datos
def get_db_connection():
    server = 'sql01'
    database = 'Gestion'
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection=yes;'
    )
    return conn


# Función para copiar archivos PDF
def copy_files():
    source_dir = r'\\fs01\Resoluciones_Temp'
    dest_dir = r'C:\Temp'

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for subdir, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.pdf'):
                full_file_name = os.path.join(subdir, file)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, dest_dir)
                    print(f'Archivo {file} copiado a {dest_dir}')


# Función para extraer texto de PDF usando PyPDF2
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() or ''
        return text.strip()
    except Exception as e:
        raise Exception(f"Error al leer el archivo PDF {pdf_path}: {e}")


# Función para procesar archivos PDF y extraer datos para la base de datos
def process_files():
    dest_dir = r'C:\Temp'
    files = [f for f in os.listdir(dest_dir) if f.endswith('.pdf')]
    processed_files = []
    invalid_files = []
    current_year = datetime.now().year

    for file in files:
        file_without_extension = os.path.splitext(file)[0]
        parts = file_without_extension.split('-')

        # Verificamos que el archivo tenga exactamente tres partes (letra, actuacion, ejercicio)
        if len(parts) == 3:
            letra, actuacion, ejercicio = parts

            # Validar que el año no sea mayor al año actual
            if ejercicio.isdigit() and int(ejercicio) <= current_year:
                processed_files.append((letra, actuacion, ejercicio, file))
            else:
                invalid_files.append(file)
        else:
            invalid_files.append(file)

    return processed_files, invalid_files


# Función para insertar en la base de datos y actualizar extractos
def insert_and_update_db(processed_files):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Truncar las tablas
    cursor.execute("TRUNCATE TABLE gestion..Wilson")
    cursor.execute("TRUNCATE TABLE gestion..Wilson2")
    conn.commit()

    # Insertar en Wilson y Wilson2
    for letra, actuacion, ejercicio, file in processed_files:
        archivo = f'{letra}-{actuacion}-{ejercicio}.pdf'
        cursor.execute("INSERT INTO gestion..Wilson (archivo) VALUES (?)", (archivo,))
    
    conn.commit()

    cursor.execute("""
        INSERT INTO Wilson2 (Letra, actuacion, ejercicio)
        SELECT 
            SUBSTRING(archivo, 1, 1) AS Letra, 
            SUBSTRING(archivo, 3, 6) AS Actuacion, 
            SUBSTRING(archivo, 10, 4) AS Ejercicio 
        FROM Wilson
    """)
    conn.commit()

    # Insertar en Maestro
    cursor.execute("""
        INSERT INTO [Gestion].[dbo].[Maestro]
        ([Boca],[letra],[actuacion],[ejercicio],[apeynom],[extracto],[fech_alta],[estado],[folio],[origen_nomenc],[Subtramite])
        SELECT 
            2 AS Boca, 
            a.Letra, 
            a.Actuacion, 
            a.Ejercicio, 
            CASE 
                WHEN a.Letra = '1' THEN 'RESOLUCION DE PRESIDENCIA' 
                WHEN a.Letra = '2' THEN 'RESOLUCION DE DIRECTORIO' 
                ELSE 'DISPOSICION DE JUBILACIONES' 
            END AS apeynom,
            'Reconocimiento optico de caracteres: ' AS Extracto, 
            GETDATE() AS Fec_alta,  
            'N' AS Estado, 
            1 AS Folio, 
            100180 AS origen_nomenc, 
            900999 AS Subtramite
        FROM Wilson2 a
        WHERE NOT EXISTS (
            SELECT 1 
            FROM gestion..Maestro b 
            WHERE b.letra = a.letra 
              AND b.actuacion = a.actuacion 
              AND b.ejercicio = a.ejercicio
        )
    """)
    conn.commit()

    # Actualizar extractos en Maestro con el contenido del PDF
    for letra, actuacion, ejercicio, file in processed_files:
        pdf_path = os.path.join(r'C:\Temp', file)
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Llamamos a la función que realiza la actualización directa
        update_record(letra, actuacion, ejercicio, extracted_text, conn)

    cursor.close()
    conn.close()


# Función para actualizar directamente el campo extracto
def update_record(letra, actuacion, ejercicio, extracted_text, connection):
    """Actualiza los registros en la base de datos con el texto extraído del OCR."""
    cursor = connection.cursor()

    # Consulta SQL para seleccionar todos los registros relevantes
    select_query = """
    SELECT extracto 
    FROM Maestro
    WHERE letra = ? 
      AND actuacion = ? 
      AND ejercicio = ?
    """
    
    print(f"Buscando registros en la base de datos para letra={letra}, actuacion={actuacion}, ejercicio={ejercicio}...")
    cursor.execute(select_query, letra, actuacion, ejercicio)
    rows = cursor.fetchall()

    if rows:
        print(f"Se encontraron {len(rows)} registros coincidentes.")
        for row in rows:
            extracto = row[0]
            print(f"Estado actual del campo 'extracto': {extracto}")

            # Si el extracto es None o está vacío, lo inicializamos
            if extracto is None or extracto.strip() == '':
                new_extracto = f"Reconocimiento optico de caracteres: {extracted_text}"
            else:
                # Si el extracto ya contiene la frase, concatenamos
                if 'Reconocimiento optico de caracteres:' in extracto:
                    new_extracto = f"{extracto.strip()} {extracted_text}"
                else:
                    # De lo contrario, reemplazamos el contenido
                    new_extracto = f"Reconocimiento optico de caracteres: {extracted_text}"

            print(f"Actualizando 'extracto' a: {new_extracto}")

            # Actualización directa
            update_query = """
            UPDATE Maestro
            SET extracto = ?
            WHERE letra = ? 
              AND actuacion = ? 
              AND ejercicio = ?
            """
            cursor.execute(update_query, new_extracto, letra, actuacion, ejercicio)
            connection.commit()
            print(f"Registro actualizado para letra={letra}, actuacion={actuacion}, ejercicio={ejercicio}")
    else:
        print(f"No se encontró ningún registro para letra={letra}, actuacion={actuacion}, ejercicio={ejercicio}")


# Función para manejar colisiones de nombres de archivo en el directorio de respaldo
def handle_file_collision(file_path, backup_dir):
    base_name = os.path.basename(file_path)
    new_file_path = os.path.join(backup_dir, base_name)

    # Si el archivo ya existe, agregar un sufijo con un número secuencial
    if os.path.exists(new_file_path):
        file_name, file_ext = os.path.splitext(base_name)
        counter = 1
        while os.path.exists(new_file_path):
            new_file_name = f"{file_name}_{counter}{file_ext}"
            new_file_path = os.path.join(backup_dir, new_file_name)
            counter += 1

    return new_file_path


# Función para limpiar y mover archivos procesados
def clean_and_move_files(processed_files):
    """
    Mueve cada archivo procesado hacia su carpeta de año correspondiente:
    \\fs01\Resoluciones\<ejercicio>
    y mantiene una copia de seguridad en C:\Temp\Procesados\PDFs_BK.
    """
    source_dir = r'\\fs01\Resoluciones_Temp'
    processed_dir = r'C:\Temp\Procesados'
    backup_dir = os.path.join(processed_dir, 'PDFs_BK')

    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    registro_path = os.path.join(processed_dir, f'registro_{timestamp}.txt')

    with open(registro_path, 'w', encoding='utf-8') as registro_file:
        registro_file.write(f"Proceso ejecutado el: {timestamp}\n")
        registro_file.write("Archivos procesados:\n")

        for (letra, actuacion, ejercicio, file) in processed_files:
            src_path = os.path.join(r'C:\Temp', file)

            # Crea la carpeta basada en el año del archivo (ejercicio)
            year_dir = os.path.join(r'\\fs01\Resoluciones', ejercicio)
            if not os.path.exists(year_dir):
                os.makedirs(year_dir)

            # Realiza copia de seguridad
            dest_backup_path = handle_file_collision(src_path, backup_dir)
            shutil.copy(src_path, dest_backup_path)

            # Mueve el archivo a la carpeta del año correspondiente
            dest_path_year = os.path.join(year_dir, file)
            # Opcional: manejar colisión también en year_dir si lo deseas
            if os.path.exists(dest_path_year):
                # Simple ejemplo de renombrado secuencial para evitar colisiones
                file_name, file_ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(dest_path_year):
                    new_file = f"{file_name}_{counter}{file_ext}"
                    dest_path_year = os.path.join(year_dir, new_file)
                    counter += 1

            shutil.move(src_path, dest_path_year)

            registro_file.write(
                f"{file} copiado en BK -> {dest_backup_path} y movido a {dest_path_year}\n"
            )

    # Eliminar los archivos en el directorio original
    for subdir, dirs, files in os.walk(source_dir, topdown=False):
        for file in files:
            if file.endswith('.pdf'):
                full_file_name = os.path.join(subdir, file)
                if os.path.isfile(full_file_name):
                    os.remove(full_file_name)
        for dir in dirs:
            dir_path = os.path.join(subdir, dir)
            # Borra carpetas vacías
            if not os.listdir(dir_path):
                os.rmdir(dir_path)


# Función para generar log de archivos inválidos
def generate_invalid_files_log(invalid_files):
    log_dir = r'C:\Temp\Procesados'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, 'log_errores.txt')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"\nErrores encontrados el: {timestamp}\n")
        if invalid_files:
            log_file.write("Archivos con nombres incorrectos o años no válidos:\n")
            for file in invalid_files:
                log_file.write(f"- {file}\n")


# Flujo principal para ejecutar el proceso completo
def main():
    copy_files()
    processed_files, invalid_files = process_files()

    if invalid_files:
        print("\nArchivos con nombres incorrectos o años no válidos:")
        for file in invalid_files:
            print(f"- {file}")
        generate_invalid_files_log(invalid_files)

    if processed_files:
        insert_and_update_db(processed_files)
        clean_and_move_files(processed_files)
    else:
        print("No se encontraron archivos válidos para procesar.")


if __name__ == "__main__":
    main()
