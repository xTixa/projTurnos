from django.db import models

class UCMais4Ects(models.Model):
    id_unidadecurricular = models.IntegerField(primary_key=True)
    id_semestre = models.IntegerField()
    id_anocurricular = models.IntegerField()
    ects = models.IntegerField()
    nome = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'uc_mais4etcs'
        verbose_name = 'UC (>4 ECTS)'
        verbose_name_plural = 'UCs (>4 ECTS)'


class CadeirasSemestre(models.Model):
    id_unidadecurricular = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=255)
    ects = models.IntegerField()
    semestre_id = models.IntegerField()
    semestre_nome = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'cadeirassemestre'
        verbose_name = 'Cadeira (2º semestre)'
        verbose_name_plural = 'Cadeiras (2º semestre)'
        
class AlunosMatriculadosPorDia(models.Model):
    id_matricula = models.IntegerField(primary_key=True)
    n_mecanografico = models.IntegerField()
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    estado = models.CharField(max_length=50)
    data_matricula = models.DateTimeField()
    dia_matricula = models.DateField()
    ano_matricula = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_alunos_matriculados_por_dia'
        
class AlunosPorOrdemAlfabetica(models.Model):
    n_mecanografico = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    id_anocurricular = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_alunos_por_ordem_alfabetica'

class Turnos(models.Model):
    id_turno = models.AutoField(primary_key=True)
    n_turno = models.IntegerField()
    capacidade = models.IntegerField()
    tipo = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'vw_turnos'

class Cursos(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    grau = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'vw_cursos'