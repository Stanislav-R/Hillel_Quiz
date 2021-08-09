from django.contrib import admin

from .models import Choice, Exam, Question, Result


admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Result)
