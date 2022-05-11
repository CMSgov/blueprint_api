from django.contrib import admin

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "acronym", "impact_level", "location", "creator")
    search_fields = ("id", "title", "acronym")
    actions = ["export_as_csv"]


admin.site.register(Project, ProjectAdmin)
