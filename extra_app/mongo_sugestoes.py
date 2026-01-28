# extra_app/mongo_sugestoes.py
from typing import List, Dict, Any, Optional
from bson.objectid import ObjectId
from bd2_projeto.mongodb import db, db_admin
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

colecao = db["sugestao"]
colecao_admin = db_admin["sugestao"]

#ao utilizar o aggregate é possível fazer operações mais complexas no MongoDB. O Processo é feito no servidor MongoDB, 
# o que pode ser mais eficiente para grandes conjuntos de dados.

class Sugestao:
    """Classe para gerenciar sugestões"""

    @staticmethod
    def inserir_sugestao(texto: str, autor_id: str, autor_nome: str, 
                        autor_email: str) -> str:
        """Insere uma nova sugestão"""
        documento = {
            "texto": texto,
            "autor_id": autor_id,
            "autor_nome": autor_nome,
            "auto_email": autor_email,
            "Like": [],
            "Dislike": [],
            "created_at": datetime.now(timezone.utc)
        }
        result = colecao.insert_one(documento)
        return str(result.inserted_id)

    @staticmethod
    def listar_sugestoes_ordenadas() -> List[Dict[str, Any]]:
        """Todas as sugestões, ordenadas por mais recente"""
        return list(colecao.find().sort("_id", -1))

    @staticmethod
    def listar_top5_por_like() -> List[Dict[str, Any]]:
        """
        Top 5 sugestões com mais likes.
        Lógica no Mongo: n_likes = tamanho do array Like, ordenar desc, limitar 5.
        """
        pipeline = [
            {
                "$addFields": {
                    "n_likes": {"$size": {"$ifNull": ["$Like", []]}}
                }
            },
            {"$sort": {"n_likes": -1, "_id": -1}},
            {"$limit": 5},
        ]
        return list(colecao.aggregate(pipeline))

    @staticmethod
    def listar_sugestoes_todas() -> List[Dict[str, Any]]:
        """Lista todas as sugestões ordenadas por mais recente"""
        return list(colecao.find({}).sort("_id", -1))

    @staticmethod
    def toggle_like(sugestao_id: str, user_id: str) -> None:
        """
        Procedimento de like no lado do Mongo.
        Se já tem like: remove.
        Se não tem: adiciona e tira de Dislike.
        """
        try:
            oid = ObjectId(sugestao_id)
        except Exception as e:
            logger.error(f"ID inválido para toggle_like: {e}")
            return

        # tenta remover se já tiver like
        result = colecao.update_one(
            {"_id": oid, "Like": user_id},
            {"$pull": {"Like": user_id}}
        )
        if result.matched_count == 0:
            # não tinha like → adiciona e tira de Dislike
            colecao.update_one(
                {"_id": oid},
                {
                    "$addToSet": {"Like": user_id},
                    "$pull": {"Dislike": user_id},
                }
            )

    @staticmethod
    def toggle_dislike(sugestao_id: str, user_id: str) -> None:
        """
        Procedimento de dislike no lado do Mongo.
        Se já tem dislike: remove.
        Se não tem: adiciona e tira de Like.
        """
        try:
            oid = ObjectId(sugestao_id)
        except Exception as e:
            logger.error(f"ID inválido para toggle_dislike: {e}")
            return

        result = colecao.update_one(
            {"_id": oid, "Dislike": user_id},
            {"$pull": {"Dislike": user_id}}
        )
        if result.matched_count == 0:
            colecao.update_one(
                {"_id": oid},
                {
                    "$addToSet": {"Dislike": user_id},
                    "$pull": {"Like": user_id},
                }
            )

    @staticmethod
    def obter_sugestao_por_id(sugestao_id: str) -> Optional[Dict[str, Any]]:
        """Obtém uma sugestão pelo ID"""
        try:
            oid = ObjectId(sugestao_id)
        except Exception:
            return None
        return colecao_admin.find_one({"_id": oid})

    @staticmethod
    def eliminar_sugestao(sugestao_id: str) -> bool:
        """Elimina uma sugestão pelo ID"""
        try:
            if len(sugestao_id) != 24 or not all(c in '0123456789abcdefABCDEF' for c in sugestao_id):
                return False
            oid = ObjectId(sugestao_id)
        except Exception as e:
            logger.error(f"Erro ao converter ID para ObjectId: {e}")
            return False
        """Elimina uma sugestão pelo ID (apenas admin)"""
        result = colecao_admin.delete_one({"_id": oid})
        return result.deleted_count > 0


