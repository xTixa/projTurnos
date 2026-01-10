from django.shortcuts import render
from bd2_projeto.mongodb import db  # importa o db do mongodb.py


def caixa_sugestoes(request):
    mensagem = None
    colecao = db["sugestao"]

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        if texto:
            colecao.insert_one({"texto": texto})
            mensagem = "Sugestão gravada com sucesso."
        else:
            mensagem = "Escreve alguma coisa antes de enviar."
    context = {
        "mensagem": mensagem,
        "area": "extra",  # <- chave para o base.html decidir a sidebar
    }
    return render(request, "extra_app/sugestoes.html", context)


