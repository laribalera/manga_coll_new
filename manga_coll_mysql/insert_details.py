import json
import mysql.connector

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# insert dados na tabela manga_collection.manga_details
def insert_data(data, conn):
    cursor = conn.cursor()
    for item in data:
        filename = item.get('filename')
        autor = item.get('autor')
        descricao = item.get('descricao')
        lancamento = item.get('lancamento')
        titulo = item.get('titulo')
        genero = item.get('genero')
        col_id = item.get('id')
        
        insert_query = """
        INSERT INTO manga_collection.manga_details (filename, autor, descricao, lancamento, titulo, genero, col_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (filename, autor, descricao, lancamento, titulo, genero, col_id))
    conn.commit()
    cursor.close()

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="manga_collection"
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

json_file_path = 'manga_collection.manga_details.json'

data = read_json(json_file_path)

conn = connect_db()

if conn:
    insert_data(data, conn)
    conn.close()
