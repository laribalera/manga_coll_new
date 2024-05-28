from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson import ObjectId
import gridfs
import os
import json
from io import BytesIO
import secrets

app = Flask(__name__)

# config para salvar as imagens na pasta do diretorio do projeto ao fazer upload
dir_proj = os.path.dirname(os.path.abspath(__file__)) 
UPLOAD_FOLDER = os.path.join(dir_proj, 'static', 'img')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#secret_key pro flash
app.secret_key = secrets.token_hex(32)


#config do mongo
client = MongoClient('localhost', 27017)
db = client['manga_collection']
fs = gridfs.GridFS(db)
collection_titles = db['all_titles']
collection_volumes = db['all_volumes']
collection_manga = db['manga_details']


@app.route('/')
def index():
    title_data = list(collection_titles.find({}))
    vol_data = list(collection_volumes.find({}))
    manga_det = list(collection_manga.find({}))

    serialized_manga_det = []
    for manga in manga_det:
        serialized_manga = {}
        for key, value in manga.items():
            if isinstance(value, ObjectId):
                serialized_manga[key] = str(value)
            else:
                serialized_manga[key] = value
        serialized_manga_det.append(serialized_manga)

    # recuperando infos para a div coleções
    pipeline = [
    {
        "$lookup": {
            "from": "all_volumes",
            "localField": "titulo",
            "foreignField": "titulo",
            "as": "col"
        }
    },
    {
        "$unwind": "$col"
    },
    {
        "$match": {
            "col.status": {"$in": ["OK", "COMPRADO", "FALTANDO"]}
        }
    },
    {
        "$group": {
            "_id": "$titulo",
            "volumes_ok": {
                "$sum": {
                    "$cond": {
                        "if": {"$ne": ["$col.status", "FALTANDO"]},
                        "then": 1,
                        "else": 0
                    }
                }
            }
        }
    }
    ]

    result = list(collection_titles.aggregate(pipeline))
    
    return render_template('new_index.html', title_data=title_data, vol_data=vol_data, result=result, manga_det=json.dumps(serialized_manga_det))

@app.route('/volumes_page')
def volumes_page():
    vol_data = list(collection_volumes.find({}))

    return render_template('volumes_page.html', vol_data=vol_data)

@app.route('/upload', methods=['POST'])

def insert_infos():
    try:
        form_data = request.form

        # Create new all_titles row
        titles = {
            'volumes': int(form_data['volumes']),
            'titulo': form_data['titulo'],
            'author': form_data['author'],
            'vol_type': form_data['vol_type']
        }
        collection_titles.insert_one(titles)
        
        # Create new all_volumes rows
        count_vol = int(form_data['volumes'])
        volumes_list = []

        for i in range(1, count_vol + 1):
            volumes = {
                'volume': i,
                'titulo': form_data['titulo'],
                'author': form_data['author'],
                'status': form_data['status']
            }
            volumes_list.append(volumes)

        collection_volumes.insert_many(volumes_list)

        # Upload da imagem da capa
        image_id = ObjectId()
        if 'photo' in request.files:
            file = request.files['photo']
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            filename = None

        # Create new manga_details row
        details = {
            '_id': ObjectId(),
            'filename': filename,
            'image_id': image_id,
            'author': form_data['author'],
            'descricao': form_data['descricao'],
            'lancamento': form_data['lancamento'],
            'titulo': form_data['titulo'],
            'genero': form_data['genero']
        }
        collection_manga.insert_one(details)

        return redirect(url_for('index'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/update', methods=['POST'])

def update_collection():
    try:
        form_data = request.form

        volume_id = form_data.get('_id')
        volume = form_data.get('volume')
        titulo = form_data.get('titulo')
        author = form_data.get('author')
        status = form_data.get('status')

        if not (volume_id and volume and titulo and author and status):
            return jsonify({'error': 'Campos obrigatórios.'}), 400


        collection_volumes.update_one({'_id': ObjectId(volume_id)}, {'$set': {'volume': int(volume), 'titulo': titulo, 'author': author, 'status': status}})
        flash('Volume atualizado com sucesso!', 'success')
        
        return redirect(url_for('volumes_page'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#delete volume unico
@app.route('/delete_vol/<id>', methods=['DELETE'])
def delete_vol(id):
    try:
        result = collection_volumes.delete_one({'_id': ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({'message': 'Volume deletado com sucesso'}), 200
        else:
            return jsonify({'message': 'Volume não encontrado'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

#delete coleção    
@app.route('/delete_col/<id>', methods=['DELETE'])
def delete_col(id):
    try:
        col = collection_titles.find_one({'_id': ObjectId(id)})
        if not col:
            return jsonify({'message': 'Coleção não encontrada'}), 404
        
        # delete dos volumes da coleção para otimizar
        delete_result = collection_volumes.delete_many({'titulo': col['titulo']})

        # delete da coleção
        result = collection_titles.delete_one({'_id': ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({
                'message': 'Coleção e volumes deletados com sucesso', 
                'volumes_deletados': delete_result.deleted_count
            }), 200
        else:
            return jsonify({'message': 'Erro ao deletar a coleção'}), 500
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    


if __name__ == '__main__':
    app.run(debug=True)
