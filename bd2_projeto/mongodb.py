from pymongo import MongoClient


MONGO_URI = "mongodb+srv://projTurnos:projTurnos123@projturnoscluster.sjnik21.mongodb.net/?retryWrites=true&w=majority&appName=projTurnosCluster"

client = MongoClient(MONGO_URI)

db = client["projTurnos"]
