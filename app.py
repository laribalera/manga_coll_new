from flask import Flask, render_template, request, jsonify, send_file
from pymongo import MongoClient
from bson import ObjectId
import json


app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['manga_collection']
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

@app.route('/insert_infos', methods=['POST'])

def insert_infos():
    form_data = request.form

    #create new all_titles row
    titles = {
        'volumes': int(form_data['volumes']),
        'titulo': form_data['titulo'],
        'author': form_data['author']  ,   
        'vol_type': form_data['vol_type']
        }
    collection_titles.insert_one(titles) 
    
    #create new all_volumes row
    count_vol = int(form_data['volumes'])
    volumes_list = []

    for i in range(1, count_vol + 1):
        volumes = {
            'volumes': i,
            'titulo': form_data['titulo'],
            'author': form_data['author']  ,   
            'status': form_data['status']
            }  
        volumes_list.append(volumes)

    collection_volumes.insert_many(volumes_list)

    #create new manga_details row
    cover = form_data['capa']
    #ajustar para subir a imagem da capa


    details = {
        'filename': , 
        'author': form_data['author'],
        'descricao': form_data['descricao'],
        'lancamento': form_data['lancamento'],
        'titulo': form_data['titulo'],
        'genero': form_data['genero']
        }

    collection_manga.insert_one(details)


if __name__ == '__main__':
    app.run(debug=True)
