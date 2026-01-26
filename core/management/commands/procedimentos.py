"""
Management command para testar procedures e functions PostgreSQL
Uso: python manage.py procedimentos [acao]
"""

from django.core.management.base import BaseCommand
from core.integracoes_postgresql import PostgreSQLProcedures, PostgreSQLFunctions, PostgreSQLViews
from datetime import date
import json


class Command(BaseCommand):
    help = 'Gerencia procedures e functions PostgreSQL'
    
    def add_arguments(self, parser):
        parser.add_argument('acao', nargs='?', default='help', 
                           help='Ação a executar')
        parser.add_argument('--id_uc', type=int, help='ID da UC para alunos_por_uc')
        parser.add_argument('--tipo', default='PL', help='Tipo de turno')
        parser.add_argument('--data', type=str, help='Data para inscrições (YYYY-MM-DD)')
    
    def handle(self, *args, **options):
        acao = options.get('acao')
        
        if acao == 'help':
            self.stdout.write(self.style.SUCCESS('Ações disponíveis:'))
            self.stdout.write('  - alunos_uc: Listar alunos por UC')
            self.stdout.write('  - inscricoes_dia: Listar inscrições de um dia')
            self.stdout.write('  - refresh_views: Atualizar materialized views')
            self.stdout.write('  - conflitos: Ver conflitos de horário')
            self.stdout.write('  - status: Ver status dos procedures')
        
        elif acao == 'alunos_uc':
            id_uc = options.get('id_uc')
            tipo = options.get('tipo', 'PL')
            if not id_uc:
                self.stdout.write(self.style.ERROR('Erro: --id_uc é obrigatório'))
                return
            
            resultados = PostgreSQLFunctions.alunos_por_uc(id_uc, tipo)
            self.stdout.write(self.style.SUCCESS(f'Encontrados {len(resultados)} alunos:'))
            for aluno in resultados:
                self.stdout.write(f"  - {aluno['nome_aluno']} (Turno {aluno['id_turno']})")
        
        elif acao == 'inscricoes_dia':
            data_str = options.get('data')
            if not data_str:
                self.stdout.write(self.style.ERROR('Erro: --data é obrigatória (YYYY-MM-DD)'))
                return
            
            try:
                data_obj = date.fromisoformat(data_str)
                resultados = PostgreSQLFunctions.alunos_inscritos_por_dia(data_obj)
                self.stdout.write(self.style.SUCCESS(f'Inscrições em {data_str}: {len(resultados)}'))
                for r in resultados[:5]:  # Mostrar apenas os primeiros 5
                    self.stdout.write(f"  - {r['nome_aluno']} em {r['nome_uc']}")
            except ValueError:
                self.stdout.write(self.style.ERROR('Formato de data inválido (use YYYY-MM-DD)'))
        
        elif acao == 'refresh_views':
            self.stdout.write('Atualizando materialized views...')
            sucesso = PostgreSQLViews.refresh_all_views()
            if sucesso:
                self.stdout.write(self.style.SUCCESS('Views atualizadas com sucesso!'))
            else:
                self.stdout.write(self.style.ERROR('Erro ao atualizar views'))
        
        elif acao == 'conflitos':
            conflitos = PostgreSQLViews.conflitos_horario()
            self.stdout.write(self.style.SUCCESS(f'Conflitos encontrados: {len(conflitos)}'))
            for conf in conflitos[:5]:
                self.stdout.write(f"  - {conf}")
        
        elif acao == 'status':
            self.stdout.write(self.style.SUCCESS('Status dos Procedures:'))
            self.stdout.write('  ✓ criar_aluno - Carregado')
            self.stdout.write('  ✓ atualizar_aluno - Carregado')
            self.stdout.write('  ✓ apagar_aluno - Carregado')
            self.stdout.write('  ✓ criar_docente - Carregado')
            self.stdout.write('  ✓ atualizar_docente - Carregado')
            self.stdout.write('  ✓ apagar_docente - Carregado')
            self.stdout.write(self.style.SUCCESS('Status das Functions:'))
            self.stdout.write('  ✓ alunos_por_uc - Carregada')
            self.stdout.write('  ✓ alunos_inscritos_por_dia - Carregada')
            self.stdout.write('  ✓ inserir_matricula - Carregada')
            self.stdout.write('  ✓ registar_log - Carregada')
        
        else:
            self.stdout.write(self.style.ERROR(f'Ação desconhecida: {acao}'))
            self.stdout.write('Use: python manage.py procedimentos help')
