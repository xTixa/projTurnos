from bd2_projeto.services.mongo_service import listar_propostas_estagio

try:
    propostas = listar_propostas_estagio()
    print(f'Encontradas {len(propostas)} propostas')
    if propostas:
        p = propostas[0]
        print('Campos disponíveis:', list(p.keys()))
        print(f'Título: {p.get("titulo")}')
        print(f'Entidade: {p.get("entidade")}')
        print(f'Descrição: {p.get("descricao", "N/A")[:100]}...')
        print(f'Requisitos: {p.get("requisitos")}')
        print(f'Orientador: {p.get("orientador_empresa")}')
except Exception as e:
    print(f'Erro: {e}')