from pymongo import MongoClient

# MongoDB - User "admin" (projTurnos)
MONGO_URI_ADMIN = "mongodb+srv://projTurnos:projTurnos123@projturnoscluster.sjnik21.mongodb.net/?retryWrites=true&w=majority&appName=projTurnosCluster"

# MongoDB - User "app" (app_user_mongo)
MONGO_URI_APP = "mongodb+srv://app_user_mongo:123@projturnoscluster.sjnik21.mongodb.net/?retryWrites=true&w=majority&appName=projTurnosCluster"

# Clients
client_admin = MongoClient(MONGO_URI_ADMIN)
client_app = MongoClient(MONGO_URI_APP)

# Bases de dados
db_admin = client_admin["projTurnos"]
db_app = client_app["projTurnos"]

# Por default, usa app
db = db_app

# Teste de ligação
if __name__ == "__main__":
    try:
        client_admin.admin.command('ping')
        print("[✓] Client ADMIN conectado com sucesso!")
    except Exception as e:
        print(f"[✗] Erro ao conectar ADMIN: {e}")
    
    try:
        client_app.admin.command('ping')
        print("[✓] Client APP conectado com sucesso!")
    except Exception as e:
        print(f"[✗] Erro ao conectar APP: {e}")
