from django.contrib import admin
from .models import Degree, Schedule

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ("code","name")

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display  = ("degree","academic_year","course_year","semester","schedule_type","shift","last_changed","published")
    list_filter   = ("degree","academic_year","course_year","semester","schedule_type","shift","published")
    search_fields = ("title",)
