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

if __name__ == '__main__':
    app.run(debug=True)
