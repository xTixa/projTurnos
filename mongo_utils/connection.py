from pymongo import MongoClient
from django.conf import settings

def get_mongo_collection(collection_name=None):
    host = settings.MONGO["HOST"]
    port = settings.MONGO["PORT"]
    db_name = settings.MONGO["DB_NAME"]
    client = MongoClient(host, port)
    db = client[db_name]
    if collection_name:
        return db[collection_name]
    return db
