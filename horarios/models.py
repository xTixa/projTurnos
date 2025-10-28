from django.db import models

class Semester(models.TextChoices):
    S1 = "1S", "1.º Semestre"
    S2 = "2S", "2.º Semestre"

class ScheduleType(models.TextChoices):
    NORMAL = "NORMAL", "Horário"
    COMP = "COMPENSACAO", "Compensação"

class Degree(models.Model):
    code = models.CharField(max_length=20, unique=True, default="EI")
    name = models.CharField(max_length=120, default="Engenharia Informática")
    def __str__(self): return f"{self.code} — {self.name}"

class CourseYear(models.IntegerChoices):
    Y1 = 1, "1.º Ano"
    Y2 = 2, "2.º Ano"
    Y3 = 3, "3.º Ano"

class Shift(models.TextChoices):
    # ajusta conforme precise (T1..T5 e/ou Turno 1/2)
    T1 = "T1", "T1"
    T2 = "T2", "T2"
    T3 = "T3", "T3"
    T4 = "T4", "T4"
    T5 = "T5", "T5"

class Schedule(models.Model):
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)       # "2025/2026"
    course_year = models.IntegerField(choices=CourseYear.choices)
    semester = models.CharField(max_length=2, choices=Semester.choices)
    schedule_type = models.CharField(max_length=12, choices=ScheduleType.choices, default=ScheduleType.NORMAL)
    shift = models.CharField(max_length=3, choices=Shift.choices, blank=True)  # opcional (só se aplicável)
    title = models.CharField(max_length=150, default="Horário")
    file = models.FileField(upload_to="horarios/", blank=True, null=True)      # se fores guardar PDFs
    external_url = models.URLField(blank=True, null=True)                      # se preferires link externo
    last_changed = models.DateField(blank=True, null=True)                     # “alterado a …”
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-academic_year","course_year","semester","schedule_type","shift"]

    def __str__(self):
        return f"{self.academic_year} {self.get_course_year_display()} {self.get_semester_display()} {self.get_schedule_type_display()} {self.shift or ''}".strip()
