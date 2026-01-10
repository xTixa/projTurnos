from django.shortcuts import render, redirect
from bd2_projeto.mongodb import db  # importa o db do mongodb.py

def caixa_sugestoes(request):
    if (not request.user.is_authenticated) and ("user_id" not in request.session):
        return redirect("home:login")
    mensagem = None
    colecao = db["sugestao"]

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        if texto:
            if request.user.is_authenticated:
                autor_id = request.user.id
                autor_nome = request.user.username
                autor_email = request.user.email
            else:
                autor_id = request.session.get("user_id")
                autor_nome = request.session.get("user_nome")
                autor_email = request.session.get("user_email")
            colecao.insert_one({
                "texto": texto,
                "autor_id": autor_id,
                "autor_nome": autor_nome,
                "auto_email": autor_email,
                "Like" : 0,
                "Dislike" : 0,
            })
            mensagem = "Sugestão gravada com sucesso."
        else:
            mensagem = "Escreve alguma coisa antes de enviar."
            
    ##lista todas as sugestões ###
    
    sugestoes = list(colecao.find().sort("_id", -1))  # Ordena por mais recente
    context = {
        "sugestoes": sugestoes,
        "mensagem": mensagem,
        "area": "extra",  # chave para o base.html decidir a sidebar
    }
    return render(request, "extra_app/sugestoes.html", context)

