import json
import mysql.connector

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# insert dados na tabela manga_collection.all_titles
def insert_data_into_db(data, conn):
    cursor = conn.cursor()
    for item in data:
        titulo = item.get('titulo')
        volumes = item.get('volumes')
        vol_type = item.get('vol_type')
        author = item.get('author')
        
        insert_query = """
        INSERT INTO manga_collection.all_titles (titulo, volumes, vol_type, author)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (titulo, volumes, vol_type, author))
    conn.commit()
    cursor.close()

def connect_to_db():
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

json_file_path = 'manga_collection.all_titles.json'

data = read_json_file(json_file_path)

conn = connect_to_db()

if conn:
    insert_data_into_db(data, conn)
    conn.close()
