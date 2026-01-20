
from django.db import models

class Aluno(models.Model):
    n_mecanografico = models.IntegerField(primary_key=True)
    id_curso = models.ForeignKey('Curso', models.DO_NOTHING, db_column='id_curso')
    id_anocurricular = models.ForeignKey('AnoCurricular', models.DO_NOTHING, db_column='id_anocurricular')
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'aluno'

class AnoCurricular(models.Model):
    id_anocurricular = models.AutoField(primary_key=True)
    ano_curricular = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'ano_curricular'

class AnoLetivo(models.Model):
    id_anoletivo = models.AutoField(primary_key=True)
    anoletivo = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'ano_letivo'

class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    grau = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'curso'

class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    n_turno = models.IntegerField()
    tipo = models.CharField(max_length=255)
    capacidade = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'turno'

class Docente(models.Model):
    id_docente = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'docente'

class Horario(models.Model):
    id_horario = models.AutoField(primary_key=True)
    id_anoletivo = models.ForeignKey(AnoLetivo, models.DO_NOTHING, db_column='id_anoletivo', blank=True, null=True)
    id_semestre = models.ForeignKey('Semestre', models.DO_NOTHING, db_column='id_semestre')
    horario = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'horario'

class HorarioPDF(models.Model):
    nome = models.CharField(max_length=200, default="Horário Oficial")
    ficheiro = models.FileField(upload_to="horarios/")
    id_curso = models.ForeignKey(
        Curso,
        models.DO_NOTHING,
        db_column="id_curso",
        null=True,
        blank=True
    )
    id_anocurricular = models.ForeignKey(
        AnoCurricular,
        models.DO_NOTHING,
        db_column="id_anocurricular",
        null=True,
        blank=True
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        curso = self.id_curso.nome if self.id_curso else "Curso desconhecido"
        ano = self.id_anocurricular.ano_curricular if self.id_anocurricular else "Ano desconhecido"
        return f"{self.nome} - {curso} - {ano}"

class AvaliacaoPDF(models.Model):
    nome = models.CharField(max_length=200, default="Calendário de Avaliações")
    ficheiro = models.FileField(upload_to="avaliacoes/")
    id_curso = models.ForeignKey(
        Curso,
        models.DO_NOTHING,
        db_column="id_curso",
        null=True,
        blank=True
    )
    id_anocurricular = models.ForeignKey(
        AnoCurricular,
        models.DO_NOTHING,
        db_column="id_anocurricular",
        null=True,
        blank=True
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        curso = self.id_curso.nome if self.id_curso else "Curso desconhecido"
        ano = self.id_anocurricular.ano_curricular if self.id_anocurricular else "Ano desconhecido"
        return f"{self.nome} - {curso} - {ano}"

class InscricaoTurno(models.Model):
    id_inscricao = models.AutoField(primary_key=True)
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico')
    id_turno = models.ForeignKey(Turno, models.DO_NOTHING, db_column='id_turno', blank=True, null=True)
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular', blank=True, null=True)
    data_inscricao = models.DateField()

    class Meta:
        managed = False
        db_table = 'inscricao_turno'

class InscritoUc(models.Model):
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico', primary_key=True)
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular')
    estado = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'inscrito_uc'
        unique_together = (('n_mecanografico', 'id_unidadecurricular'),)
    
    def __str__(self):
        return f"{self.n_mecanografico} - {self.id_unidadecurricular}"

class LecionaUc(models.Model):
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular')
    id_docente = models.ForeignKey(Docente, models.DO_NOTHING, db_column='id_docente')

    class Meta:
        managed = False
        db_table = 'leciona_uc'
        unique_together = (('id_unidadecurricular', 'id_docente'),)

class Matricula(models.Model):
    id_matricula = models.AutoField(primary_key=True)
    id_anoletivo = models.ForeignKey(AnoLetivo, models.DO_NOTHING, db_column='id_anoletivo')
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico')
    data_matricula = models.DateField()
    estado = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'matricula'

class Semestre(models.Model):
    id_semestre = models.AutoField(primary_key=True)
    semestre = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'semestre'

class TurnoUc(models.Model):
    id_turno = models.OneToOneField(Turno, models.DO_NOTHING, db_column='id_turno', primary_key=True)
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular')
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        managed = False
        db_table = 'turno_uc'

class UnidadeCurricular(models.Model):
    id_unidadecurricular = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    ects = models.FloatField()
    id_anocurricular = models.ForeignKey(AnoCurricular, models.DO_NOTHING, db_column='id_anocurricular')
    id_semestre = models.ForeignKey(Semestre, models.DO_NOTHING, db_column='id_semestre')
    id_curso = models.ForeignKey(Curso, models.DO_NOTHING, db_column='id_curso')

    class Meta:
        managed = False
        db_table = 'unidade_curricular'

class VwTopDocenteUcAnoCorrente(models.Model):
    id_docente = models.IntegerField()
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    total_ucs = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_top_docente_uc_ano_corrente'

class VwAlunosInscricoes2025(models.Model):
    id_inscricao = models.IntegerField()
    data_inscricao = models.DateField()
    n_mecanografico = models.IntegerField()
    aluno_nome = models.CharField(max_length=255)
    aluno_email = models.CharField(max_length=255)
    id_unidadecurricular = models.IntegerField()
    uc_nome = models.CharField(max_length=255)
    id_turno = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_alunos_inscricoes_2025'

class LogEvento(models.Model):
    id_log = models.AutoField(primary_key=True)
    data_hora = models.DateTimeField()
    operacao = models.CharField(max_length=255)
    detalhes = models.TextField()
    utilizador_db = models.CharField(max_length=255)
    chave_primaria = models.CharField(max_length=255)
    entidade = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'log_eventos'
        ordering = ['-data_hora']

class AuditoriaInscricao(models.Model):
    RESULTADO_CHOICES = [
        ('sucesso', 'Sucesso'),
        ('turno_cheio', 'Turno Cheio'),
        ('conflito_horario', 'Conflito de Horário'),
        ('nao_autorizado', 'Não Autorizado'),
        ('uc_duplicada', 'UC Duplicada'),
        ('erro_sistema', 'Erro do Sistema'),
    ]
    
    id_auditoria = models.AutoField(primary_key=True)
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico', null=True, blank=True)
    id_turno = models.ForeignKey(Turno, models.DO_NOTHING, db_column='id_turno', null=True, blank=True)
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular', null=True, blank=True)
    data_tentativa = models.DateTimeField(auto_now_add=True)
    resultado = models.CharField(max_length=50, choices=RESULTADO_CHOICES)
    motivo_rejeicao = models.TextField(null=True, blank=True)
    tempo_processamento_ms = models.IntegerField(default=0, help_text="Tempo de processamento em millisegundos")
    
    class Meta:
        managed = True
        db_table = 'auditoria_inscricao'
        ordering = ['-data_tentativa']
        indexes = [
            models.Index(fields=['n_mecanografico', '-data_tentativa']),
            models.Index(fields=['resultado']),
            models.Index(fields=['data_tentativa']),
        ]
    
    def __str__(self):
        return f"{self.n_mecanografico} — {self.id_unidadecurricular.nome} ({self.resultado})" if self.n_mecanografico else "Auditoria desconhecida"


# VISTAS MATERIALIZADAS
class MvEstatisticasTurno(models.Model):
    id_turno = models.IntegerField(primary_key=True)
    n_turno = models.IntegerField()
    tipo = models.CharField(max_length=255)
    capacidade = models.IntegerField()
    id_unidadecurricular = models.IntegerField()
    uc_nome = models.CharField(max_length=255)
    ects = models.FloatField()
    curso_nome = models.CharField(max_length=255)
    ano_curricular = models.CharField(max_length=255)
    total_inscritos = models.IntegerField()
    vagas_disponiveis = models.IntegerField()
    taxa_ocupacao_percent = models.DecimalField(max_digits=5, decimal_places=2)
    turno_cheio = models.BooleanField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        managed = False
        db_table = 'mv_estatisticas_turno'

class MvResumoInscricoesAluno(models.Model):
    n_mecanografico = models.IntegerField(primary_key=True)
    aluno_nome = models.CharField(max_length=255)
    aluno_email = models.CharField(max_length=255)
    curso_nome = models.CharField(max_length=255)
    ano_curricular = models.CharField(max_length=255)
    total_ucs_inscritas = models.IntegerField()
    total_turnos_inscritos = models.IntegerField()
    total_ects = models.FloatField()
    primeira_inscricao = models.DateField(null=True)
    ultima_inscricao = models.DateField(null=True)
    dias_com_atividade = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mv_resumo_inscricoes_aluno'

class MvUcsMaisProcuradas(models.Model):
    id_unidadecurricular = models.IntegerField(primary_key=True)
    uc_nome = models.CharField(max_length=255)
    ects = models.FloatField()
    curso_nome = models.CharField(max_length=255)
    ano_curricular = models.CharField(max_length=255)
    semestre = models.CharField(max_length=255)
    total_alunos_inscritos = models.IntegerField()
    total_turnos_com_inscricoes = models.IntegerField()
    total_inscricoes = models.IntegerField()
    capacidade_total_turnos = models.IntegerField()
    taxa_preenchimento_global_percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'mv_ucs_mais_procuradas'

class MvCargaDocentes(models.Model):
    id_docente = models.IntegerField(primary_key=True)
    docente_nome = models.CharField(max_length=255)
    docente_email = models.CharField(max_length=255)
    total_ucs = models.IntegerField()
    total_ects_lecionados = models.FloatField()
    total_turnos = models.IntegerField()
    total_alunos_distintos = models.IntegerField()
    ucs_lecionadas = models.TextField()

    class Meta:
        managed = False
        db_table = 'mv_carga_docentes'

class MvInscricoesPorDia(models.Model):
    data = models.DateField(primary_key=True)
    total_inscricoes = models.IntegerField()
    alunos_distintos = models.IntegerField()
    ucs_distintas = models.IntegerField()
    turnos_distintos = models.IntegerField()
    dia_semana = models.IntegerField()
    hora_pico = models.IntegerField()
    nome_dia_semana = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'mv_inscricoes_por_dia'

class MvConflitosHorario(models.Model):
    n_mecanografico = models.IntegerField()
    aluno_nome = models.CharField(max_length=255)
    turno1_id = models.IntegerField()
    uc1_nome = models.CharField(max_length=255)
    turno1_inicio = models.TimeField()
    turno1_fim = models.TimeField()
    turno2_id = models.IntegerField()
    uc2_nome = models.CharField(max_length=255)
    turno2_inicio = models.TimeField()
    turno2_fim = models.TimeField()

    class Meta:
        managed = False
        db_table = 'mv_conflitos_horario'
