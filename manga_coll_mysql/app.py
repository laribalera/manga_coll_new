from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import mysql.connector
import os
import json
import secrets

app = Flask(__name__)

# config para salvar as imagens na pasta do diretorio do projeto ao fazer upload
dir_proj = os.path.dirname(os.path.abspath(__file__)) 
UPLOAD_FOLDER = os.path.join(dir_proj, 'static', 'img')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# secret_key pro flash
app.secret_key = secrets.token_hex(32)

# config do MySQL
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'manga_collection',
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM all_titles")
    title_data = cursor.fetchall()

    cursor.execute("SELECT * FROM all_volumes")
    vol_data = cursor.fetchall()

    cursor.execute("SELECT * FROM manga_details")
    manga_det = cursor.fetchall()

    serialized_manga_det = json.dumps(manga_det)

    # recuperando infos para a div coleções
    query = """
    SELECT t.titulo, SUM(CASE WHEN v.status IN ('OK', 'COMPRADO') THEN 1 ELSE 0 END) AS volumes_ok
    FROM all_titles t
    JOIN all_volumes v ON t.titulo = v.titulo
    WHERE v.status IN ('OK', 'COMPRADO', 'FALTANDO')
    GROUP BY t.titulo
    """
    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('new_index.html', title_data=title_data, vol_data=vol_data, result=result, manga_det=serialized_manga_det)

@app.route('/volumes_page')
def volumes_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM all_volumes")
    vol_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('volumes_page.html', vol_data=vol_data)

@app.route('/upload', methods=['POST'])
def insert_infos():
    try:
        form_data = request.form

        conn = get_db_connection()
        cursor = conn.cursor()

        # Create new all_titles row
        titles_query = """
        INSERT INTO all_titles (volumes, titulo, author, vol_type)
        VALUES (%s, %s, %s, %s)
        """
        titles_data = (int(form_data['volumes']), form_data['titulo'], form_data['author'], form_data['vol_type'])
        cursor.execute(titles_query, titles_data)
        
        # Create new all_volumes rows
        count_vol = int(form_data['volumes'])
        volumes_list = []

        for i in range(1, count_vol + 1):
            volumes_list.append((i, form_data['titulo'], form_data['author'], form_data['status']))

        volumes_query = """
        INSERT INTO all_volumes (volume, titulo, author, status)
        VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(volumes_query, volumes_list)

        # Upload da imagem da capa
        if 'photo' in request.files:
            file = request.files['photo']
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            filename = None

        # Create new manga_details row
        details_query = """
        INSERT INTO manga_details (filename, author, descricao, lancamento, titulo, genero)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        details_data = (filename, form_data['author'], form_data['descricao'], form_data['lancamento'], form_data['titulo'], form_data['genero'])
        cursor.execute(details_query, details_data)

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('index'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update', methods=['POST'])
def update_collection():
    try:
        form_data = request.form

        volume_id = form_data.get('id')
        volume = form_data.get('volume')
        titulo = form_data.get('titulo')
        author = form_data.get('author')
        status = form_data.get('status')

        if not (volume_id and volume and titulo and author and status):
            return jsonify({'error': 'Campos obrigatórios.'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        update_query = """
        UPDATE all_volumes
        SET volume = %s, titulo = %s, author = %s, status = %s
        WHERE id = %s
        """
        update_data = (int(volume), titulo, author, status, volume_id)
        cursor.execute(update_query, update_data)

        conn.commit()
        cursor.close()
        conn.close()

        flash('Volume atualizado com sucesso!', 'success')

        return redirect(url_for('volumes_page'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_vol/<id>', methods=['DELETE'])
def delete_vol(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        delete_query = "DELETE FROM all_volumes WHERE id = %s"
        cursor.execute(delete_query, (id,))

        conn.commit()
        cursor.close()
        conn.close()

        if cursor.rowcount == 1:
            return jsonify({'message': 'Volume deletado com sucesso'}), 200
        else:
            return jsonify({'message': 'Volume não encontrado'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/delete_col/<id>', methods=['DELETE'])
def delete_col(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        find_query = "SELECT titulo FROM all_titles WHERE id = %s"
        cursor.execute(find_query, (id,))
        col = cursor.fetchone()

        if not col:
            return jsonify({'message': 'Coleção não encontrada'}), 404

        # delete dos volumes da coleção para otimizar
        delete_volumes_query = "DELETE FROM all_volumes WHERE titulo = %s"
        cursor.execute(delete_volumes_query, (col['titulo'],))

        # delete da coleção
        delete_collection_query = "DELETE FROM all_titles WHERE id = %s"
        cursor.execute(delete_collection_query, (id,))

        conn.commit()
        cursor.close()
        conn.close()

        if cursor.rowcount == 1:
            return jsonify({
                'message': 'Coleção e volumes deletados com sucesso',
                'volumes_deletados': cursor.rowcount
            }), 200
        else:
            return jsonify({'message': 'Erro ao deletar a coleção'}), 500
    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
