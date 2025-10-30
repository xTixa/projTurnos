from django.db import models

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

class Semestre(models.Model):
    id_semestre = models.AutoField(primary_key=True)
    semestre = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'semestre'

class UnidadeCurricular(models.Model):
    id_unidadecurricular = models.AutoField(primary_key=True)
    id_semestre = models.ForeignKey(Semestre, models.DO_NOTHING, db_column='id_semestre')
    id_anocurricular = models.ForeignKey(AnoCurricular, models.DO_NOTHING, db_column='id_anocurricular')
    ects = models.IntegerField()
    nome = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'unidade_curricular'

class Aluno(models.Model):
    n_mecanografico = models.IntegerField(primary_key=True)
    id_curso = models.ForeignKey(Curso, models.DO_NOTHING, db_column='id_curso')
    id_anocurricular = models.ForeignKey(AnoCurricular, models.DO_NOTHING, db_column='id_anocurricular')
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'aluno'

class Horario(models.Model):
    id_horario = models.AutoField(primary_key=True)
    id_anoletivo = models.ForeignKey(AnoLetivo, models.DO_NOTHING, db_column='id_anoletivo', blank=True, null=True)
    id_semestre = models.ForeignKey(Semestre, models.DO_NOTHING, db_column='id_semestre')
    horario = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'horario'

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
    id_unidadecurricular = models.ForeignKey(UnidadeCurricular, models.DO_NOTHING, db_column='id_unidadecurricular')

    class Meta:
        managed = False
        db_table = 'turno_uc'
        unique_together = (('id_turno', 'id_unidadecurricular'),)

class InscricaoTurno(models.Model):
    id_inscricao = models.AutoField(primary_key=True)
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico')
    id_turno = models.ForeignKey(TurnoUc, models.DO_NOTHING, db_column='id_turno', blank=True, null=True, related_name='inscricao_turnos_turno')
    id_unidadecurricular = models.IntegerField(blank=True, null=True)
    data_inscricao = models.DateField()

    class Meta:
        managed = False
        db_table = 'inscricao_turno'

class InscritoUc(models.Model):
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico')
    id_unidadecurricular = models.ForeignKey(UnidadeCurricular, models.DO_NOTHING, db_column='id_unidadecurricular')
    estado = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'inscrito_uc'
        unique_together = (('n_mecanografico', 'id_unidadecurricular'),)

class Matricula(models.Model):
    id_matricula = models.AutoField(primary_key=True)
    id_anoletivo = models.ForeignKey(AnoLetivo, models.DO_NOTHING, db_column='id_anoletivo')
    n_mecanografico = models.ForeignKey(Aluno, models.DO_NOTHING, db_column='n_mecanografico')
    data_matricula = models.DateField()
    estado = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'matricula'

class LecionaUc(models.Model):
    id_unidadecurricular = models.ForeignKey(UnidadeCurricular, models.DO_NOTHING, db_column='id_unidadecurricular')
    id_docente = models.ForeignKey(Docente, models.DO_NOTHING, db_column='id_docente')

    class Meta:
        managed = False
        db_table = 'leciona_uc'
        unique_together = (('id_unidadecurricular', 'id_docente'),)
