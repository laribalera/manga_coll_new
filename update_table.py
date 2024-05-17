from pymongo import MongoClient
import gridfs
import os

client = MongoClient('localhost', 27017)
# se precisar, trocar table
db = client['manga_collection']
table = db['all_titles']

# coloca aqui o nome da coluna que quer criar 
#table.update_many({}, {"$set": {"genero": ""}})

#print("Campos adicionados")


# deletar colunas

#table.deleteMany({ "titulo": "teste" })

#deletar coluna

table.update_many({}, { "$unset": { "andamento": "" } })