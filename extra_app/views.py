from django.shortcuts import render, redirect
from huggingface_hub import login
from bd2_projeto.mongodb import db_admin  # importa o db do mongodb.py
from extra_app.mongo_sugestoes import Sugestao
from django.contrib import messages
from bson.errors import InvalidId
from django.core.paginator import Paginator


def caixa_sugestoes(request):
    if (not request.user.is_authenticated) and ("user_id" not in request.session):
        return redirect("home:login")
    
    mensagem = None

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        print("VIEW FEEDBACK", texto, request.POST)
        
        if texto:
            if request.user.is_authenticated:
                autor_id = str(request.user.id)
                autor_nome = request.user.username
                autor_email = request.user.email
            else:
                autor_id = request.session.get("user_id")
                autor_nome = request.session.get("user_nome")
                autor_email = request.session.get("user_email")
            
            # Usa a classe Sugestao para inserir
            Sugestao.inserir_sugestao(texto, autor_id, autor_nome, autor_email)
            mensagem = "Sugestão gravada com sucesso."
        else:
            mensagem = "Escreve alguma coisa antes de enviar."
    
    # Lista todas as sugestões
    sugestoes = Sugestao.listar_sugestoes_ordenadas()
    
    # Top 5 com mais likes (usa aggregate no Mongo!)
    sugestoes_top = Sugestao.listar_top5_por_like()
    
    if request.user.is_authenticated:
        user_id = str(request.user.id)
    else:
        user_id = request.session.get("user_id")

    print("USER_ID:", user_id)
    
    # Adiciona campos para o template
    for s in sugestoes:
        s["id"] = str(s["_id"])
        s["user_liked"] = user_id in s.get("Like", [])
        s["user_disliked"] = user_id in s.get("Dislike", [])
        print("DEBUG:", s["id"], s["user_liked"], s["user_disliked"])

    # Converte top5 também
    for s in sugestoes_top:
        s["id"] = str(s["_id"])
        s["user_liked"] = user_id in s.get("Like", [])
        s["user_disliked"] = user_id in s.get("Dislike", [])

    return render(request, 'extra_app/sugestoes.html', {
        'sugestoes': sugestoes,
        'sugestoes_top': sugestoes_top,
        'mensagem': mensagem,
        'area': 'extra',    
    })


def feedback_sugestao(request, sugestao_id):
    print("ID DA VIEW:", repr(sugestao_id))

    if request.user.is_authenticated:
        user_id = str(request.user.id)
    else:
        user_id = request.session.get("user_id")

    if not user_id:
        return redirect("home:login")
    
    acao = request.POST.get("acao")
    print("acao", acao, request.POST)
    
    if acao == "dislike":
        Sugestao.toggle_dislike(sugestao_id, user_id)
    elif acao == "like":
        Sugestao.toggle_like(sugestao_id, user_id)
    
    return redirect("extra_app:sugestoes_todas")


def sugestoes_eliminar(request, sugestao_id):
    """
    Elimina uma sugestão apenas para users staff.
    Redireciona para lista após delete ou erro.
    """
    # Verifica staff
    if not request.user.is_staff:
        messages.error(request, "Sem permissão para eliminar sugestões.")
        return redirect("extra_app:sugestoes_todas")
    
    # Usa o método da classe Sugestao
    if Sugestao.eliminar_sugestao(sugestao_id):
        messages.success(request, "Sugestão eliminada com sucesso!")
    else:
        messages.error(request, "Erro ao eliminar: ID inválido ou sugestão não existe.")
    
    return redirect("extra_app:sugestoes_todas")


def sugestoes_todas(request):
    if request.user.is_authenticated:
        user_id = str(request.user.id)
    else:
        user_id = request.session.get("user_id")

    if not user_id:
        return redirect("home:login")
    
    # Lista todas as sugestões
    sugestoes = Sugestao.listar_sugestoes_todas()
    
    # Adiciona campos para o template
    for s in sugestoes:
        s["id"] = str(s["_id"])
        s["user_liked"] = user_id in s.get("Like", [])
        s["user_disliked"] = user_id in s.get("Dislike", [])

    context = {
        "area": "extra",
        "sugestoes": sugestoes,
    }
    return render(request, "extra_app/sugestoes_todas.html", context)
