from django.contrib import admin

from .forms import CatalogAdminForm
from .models import Catalog


class CatalogAdmin(admin.ModelAdmin):
    form = CatalogAdminForm
    list_display = ("id", "name", "file_name", "created", "updated")
    search_fields = ("id", "name", "file_name")
    actions = ["export_as_csv"]


admin.site.register(Catalog, CatalogAdmin)
