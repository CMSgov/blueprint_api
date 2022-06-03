from django.contrib import admin

from .models import Catalog

class CatalogAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "file_name", "created", "updated")
    search_fields = ("id", "name", "file_name")
    actions = ["export_as_csv"]

admin.site.register(Catalog, CatalogAdmin)
