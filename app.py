from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['manga_collection']
collection_titles = db['all_titles']
collection_volumes = db['all_volumes']

@app.route('/')
def index():
    title_data = list(collection_titles.find({}, {'_id': 0}))
    vol_data = list(collection_volumes.find({}, {'_id': 0}))

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

    for item in result:
        print(item['_id'], item['volumes_ok'])

    if not result:
        return "0"

    return render_template('index.html', title_data=title_data, vol_data=vol_data, result=result)




if __name__ == '__main__':
    app.run(debug=True)
