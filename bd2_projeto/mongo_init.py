"""
Script de inicialização do MongoDB
Executa setup necessário (índices, coleções especiais)
Chamar em manage.py shell ou em signals do Django
"""

from bd2_projeto.mongodb import db
from bd2_projeto.services.mongo_service import criar_indices
from datetime import datetime


def inicializar_mongodb():
    """Executa todas as inicializações necessárias no MongoDB"""
    
    print("=" * 50)
    print("🚀 Inicializando MongoDB...")
    print("=" * 50)
    
    # ✅ 1. Criar índices
    print("\n📊 Criando índices...")
    criar_indices()
    
    # ✅ 2. Criar coleção time-series para análise temporal
    try:
        print("\n⏰ Criando coleção time-series...")
        db.create_collection(
            "inscricoes_timeline",
            timeseries={
                "timeField": "timestamp",
                "metaField": "metadata",
                "granularity": "hours"
            }
        )
        print("  ✓ Coleção time-series criada")
    except Exception as e:
        print(f"  ⚠ Coleção time-series pode já existir: {str(e)}")
    
    # ✅ 3. Criar índice de TTL para limpeza automática de logs antigos
    try:
        print("\n🗑️ Criando índice TTL para limpeza automática...")
        # Logs com mais de 30 dias são deletados automaticamente
        db.logs.create_index("timestamp", expireAfterSeconds=30*24*60*60)
        print("  ✓ Índice TTL criado (30 dias)")
    except Exception as e:
        print(f"  ⚠ Índice TTL pode já existir: {str(e)}")
    
    # ✅ 4. Validação de schemas (optional)
    try:
        print("\n✔️ Configurando validação de schema...")
        db.command({
            "collMod": "auditoria_inscricoes",
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["aluno_id", "resultado", "timestamp"],
                    "properties": {
                        "aluno_id": {"bsonType": "int"},
                        "turno_id": {"bsonType": "int"},
                        "resultado": {"enum": ["sucesso", "turno_cheio", "conflito_horario", "nao_autorizado", "uc_duplicada", "erro_sistema"]},
                        "timestamp": {"bsonType": "date"},
                        "tempo_processamento_ms": {"bsonType": "int"}
                    }
                }
            }
        })
        print("  ✓ Validação de schema configurada")
    except Exception as e:
        print(f"  ⚠ Validação pode já estar configurada: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ MongoDB inicializado com sucesso!")
    print("=" * 50)


if __name__ == "__main__":
    inicializar_mongodb()
