Projeto UC - Base de Dados II. 

David Borges - 27431
Susana Tavares - 27467
Patricia Oliveira - 22525
Ana Almeida - 27467

# Iniciar ambiente virtual
python -m venv nome_do_ambiente

# Inicia ambiente virtual
.\venv\Scripts\activate

## Requirements 
pip install -r requirements.txt

## Inciar projeto
django-admin startproject <nome_do_projeto>

## Iniciar django
python manage.py runserver

#####################################

## Criar nova app
python manage.py startapp nome_projeto 

## settings.py (INSTALLED_APPS)
INSTALLED_APPS = [
    # ...
    "nome_projeto",
]
