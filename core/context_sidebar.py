from .models import Aluno

def user_cursotdm(request):
    context = {
        'is_aluno_ei': False,
        'is_aluno_tdm': False,
        'is_aluno_rsi': False,
        'is_aluno_dwdm': False,
        'is_aluno_mestrado': False,
    }
    
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        try:
            aluno = Aluno.objects.get(n_mecanografico=request.session["user_id"])
            
            # Define as flags baseado no id_curso
            if aluno.id_curso_id == 1:
                context['is_aluno_ei'] = True
            elif aluno.id_curso_id == 2:
                context['is_aluno_tdm'] = True
            elif aluno.id_curso_id == 3:
                context['is_aluno_rsi'] = True
            elif aluno.id_curso_id == 4:
                context['is_aluno_dwdm'] = True
            elif aluno.id_curso_id == 5:
                context['is_aluno_mestrado'] = True
                
        except Aluno.DoesNotExist:
            pass
    
    return context