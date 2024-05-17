from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson import ObjectId
import gridfs
import os
import json
from io import BytesIO

app = Flask(__name__)

# config para salvar as imagens na pasta do diretorio do projeto ao fazer upload
dir_proj = os.path.dirname(os.path.abspath(__file__)) 
UPLOAD_FOLDER = os.path.join(dir_proj, 'static', 'img')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
                "col.status": {"$in": ["OK", "COMPRADO"]}
            }
        },
        {
            "$group": {
                "_id": "$titulo",
                "volumes_ok": {"$sum": 1}
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
                'volumes': i,
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

if __name__ == '__main__':
    app.run(debug=True)
