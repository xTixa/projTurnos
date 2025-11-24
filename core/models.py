# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
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


class InscricaoTurno(models.Model):
    id_inscricao = models.AutoField(primary_key=True)
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico')
    id_turno = models.ForeignKey('TurnoUc', models.DO_NOTHING, db_column='id_turno', blank=True, null=True)
    id_unidadecurricular = models.IntegerField(blank=True, null=True)
    data_inscricao = models.DateField()

    class Meta:
        managed = False
        db_table = 'inscricao_turno'


class InscritoUc(models.Model):
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico')
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular')
    estado = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'inscrito_uc'
        unique_together = (('n_mecanografico', 'id_unidadecurricular'),)


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


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    n_turno = models.IntegerField()
    tipo = models.CharField(max_length=255)
    capacidade = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'turno'


class TurnoUc(models.Model):
    id_turno = models.ForeignKey(Turno, models.DO_NOTHING, db_column='id_turno')
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular')

    class Meta:
        managed = False
        db_table = 'turno_uc'
        unique_together = (('id_turno', 'id_unidadecurricular'),)


class UnidadeCurricular(models.Model):
    id_unidadecurricular = models.AutoField(primary_key=True)
    id_semestre = models.ForeignKey(Semestre, models.DO_NOTHING, db_column='id_semestre')
    id_anocurricular = models.ForeignKey(AnoCurricular, models.DO_NOTHING, db_column='id_anocurricular')
    ects = models.IntegerField()
    nome = models.CharField(max_length=255)

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


class HorarioPDF(models.Model):
    nome = models.CharField(max_length=200, default="Horário Oficial")
    ficheiro = models.FileField(upload_to="horarios/")
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.atualizado_em.date()})"