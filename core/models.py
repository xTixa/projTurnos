from django.db import models

# =======================
# MODELO: ALUNO
# Alunos matriculados, referencia curso e ano curricular
# =======================
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

# =======================
# MODELO: ANOCURRICULAR
# Lista de anos curriculares (ex: 1º, 2º, 3º)
# =======================
class AnoCurricular(models.Model):
    id_anocurricular = models.AutoField(primary_key=True)
    ano_curricular = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'anocurricular'

# =======================
# MODELO: ANOLETIVO
# Anos letivos (ex: 2025/2026)
# =======================
class AnoLetivo(models.Model):
    id_anoletivo = models.AutoField(primary_key=True)
    anoletivo = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'anoletivo'

# =======================
# MODELO: CURSO
# Cursos oferecidos (ex: Engenharia Informática)
# =======================
class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    grau = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'curso'

# =======================
# MODELO: DOCENTE
# Professores/docentes do curso
# =======================
class Docente(models.Model):
    id_docente = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'docente'

# =======================
# MODELO: HORARIO
# Horários de turnos/semestre
# =======================
class Horario(models.Model):
    id_horario = models.AutoField(primary_key=True)
    id_anoletivo = models.ForeignKey('AnoLetivo', models.DO_NOTHING, db_column='id_anoletivo', null=True)
    id_semestre = models.ForeignKey('Semestre', models.DO_NOTHING, db_column='id_semestre')
    horario = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'horario'

# =======================
# MODELO: INSCRICAOTURNO
# Registos de inscrição em turnos, relaciona aluno e turno_uc
# =======================
class InscricaoTurno(models.Model):
    id_inscricao = models.AutoField(primary_key=True)
    n_mecanografico = models.ForeignKey('Aluno', models.DO_NOTHING, db_column='n_mecanografico')
    id_turno = models.ForeignKey('TurnoUc', models.DO_NOTHING, db_column='id_turno', null=True)
    id_unidadecurricular = models.ForeignKey('TurnoUc', models.DO_NOTHING, db_column='id_unidadecurricular', null=True)
    data_inscricao = models.DateField()

    class Meta:
        managed = False
        db_table = 'inscricaoturno'

# =======================
# MODELO: INSCRITOUC
# Inscrições do aluno em cada UC, inclui estado (ativo/inativo)
# PK composta por n_mecanografico e id_unidadecurricular
# =======================
class InscritoUc(models.Model):
    n_mecanografico = models.ForeignKey('Aluno', models.DO_NOTHING, db_column='n_mecanografico')
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular')
    estado = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'inscritouc'
        unique_together = (('n_mecanografico', 'id_unidadecurricular'),)

# =======================
# MODELO: LECIONAUC
# Relacionamento docente-UC (quem leciona cada UC)
# PK composta por id_unidadecurricular e id_docente
# =======================
class LecionaUc(models.Model):
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular')
    id_docente = models.ForeignKey('Docente', models.DO_NOTHING, db_column='id_docente')

    class Meta:
        managed = False
        db_table = 'lecionauc'
        unique_together = (('id_unidadecurricular', 'id_docente'),)

# =======================
# MODELO: MATRICULA
# Matrículas dos alunos em anos letivos
# =======================
class Matricula(models.Model):
    id_matricula = models.AutoField(primary_key=True)
    id_anoletivo = models.ForeignKey('AnoLetivo', models.DO_NOTHING, db_column='id_anoletivo')
    n_mecanografico = models.ForeignKey('Aluno', models.DO_NOTHING, db_column='n_mecanografico')
    data_matricula = models.DateField()
    estado = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'matricula'

# =======================
# MODELO: SEMESTRE
# Semestres letivos
# =======================
class Semestre(models.Model):
    id_semestre = models.AutoField(primary_key=True)
    semestre = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'semestre'

# =======================
# MODELO: TURNO
# Turnos com capacidade e tipo (ex: Laboratório/Teórico)
# =======================
class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    n_turno = models.IntegerField()
    tipo = models.CharField(max_length=255)
    capacidade = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'turno'

# =======================
# MODELO: TURNOUC
# Turnos de cada unidade curricular (PK composta)
# =======================
class TurnoUc(models.Model):
    id_turno = models.ForeignKey('Turno', models.DO_NOTHING, db_column='id_turno')
    id_unidadecurricular = models.ForeignKey('UnidadeCurricular', models.DO_NOTHING, db_column='id_unidadecurricular')

    class Meta:
        managed = False
        db_table = 'turnouc'
        unique_together = (('id_turno', 'id_unidadecurricular'),)

# =======================
# MODELO: UNIDADECURRICULAR
# Unidades curriculares/disciplina do curso
# =======================
class UnidadeCurricular(models.Model):
    id_unidadecurricular = models.AutoField(primary_key=True)
    id_semestre = models.ForeignKey('Semestre', models.DO_NOTHING, db_column='id_semestre')
    id_anocurricular = models.ForeignKey('AnoCurricular', models.DO_NOTHING, db_column='id_anocurricular')
    ects = models.IntegerField()
    nome = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'unidadecurricular'

