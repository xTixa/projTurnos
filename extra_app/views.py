from django.shortcuts import render, redirect
from bd2_projeto.mongodb import db  # importa o db do mongodb.py
from bson.objectid import ObjectId



def caixa_sugestoes(request):
    if (not request.user.is_authenticated) and ("user_id" not in request.session):
        return redirect("home:login")
    
    mensagem = None
    colecao = db["sugestao"]

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
            colecao.insert_one({
                "texto": texto,
                "autor_id": autor_id,
                "autor_nome": autor_nome,
                "auto_email": autor_email,
                "Like" : [],
                "Dislike" : [],
            })
            mensagem = "Sugestão gravada com sucesso."
        else:
            mensagem = "Escreve alguma coisa antes de enviar."
            
    ##lista todas as sugestões ###
    
    
    
    sugestoes = list(colecao.find().sort("_id", -1))  # Ordena por mais recente
    
    if request.user.is_authenticated:
        user_id = str(request.user.id)
    else:
        user_id = request.session.get("user_id")

    print("USER_ID:", user_id)
    
    for s in sugestoes:
        s["id"] = str(s["_id"]) # Converte ObjectId para string para uso no template
        s["user_liked"] = user_id in s.get("Like", [])
        s["user_disliked"] = user_id in s.get("Dislike", [])
        print("DEBUG:", s["id"], s["user_liked"], s["user_disliked"])

    context = {
        "sugestoes": sugestoes,
        "mensagem": mensagem,
        "area": "extra",  # chave para o base.html decidir a sidebar
    }
    return render(request, "extra_app/sugestoes.html", context)

## Like ou Dislike nas sugestões ###
def feedback_sugestao(request, sugestao_id):
    colecao = db["sugestao"]
    
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
        doc = colecao.find_one({"_id": ObjectId(sugestao_id)})
        if user_id in doc.get("Dislike", []):
            # já tinha like → remove
            colecao.update_one(
            {"_id": ObjectId(sugestao_id)},
            {"$pull": {"Dislike": user_id}}
            )
        else:
            # não tinha like → adiciona e tira de dislike
            colecao.update_one(
                {"_id": ObjectId(sugestao_id)},
                {
                    "$addToSet": {"Dislike": user_id},
                    "$pull": {"Like": user_id},
                }
            )
    elif acao == "like":
        doc = colecao.find_one({"_id": ObjectId(sugestao_id)})
        if user_id in doc.get("Like", []):
            colecao.update_one(
            {"_id": ObjectId(sugestao_id)},
            {"$pull": {"Like": user_id}}
            )
        else: 
            colecao.update_one(
                {"_id": ObjectId(sugestao_id)},
                {
                    "$addToSet": {"Like": user_id},
                    "$pull": {"Dislike": user_id},
                }
            )
    return redirect("extra_app:sugestao")

