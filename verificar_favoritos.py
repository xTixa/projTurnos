from bd2_projeto.services.mongo_service import listar_favoritos, verificar_favorito

# Substitua pelo ID do aluno que quer verificar
aluno_id = 1  # Exemplo: ID do aluno

print(f"Favoritos do aluno {aluno_id}:")
favoritos = listar_favoritos(aluno_id)
if favoritos:
    for fav in favoritos:
        print(f" - Proposta ID: {fav['proposta_id']}")
else:
    print("Nenhum favorito encontrado.")

# Verificar uma proposta específica
proposta_id = "675a1234567890abcdef12345"  # Substitua pelo ID da proposta
is_fav = verificar_favorito(aluno_id, proposta_id)
print(f"A proposta {proposta_id} é favorita? {is_fav}")</content>
<parameter name="filePath">c:\Users\User\Desktop\bd2\projTurnos\verificar_favoritos.py