# main.py
import os
import shutil
import pyodbc
import PyPDF2
from datetime import datetime

def get_db_connection():
    server = 'sql01'
    database = 'Gestion'
    conn = pyodbc.connect(
        f'DRIVER={{SQL Server Native Client 10.0}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection=yes;'
    )
    return conn

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

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
        return text.strip()
    except Exception as e:
        raise Exception(f"Error al leer el archivo PDF {pdf_path}: {e}")

def process_files():
    dest_dir = r'C:\Temp'
    files = [f for f in os.listdir(dest_dir) if f.endswith('.pdf')]
    processed_files = []
    invalid_files = []
    current_year = datetime.now().year

    for file in files:
        file_without_extension = os.path.splitext(file)[0]
        parts = file_without_extension.split('-')
        if len(parts) == 3:
            letra, actuacion, ejercicio = parts
            if ejercicio.isdigit() and int(ejercicio) <= current_year:
                processed_files.append((letra, actuacion, ejercicio, file))
            else:
                invalid_files.append(file)
        else:
            invalid_files.append(file)

    return processed_files, invalid_files

def insert_and_update_db(processed_files):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE gestion..Wilson")
    cursor.execute("TRUNCATE TABLE gestion..Wilson2")
    conn.commit()

    for letra, actuacion, ejercicio, file in processed_files:
        archivo = f'{letra}-{actuacion}-{ejercicio}.pdf'
        cursor.execute("INSERT INTO gestion..Wilson (archivo) VALUES (?)", (archivo,))
    conn.commit()

    cursor.execute("""
        INSERT INTO Wilson2 (Letra, actuacion, ejercicio)
        SELECT 
            SUBSTRING(archivo, 1, 1),
            SUBSTRING(archivo, 3, 6),
            SUBSTRING(archivo, 10, 4)
        FROM Wilson
    """)
    conn.commit()

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

    for letra, actuacion, ejercicio, file in processed_files:
        pdf_path = os.path.join(r'C:\Temp', file)
        extracted_text = extract_text_from_pdf(pdf_path)
        update_record(letra, actuacion, ejercicio, extracted_text, conn)

    cursor.close()
    conn.close()

def update_record(letra, actuacion, ejercicio, extracted_text, connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT extracto FROM Maestro
        WHERE letra = ? AND actuacion = ? AND ejercicio = ?
    """, letra, actuacion, ejercicio)

    rows = cursor.fetchall()
    if rows:
        for row in rows:
            extracto = row[0] or ''
            if 'Reconocimiento optico de caracteres:' in extracto:
                new_extracto = f"{extracto.strip()} {extracted_text}"
            else:
                new_extracto = f"Reconocimiento optico de caracteres: {extracted_text}"

            cursor.execute("""
                UPDATE Maestro SET extracto = ?
                WHERE letra = ? AND actuacion = ? AND ejercicio = ?
            """, new_extracto, letra, actuacion, ejercicio)
            connection.commit()

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

def clean_and_move_files(processed_files):
    source_dir = r'\\fs01\Resoluciones_Temp'
    processed_dir = r'C:\Temp\Procesados'
    backup_dir = os.path.join(processed_dir, 'PDFs_BK')
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    registro_path = os.path.join(processed_dir, f'registro_{timestamp}.txt')

    with open(registro_path, 'w', encoding='utf-8') as registro_file:
        registro_file.write(f"Proceso ejecutado el: {timestamp}\nArchivos procesados:\n")

        for (letra, actuacion, ejercicio, file) in processed_files:
            src_path = os.path.join(r'C:\Temp', file)
            year_dir = os.path.join(r'\\fs01\Resoluciones', ejercicio)
            os.makedirs(year_dir, exist_ok=True)

            dest_backup_path = handle_file_collision(src_path, backup_dir)
            shutil.copy(src_path, dest_backup_path)

            dest_path_year = os.path.join(year_dir, file)
            if os.path.exists(dest_path_year):
                file_name, file_ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(dest_path_year):
                    new_file = f"{file_name}_{counter}{file_ext}"
                    dest_path_year = os.path.join(year_dir, new_file)
                    counter += 1

            shutil.move(src_path, dest_path_year)
            registro_file.write(f"{file} copiado en BK -> {dest_backup_path} y movido a {dest_path_year}\n")

    for subdir, dirs, files in os.walk(source_dir, topdown=False):
        for file in files:
            if file.endswith('.pdf'):
                os.remove(os.path.join(subdir, file))
        for dir in dirs:
            dir_path = os.path.join(subdir, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)

def generate_invalid_files_log(invalid_files):
    log_dir = r'C:\Temp\Procesados'
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'log_errores.txt')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"\nErrores encontrados el: {timestamp}\n")
        for file in invalid_files:
            log_file.write(f"- {file}\n")

def ejecutar_proceso_completo():
    copy_files()
    processed_files, invalid_files = process_files()
    if invalid_files:
        generate_invalid_files_log(invalid_files)
    if processed_files:
        insert_and_update_db(processed_files)
        clean_and_move_files(processed_files)
        return True
    return False
