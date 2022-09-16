from django.contrib import admin

from .forms import ComponentAdminForm
from .models import Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    form = ComponentAdminForm
    list_display = ("id", "title", "supported_catalog_versions", "created", "updated")
