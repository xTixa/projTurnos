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
    id_curso = models.IntegerField()
    id_anocurricular = models.IntegerField()
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
    id_anoletivo = models.IntegerField()
    nome = models.CharField(max_length=255)
    grau = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'curso'


class Docente(models.Model):
    id_docente = models.AutoField(primary_key=True)
    id_curso = models.IntegerField(blank=True, null=True)
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'docente'


class Horario(models.Model):
    id_horario = models.AutoField(primary_key=True)
    id_anoletivo = models.IntegerField(blank=True, null=True)
    id_turno = models.IntegerField(blank=True, null=True)
    id_semestre = models.IntegerField()
    horario = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'horario'


class InscricaoTurno(models.Model):
    id_inscricao = models.AutoField(primary_key=True)
    n_mecanografico = models.IntegerField()
    id_turno = models.IntegerField()
    data_inscricao = models.DateField()

    class Meta:
        managed = False
        db_table = 'inscricao_turno'


class InscritoUc(models.Model):
    pk = models.CompositePrimaryKey('n_mecanografico', 'id_unidadecurricular')
    n_mecanografico = models.IntegerField()
    id_unidadecurricular = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'inscrito_uc'


class LecionaUc(models.Model):
    pk = models.CompositePrimaryKey('id_unidadecurricular', 'id_docente')
    id_unidadecurricular = models.IntegerField()
    id_docente = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'leciona_uc'


class Matricula(models.Model):
    id_matricula = models.AutoField(primary_key=True)
    id_curso = models.IntegerField()
    id_anoletivo = models.IntegerField()
    n_mecanografico = models.IntegerField()
    data_matricula = models.DateField()
    estado = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'matricula'


class Pertencer(models.Model):
    pk = models.CompositePrimaryKey('n_mecanografico', 'id_turno')
    n_mecanografico = models.IntegerField()
    id_turno = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pertencer'


class Relationship19(models.Model):
    pk = models.CompositePrimaryKey('id_semestre', 'id_anoletivo')
    id_semestre = models.IntegerField()
    id_anoletivo = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'relationship_19'


class Semestre(models.Model):
    id_semestre = models.AutoField(primary_key=True)
    id_anocurricular = models.IntegerField(blank=True, null=True)
    semestre = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'semestre'


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    n_turno = models.IntegerField()
    tipo = models.CharField(max_length=255)
    capacidade = models.IntegerField()
    duracao = models.TimeField()

    class Meta:
        managed = False
        db_table = 'turno'


class TurnoUc(models.Model):
    pk = models.CompositePrimaryKey('id_turno', 'id_unidadecurricular')
    id_turno = models.IntegerField()
    id_unidadecurricular = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'turno_uc'


class UnidadeCurricular(models.Model):
    id_unidadecurricular = models.AutoField(primary_key=True)
    id_curso = models.IntegerField()
    id_semestre = models.IntegerField()
    id_anocurricular = models.IntegerField()
    ects = models.IntegerField()
    nome = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'unidade_curricular'
