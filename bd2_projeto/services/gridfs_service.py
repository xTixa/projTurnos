from gridfs import GridFS
from ..mongodb import db, client
from datetime import datetime
from bson.objectid import ObjectId
import io

# Cria uma instância do GridFS
fs = GridFS(db)

# GridFS para PDFs de horários
fs_horarios = GridFS(db, collection="horarios_pdf")

# GridFS para PDFs de avaliações
fs_avaliacoes = GridFS(db, collection="avaliacoes_pdf")

def upload_pdf_horario(ficheiro_file, nome, id_curso, id_anocurricular):
    try:
        # Lê o conteúdo do ficheiro para memória
        ficheiro_content = ficheiro_file.read()
        
        # Define os metadados que serão guardados com o ficheiro
        metadata = {
            "nome": nome,
            "id_curso": id_curso,
            "id_anocurricular": id_anocurricular,
            "tipo": "horario",
            "upload_data": datetime.now(),
            "tamanho": len(ficheiro_content),  # Tamanho em bytes
            "nome_ficheiro_original": ficheiro_file.name
        }
        
        # Faz upload para o GridFS com metadados
        file_id = fs_horarios.put(
            ficheiro_content,
            filename=nome,
            metadata=metadata
        )
        
        print(f"PDF de horário armazenado no MongoDB com ID: {file_id}")
        
        return {
            "file_id": str(file_id),
            "filename": nome,
            "upload_date": datetime.now(),
            "metadata": metadata
        }
    
    except Exception as e:
        print(f"Erro ao fazer upload do PDF de horário: {str(e)}")
        raise Exception(f"Erro ao armazenar PDF no MongoDB: {str(e)}")


def upload_pdf_avaliacao(ficheiro_file, nome, id_curso, id_anocurricular):
    try:
        ficheiro_content = ficheiro_file.read()
        
        metadata = {
            "nome": nome,
            "id_curso": id_curso,
            "id_anocurricular": id_anocurricular,
            "tipo": "avaliacao",
            "upload_data": datetime.now(),
            "tamanho": len(ficheiro_content),
            "nome_ficheiro_original": ficheiro_file.name
        }
        
        file_id = fs_avaliacoes.put(
            ficheiro_content,
            filename=nome,
            metadata=metadata
        )
        
        print(f"PDF de avaliação armazenado no MongoDB com ID: {file_id}")
        
        return {
            "file_id": str(file_id),
            "filename": nome,
            "upload_date": datetime.now(),
            "metadata": metadata
        }
    
    except Exception as e:
        print(f"Erro ao fazer upload do PDF de avaliação: {str(e)}")
        raise Exception(f"Erro ao armazenar PDF no MongoDB: {str(e)}")

def download_pdf(file_id, tipo_pdf="horario"):
    try:
        # Se file_id for string, converte para ObjectId
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        
        # Escolhe o GridFS correto baseado no tipo
        gridfs_instance = fs_horarios if tipo_pdf == "horario" else fs_avaliacoes
        
        # Recupera o ficheiro do GridFS
        # get() retorna um GridOut object que funciona como um ficheiro
        grid_out = gridfs_instance.get(file_id)
        
        # Cria um BytesIO (ficheiro virtual em memória)
        pdf_bytes = io.BytesIO(grid_out.read())
        pdf_bytes.seek(0)  # Coloca o cursor no início
        
        print(f"PDF {file_id} descarregado do MongoDB")
        
        return pdf_bytes, grid_out.metadata
    
    except Exception as e:
        print(f"Erro ao descarregar PDF: {str(e)}")
        raise Exception(f"Erro ao recuperar PDF do MongoDB: {str(e)}")

def listar_pdfs_horarios(id_curso=None, id_anocurricular=None, limite=10):
    try:
        # Constrói filtro dinâmico baseado nos parâmetros
        filtro = {"metadata.tipo": "horario"}
        
        if id_curso:
            filtro["metadata.id_curso"] = id_curso
        
        if id_anocurricular:
            filtro["metadata.id_anocurricular"] = id_anocurricular
        
        # Busca na coleção de metadados do GridFS
        # Ordena por data de upload (mais recentes primeiro)
        pdfs = list(
            db.horarios_pdf_files.find(filtro)
            .sort("uploadDate", -1)
            .limit(limite)
        )
        
        # Converte ObjectId para string (JSON serializable)
        for pdf in pdfs:
            pdf["_id"] = str(pdf["_id"])
        
        print(f"{len(pdfs)} PDFs de horários encontrados")
        
        return pdfs
    
    except Exception as e:
        print(f"Erro ao listar PDFs de horários: {str(e)}")
        return []


def listar_pdfs_avaliacoes(id_curso=None, id_anocurricular=None, limite=10):
    try:
        # Filtro similar ao dos horários
        filtro = {"metadata.tipo": "avaliacao"}
        
        if id_curso:
            filtro["metadata.id_curso"] = id_curso
        
        if id_anocurricular:
            filtro["metadata.id_anocurricular"] = id_anocurricular
        
        # Busca na coleção de metadados do GridFS para avaliações
        pdfs = list(
            db.avaliacoes_pdf_files.find(filtro)
            .sort("uploadDate", -1)
            .limit(limite)
        )
        
        # Converte ObjectId para string
        for pdf in pdfs:
            pdf["_id"] = str(pdf["_id"])
        
        print(f"{len(pdfs)} PDFs de avaliações encontrados")
        
        return pdfs
    
    except Exception as e:
        print(f"Erro ao listar PDFs de avaliações: {str(e)}")
        return []

def eliminar_pdf(file_id, tipo_pdf="horario"):
    try:
        
        # Se file_id for string, converte para ObjectId
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        
        # Escolhe o GridFS correto
        gridfs_instance = fs_horarios if tipo_pdf == "horario" else fs_avaliacoes
        
        # Deleta o ficheiro (também apaga automaticamente chunks relacionados)
        gridfs_instance.delete(file_id)
        
        print(f"PDF {file_id} eliminado do MongoDB")
        
        return True
    
    except Exception as e:
        print(f"Erro ao eliminar PDF: {str(e)}")
        return False

def atualizar_metadados_pdf(file_id, nome_novo=None, tipo_pdf="horario"):
    try:
        
        # Se file_id for string, converte para ObjectId
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        
        # Escolhe a coleção de ficheiros correta
        colecao_ficheiros = db.horarios_pdf_files if tipo_pdf == "horario" else db.avaliacoes_pdf_files
        
        # Atualiza apenas se nome_novo foi fornecido
        atualizacoes = {}
        if nome_novo:
            atualizacoes["filename"] = nome_novo
            atualizacoes["metadata.nome"] = nome_novo
        
        # Adiciona timestamp de atualização
        atualizacoes["metadata.atualizado_em"] = datetime.now()
        
        # Executa a atualização na BD
        resultado = colecao_ficheiros.update_one(
            {"_id": file_id},
            {"$set": atualizacoes}
        )
        
        if resultado.modified_count > 0:
            print(f"Metadados do PDF {file_id} atualizados")
            return True
        else:
            print(f"PDF {file_id} não encontrado")
            return False
    
    except Exception as e:
        print(f"Erro ao atualizar metadados: {str(e)}")
        return False

def obter_stats_armazenamento():
    try:
        # Conta documentos de horários
        total_horarios = db.horarios_pdf_files.count_documents({})
        
        # Conta documentos de avaliações
        total_avaliacoes = db.avaliacoes_pdf_files.count_documents({})
        
        # Soma tamanho total de todos os horários
        pipeline_horarios = [
            {"$group": {"_id": None, "tamanho_total": {"$sum": "$length"}}}
        ]
        resultado_horarios = list(db.horarios_pdf_files.aggregate(pipeline_horarios))
        tamanho_horarios = resultado_horarios[0]["tamanho_total"] if resultado_horarios else 0
        
        # Soma tamanho total de todas as avaliações
        pipeline_avaliacoes = [
            {"$group": {"_id": None, "tamanho_total": {"$sum": "$length"}}}
        ]
        resultado_avaliacoes = list(db.avaliacoes_pdf_files.aggregate(pipeline_avaliacoes))
        tamanho_avaliacoes = resultado_avaliacoes[0]["tamanho_total"] if resultado_avaliacoes else 0
        
        stats = {
            "total_horarios": total_horarios,
            "total_avaliacoes": total_avaliacoes,
            "tamanho_horarios_mb": round(tamanho_horarios / (1024 * 1024), 2),
            "tamanho_avaliacoes_mb": round(tamanho_avaliacoes / (1024 * 1024), 2),
            "tamanho_total_mb": round((tamanho_horarios + tamanho_avaliacoes) / (1024 * 1024), 2)
        }
        
        return stats
    
    except Exception as e:
        print(f"Erro ao obter estatísticas: {str(e)}")
        return {}
