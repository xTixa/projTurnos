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

