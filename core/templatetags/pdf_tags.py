# ==========================================
# TEMPLATE TAGS PARA SERVIR PDFs DO MongoDB
# ==========================================
#
# Este módulo cria template tags customizados para gerar URLs
# de PDFs armazenados no MongoDB via GridFS

from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def pdf_url(pdf_obj, tipo_pdf):
    """
    Gera o URL correto para um PDF, seja do MongoDB ou do filesystem
    
    Args:
        pdf_obj: Objeto HorarioPDF ou AvaliacaoPDF
        tipo_pdf: Tipo do PDF ("horario" ou "avaliacao")
    
    Returns:
        URL do PDF (MongoDB ou media)
    
    Uso no template:
        {% load pdf_tags %}
        <a href="{% pdf_url item.pdf 'horario' %}">Ver PDF</a>
    """
    try:
        # ==========================================
        # VERIFICA SE ESTÁ NO MongoDB
        # ==========================================
        # Se o ficheiro começa com "mongodb_gridfs:", está no MongoDB
        ficheiro_path = str(pdf_obj.ficheiro)
        
        if ficheiro_path.startswith("mongodb_gridfs:"):
            # Extrai o file_id do MongoDB
            file_id = ficheiro_path.replace("mongodb_gridfs:", "")
            
            # Gera URL da view que serve PDFs do MongoDB
            # Formato: /pdf-mongodb/horario/FILE_ID/
            return reverse('home:servir_pdf_mongodb', kwargs={
                'tipo_pdf': tipo_pdf,
                'file_id': file_id
            })
        
        # ==========================================
        # SE NÃO ESTÁ NO MongoDB, USA URL NORMAL
        # ==========================================
        # Para ficheiros no filesystem (compatibilidade com PDFs antigos)
        return pdf_obj.ficheiro.url
    
    except Exception as e:
        # Se algo correr mal, retorna "#" (link vazio)
        print(f"Erro ao gerar URL do PDF: {str(e)}")
        return "#"


@register.filter
def is_mongodb_pdf(pdf_obj):
    """
    Verifica se um PDF está no MongoDB
    
    Args:
        pdf_obj: Objeto HorarioPDF ou AvaliacaoPDF
    
    Returns:
        True se está no MongoDB, False caso contrário
    
    Uso no template:
        {% if item.pdf|is_mongodb_pdf %}
            <span>PDF no MongoDB</span>
        {% endif %}
    """
    try:
        ficheiro_path = str(pdf_obj.ficheiro)
        return ficheiro_path.startswith("mongodb_gridfs:")
    except:
        return False
