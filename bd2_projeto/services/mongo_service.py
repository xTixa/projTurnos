from ..mongodb import db
from datetime import datetime

def adicionar_log(acao, detalhes=None):
    log = {
        "acao": acao,
        "detalhes": detalhes or {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db.logs.insert_one(log)
    return log

def listar_logs():
    return list(db.logs.find({}, {"_id": 0}))
