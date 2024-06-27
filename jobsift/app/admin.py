from django.contrib import admin
from .forms import JobBoardSelectorForm
from .models import JobBoardSelector

class JobBoardSelectorAdmin(admin.ModelAdmin):
    form = JobBoardSelectorForm

admin.site.register(JobBoardSelector, JobBoardSelectorAdmin)