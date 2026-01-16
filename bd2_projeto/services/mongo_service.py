from ..mongodb import db
from datetime import datetime
import time
import json

# ==========================================
# INICIALIZAÇÃO — ÍNDICES
# ==========================================

def criar_indices():
    """Cria índices necessários nas coleções MongoDB"""
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
        
        print("✓ Índices MongoDB criados com sucesso")
    except Exception as e:
        print(f"⚠ Erro ao criar índices: {str(e)}")

# ==========================================
# LOGS COM CONTEXTO COMPLETO
# ==========================================

def adicionar_log(acao, detalhes=None, request=None):
    """
    Adiciona log com contexto completo (IP, user-agent, duração)
    
    Args:
        acao: Tipo de ação (ex: 'inscricao_turno', 'consulta_plano')
        detalhes: Dict com dados adicionais
        request: Objeto request do Django (para capturar contexto)
    """
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
    """
    Lista logs com filtro opcional
    
    Args:
        filtro: Dict com filtros (ex: {"acao": "inscricao_turno"})
        limite: Número máximo de logs a retornar
    """
    return list(db.logs.find(filtro or {}, {"_id": 0}).sort("timestamp", -1).limit(limite))

# ==========================================
# AUDITORIA DE INSCRIÇÕES
# ==========================================

def registar_auditoria_inscricao(aluno_id, turno_id, uc_id, uc_nome, resultado, motivo_rejeicao=None, tempo_ms=0):
    """
    Registra tentativa de inscrição em turno (para análise)
    
    Args:
        aluno_id: ID do aluno
        turno_id: ID do turno
        uc_id: ID da UC
        uc_nome: Nome da UC
        resultado: 'sucesso', 'turno_cheio', 'conflito_horario', 'nao_autorizado'
        motivo_rejeicao: Descrição detalhada se rejeitado
        tempo_ms: Tempo de processamento em millisegundos
    """
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
    """
    Valida se aluno pode se inscrever (sem duplicatas)
    Retorna (pode_inscrever: bool, motivo: str)
    """
    # Verificar se já tem inscrição neste turno
    existe = db.auditoria_inscricoes.find_one({
        "aluno_id": aluno_id,
        "turno_id": turno_id,
        "resultado": "sucesso"
    })
    
    if existe:
        return False, "Já está inscrito neste turno"
    
    return True, "Pode inscrever"

# ==========================================
# LOGGING DE CONSULTAS
# ==========================================

def registar_consulta_aluno(aluno_id, aluno_nome, tipo_consulta, detalhes=None):
    """
    Registra quando aluno consulta plano, horários, etc
    
    Args:
        aluno_id: N_mecanografico do aluno
        aluno_nome: Nome do aluno
        tipo_consulta: 'plano_curricular', 'horarios', 'avaliacoes', 'contactos'
        detalhes: Info adicional (ex: qual curso consultou)
    """
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

# ==========================================
# LOGGING DE ATIVIDADES DOCENTES
# ==========================================

def registar_atividade_docente(docente_id, docente_nome, tipo_atividade, detalhes=None):
    """
    Registra atividades de docentes (aulas lecionadas, atualizações, etc)
    
    Args:
        docente_id: ID do docente
        docente_nome: Nome do docente
        tipo_atividade: 'aula_lecionada', 'ausencia', 'atualizacao_grades', etc
        detalhes: Info adicional
    """
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

# ==========================================
# PROPOSTAS DE ESTÁGIO
# ==========================================

def criar_proposta_estagio(aluno_id, aluno_nome, titulo, descricao, empresa, orientador=None, status="pendente"):
    """
    Cria uma nova proposta de estágio
    
    Args:
        aluno_id: ID do aluno
        aluno_nome: Nome do aluno
        titulo: Título da proposta
        descricao: Descrição detalhada
        empresa: Nome da empresa
        orientador: Nome do orientador (opcional)
        status: Status inicial ('pendente', 'aprovada', 'rejeitada')
    """
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
    result = db.proposta_estagio.insert_one(proposta)
    proposta["_id"] = result.inserted_id
    return proposta

def listar_propostas_estagio(filtro=None, limite=100):
    """
    Lista propostas de estágio com filtro opcional
    
    Args:
        filtro: Dict com filtros (ex: {"status": "pendente"})
        limite: Número máximo de propostas a retornar
    """
    return list(db.proposta_estagio.find(filtro or {}, {"_id": 0}).sort("timestamp", -1).limit(limite))

def atualizar_proposta_estagio(aluno_id, titulo, updates):
    """
    Atualiza uma proposta de estágio
    
    Args:
        aluno_id: ID do aluno
        titulo: Título da proposta (para identificar)
        updates: Dict com campos a atualizar
    """
    updates["timestamp"] = datetime.now()
    updates["data_formatada"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    result = db.proposta_estagio.update_one(
        {"aluno_id": aluno_id, "titulo": titulo},
        {"$set": updates}
    )
    return result.modified_count > 0

def deletar_proposta_estagio(aluno_id, titulo):
    """
    Deleta uma proposta de estágio
    
    Args:
        aluno_id: ID do aluno
        titulo: Título da proposta
    """
    result = db.proposta_estagio.delete_one({"aluno_id": aluno_id, "titulo": titulo})
    return result.deleted_count > 0

# ==========================================
# AGGREGATIONS — ANÁLISE DE DADOS
# ==========================================

def analisar_taxa_sucesso_inscricoes(filtro_uc_id=None):
    """
    Analisa taxa de sucesso de inscrições por resultado
    Retorna estatísticas agrupadas
    """
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
    
    return list(db.auditoria_inscricoes.aggregate(pipeline))

def analisar_inscricoes_por_dia():
    """
    Análise temporal: quantas inscrições por dia
    """
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
    return list(db.auditoria_inscricoes.aggregate(pipeline))

def analisar_alunos_mais_ativos():
    """
    Quais alunos fizeram mais tentativas de inscrição
    """
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
    return list(db.auditoria_inscricoes.aggregate(pipeline))

def analisar_ucs_mais_procuradas():
    """
    Quais UCs têm mais inscrições/tentativas
    """
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
    return list(db.auditoria_inscricoes.aggregate(pipeline))

def analisar_turnos_sobrecarregados():
    """
    Quais turnos têm mais rejeições por 'turno_cheio'
    """
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
    return list(db.auditoria_inscricoes.aggregate(pipeline))

# ==========================================
# LOGGING DE ERROS
# ==========================================

def registar_erro(funcao, erro_msg, detalhes=None):
    """
    Registra erros ocorridos no sistema para análise
    """
    erro = {
        "funcao": funcao,
        "erro_msg": erro_msg,
        "detalhes": detalhes or {},
        "timestamp": datetime.now(),
        "data_formatada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db.erros.insert_one(erro)
    return erro

# ==========================================
# AGREGAÇÃO DE LOGS (MÚLTIPLAS COLEÇÕES)
# ==========================================

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
    """
    Consolida eventos das coleções Mongo (logs, consultas_alunos, atividades_docentes,
    auditoria_inscricoes, erros) para exibição unificada.
    """
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
    for doc in db.erros.find({}, {"_id": 0}).sort("timestamp", -1).limit(limite):
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

# ==========================================
# AUDITORIA DE CRUD DE USERS
# ==========================================

def registar_auditoria_user(operacao, user_id, user_tipo, detalhes=None, request=None):
    """
    Registra operações CRUD de utilizadores no MongoDB
    
    Args:
        operacao: 'CREATE', 'UPDATE', 'DELETE'
        user_id: ID do utilizador
        user_tipo: Tipo ('Admin', 'Aluno', 'Docente')
        detalhes: Dict com campos alterados (username, email, etc)
        request: Objeto request do Django
    """
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
    """
    Lista auditoria de users com filtro opcional
    
    Args:
        filtro: Dict com filtros (ex: {"operacao": "CREATE"})
        limite: Número máximo de logs a retornar
    """
    return list(db.auditoria_users.find(filtro or {}, {"_id": 0}).sort("timestamp", -1).limit(limite))
