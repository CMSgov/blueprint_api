from django.contrib import admin

from .forms import ComponentAdminForm
from .models import Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    form = ComponentAdminForm
    list_display = ("title", "catalog", "created", "updated")
