from ..mongodb import db
from datetime import datetime
import time
import json
from bd2_projeto.mongodb import db, db_admin

colecao_admin = db_admin["erros"]
colecao_admin = db_admin["auditoria_inscricoes"]
colecao_admin = db_admin["auditoria_users"]
colecao_admin = db_admin["avaliacoes_pdf.chunks"]
colecao_admin = db_admin["avaliacoes_pdf.files"]
colecao_admin = db_admin["consultas_alunos"]
colecao_admin = db_admin["horarios_pdf.chunks"]
colecao_admin = db_admin["horarios_pdf.files"]
colecao_admin = db_admin["logs"]

def criar_indices():
    try:
        # Índices para logs
        db.logs.create_index("timestamp")
        db.logs.create_index("acao")
        db.logs.create_index([("utilizador", 1), ("timestamp", -1)])
        
        # Índices para auditoria de inscrições
        db.auditoria_inscricoes.create_index("timestamp")
        db.auditoria_inscricoes.create_index("aluno_id")
        db.auditoria_inscricoes.create_index("resultado")
        db.auditoria_inscricoes.create_index([("aluno_id", 1), ("timestamp", -1)])
        
        # Índices para consultas
        db.consultas_alunos.create_index("timestamp")
        db.consultas_alunos.create_index("aluno_id")
        db.consultas_alunos.create_index("tipo_consulta")
        
        # Índices para atividades de docentes
        db.atividades_docentes.create_index("timestamp")
        db.atividades_docentes.create_index("docente_id")
        
        # Índices para propostas de estágio
        db.proposta_estagio.create_index("timestamp")
        db.proposta_estagio.create_index("aluno_id")
        db.proposta_estagio.create_index("status")
        db.proposta_estagio.create_index([("aluno_id", 1), ("timestamp", -1)])
        
        # Índices para favoritos
        db.favoritos.create_index("aluno_id")
        db.favoritos.create_index("proposta_id")
        db.favoritos.create_index([("aluno_id", 1), ("proposta_id", 1)], unique=True)
        
        print("Índices MongoDB criados com sucesso")
    except Exception as e:
        print(f"Erro ao criar índices: {str(e)}")


def adicionar_log(acao, detalhes=None, request=None):
    log = {
        "acao": acao,
        "detalhes": detalhes or {},
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Adicionar contexto se request fornecido
    if request:
        log["contexto"] = {
            "ip": request.META.get('REMOTE_ADDR', 'desconhecido'),
            "user_agent": request.META.get('HTTP_USER_AGENT', 'desconhecido')[:200],
            "metodo": request.method,
            "caminho": request.path,
            "utilizador": getattr(request.user, 'username', 'anonimo') if request.user.is_authenticated else 'anonimo'
        }
    
    db.logs.insert_one(log)
    return log

def listar_logs(filtro=None, limite=100):
    return list(db.logs.find(filtro or {}, {"_id": 0}).sort("timestamp", -1).limit(limite))

def registar_auditoria_inscricao(aluno_id, turno_id, uc_id, uc_nome, resultado, motivo_rejeicao=None, tempo_ms=0):
    auditoria = {
        "aluno_id": aluno_id,
        "turno_id": turno_id,
        "uc_id": uc_id,
        "uc_nome": uc_nome,
        "resultado": resultado,
        "motivo_rejeicao": motivo_rejeicao,
        "tempo_processamento_ms": tempo_ms,
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db.auditoria_inscricoes.insert_one(auditoria)
    return auditoria

def validar_inscricao_disponivel(aluno_id, turno_id):
    # Verificar se já tem inscrição neste turno
    existe = db.auditoria_inscricoes.find_one({
        "aluno_id": aluno_id,
        "turno_id": turno_id,
        "resultado": "sucesso"
    })
    
    if existe:
        return False, "Já está inscrito neste turno"
    
    return True, "Pode inscrever"

def registar_consulta_aluno(aluno_id, aluno_nome, tipo_consulta, detalhes=None):
    consulta = {
        "aluno_id": aluno_id,
        "aluno_nome": aluno_nome,
        "tipo_consulta": tipo_consulta,
        "detalhes": detalhes or {},
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db.consultas_alunos.insert_one(consulta)
    return consulta

def registar_atividade_docente(docente_id, docente_nome, tipo_atividade, detalhes=None):
    atividade = {
        "docente_id": docente_id,
        "docente_nome": docente_nome,
        "tipo_atividade": tipo_atividade,
        "detalhes": detalhes or {},
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db.atividades_docentes.insert_one(atividade)
    return atividade

def criar_proposta_estagio(aluno_id, aluno_nome, titulo, descricao, empresa, orientador=None, status="pendente"):
    proposta = {
        "aluno_id": aluno_id,
        "aluno_nome": aluno_nome,
        "titulo": titulo,
        "descricao": descricao,
        "empresa": empresa,
        "orientador": orientador,
        "status": status,
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    result = db_admin.proposta_estagio.insert_one(proposta)
    proposta["_id"] = result.inserted_id
    return proposta

def listar_propostas_estagio(filtro=None, limite=100):
    return list(db.proposta_estagio.find(filtro or {}, {"_id": 0}).sort("timestamp", -1).limit(limite))

def atualizar_proposta_estagio(aluno_id, titulo, updates):
    updates["timestamp"] = datetime.now()
    updates["data_formatada"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    result = db_admin.proposta_estagio.update_one(
        {"aluno_id": aluno_id, "titulo": titulo},
        {"$set": updates}
    )
    return result.modified_count > 0

def eliminar_proposta_estagio(aluno_id, titulo):
    result = db_admin.proposta_estagio.delete_one({"aluno_id": aluno_id, "titulo": titulo})
    return result.deleted_count > 0

def adicionar_favorito(aluno_id, proposta_id):
    favorito = {
        "aluno_id": aluno_id,
        "proposta_id": proposta_id,
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Evita duplicatas
    db.favoritos.update_one(
        {"aluno_id": aluno_id, "proposta_id": proposta_id},
        {"$set": favorito},
        upsert=True
    )
    return True

def remover_favorito(aluno_id, proposta_id):
    result = db.favoritos.delete_one({"aluno_id": aluno_id, "proposta_id": proposta_id})
    return result.deleted_count > 0

def verificar_favorito(aluno_id, proposta_id):
    return db.favoritos.find_one({"aluno_id": aluno_id, "proposta_id": proposta_id}) is not None

def listar_favoritos(aluno_id):
    # Busca os favoritos do aluno
    favoritos = list(db.favoritos.find({"aluno_id": aluno_id}, {"_id": 0, "proposta_id": 1}))
    
    if not favoritos:
        return []
    
    # Busca as propostas correspondentes
    proposta_ids = [int(fav["proposta_id"]) for fav in favoritos]
    propostas = list(db.proposta_estagio.find({"id_proposta": {"$in": proposta_ids}}))
    
    return propostas

def analisar_taxa_sucesso_inscricoes(filtro_uc_id=None):
    pipeline = [
        {
            "$group": {
                "_id": "$resultado",
                "count": {"$sum": 1},
                "tempo_medio_ms": {"$avg": "$tempo_processamento_ms"},
                "tempo_max_ms": {"$max": "$tempo_processamento_ms"}
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    if filtro_uc_id:
        pipeline.insert(0, {"$match": {"uc_id": filtro_uc_id}})
    
    return list(db_admin.auditoria_inscricoes.aggregate(pipeline))

def analisar_inscricoes_por_dia():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$timestamp"
                    }
                },
                "total_tentativas": {"$sum": 1},
                "sucesso": {
                    "$sum": {
                        "$cond": [{"$eq": ["$resultado", "sucesso"]}, 1, 0]
                    }
                }
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    return list(db_admin.auditoria_inscricoes.aggregate(pipeline))

def analisar_alunos_mais_ativos():
    pipeline = [
        {
            "$group": {
                "_id": "$aluno_id",
                "total_tentativas": {"$sum": 1},
                "sucessos": {
                    "$sum": {
                        "$cond": [{"$eq": ["$resultado", "sucesso"]}, 1, 0]
                    }
                },
                "taxa_sucesso": {
                    "$avg": {
                        "$cond": [{"$eq": ["$resultado", "sucesso"]}, 1, 0]
                    }
                }
            }
        },
        {
            "$sort": {"total_tentativas": -1}
        },
        {
            "$limit": 20
        }
    ]
    return list(db_admin.auditoria_inscricoes.aggregate(pipeline))

def analisar_ucs_mais_procuradas():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "uc_id": "$uc_id",
                    "uc_nome": "$uc_nome"
                },
                "total_tentativas": {"$sum": 1},
                "sucessos": {
                    "$sum": {
                        "$cond": [{"$eq": ["$resultado", "sucesso"]}, 1, 0]
                    }
                }
            }
        },
        {
            "$sort": {"sucessos": -1}
        }
    ]
    return list(db_admin.auditoria_inscricoes.aggregate(pipeline))

def analisar_turnos_sobrecarregados():
    pipeline = [
        {
            "$match": {"resultado": "turno_cheio"}
        },
        {
            "$group": {
                "_id": "$turno_id",
                "rejeicoes_por_limite": {"$sum": 1}
            }
        },
        {
            "$sort": {"rejeicoes_por_limite": -1}
        }
    ]
    return list(db_admin.auditoria_inscricoes.aggregate(pipeline))

def registar_erro(funcao, erro_msg, detalhes=None):
    erro = {
        "funcao": funcao,
        "erro_msg": erro_msg,
        "detalhes": detalhes or {},
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db_admin.erros.insert_one(erro)
    return erro

def _parse_ts(doc):
    ts = doc.get("timestamp") or doc.get("data_formatada")
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(ts, fmt)
            except Exception:
                continue
    return None

def _str_val(val):
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    try:
        return json.dumps(val, ensure_ascii=False)
    except Exception:
        return str(val)


def listar_eventos_mongo(filtro_acao=None, filtro_entidade=None, limite=500):
    eventos = []
    limite = 1000 if limite > 1000 else (100 if limite < 1 else limite)

    def add_evento(doc, fonte, operacao, entidade, chave="", utilizador="", ip="", user_agent="", detalhes=None):
        # filtros
        if filtro_acao and str(operacao).lower() != str(filtro_acao).lower():
            return
        if filtro_entidade and filtro_entidade.lower() not in str(entidade).lower():
            return
        ts_dt = _parse_ts(doc) or datetime.min
        eventos.append({
            "id": str(doc.get("_id", "")),
            "fonte": fonte,
            "data": ts_dt,
            "data_display": doc.get("data_formatada") or (ts_dt.strftime("%Y-%m-%d %H:%M:%S") if ts_dt != datetime.min else ""),
            "operacao": operacao,
            "entidade": entidade,
            "chave": chave,
            "utilizador": utilizador,
            "ip": ip,
            "user_agent": user_agent,
            "detalhes": _str_val(detalhes),
        })

    # Coleção logs
    filtro_logs = {}
    if filtro_acao:
        filtro_logs["acao"] = filtro_acao
    for log in db.logs.find(filtro_logs, {"_id": 0}).sort("timestamp", -1).limit(limite):
        det = log.get("detalhes") or {}
        ent = det.get("entidade", "") if isinstance(det, dict) else ""
        add_evento(
            log,
            fonte="Mongo",
            operacao=log.get("acao", ""),
            entidade=ent,
            chave=det.get("chave", "") if isinstance(det, dict) else "",
            utilizador=(log.get("contexto") or {}).get("utilizador", ""),
            ip=(log.get("contexto") or {}).get("ip", ""),
            user_agent=(log.get("contexto") or {}).get("user_agent", ""),
            detalhes=det,
        )

    # Consultas de alunos
    for doc in db.consultas_alunos.find({}, {"_id": 0}).sort("timestamp", -1).limit(limite):
        add_evento(
            doc,
            fonte="Mongo",
            operacao=doc.get("tipo_consulta", "consulta_aluno"),
            entidade="consulta_aluno",
            chave=doc.get("aluno_id", ""),
            utilizador=doc.get("aluno_nome", ""),
            detalhes=doc.get("detalhes") or {},
        )

    # Atividades de docentes
    for doc in db.atividades_docentes.find({}, {"_id": 0}).sort("timestamp", -1).limit(limite):
        add_evento(
            doc,
            fonte="Mongo",
            operacao=doc.get("tipo_atividade", "atividade_docente"),
            entidade="atividade_docente",
            chave=doc.get("docente_id", ""),
            utilizador=doc.get("docente_nome", ""),
            detalhes=doc.get("detalhes") or {},
        )

    # Auditoria de inscrições
    for doc in db.auditoria_inscricoes.find({}, {"_id": 0}).sort("timestamp", -1).limit(limite):
        add_evento(
            doc,
            fonte="Mongo",
            operacao=doc.get("resultado", "auditoria_inscricao"),
            entidade="auditoria_inscricao",
            chave=f"{doc.get('aluno_id', '')}:{doc.get('turno_id', '')}",
            utilizador=doc.get("aluno_id", ""),
            detalhes={
                "uc": doc.get("uc_nome", ""),
                "motivo": doc.get("motivo_rejeicao", ""),
                "tempo_ms": doc.get("tempo_processamento_ms", 0),
            },
        )

    # Erros
    for doc in db_admin.erros.find({}, {"_id": 0}).sort("timestamp", -1).limit(limite):
        add_evento(
            doc,
            fonte="Mongo",
            operacao="erro",
            entidade=doc.get("funcao", "erro"),
            chave="",
            utilizador="",
            detalhes={
                "erro": doc.get("erro_msg", ""),
                "detalhes": doc.get("detalhes") or {},
            },
        )

    # Ordenar e cortar
    eventos = sorted(eventos, key=lambda e: e.get("data") or datetime.min, reverse=True)
    return eventos[:limite]

def registar_auditoria_user(operacao, user_id, user_tipo, detalhes=None, request=None):
    auditoria = {
        "operacao": operacao,
        "user_id": user_id,
        "user_tipo": user_tipo,
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detalhes": detalhes or {}
    }
    
    if request:
        auditoria["contexto"] = {
            "ip": request.META.get('REMOTE_ADDR', 'desconhecido'),
            "user_agent": request.META.get('HTTP_USER_AGENT', 'desconhecido')[:200],
            "admin": getattr(request.user, 'username', 'anonimo') if request.user.is_authenticated else 'anonimo'
        }
    
    db.auditoria_users.insert_one(auditoria)
    return auditoria

def listar_auditoria_users(filtro=None, limite=100):
    return list(db.auditoria_users.find(filtro or {}, {"_id": 0}).sort("timestamp", -1).limit(limite))
