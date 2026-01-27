import json
from core.utils import registar_log, admin_required, aluno_required, user_required, docente_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connections
from django.shortcuts import render
from django.contrib import messages
from core.utils import admin_required

def _executar_funcao_lote(nome_func, conteudo_csv):
    with connections["admin"].cursor() as cursor:
        cursor.execute(f"SELECT {nome_func}(%s)", [conteudo_csv])

@admin_required
@require_http_methods(["POST"])
def importar_alunos_csv(request):
    if 'file' not in request.FILES:
        return JsonResponse({'erro': 'Ficheiro não enviado.'}, status=400)
    file = request.FILES['file']
    try:
        conteudo_csv = file.read().decode('utf-8')
    except UnicodeDecodeError:
        file.seek(0)
        conteudo_csv = file.read().decode('latin1')
    try:
        _executar_funcao_lote('importar_alunos_csv', conteudo_csv)
        return JsonResponse({'status': 'ok'})
    except Exception as exc:
        return JsonResponse({'status': 'erro', 'detalhe': str(exc)}, status=500)

@admin_required
def admin_import_data(request):
    if request.method == "POST":
        if 'file' not in request.FILES:
            messages.error(request, "Ficheiro não enviado.")
            return render(request, "admin/import_data.html")
        file = request.FILES['file']
        try:
            conteudo_csv = file.read().decode('utf-8')
        except UnicodeDecodeError:
            file.seek(0)
            conteudo_csv = file.read().decode('latin1')
        print('--- CSV LIDO ---')
        print(conteudo_csv)
        try:
            _executar_funcao_lote('importar_alunos_csv', conteudo_csv)
            messages.success(request, "Importação concluída com sucesso!")
        except Exception as exc:
            messages.error(request, f"Erro na importação: {exc}")
    return render(request, "admin/import_data.html")

@admin_required
@require_http_methods(["POST"])
def importar_alunos_json(request):
    if 'file' not in request.FILES:
        messages.error(request, "Ficheiro não enviado.")
        return render(request, "admin/import_data.html")
    file = request.FILES['file']
    try:
        conteudo_json = file.read().decode('utf-8')
    except UnicodeDecodeError:
        file.seek(0)
        conteudo_json = file.read().decode('latin1')
    print('--- JSON LIDO ---')
    print(conteudo_json)
    try:
        # Valida se é um array de objetos
        data = json.loads(conteudo_json)
        if not isinstance(data, list):
            messages.error(request, "O ficheiro JSON deve conter uma lista de alunos.")
            return render(request, "admin/import_data.html")
        with connections["admin"].cursor() as cursor:
            cursor.execute("SELECT importar_alunos_json(%s::json)", [json.dumps(data)])
        messages.success(request, "Importação de alunos (JSON) concluída com sucesso!")
    except Exception as exc:
        messages.error(request, f"Erro na importação JSON: {exc}")
    return render(request, "admin/import_data.html")
