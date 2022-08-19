from django_filters import rest_framework as filters

from projects.models import ProjectControl


class ProjectControlFilter(filters.FilterSet):
    class Meta:
        model = ProjectControl
        fields = {
            "status": ["exact", "iexact", "in", ]
        }
