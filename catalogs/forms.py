from django.forms import ModelForm

from .models import Catalog


class CatalogAdminForm(ModelForm):
    class Meta:
        model = Catalog
        fields = "__all__"
