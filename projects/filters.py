from django_filters import rest_framework as filters

from .models import ProjectControl


class ProjectControlListFilter(filters.FilterSet):
    class Meta:
        model = ProjectControl
        fields = ["status"]
