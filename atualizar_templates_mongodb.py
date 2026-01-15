"""
Script para atualizar todos os templates HTML que usam pdf.ficheiro.url
para usar o novo template tag pdf_url que suporta MongoDB GridFS

Este script:
1. Adiciona {% load pdf_tags %} nos templates
2. Substitui {{ item.pdf.ficheiro.url }} por {% pdf_url item.pdf 'tipo' %}
"""

import os
import re

# Caminhos dos templates (relativos)
# Obtém o diretório atual do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "core", "templates")

# Mapeamento de ficheiros para tipo de PDF
HORARIOS_FILES = [
    "tdm/horarios_tdm.html",
    "ei/horarios.html",
    "rsi/horarios_rsi.html",
    "eisi/horarios_mestrado.html",
    "dwdm/horarios_dwdm.html"
]

AVALIACOES_FILES = [
    "tdm/avaliacoes_tdm.html",
    "ei/avaliacoes.html",
    "rsi/avaliacoes_rsi.html",
    "eisi/avaliacoes_mestrado.html",
    "dwdm/avaliacoes_dwdm.html"
]


def atualizar_template(filepath, tipo_pdf):
    """Atualiza um template para usar pdf_tags"""
    
    caminho_completo = os.path.join(TEMPLATES_DIR, filepath)
    
    if not os.path.exists(caminho_completo):
        print(f"Ficheiro não encontrado: {filepath}")
        return False
    
    # Lê o conteúdo
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Verifica se já tem o load pdf_tags
    if '{% load pdf_tags %}' in conteudo:
        print(f"Já atualizado: {filepath}")
        return False
    
    # Adiciona {% load pdf_tags %} após {% load static %}
    conteudo = conteudo.replace(
        '{% load static %}',
        '{% load static %}\n{% load pdf_tags %}'
    )
    
    # Substitui {{ item.pdf.ficheiro.url }} por {% pdf_url item.pdf 'tipo' %}
    # Padrão mais flexível para capturar variações
    padrao = r'{{\s*(\w+\.pdf)\.ficheiro\.url\s*}}'
    substituicao = r"{% pdf_url \1 '" + tipo_pdf + r"' %}"
    
    conteudo_novo = re.sub(padrao, substituicao, conteudo)
    
    # Salva o ficheiro atualizado
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        f.write(conteudo_novo)
    
    print(f"Atualizado: {filepath}")
    return True


def main():
    """Executa as atualizações"""
    print("=" * 60)
    print("ATUALIZAÇÃO DE TEMPLATES PARA USAR MONGODB GridFS")
    print("=" * 60)
    
    print("\nAtualizando templates de HORÁRIOS...")
    for ficheiro in HORARIOS_FILES:
        atualizar_template(ficheiro, 'horario')
    
    print("\nAtualizando templates de AVALIAÇÕES...")
    for ficheiro in AVALIACOES_FILES:
        atualizar_template(ficheiro, 'avaliacao')
    
    print("\n" + "=" * 60)
    print("ATUALIZAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print("\nOs templates agora usam {% pdf_url %} que:")
    print("  • Serve PDFs do MongoDB se começarem com 'mongodb_gridfs:'")
    print("  • Serve PDFs do filesystem para PDFs antigos (compatibilidade)")
    print("=" * 60)


if __name__ == "__main__":
    main()
